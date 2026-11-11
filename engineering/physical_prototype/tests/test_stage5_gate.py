import math
import numpy as np

from rft_qpu.stage5_gate import (
    apply_local_z,
    conditional_phase_invariant,
    fit_local_z_between_matrices,
    fit_local_z_to_target,
    iswap_target,
    raised_cosine_envelope,
)


def test_ideal_iswap_has_zero_conditional_phase_invariant():
    assert abs(conditional_phase_invariant(iswap_target())) < 1e-14


def test_local_z_alignment_recovers_phase_gauge_equivalence():
    target = iswap_target()
    parameters = np.array([0.37, -0.21, 0.14, 0.19, -0.31])
    phase_shifted = apply_local_z(target, parameters)
    aligned = fit_local_z_between_matrices(target, phase_shifted)
    assert aligned["phase_aligned_frobenius_difference"] < 1e-10
    assert aligned["raw_frobenius_difference"] > 0.1


def test_local_z_fit_reports_unit_process_overlap_for_iswap():
    result = fit_local_z_to_target(iswap_target())
    assert result["projected_process_overlap"] > 1.0 - 1e-12
    assert result["average_logical_state_fidelity_including_leakage"] > 1.0 - 1e-12


def test_raised_cosine_has_zero_endpoints_and_unit_plateau():
    duration = 1.0
    frequency = 1000.0
    ramp = 8.0 / frequency
    assert raised_cosine_envelope(0.0, duration, frequency, 8.0) == 0.0
    assert abs(raised_cosine_envelope(ramp / 2, duration, frequency, 8.0) - 0.5) < 1e-14
    assert raised_cosine_envelope(duration / 2, duration, frequency, 8.0) == 1.0
    assert raised_cosine_envelope(duration, duration, frequency, 8.0) == 0.0


def test_fixed_dc_basis_rebuilds_expected_four_dressed_logical_states():
    from rft_qpu.stage5_gate import build_fixed_basis_model

    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    assert model.h_static_MHz.shape == (125, 125)
    assert np.allclose(model.h_static_MHz, model.h_static_MHz.conj().T, atol=1e-10)
    assert model.logical_eigen_indices == [0, 3, 1, 7]
    assert np.linalg.norm(model.delta_h_coupler(model.flux_dc_Phi0)) < 1e-9


def test_conditional_phase_invariant_is_unchanged_by_local_z_and_global_phase():
    source = np.eye(4, dtype=np.complex128)
    source[0, 0] = np.exp(0.23j)
    source[3, 3] = np.exp(-0.17j)
    source[2, 1] = 0.8 * np.exp(1.1j)
    source[1, 2] = 0.75 * np.exp(-0.9j)
    parameters = np.array([0.41, -0.27, 0.16, 0.33, -0.22])
    before = conditional_phase_invariant(source)
    after = conditional_phase_invariant(apply_local_z(source, parameters))
    assert abs(np.angle(np.exp(1j * (before - after)))) < 1e-13
