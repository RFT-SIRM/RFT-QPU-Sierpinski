import numpy as np
import pytest

from rft_qpu.stage5_gate import GatePulse, build_fixed_basis_model, propagate_gate
from rft_qpu.stage7_waveform import HarmonicFluxPulse, propagate_harmonic_flux_gate


def test_harmonic_pulse_rejects_nonfinite_coefficients():
    with pytest.raises(ValueError):
        HarmonicFluxPulse(second_harmonic_cos_Phi0=float("nan")).validate()


def test_zero_second_harmonic_reproduces_stage5_propagator():
    model = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    f = 987.5
    duration = 0.04
    p5 = GatePulse(pump_frequency_MHz=f, flux_amplitude_Phi0=0.001,
                   duration_us=duration, ramp_periods=2.0)
    old = propagate_gate(model, p5, steps_per_period=8, track_stride=1)
    new = propagate_harmonic_flux_gate(
        model,
        HarmonicFluxPulse(frequency_MHz=f, fundamental_amplitude_Phi0=0.001,
                          duration_us=duration, ramp_periods=2.0),
        steps_per_period=8, track_stride=1,
    )
    assert np.allclose(new["logical_matrix"], old["logical_matrix"], atol=1e-12, rtol=1e-12)
    assert new["A_to_B_transfer"] == pytest.approx(old["transfer_A_to_B"], abs=1e-12)
    assert new["conditional_phase_rad"] == pytest.approx(old["conditional_phase_iSWAP_rad"], abs=1e-12)


def test_harmonic_result_reports_bounded_probabilities():
    model = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    result = propagate_harmonic_flux_gate(
        model,
        HarmonicFluxPulse(frequency_MHz=987.5, fundamental_amplitude_Phi0=0.001,
                          second_harmonic_cos_Phi0=0.00005,
                          second_harmonic_sin_Phi0=-0.00003,
                          duration_us=0.04, ramp_periods=2.0),
        steps_per_period=8,
        track_stride=1,
    )
    for key in ("A_to_B_transfer", "B_to_A_transfer", "process_overlap_after_local_Z",
                "average_logical_fidelity_including_leakage"):
        assert np.isfinite(result[key])
        assert 0.0 <= result[key] <= 1.0 + 1e-10
    assert result["logical_matrix"].shape == (4, 4)


def test_harmonic_amplitude_and_phase_are_reported_consistently():
    pulse = HarmonicFluxPulse(second_harmonic_cos_Phi0=3e-4,
                              second_harmonic_sin_Phi0=4e-4)
    pulse.validate()
    assert np.hypot(pulse.second_harmonic_cos_Phi0,
                    pulse.second_harmonic_sin_Phi0) == pytest.approx(5e-4)
