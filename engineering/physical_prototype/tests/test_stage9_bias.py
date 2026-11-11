import numpy as np
import pytest

from rft_qpu.stage5_gate import build_fixed_basis_model
from rft_qpu.stage9_bias import build_bias_shifted_model


def test_zero_bias_offset_preserves_stage5_static_point():
    base = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    shifted = build_bias_shifted_model(base, 0.0)
    assert shifted.bias_flux_Phi0 == pytest.approx(base.flux_dc_Phi0, abs=1e-15)
    assert np.allclose(shifted.model.h_static_MHz, base.h_static_MHz, atol=1e-11)
    assert np.allclose(shifted.model.eigenvalues_MHz, base.eigenvalues_MHz, atol=1e-9)
    assert shifted.dressed_AB_detuning_MHz == pytest.approx(
        abs(base.eigenvalues_MHz[3] - base.eigenvalues_MHz[1]), abs=1e-8
    )


def test_shifted_drive_term_is_zero_at_new_static_bias():
    base = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    shifted = build_bias_shifted_model(base, -0.0075)
    delta = shifted.model.delta_h_coupler(shifted.bias_flux_Phi0)
    assert np.linalg.norm(delta, ord="fro") < 1e-11
    assert shifted.minimum_bare_overlap > 0.99
    assert len(set(shifted.model.logical_eigen_indices)) == 4


def test_small_negative_bias_offset_changes_static_zz_smoothly():
    base = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    zero = build_bias_shifted_model(base, 0.0)
    shifted = build_bias_shifted_model(base, -0.0075)
    assert np.isfinite(shifted.static_ZZ_MHz)
    assert shifted.static_ZZ_MHz > zero.static_ZZ_MHz
    assert shifted.minimum_bare_overlap > 0.99


def test_nonfinite_bias_offset_is_rejected():
    base = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    with pytest.raises(ValueError, match="finite"):
        build_bias_shifted_model(base, float("nan"))
