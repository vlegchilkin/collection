import os
from pathlib import Path
import collections as cl
import subprocess

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


def inners(index_root: Path, series_context: Path):
    numbers = cl.defaultdict(dict)
    for filename in os.listdir(index_root / series_context / "thumbnails" / "inner"):
        if not filename.endswith(".png"):
            continue
        number, *opt, state = filename.split(".")[:-1]
        numbers[int(number)][opt[0] if opt else None] = int(state)

    index_section = "Collection<br/>"
    readme_section = ""
    for number in sorted(numbers):
        readme_section += "<span style=\"display: inline-block;\">\n"
        for idx, opt in enumerate(sorted(numbers[number], key=lambda x: x or '')):
            quality = numbers[number][opt]
            filename = f"{number}{f'.{opt}' if opt else ''}.{quality}.png"
            title = str(number) + (f"<sup>{idx}</sup>" if idx > 0 else '')
            opt_title = (opt or '').replace("_", " ").capitalize()
            inner_view_url = f"thumbnails/inner/{filename}"
            index_section += (
                f"\n{INDENT}"
                f"<a class='{qualities[quality]}' "
                f"href='{series_context}/{inner_view_url}' "
                f"title='{opt_title}' target='_blank'>{title}</a>"
            )
            readme_section += (
                f"\t<a href='{inner_view_url}' title='{opt_title}'>"
                f"<img src='thumbnails/inner/{filename}' alt='{opt_title}'>"
                f"</a>\n"
            )
        readme_section += "</span>\n"

    return readme_section, index_section


def outers(index_root: Path, series_context: Path):
    years = cl.defaultdict(lambda: cl.defaultdict(dict))
    options = set()
    for filename in os.listdir(index_root / series_context / "thumbnails" / "outer"):
        if not filename.endswith(".png"):
            continue
        year, opt, state = filename.split(".")[:-1]
        *group_data, ver = opt.split("_")
        group = "" if not group_data else " ".join(group_data).capitalize()
        years[year][group][opt] = state
        options.add(int(ver))
    index_section = ""
    opt_column = {opt: idx for idx, opt in enumerate(sorted(options))}
    readme_section = (
            "|Year|" + "|".join([str(opt) for opt in opt_column]) + "|\n" +
            "|:--:|" + ":-:|" * (len(options)) + "\n"
    )

    for year in sorted(years):
        for group, vers in sorted(years[year].items()):
            index_section += f"{format_date(year)}{f' {group}' if group else ""}<br/>"
            readme_section += f"|{format_date(year)}{f' {group}' if group else ""}|"
            for opt in sorted(vers, key=lambda k: int(k.split("_")[-1])):
                quality = vers[opt]
                filename = f"{year}.{opt}.{quality}.png"
                index_section += (
                    f"\n{INDENT}<a href='{series_context}/thumbnails/outer/{filename}' target='_blank'>"
                    f"<img src='{series_context}/thumbnails/outer/{filename}' width='50' alt='{year}.{opt}'/>"
                    f"</a>"
                )
                readme_section += f"[<img src='thumbnails/outer/{filename}'>](thumbnails/outer/{filename})|"
            index_section += f"\n{INDENT}<br/>"
            readme_section += "\n"

    return readme_section, index_section


def resolve_indent():
    outers_pos = state_template.index("{{ outers }}")
    return " " * ((outers_pos - state_template.rindex("\n", 0, outers_pos)) - 1)


INDENT = resolve_indent()


def build(index_filepath: Path, series_path: Path):
    index_root = index_filepath.parent
    series_context = series_path.relative_to(index_root)
    title = " ".join([v.capitalize() for v in series_path.parts[2:]])
    outer_readme, outer_index = outers(index_root, series_context)
    inner_readme, inner_index = inners(index_root, series_context)
    result = (
        state_template
        .replace("{{ title }}", title)
        .replace("{{ outers }}", outer_index)
        .replace("{{ inners }}", inner_index)
    )
    state = index_filepath.read_text()
    marker = f"({series_context})\n\n"
    print(marker)
    start_offset = state.index(marker) + len(marker)
    try:
        end_offset = state.index("\n## ", start_offset)
    except ValueError:
        end_offset = len(state)
    state = state[0:start_offset] + result + state[end_offset:]
    with open(index_filepath, "w") as f:
        f.write(state)

    readme_filepath = index_root / series_context / "README.md"
    readme = readme_filepath.read_text()
    marker = "\n### My collection\n\n"
    start_offset = readme.index(marker) + len(marker)
    readme = readme[0:start_offset] + outer_readme + "\n" + inner_readme + "\n"
    with open(readme_filepath, "w") as f:
        f.write(readme)


if __name__ == "__main__":
    index_file = None
    for root, dirs, files in os.walk("../gum_wrappers/kent/turbo"):
        if "index.md" in files:
            index_file = Path(root) / "index.md"
        if "thumbnails" in dirs:
            build(index_file, Path(root))
