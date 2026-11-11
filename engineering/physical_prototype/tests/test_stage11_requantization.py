from __future__ import annotations

import numpy as np
import pytest

from rft_qpu.circuit_quantization import CircuitParameters
from rft_qpu.stage11_requantization import (
    analyze_bias_requantization,
    diagonalize_local_coupler,
)


def test_explicit_flux_requantization_is_hermitian_and_normalized():
    params = CircuitParameters(charge_cutoff=8, levels_kept=5)
    point = diagonalize_local_coupler(params, 0.259343676252319, 8)
    assert point.energies_MHz.shape == (17,)
    assert np.all(np.diff(point.energies_MHz) >= 0)
    assert np.allclose(point.eigenvectors.conj().T @ point.eigenvectors, np.eye(17), atol=1e-11)
    for op in (point.n_matrix, point.cos_matrix, point.sin_matrix):
        assert np.allclose(op, op.conj().T, atol=1e-10)


def test_same_flux_gives_unit_overlap_and_zero_operator_drift():
    params = CircuitParameters(charge_cutoff=8, levels_kept=5)
    report, _ = analyze_bias_requantization(
        params, 0.266843676252319, 0.0, charge_cutoffs=(8,), levels_kept=(3, 5)
    )
    for row in report["rows"]:
        assert row["minimum_state_overlap_probability"] > 1.0 - 1e-10
        assert row["minimum_retained_subspace_singular_value"] > 1.0 - 1e-10
        assert abs(row["delta_f01_MHz"]) < 1e-10
        assert row["n_matrix_frobenius_difference"] < 1e-10


def test_bias_shift_changes_spectrum_and_reports_all_truncations():
    params = CircuitParameters(charge_cutoff=8, levels_kept=5)
    report, arrays = analyze_bias_requantization(
        params, 0.266843676252319, -0.0075,
        charge_cutoffs=(8, 10, 12), levels_kept=(3, 4, 5),
    )
    assert len(report["rows"]) == 9
    assert len(arrays) > 0
    assert report["shifted_flux_Phi0"] == pytest.approx(0.259343676252319)
    assert abs(report["rows"][0]["delta_f01_MHz"]) > 1e-4
    assert all(0.0 <= r["minimum_state_overlap_probability"] <= 1.0 + 1e-10 for r in report["rows"])
    assert all(0.0 <= r["minimum_retained_subspace_singular_value"] <= 1.0 + 1e-10 for r in report["rows"])


def test_invalid_flux_is_rejected():
    params = CircuitParameters(charge_cutoff=8, levels_kept=5)
    with pytest.raises(ValueError):
        diagonalize_local_coupler(params, 0.5, 8)
