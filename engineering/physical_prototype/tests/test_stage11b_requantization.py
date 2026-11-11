from __future__ import annotations

import numpy as np

from rft_qpu.stage5_gate import GatePulse, propagate_gate
from rft_qpu.stage11b_requantization import build_requantized_model


def test_requantized_three_mode_hamiltonian_is_hermitian_and_tracked():
    built = build_requantized_model(
        charge_cutoff=8,
        levels_kept=3,
        bias_flux_Phi0=0.25934367625232047,
    )
    model = built.model
    assert model.h_static_MHz.shape == (27, 27)
    assert np.allclose(model.h_static_MHz, model.h_static_MHz.conj().T, atol=2e-10)
    assert len(set(model.logical_eigen_indices)) == 4
    assert built.diagnostics["minimum_bare_product_overlap"] > 0.9


def test_requantized_drive_is_zero_at_the_new_dc_bias_and_hermitian_away_from_it():
    bias = 0.25934367625232047
    model = build_requantized_model(
        charge_cutoff=8,
        levels_kept=3,
        bias_flux_Phi0=bias,
    ).model
    assert np.linalg.norm(model.delta_h_coupler(bias), ord="fro") < 1e-12
    driven = model.delta_h_coupler(bias + 0.001)
    assert np.allclose(driven, driven.conj().T, atol=2e-10)
    assert np.linalg.norm(driven, ord="fro") > 0.0


def test_requantized_model_propagates_a_finite_four_state_logical_matrix():
    model = build_requantized_model(
        charge_cutoff=8,
        levels_kept=3,
        bias_flux_Phi0=0.25934367625232047,
    ).model
    pulse = GatePulse(
        pump_frequency_MHz=987.6092214991908,
        flux_amplitude_Phi0=0.0,
        duration_us=0.001,
        ramp_periods=0.0,
    )
    result = propagate_gate(model, pulse, steps_per_period=8)
    assert result["logical_matrix"].shape == (4, 4)
    assert np.isfinite(result["logical_matrix"]).all()
    assert result["max_norm_error_sampled"] < 1e-8
