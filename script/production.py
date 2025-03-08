import re
from numbers import Number
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors
import itertools as it

from script import OuterRelease

# COLORS = {
#     "black": "black",
#     "2000": "yellow",
#     "2003": "green",
#     "2007": "cyan",
#     "classic": "orange",
#     "sport": "blue",
#     "super": "red"
# }
COLORS = {
    "black": "tab:brown",
    "super": "tab:red",
    "classic": "tab:orange",
    "sport": "tab:blue",
    "2000": "tab:pink",
    "2003": "tab:olive",
    "2007": "tab:cyan",

    "1-100": "black",
    "101-200": "tab:orange",
}

SERIES_RE = re.compile(r"^\[(.*)\]\((.*)\)$")


class Product(Number):
    def __hash__(self):
        return self.id.__hash__()

    def __init__(self, index: int, description: str, releases: List[OuterRelease]):
        self.id = index
        self.releases = releases
        self.title, self.path = SERIES_RE.match(description).groups()
        self.epoch = self.path.split("/")[0]
        self.color = (COLORS[self.epoch], 1)

    def __eq__(self, __value: 'Product'):
        return self.id == __value.id

    def __str__(self):
        return self.path


def draw(releases: dict[str, List[OuterRelease]], output_file):
    dates = set()
    for outers in releases.values():
        for release in outers:
            prod = f"{release.year}.{release.month}"
            dates.add(prod)

    moments = sorted(dates)
    products = [Product(idx, description, releases) for idx, (description, releases) in enumerate(releases.items())]
    epoch_groups = [(k, list(g)) for k, g in it.groupby(products, lambda p: p.epoch)]
    for epoch, epoch_products in epoch_groups:
        x = len(epoch_products)
        _start = 0.9
        for i in range(x):
            _transparency = _start - i * 0.1
            epoch_products[i].color = (COLORS[epoch], _transparency)

    df = pd.DataFrame(0, index=products, columns=moments)
    for product in products:
        months_produced = list({f"{r.year}.{r.month}" for r in product.releases})
        df.loc[product, months_produced] = 1

    fig, ax = plt.subplots(figsize=(24, 8))  # Adjust figure size for better fit

    for i, product in enumerate(df.index):
        for j, month in enumerate(df.columns):
            color = product.color if df.iloc[i, j] == 1 else 'white'
            ax.add_patch(plt.Rectangle((j, i), 1, 1, color=color))

    # Adjust the tick positions and labels
    ax.set_xticks(np.arange(len(moments)) + 0.5)  # Center labels
    ax.set_xticklabels(moments, rotation=90, ha="center", fontsize=10)

    ax.set_yticks(np.arange(len(products)) + 0.5)  # Center labels
    ax.set_yticklabels([product.title for product in products], fontsize=12, weight='bold')
    [t.set_color(products[idx].color) for idx, t in enumerate(ax.yaxis.get_ticklabels())]

    # Set labels, title
    ax.set_xlabel("(C) Vitaly Legchilkin", fontsize=12, loc="right")
    ax.set_title("Kent Turbo Series Production", fontsize=16, pad=20)

    # Set limits to align edges
    ax.set_xlim(0, len(moments))
    ax.set_ylim(0, len(products))

    for i, product in enumerate(products):
        y_center = i + 0.5
        ax.axhline(y=y_center, color=product.color, linestyle="--", linewidth=1)

    for i, _ in enumerate(moments):
        x_center = i + 0.5
        ax.axvline(x=x_center, color="gray", linestyle="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')


def update_production(index_filepath: Path, title_releases: dict[str, list[OuterRelease]]):
    state = index_filepath.read_text()
    series_offsets = {title: state.find(title) for title in title_releases.keys()}
    sorted_titles = sorted(series_offsets.keys(), key=lambda x: series_offsets[x])
    sorted_releases = {title: title_releases[title] for title in sorted_titles}

    png_path = index_filepath.parent / "kent_turbo_producing.png"
    draw(sorted_releases, str(png_path.absolute()))
