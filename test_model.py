import numpy as np
import pytest

from model import initial_frequencies, migration_step, residual, selection_step, simulate


def test_selection_fixed_points():
    freqs = np.array([[[0.0, 0.5, 1.0]]])
    updated = selection_step(freqs, s=0.1)
    assert updated[0, 0, 0] == pytest.approx(0.0)
    assert updated[0, 0, 1] == pytest.approx(0.5)
    assert updated[0, 0, 2] == pytest.approx(1.0)


def test_selection_moves_away_from_center():
    freqs = np.array([[[0.6, 0.4, 0.5]]])
    updated = selection_step(freqs, s=0.1)
    assert updated[0, 0, 0] > 0.6
    assert updated[0, 0, 1] < 0.4


def test_selection_stays_in_unit_interval():
    rng = np.random.default_rng(0)
    freqs = rng.uniform(0, 1, size=(16, 16, 3))
    updated = selection_step(freqs, s=1.0)
    assert updated.min() >= 0.0
    assert updated.max() <= 1.0


def test_selection_rejects_out_of_range_s():
    freqs = np.full((1, 1, 1), 0.5)
    with pytest.raises(ValueError):
        selection_step(freqs, s=1.5)
    with pytest.raises(ValueError):
        selection_step(freqs, s=-0.1)


def test_migration_zero_is_identity():
    rng = np.random.default_rng(0)
    freqs = rng.uniform(0, 1, size=(4, 4, 2))
    assert np.allclose(migration_step(freqs, m=0.0), freqs)


def test_migration_one_replaces_with_neighbor_mean():
    freqs = np.zeros((4, 4, 1))
    freqs[0, 0, 0] = 1.0
    updated = migration_step(freqs, m=1.0)
    # (0,0)'s own value is fully discarded; its neighbours (all zero) fill it.
    assert updated[0, 0, 0] == pytest.approx(0.0)
    # each neighbour of (0,0) receives 1/4 from it via torus wraparound.
    assert updated[1, 0, 0] == pytest.approx(0.25)
    assert updated[0, 1, 0] == pytest.approx(0.25)
    assert updated[-1, 0, 0] == pytest.approx(0.25)
    assert updated[0, -1, 0] == pytest.approx(0.25)


def test_migration_conserves_mean():
    rng = np.random.default_rng(0)
    freqs = rng.uniform(0, 1, size=(8, 8, 3))
    updated = migration_step(freqs, m=0.3)
    assert np.allclose(updated.mean(axis=(0, 1)), freqs.mean(axis=(0, 1)))


def test_migration_rejects_out_of_range_m():
    freqs = np.full((1, 1, 1), 0.5)
    with pytest.raises(ValueError):
        migration_step(freqs, m=1.5)
    with pytest.raises(ValueError):
        migration_step(freqs, m=-0.1)


def test_simulate_reproducible_for_fixed_seed():
    a = simulate(s=0.05, m=0.05, generations=50, seed=42)
    b = simulate(s=0.05, m=0.05, generations=50, seed=42)
    assert np.array_equal(a, b)


def test_simulate_rejects_negative_generations():
    with pytest.raises(ValueError):
        simulate(s=0.05, m=0.05, generations=-1, seed=0)


def test_simulate_zero_generations_returns_initial_condition():
    rng_seed = 7
    freqs = simulate(s=0.05, m=0.05, generations=0, seed=rng_seed)
    expected = initial_frequencies(np.random.default_rng(rng_seed))
    assert np.array_equal(freqs, expected)


def test_strong_migration_reaches_equilibrium_within_generation_budget():
    """m/s=5 should fully homogenize and the residual should confirm it."""
    freqs = simulate(s=0.05, m=0.25, generations=20_000, seed=0)
    assert freqs.std(axis=(0, 1)).max() < 1e-6
    assert residual(freqs, s=0.05, m=0.25) < 1e-9


def test_weak_migration_does_not_homogenize():
    """m/s=0.1 should leave persistent spatial variation, not converge to one value."""
    freqs = simulate(s=0.05, m=0.005, generations=20_000, seed=0)
    assert freqs.std(axis=(0, 1)).min() > 0.1
