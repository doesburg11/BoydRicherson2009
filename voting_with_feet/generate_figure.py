"""Reproduce the structure of Figs. 6-7 in Boyd & Richerson (2009), "Voting
with your feet": for a grid of (m0/beta, initial p0), classify which of the
three stable equilibria the system reaches, starting from x1=1, x2=0 (behavior
1 initially fixed in subpopulation 1, behavior 2 fixed in subpopulation 2).

Three outcomes, matching the paper's own three labeled regions:
- monomorphic at behavior 1 (x1 = x2 ~= 1)
- monomorphic at behavior 2 (x1 = x2 ~= 0)
- polymorphic (x1 and x2 settle at different values)

Uses the paper's own Fig. 6 parameters (d=0.2, h=0.2, g=0.4, giving
x_hat=0.4 -- confirmed against the paper's stated value in
test_model.py) across three panels for mu = 0, 1, 2, matching
the paper's own three-panel comparison.

This is a coarser reproduction than the paper's own smooth boundary curves
(computed here as a grid classification rather than a traced boundary), but
the same qualitative regions and their expected shift with mu should be
visible: higher mu shrinks the migration-rate range needed to reach the
polymorphic regime, and within it, biases the reachable region toward the
group-beneficial behavior 1.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from model import Params, simulate, step

D, H, G = 0.2, 0.2, 0.4
BETA = 1.0
GENERATIONS = 3000
MU_VALUES = [0.0, 1.0, 2.0]
M0_OVER_BETA = np.linspace(0.001, 0.08, 40)
P0_VALUES = np.linspace(0.02, 0.98, 40)

MONO_1, MONO_2, POLY = 0, 1, 2
COLORS = ["#F4C542", "#4C6EF5", "#2CA02C"]
LABELS = ["monomorphic: behavior 1", "monomorphic: behavior 2", "polymorphic"]


def classify(x1: float, x2: float) -> int:
    if abs(x1 - x2) < 0.05:
        return MONO_1 if (x1 + x2) / 2 > 0.5 else MONO_2
    return POLY


def compute_grid(mu: float) -> tuple[np.ndarray, float]:
    """Returns the classified outcome grid and the largest residual (max
    change one more generation would make) found anywhere in it -- a
    convergence check for the classify() calls, which assume equilibrium
    has been reached by GENERATIONS steps."""
    grid = np.zeros((len(P0_VALUES), len(M0_OVER_BETA)), dtype=int)
    max_residual = 0.0
    for i, p0 in enumerate(P0_VALUES):
        for j, ratio in enumerate(M0_OVER_BETA):
            params = Params(d=D, h=H, g=G, beta=BETA, mu=mu, m0=ratio * BETA)
            x1, x2, frac1 = simulate(
                x1_0=1.0, x2_0=0.0, p0=p0, params=params, generations=GENERATIONS
            )
            grid[i, j] = classify(x1, x2)
            x1n, x2n, fracn = step(x1, x2, frac1, params)
            residual = max(abs(x1n - x1), abs(x2n - x2), abs(fracn - frac1))
            max_residual = max(max_residual, residual)
    return grid, max_residual


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    cmap = plt.matplotlib.colors.ListedColormap(COLORS)
    for ax, mu in zip(axes, MU_VALUES):
        grid, max_residual = compute_grid(mu)
        print(f"mu={mu:.0f}: max residual across grid = {max_residual:.2e}")
        ax.imshow(
            grid,
            origin="lower",
            aspect="auto",
            cmap=cmap,
            vmin=0,
            vmax=2,
            extent=(M0_OVER_BETA[0], M0_OVER_BETA[-1], P0_VALUES[0], P0_VALUES[-1]),
        )
        ax.set_title(f"mu = {mu:.0f}")
        ax.set_xlabel("m0 / beta")
    axes[0].set_ylabel("initial p0 (fraction in subpopulation 1)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLORS]
    fig.legend(handles, LABELS, loc="lower center", ncol=3, frameon=False)
    fig.suptitle(
        "Boyd & Richerson (2009) 'Voting with your feet': equilibrium outcome\n"
        f"(d={D}, h={H}, g={G}, x_hat={(D + H) / (2 * D + G + H):.2f}; "
        "x1=1, x2=0 initially)"
    )
    fig.tight_layout(rect=(0, 0.1, 1, 0.92))
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "outcomes.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
