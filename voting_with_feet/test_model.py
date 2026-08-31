import pytest

from model import (
    Params,
    average_payoff,
    migration_rate,
    payoffs,
    simulate,
    step,
    within_group_update,
)


def make_params(mu=1.0, m0=0.02, beta=1.0, d=0.02, h=0.2, g=0.4):
    return Params(d=d, h=h, g=g, beta=beta, mu=mu, m0=m0)


def test_payoffs_equal_at_x_hat():
    p = make_params()
    w1, w2 = payoffs(p.x_hat, p)
    assert w1 == pytest.approx(w2)


def test_fig6_calibration_x_hat_is_0_4():
    """Paper states d=0.2, h=0.2, g=0.4 gives x_hat=0.4 (Fig. 6 caption) --
    an external check that the corrected equation (2) denominator is
    right."""
    p = Params(d=0.2, h=0.2, g=0.4, beta=1.0, mu=0.0, m0=0.0)
    assert p.x_hat == pytest.approx(0.4)


def test_behavior_1_is_ess_when_common():
    p = make_params()
    w1, w2 = payoffs(1.0, p)
    assert w1 > w2


def test_behavior_2_is_ess_when_common():
    p = make_params()
    w1, w2 = payoffs(0.0, p)
    assert w1 < w2


def test_migration_rate_clamped_to_unit_interval():
    """The paper assumes parameters keep eq. 7 in [0, 1] on its own; this
    checks the deliberate saturating extension used here for parameters
    where that assumption doesn't hold (see module docstring)."""
    p = make_params(m0=0.5, mu=10.0)
    assert migration_rate(w_from=0.0, w_to=100.0, p=p) == pytest.approx(1.0)
    assert migration_rate(w_from=100.0, w_to=0.0, p=p) == pytest.approx(0.0)


def test_within_group_update_clamped_to_unit_interval():
    """Same saturating-extension concern as migration_rate, for eq. 4:
    a large enough beta can push x' outside [0, 1] without clipping."""
    p = make_params(beta=10.0)
    assert within_group_update(0.01, p) == pytest.approx(0.0)
    assert within_group_update(0.99, p) == pytest.approx(1.0)


def test_zero_migration_leaves_subpopulation_sizes_unchanged():
    p = make_params(m0=0.0)
    _, _, frac1 = step(x1=1.0, x2=0.0, frac1=0.3, p=p)
    assert frac1 == pytest.approx(0.3)


def test_zero_migration_isolates_subpopulations():
    """With m0=0, each subpopulation evolves independently under
    within-group imitation alone -- migration has no effect on x."""
    p = make_params(m0=0.0)
    x1, x2, _ = step(x1=1.0, x2=0.0, frac1=0.3, p=p)
    assert x1 == pytest.approx(within_group_update(1.0, p))
    assert x2 == pytest.approx(within_group_update(0.0, p))


def test_subpopulation_sizes_conserve_total_population():
    p = make_params(m0=0.1, mu=2.0)
    x1, x2, frac1 = 0.9, 0.1, 0.5
    for _ in range(50):
        x1, x2, frac1 = step(x1, x2, frac1, p)
        assert 0.0 <= frac1 <= 1.0


def test_migration_conserves_total_behavior_1_count():
    """Migration alone (post within-group update, pre-migration) must not
    change the total count of behavior-1 individuals -- it only moves
    individuals between subpopulations, it doesn't change their behavior.
    This is the invariant the eq. (6) second-denominator bug (see module
    docstring) would have broken: using subpopulation 1's post-migration
    size as the denominator for x2'' too would silently violate it."""
    p = make_params(m0=0.15, mu=2.0)
    x1, x2, frac1 = 0.85, 0.2, 0.35
    x1p = within_group_update(x1, p)
    x2p = within_group_update(x2, p)
    total_before = frac1 * x1p + (1 - frac1) * x2p

    x1_new, x2_new, frac1_new = step(x1, x2, frac1, p)
    total_after = frac1_new * x1_new + (1 - frac1_new) * x2_new

    assert total_after == pytest.approx(total_before, abs=1e-12)


def test_average_payoff_difference_matches_paper_equation_8():
    """Eq. 8 (as transcribed) is algebraically equivalent to computing
    average_payoff directly and subtracting -- confirms eq. 8 was not
    itself a source of error (see module docstring)."""
    p = make_params()
    xi, xj = 0.65, 0.2
    direct = average_payoff(xi, p) - average_payoff(xj, p)
    eq8 = (xi**2 - xj**2) * p.g - (
        xi * (1 - xi) - xj * (1 - xj)
    ) * (p.h + 2 * p.d)
    assert direct == pytest.approx(eq8)


def test_symmetric_when_mu_zero_and_g_equals_h():
    """Paper: 'when migration is not payoff biased (mu=0), the equilibria
    are symmetrical so that x_hat_1 = 1 - x_hat_2 and p_hat = 0.5.'

    This exact relation only holds when x_hat=0.5, i.e. when g=h (verified
    analytically: within_group_update(1-x) = 1-within_group_update(x) for
    all x iff x_hat=0.5, which requires g=h given x_hat=(d+h)/(2d+g+h)).
    With g != h (e.g. the Fig. 6 params, g=0.4, h=0.2, x_hat=0.4), mu=0
    still gives p_hat=0.5 exactly, but x1 and x2 settle at values that do
    NOT sum to 1 -- confirmed by direct simulation, not just theory. The
    paper's own phrasing doesn't flag this g=h precondition explicitly.
    """
    p = Params(d=0.02, h=0.3, g=0.3, beta=1.0, mu=0.0, m0=0.01)
    assert p.x_hat == pytest.approx(0.5)
    x1, x2, frac1 = simulate(
        x1_0=1.0, x2_0=0.0, p0=0.5, params=p, generations=5000
    )
    assert x1 == pytest.approx(1 - x2, abs=1e-9)
    assert frac1 == pytest.approx(0.5, abs=1e-9)


def test_high_migration_converges_to_monomorphic():
    """Fig. 3: high migration -> only monomorphic equilibria are stable."""
    p = Params(d=0.02, h=0.2, g=0.4, beta=1.0, mu=2.0, m0=0.04)
    x1, x2, _ = simulate(
        x1_0=1.0, x2_0=0.0, p0=0.5, params=p, generations=5000
    )
    assert x1 == pytest.approx(x2, abs=1e-3)


def test_low_migration_preserves_polymorphism():
    """Fig. 4: low enough migration -> polymorphic equilibrium is stable."""
    p = Params(d=0.2, h=0.2, g=0.4, beta=1.0, mu=2.0, m0=0.01)
    x1, x2, _ = simulate(
        x1_0=1.0, x2_0=0.0, p0=0.5, params=p, generations=5000
    )
    assert x1 - x2 > 0.3


def test_average_payoff_matches_weighted_payoffs():
    p = make_params()
    x = 0.7
    w1, w2 = payoffs(x, p)
    assert average_payoff(x, p) == pytest.approx(x * w1 + (1 - x) * w2)


def test_simulate_rejects_negative_generations():
    p = make_params()
    with pytest.raises(ValueError):
        simulate(x1_0=1.0, x2_0=0.0, p0=0.5, params=p, generations=-1)


def test_simulate_rejects_out_of_range_initial_conditions():
    p = make_params()
    with pytest.raises(ValueError):
        simulate(x1_0=1.5, x2_0=0.0, p0=0.5, params=p, generations=10)
    with pytest.raises(ValueError):
        simulate(x1_0=0.5, x2_0=0.0, p0=-0.1, params=p, generations=10)
