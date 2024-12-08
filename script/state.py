import dataclasses as dc
import os
import re
from pathlib import Path
import collections as cl
import subprocess

from script import OuterRelease
from script.production import update_production

state_template = Path("../templates/state.html").read_text()
qualities = {
    0: "missed",
    1: "bad",
    2: "poor",
    3: "good",
    4: "enough",
    5: "perfect"
}
base_url = "https://raw.githubusercontent.com/vlegchilkin/collection"


def format_date(value):
    return value.replace("+", "<br/>").replace("_", " ")


def get_file_view_url(index_root: Path, series_context: Path, file_commits, filepath) -> str:
    context = index_root / series_context
    return f"{base_url}/{file_commits[filepath]}/{context.relative_to("..")}/{filepath}"


SERIES_PATH_REG = re.compile(r"^(.*)/(\d+)-(\d+)$")


def inners(index_root: Path, series_context: Path):
    numbers = cl.defaultdict(dict)
    for filename in os.listdir(index_root / series_context / "thumbnails" / "inner"):
        if filename == MISSED_PNG or not filename.endswith(".png"):
            continue
        number, *opt, state = filename.split(".")[:-1]
        numbers[opt[0] if opt else None][int(number)] = (filename, int(state))

    if match := SERIES_PATH_REG.match(str(series_context)):
        lo, hi = map(int, match.groups()[1:])
    else:
        lo, hi = min(numbers[None]), max(numbers[None])

    additional_groups = [k for k, v in numbers.items() if k is not None and len(v) > 3]
    main_groups = ([None] if None in numbers else []) + sorted(additional_groups)

    index_section = ""
    for idx, option in enumerate(main_groups):
        if idx > 0:
            index_section += "<br/>"
        opt_title = (option or "").replace("_", " ").capitalize()

        option_section = ""
        counter = 0
        for number in range(lo, hi + 1):
            filename, quality = numbers[option][number] if number in numbers[option] else (None, None)
            counter += 1 if filename else 0
            inner_view_url = f"{series_context}/thumbnails/inner/{filename}" if filename else MISSED_PNG
            option_section += (
                f"\n{INDENT}"
                f"<a class='{qualities[quality or 0]}' "
                f"href='{inner_view_url}' "
                f"title='{opt_title}' target='_blank'>{number}</a>"
            )
        index_section += f"{opt_title} ({counter}/{hi - lo + 1})<br/>" + option_section

    readme_section = ""
    for number in range(lo, hi + 1):
        readme_section += "<span style=\"display: inline-block;\">\n"
        groups = main_groups + [group for group in numbers if group not in main_groups and number in numbers[group]]
        for option in groups:
            filename, quality = numbers[option][number] if number in numbers[option] else (None, None)
            opt_title = (option or "").replace("_", " ").capitalize()
            inner_view_url = f"thumbnails/inner/{filename}" if filename else f"{MISSED_ROOT}/{MISSED_PNG}"
            readme_section += (
                f"\t<a href='{inner_view_url}' title='{opt_title}'>"
                f"<img src='{inner_view_url}' alt='{opt_title}'>"
                f"</a>\n"
            )
        readme_section += "</span>\n"

    return readme_section, index_section.strip()


OUTER_REG = re.compile(r"^(\d{4})_(\d{2})(\{.*})?\[(\d{1,2})](.*)?$")



MISSED_PNG = "missed.png"
MISSED_OUTER_PNG = "missed_outer.png"
MISSED_ROOT = "/collection/gum_wrappers/kent/turbo/"


def outers(index_root: Path, series_context: Path) -> tuple[str, str, list[OuterRelease]]:
    root_folder = index_root / series_context / "thumbnails" / "outer"
    folders = sorted([name for name in os.listdir(root_folder) if os.path.isdir(root_folder / name)])
    releases = []
    for folder in folders:
        collection = {}
        for filename in os.listdir(root_folder / folder):
            if filename.endswith(".gitkeep"):
                continue
            try:
                number, quality, _ = filename.split(".")
            except Exception as ex:
                print(filename)
                raise ex

            collection[int(number)] = (filename, int(quality))
        groups = OUTER_REG.match(folder).groups()
        releases.append(
            OuterRelease(
                folder=folder,
                year=groups[0],
                month=groups[1],
                product_no=groups[2].removeprefix("{").removesuffix("}") if groups[2] else None,
                total=int(groups[3]),
                caption=groups[4],
                collection=collection
            )
        )

    index_section = ""
    opt_column = list(range(1, max(release.total for release in releases) + 1))
    readme_section = (
            "|Release|" + "|".join([str(opt) for opt in opt_column]) + "|\n" +
            "|:--:|" + ":-:|" * (len(opt_column)) + "\n"
    )

    for release in releases:
        product_no = f" [{release.product_no.replace("_", "")}]" if release.product_no is not None else ""
        caption = f" {release.caption.replace("_", " ")}" if release.caption is not None else ""

        title = f"{release.year}.{release.month}{product_no}{caption}"
        index_section += f"{title}<br/>"
        readme_section += f"|{title}|"
        for opt in opt_column:
            if opt <= release.total:
                filename, quality = release.collection.get(opt, (None, 0))

                if filename is not None:
                    ref = f"thumbnails/outer/{release.folder}/{filename}"
                    index_ref = f"{series_context}/{ref}"
                else:
                    ref = index_ref = f"{MISSED_ROOT}/{MISSED_OUTER_PNG}"
                index_section += (
                    f"\n{INDENT}<a href='{index_ref}' target='_blank'>"
                    f"<img src='{index_ref}' width='50' alt='{title}.{opt}'/>"
                    f"</a>"
                )
                readme_section += f"[<img src='{ref}'>]({ref})|"
            else:
                readme_section += f"|"

        index_section += f"\n{INDENT}<br/>"
        readme_section += "\n"

    return readme_section, index_section, releases


def resolve_indent():
    outers_pos = state_template.index("{{ outers }}")
    return " " * ((outers_pos - state_template.rindex("\n", 0, outers_pos)) - 1)


INDENT = resolve_indent()


@dc.dataclass
class IndexSection:
    title: str
    body_start_offset: int
    body_end_offset: int


def find_section(index_text: str, series_context: Path) -> IndexSection:
    x = re.compile(fr"## (\[.*\]\({series_context}\))\n\n")
    match = re.search(x, index_text)
    title = match.groups()[0]
    start_offset = match.end()
    try:
        end_offset = index_text.index("\n## ", start_offset)
    except ValueError:
        end_offset = len(index_text)
    return IndexSection(title, start_offset, end_offset)


def build(index_filepath: Path, series_path: Path) -> tuple[str, list[OuterRelease]]:
    print(f"build: {series_path}")

    index_root = index_filepath.parent
    series_context = series_path.relative_to(index_root)
    title = " ".join([v.capitalize() for v in series_path.parts[2:]])
    outer_readme, outer_index, releases = outers(index_root, series_context)
    inner_readme, inner_index = inners(index_root, series_context)
    result = (
        state_template
        .replace("{{ title }}", title)
        .replace("{{ outers }}", outer_index)
        .replace("{{ inners }}", inner_index)
    )
    state = index_filepath.read_text()

    section = find_section(state, series_context)
    state = state[0:section.body_start_offset] + result + state[section.body_end_offset:]
    with open(index_filepath, "w") as f:
        f.write(state)

    readme_filepath = index_root / series_context / "README.md"
    readme = readme_filepath.read_text()
    marker = "\n### My collection\n\n"
    start_offset = readme.index(marker) + len(marker)
    readme = readme[0:start_offset] + outer_readme + "\n" + inner_readme + "\n"
    with open(readme_filepath, "w") as f:
        f.write(readme)

    return section.title, releases


if __name__ == "__main__":
    index_file = None
    series_releases = dict()
    for root, dirs, files in os.walk("../gum_wrappers/kent/turbo"):
        if "index.md" in files:
            index_file = Path(root) / "index.md"
        if "thumbnails" in dirs:
            title, releases = build(index_file, Path(root))
            series_releases[title] = releases
    update_production(index_file, series_releases)
