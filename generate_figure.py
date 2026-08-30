"""Reproduce Figure 1 of Boyd & Richerson (2009): migration vs. selection.

The paper labels its three panels m >= s, 2m = s, and 10m = s, and states
the qualitative result: strong migration relative to selection
homogenizes all groups, comparable rates leave simple clines, and weak
migration leaves complex small-scale variation persisting at
equilibrium. It does not publish the exact discrete recursion behind
those numbers (no code or supplementary model is released with the
paper), so this script uses its own bistable local-selection map (see
model.py) and empirically calibrated m/s ratios that reproduce the same
three qualitative regimes in that map, rather than assuming the paper's
literal thresholds transfer unchanged. See README.md ("Calibration
note") for the sensitivity analysis behind this choice.

Panel (a): m/s = 5    -- migration dominant: full homogenization (all
                          traits converge to one value across every
                          subpopulation).
Panel (b): m/s = 1    -- balanced (the paper's own m = s boundary):
                          partial homogenization, clines in the traits
                          that have not fully converged.
Panel (c): m/s = 0.1  -- selection dominant: complex small-scale
                          patchwork persists indefinitely.

Each subpopulation's frequency vector (p1, p2, p3) is rendered directly
as an RGB colour, following the paper's own Figure 1 convention.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from model import residual, simulate

S = 0.05
GENERATIONS = 20000
SEED = 0

PANELS = [
    ("(a)  m/s = 5", S * 5),
    ("(b)  m/s = 1", S * 1),
    ("(c)  m/s = 0.1", S * 0.1),
]


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.6))
    for ax, (label, m) in zip(axes, PANELS):
        freqs = simulate(s=S, m=m, generations=GENERATIONS, seed=SEED)
        r = residual(freqs, s=S, m=m)
        print(f"{label}: residual after {GENERATIONS} generations = {r:.2e}")
        ax.imshow(freqs, interpolation="nearest")
        ax.set_title(label)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(
        "Replication of Boyd & Richerson (2009), Figure 1\n"
        f"(s={S}, 16x16 torus, 3 binary traits, same random initial condition)"
    )
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "figure1_replication.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
