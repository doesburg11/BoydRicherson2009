"""Replication of the model in:

Boyd, R., & Richerson, P. J. (2009). Voting with your feet: payoff
biased migration and the evolution of group beneficial behavior.
Journal of Theoretical Biology, 257(2), 331-339.

Two subpopulations (1 and 2) each carry a frequency x_i of "behavior 1"
(the alternative being "behavior 2"). Within each subpopulation, payoffs
make behavior 1 an ESS when common and behavior 2 an ESS when common --
a coordination game with a single unstable equilibrium x_hat separating
the two basins of attraction. Migration between the two subpopulations
is biased toward whichever one currently has the higher average payoff
("voting with your feet"), controlled by bias strength `mu`.

Two apparent OCR errors in the extracted paper text were corrected here
after independent symbolic verification (see test_model.py
and the git history for the derivation):

1. The paper's equation (2) is transcribed as x_hat = (d+h)/(g+h+d).
   Deriving x_hat directly from equation (1) by setting W_i1 = W_i2
   gives x_hat = (d+h)/(2d+g+h) instead -- an extra `d` in the
   denominator. This is confirmed by the paper's own worked example:
   Fig. 6 states "d=0.2, h=0.2, g=0.4" and "x_hat is 0.4" -- only the
   (2d+g+h) denominator reproduces that number (0.4/0.8=0.5 with the
   transcribed denominator vs. 0.4/1.0=0.4 with the corrected one).
2. Equation (6)'s two fractions are transcribed with the same
   denominator, `p(1-m12)+(1-p)m21` (the post-migration size of
   subpopulation 1). Population conservation requires the second
   fraction (for x''_2) to instead use the post-migration size of
   subpopulation 2, `(1-p)(1-m21)+p*m12`, which equals
   `1 - p(1-m12) - (1-p)m21` by conservation of total population. Using
   the same denominator for both would not conserve the total count of
   individuals carrying behavior 1 across the two subpopulations.

Equation (8), the average-payoff-difference formula, is not used
directly in this code -- average payoffs are instead computed by
directly weighting equation (1)'s payoffs (`average_payoff` below).
The two are algebraically equivalent (verified in
test_model.py); equation (8) is just the pre-expanded form
of that same computation and was not itself a source of error.

`within_group_update` and `migration_rate` clip/clamp their outputs to
stay within their valid domain. This matters outside the paper's own
example parameters: the paper implicitly assumes `beta`, `d`, `g`, `h`
are small enough that equations (4) and (7) never leave [0, 1] on their
own. For parameters where that assumption doesn't hold (e.g. `beta` too
large), an unclipped equation (4) can push a frequency below 0 or above
1, and an unclamped equation (7) can produce a migration "rate" outside
[0, 1]. Clipping/clamping is a deliberate saturating extension beyond
the paper's implicit safe range, not a feature of the original model --
it keeps every quantity meaningful (a frequency, a rate) rather than
letting the recursion silently produce nonsense.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    """Payoff-game and migration parameters (paper's d, h, g, beta, mu, m0)."""

    d: float
    h: float
    g: float
    beta: float
    mu: float
    m0: float

    @property
    def x_hat(self) -> float:
        """Unstable equilibrium separating the two basins of attraction (eq. 2, corrected)."""
        return (self.d + self.h) / (2 * self.d + self.g + self.h)


def payoffs(x: float, p: Params) -> tuple[float, float]:
    """W_i1(x), W_i2(x) -- payoffs to behavior 1 and behavior 2 (eq. 1)."""
    w1 = 1 - p.h + x * (p.d + p.g + p.h)
    w2 = 1 + p.d - x * p.d
    return w1, w2


def average_payoff(x: float, p: Params) -> float:
    """Average payoff in a subpopulation with behavior-1 frequency x."""
    w1, w2 = payoffs(x, p)
    return x * w1 + (1 - x) * w2


def within_group_update(x: float, p: Params) -> float:
    """One generation of payoff-biased imitation within a subpopulation (eq. 3/4).

    x' = x + beta * x * (1-x) * (W1(x) - W2(x)), clipped to [0, 1] -- see
    the module docstring for why clipping is needed outside the paper's
    own (small-beta) example parameter range.
    """
    w1, w2 = payoffs(x, p)
    updated = x + p.beta * x * (1 - x) * (w1 - w2)
    return min(max(updated, 0.0), 1.0)


def migration_rate(w_from: float, w_to: float, p: Params) -> float:
    """Fraction migrating from the subpopulation with payoff w_from to the one
    with payoff w_to (eq. 7): m0 * (1 + mu * (w_to - w_from)), clamped to [0, 1]
    -- the paper specifies mu is "chosen so migration rates are always between
    zero and one" for the parameter ranges it explores; clamping here makes
    that explicit and keeps the model well-defined outside that range too.
    """
    rate = p.m0 * (1 + p.mu * (w_to - w_from))
    return min(max(rate, 0.0), 1.0)


def step(x1: float, x2: float, frac1: float, p: Params) -> tuple[float, float, float]:
    """One full generation: within-group imitation, then payoff-biased migration.

    frac1 is the fraction of the total population in subpopulation 1 (the
    paper's `p`, renamed here to avoid clashing with the Params instance).
    Returns the updated (x1, x2, frac1).
    """
    x1p = within_group_update(x1, p)
    x2p = within_group_update(x2, p)

    w1 = average_payoff(x1p, p)
    w2 = average_payoff(x2p, p)
    m12 = migration_rate(w_from=w1, w_to=w2, p=p)
    m21 = migration_rate(w_from=w2, w_to=w1, p=p)

    size1 = frac1 * (1 - m12) + (1 - frac1) * m21
    size2 = (1 - frac1) * (1 - m21) + frac1 * m12  # = 1 - size1, kept explicit

    count1_in_1 = x1p * frac1 * (1 - m12) + x2p * (1 - frac1) * m21
    count1_in_2 = x2p * (1 - frac1) * (1 - m21) + x1p * frac1 * m12

    x1_new = count1_in_1 / size1 if size1 > 0 else x1p
    x2_new = count1_in_2 / size2 if size2 > 0 else x2p
    return x1_new, x2_new, size1


def simulate(
    x1_0: float,
    x2_0: float,
    p0: float,
    params: Params,
    generations: int,
) -> tuple[float, float, float]:
    """Run `generations` steps from the given initial condition."""
    if generations < 0:
        raise ValueError(f"generations must be >= 0, got {generations}")
    for name, value in (("x1_0", x1_0), ("x2_0", x2_0), ("p0", p0)):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {value}")
    x1, x2, frac1 = x1_0, x2_0, p0
    for _ in range(generations):
        x1, x2, frac1 = step(x1, x2, frac1, params)
    return x1, x2, frac1
