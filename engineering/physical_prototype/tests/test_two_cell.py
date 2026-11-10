import numpy as np

from rft_qpu.two_cell import analyze_two_cell_interaction


def test_two_cell_projection_is_nonzero_and_entangling():
    report = analyze_two_cell_interaction(
        level=1,
        chi_over_J_values=(0.01, 0.05),
        chi_over_2pi_MHz=10.0,
    )
    assert report["n_transmons_two_cell"] == 24
    assert abs(report["effective_nonlocal_interaction_coefficient_over_chi"] - 0.00783608327249) < 1e-12
    values = report["projected_interaction_eigenvalues_at_chi_over_J_1"]
    assert values[0] < 0 < values[-1]
    assert abs(report["ideal_maximally_entangling_time_us"] - 1.5951846816) < 1e-9
    assert report["chi_sweep"][1]["gap_after_logical_quartet_over_J"] > 1.3
