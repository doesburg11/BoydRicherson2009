"""Supplementary figure: sweep m/s = 0.1, 0.2, ..., 1.0, 2.0, ..., 5.0.

Not a reproduction of anything in the paper -- the paper only shows the
three example ratios (m>=s, 2m=s, 10m=s) reproduced in generate_figure.py.
This sweep instead shows the full transition from patchwork to full
homogenization as m/s rises, at one fixed seed, so the progression can be
read directly rather than inferred from three snapshots. The fine 0.1
steps up to 1.0 cover the paper's own regime boundary; the coarse 1.0
steps from 1.0 to 5.0 extend past it to confirm homogenization is a
stable end state, not something that reverts at higher m/s.

Uses 100,000 generations: a check found m/s=0.8 at seed 0 has residual
3.39e-05 after 20,000 generations (not fully converged yet) but exactly
0.0 by 100,000, so the longer budget is used throughout to guarantee
every panel is a genuine equilibrium, not a slow transient.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from legend import add_trait_legend
from model import residual, simulate

S = 0.05
SEED = 0
GENERATIONS = 100_000
RATIOS = [round(i / 10, 1) for i in range(1, 11)] + [2.0, 3.0, 4.0, 5.0]


def main() -> None:
    fig, axes = plt.subplots(2, 7, figsize=(19, 6))
    for ax, ratio in zip(axes.flat, RATIOS):
        m = S * ratio
        freqs = simulate(s=S, m=m, generations=GENERATIONS, seed=SEED)
        r = residual(freqs, s=S, m=m)
        print(f"m/s={ratio:.1f}: residual after {GENERATIONS} generations = {r:.2e}")
        display_freqs = freqs.round()
        ax.imshow(display_freqs, interpolation="nearest")
        ax.set_title(f"m/s = {ratio:.1f}")
        ax.set_xticks([])
        ax.set_yticks([])
    for ax in axes.flat[len(RATIOS):]:
        ax.axis("off")
    fig.suptitle(
        "Boyd & Richerson (2009) model: m/s sweep at fixed seed\n"
        f"(s={S}, seed={SEED}, 16x16 torus, 3 binary traits, "
        f"{GENERATIONS:,} generations)"
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    add_trait_legend(fig)
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "ratio_sweep.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
