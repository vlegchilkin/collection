import datetime
import re
from pathlib import Path
from typing import List, Any

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import pandas as pd
import numpy as np
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.figure import Figure

from script import OuterRelease


def draw(releases: dict[str, List[OuterRelease]], output_file):
    name_re = re.compile(r"^\[(.*)\]\(.*\)$")
    dates = set()
    for outers in releases.values():
        for release in outers:
            prod = f"{release.year}.{release.month}"
            dates.add(prod)

    moments = sorted(dates)
    products = list(releases.keys())

    df = pd.DataFrame(0, index=products, columns=moments)
    for title, rs in releases.items():
        months_produced = list({f"{r.year}.{r.month}" for r in rs})
        df.loc[title, months_produced] = 1

    colors = list(mcolors.TABLEAU_COLORS.values())

    fig, ax = plt.subplots(figsize=(24, 8))  # Adjust figure size for better fit

    for i, product in enumerate(df.index):
        for j, month in enumerate(df.columns):
            color = colors[i % len(colors)] if df.iloc[i, j] == 1 else 'white'
            ax.add_patch(plt.Rectangle((j, i), 1, 1, color=color))

    # Adjust the tick positions and labels
    ax.set_xticks(np.arange(len(moments)) + 0.5)  # Center labels
    ax.set_xticklabels(moments, rotation=90, ha="center", fontsize=10)
    ax.set_yticks(np.arange(len(products)) + 0.5)  # Center labels
    ax.set_yticklabels(products, fontsize=10)
    ax.set_yticklabels([name_re.match(product).groups()[0] for product in products], fontsize=10)
    [t.set_color(colors[idx % len(colors)]) for idx, t in enumerate(ax.yaxis.get_ticklabels())]

    # Set labels, title
    ax.set_xlabel("(C) Vitaly Legchilkin", fontsize=12, loc="right")
    ax.set_title("Kent Turbo Series Production", fontsize=16, pad=20)

    # Invert y-axis, ensure tight layout, and set aspect ratio
    # ax.invert_yaxis()
    ax.set_xlim(0, len(moments))  # Set limits to align edges
    ax.set_ylim(0, len(products))

    # Manually add horizontal grid lines for each product
    for i, product in enumerate(products):
        y_center = i + 0.5  # Center the grid line
        ax.axhline(y=y_center, color=colors[i % len(colors)], linestyle="--", linewidth=1)

    # Add minor gridlines for overall clarity
    ax.set_xticks(np.arange(0, len(moments)), minor=True)
    ax.grid(which="minor", color="gray", linestyle="--", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Add gridlines for clarity
    # ax.set_xticks(np.arange(0, len(moments)), minor=True)
    # ax.set_yticks(np.arange(0, len(products)), minor=True)
    # ax.grid(which="minor", color="gray", linestyle="--", linewidth=0.5)
    # ax.tick_params(which="minor", bottom=False, left=False)
    # [t.set_color(colors[idx % len(colors)]) for idx, t in enumerate(ax.yaxis.get_ticklines())]


    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')


def update_production(index_filepath: Path, title_releases: dict[str, list[OuterRelease]]):
    state = index_filepath.read_text()
    series_offsets = {title: state.find(title) for title in title_releases.keys()}
    sorted_titles = sorted(series_offsets.keys(), key=lambda x: series_offsets[x])
    sorted_releases = {title: title_releases[title] for title in sorted_titles}
    # res = []
    # for title in sorted_titles:
    #     releases = title_releases[title]
    #     dates = [f"{release.year}.{release.month}" for release in releases]
    #     first, last = min(dates), max(dates)
    #     res.append((title, first, last))
    #
    # marker = "\n## Producing\n\n"
    # start_offset = state.index(marker) + len(marker)
    # try:
    #     end_offset = state.index("\n## ", start_offset)
    # except ValueError:
    #     end_offset = len(state)
    # print("\\\n".join(res))
    png_path = index_filepath.parent / "kent_turbo_producing.png"
    draw(sorted_releases, str(png_path.absolute()))

    # state = state[0:start_offset] + res + state[end_offset:]
    # with open(index_filepath, "w") as f:
    #     f.write(state)
