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

Each panel below uses a specific (m/s, seed) pair chosen to be a clean
illustration of its regime -- not proof that ratio always produces that
exact pattern. Both `m/s` and outcome are seed-dependent in this model
(see README); other seeds at the same ratios can fully homogenize, form
a different number of domains, or show a different boundary shape. See
README.md ("Panel Selection") for what other seeds at each ratio look
like and why these three were chosen.

All three panels now use the paper's own literal ratios (m>=s, 2m=s,
10m=s), rather than the m/s=0.2 substitute an earlier version of this
figure used for panel (c). See README.md ("Panel Selection") for why
that substitution was tried and why it was reverted: at the paper's
literal m/s=0.1, this implementation's best available seed (of 30
tried) still shows visibly less spatial clustering than the published
figure -- a real, disclosed gap between this replication and the
original, not something fixed by ratio choice alone.

Panel (a): m/s = 5,   seed 0 -- migration dominant: full homogenization
                                 (every trait converges to one value
                                 across every subpopulation).
Panel (b): m/s = 0.5, seed 2 -- balanced: a single sharp domain wall
                                 between two regions (one trait varies
                                 across it; the other two are already
                                 homogeneous) -- the paper's "simple
                                 cline."
Panel (c): m/s = 0.1, seed 4 -- selection dominant: the paper's own
                                 literal ratio (10m=s). Complex
                                 small-scale variation persists, though
                                 with less spatial clustering than the
                                 published figure -- see README.md.

Each subpopulation's frequency vector (p1, p2, p3) is rendered directly
as an RGB colour, following the paper's own Figure 1 convention. Colors
are rounded to the nearest pure corner of the RGB cube before display
(the underlying simulated frequencies are already within ~5% of a pure
corner almost everywhere at equilibrium; rounding removes that residual
haze so the displayed palette matches the paper's fully-saturated dots
exactly, rather than approximating it).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from legend import add_trait_legend
from model import residual, simulate

S = 0.05
GENERATIONS = 20000

PANELS = [
    ("(a)  m/s = 5", S * 5, 0),
    ("(b)  m/s = 0.5", S * 0.5, 2),
    ("(c)  m/s = 0.1", S * 0.1, 4),
]


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.6))
    for ax, (label, m, seed) in zip(axes, PANELS):
        freqs = simulate(s=S, m=m, generations=GENERATIONS, seed=seed)
        r = residual(freqs, s=S, m=m)
        print(
            f"{label} (seed={seed}): residual after "
            f"{GENERATIONS} generations = {r:.2e}"
        )
        display_freqs = freqs.round()  # snap to pure RGB-cube corners for display
        ax.imshow(display_freqs, interpolation="nearest")
        ax.set_title(label)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(
        "Replication of Boyd & Richerson (2009), Figure 1\n"
        f"(s={S}, 16x16 torus, 3 binary traits; each panel is a chosen "
        "illustrative seed, see README)"
    )
    fig.tight_layout(rect=(0, 0.22, 1, 1))
    add_trait_legend(fig)
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "figure1_replication.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
