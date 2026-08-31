"""Shared legend for the 8 RGB-cube corners used by both figure scripts.

Each subpopulation carries 3 independent binary traits, mapped directly
to the R, G, B channels (trait 1 -> red, trait 2 -> green, trait 3 ->
blue), following the paper's own Figure 1 convention. A cell's color is
therefore one of the 8 corners of the RGB cube -- which trait
combination currently dominates that subpopulation -- with no
combination privileged as "better" than any other.
"""
from __future__ import annotations

from matplotlib.patches import Patch

CORNERS = [
    ((0, 0, 0), "0,0,0  black"),
    ((1, 0, 0), "1,0,0  red"),
    ((0, 1, 0), "0,1,0  green"),
    ((0, 0, 1), "0,0,1  blue"),
    ((1, 1, 0), "1,1,0  yellow"),
    ((1, 0, 1), "1,0,1  magenta"),
    ((0, 1, 1), "0,1,1  cyan"),
    ((1, 1, 1), "1,1,1  white"),
]


def add_trait_legend(fig) -> None:
    """Add an 8-swatch legend mapping (trait1, trait2, trait3) to color."""
    patches = [
        Patch(facecolor=color, edgecolor="black", label=label)
        for color, label in CORNERS
    ]
    fig.legend(
        handles=patches,
        loc="lower center",
        ncol=4,
        title="(trait1, trait2, trait3) = (R, G, B)",
        frameon=False,
        bbox_to_anchor=(0.5, 0.0),
    )
