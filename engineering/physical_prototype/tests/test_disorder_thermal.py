from rft_qpu.disorder import run_disorder_study
from rft_qpu.thermal import boltzmann_factor, required_J_for_population


def test_time_reversal_preserving_edge_disorder_keeps_doublet_degenerate():
    report = run_disorder_study(level=1, samples=12, edge_fractional_disorder=(0.05,), time_reversal_breaking_field=())
    assert report["edge_weight_disorder"][0]["ground_splitting_max_over_J"] < 1e-10


def test_thermal_scale_is_reported_as_a_warning_benchmark():
    required = required_J_for_population(1.39371269308684, 10.0, 0.01)
    assert required > 600.0
    assert 0 < boltzmann_factor(13.9371269309, 10.0) < 1
