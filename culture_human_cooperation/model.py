"""Replication of the illustrative model in Section 3(b)-(c) of:

Boyd, R., & Richerson, P. J. (2009). Culture and the evolution of human
cooperation. Phil. Trans. R. Soc. B, 364, 3281-3288.

Three independent binary cultural traits sit on a 16x16 torus of
subpopulations. Each trait is frequency-dependent so that whichever variant
is locally common is favoured by within-group selection -- there are eight
stable equilibria, one per corner of the {0,1}^3 cube. Each generation,
subpopulations exchange a fraction `m` of their members with their four
nearest neighbours (stepping-stone migration). Migration is the
homogenizing force here; local bistable selection is what preserves or
amplifies between-group differences once they exist. When `m` is small
relative to the selection coefficient `s`, that local selection wins and
between-group variation persists -- which is the paper's own point: rapid
local (cultural) adaptation increases heritable variation between groups,
the raw material cultural group selection acts on.
"""
from __future__ import annotations

import numpy as np

GRID_SIZE = 16
N_TRAITS = 3


def initial_frequencies(
    rng: np.random.Generator, grid_size: int = GRID_SIZE, n_traits: int = N_TRAITS
) -> np.ndarray:
    """Random initial frequencies per subpopulation per trait, as in the paper."""
    return rng.uniform(0.0, 1.0, size=(grid_size, grid_size, n_traits))


def selection_step(freqs: np.ndarray, s: float) -> np.ndarray:
    """Within-group frequency-dependent selection.

    p' = p + s * p * (1 - p) * (2p - 1)

    This has stable fixed points at p=0 and p=1 and an unstable fixed point
    at p=0.5, matching the paper's description: "Each variant is
    evolutionarily stable when common" (Sec. 3b). Valid for 0 <= s <= 1;
    outside that range the map is not guaranteed to stay within [0, 1] and
    a negative `s` reverses the bistable dynamics (interior point becomes
    the stable one).
    """
    if not 0.0 <= s <= 1.0:
        raise ValueError(f"s must be in [0, 1], got {s}")
    p = freqs
    updated = p + s * p * (1.0 - p) * (2.0 * p - 1.0)
    return np.clip(updated, 0.0, 1.0)


def migration_step(freqs: np.ndarray, m: float) -> np.ndarray:
    """Stepping-stone migration on a torus.

    Each subpopulation exchanges a fraction `m` of its members with its four
    nearest neighbours (Sec. 3b): it loses fraction `m` overall and receives
    immigrants at rate `m` in total, drawn evenly from the four neighbours.
    Valid for 0 <= m <= 1: outside that range this is no longer a convex
    combination of neighbour frequencies and can leave [0, 1].
    """
    if not 0.0 <= m <= 1.0:
        raise ValueError(f"m must be in [0, 1], got {m}")
    up = np.roll(freqs, -1, axis=0)
    down = np.roll(freqs, 1, axis=0)
    left = np.roll(freqs, -1, axis=1)
    right = np.roll(freqs, 1, axis=1)
    neighbor_mean = (up + down + left + right) / 4.0
    return (1.0 - m) * freqs + m * neighbor_mean


def residual(freqs: np.ndarray, s: float, m: float) -> float:
    """Max absolute change one more generation would make -- an equilibrium check."""
    stepped = migration_step(selection_step(freqs, s), m)
    return float(np.max(np.abs(stepped - freqs)))


def simulate(
    s: float,
    m: float,
    generations: int,
    seed: int,
    grid_size: int = GRID_SIZE,
    n_traits: int = N_TRAITS,
) -> np.ndarray:
    """Run selection + migration for `generations` steps, return final frequencies."""
    if generations < 0:
        raise ValueError(f"generations must be >= 0, got {generations}")
    rng = np.random.default_rng(seed)
    freqs = initial_frequencies(rng, grid_size, n_traits)
    for _ in range(generations):
        freqs = selection_step(freqs, s)
        freqs = migration_step(freqs, m)
    return freqs
