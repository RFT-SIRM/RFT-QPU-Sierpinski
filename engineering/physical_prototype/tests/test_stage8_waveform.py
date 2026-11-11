import math
import numpy as np
import pytest

from rft_qpu.stage5_gate import GatePulse, build_fixed_basis_model, propagate_gate
from rft_qpu.stage8_waveform import (
    ChirpedFluxPulse,
    asymmetric_raised_cosine_envelope,
    instantaneous_phase_rad,
    propagate_chirped_gate,
)


def test_asymmetric_envelope_has_correct_endpoints_and_plateau():
    f = 1000.0
    duration = 0.020
    rise = 4.0 / f
    fall = 6.0 / f
    assert asymmetric_raised_cosine_envelope(0.0, duration, f, 4.0, 6.0) == pytest.approx(0.0)
    assert asymmetric_raised_cosine_envelope(rise, duration, f, 4.0, 6.0) == pytest.approx(1.0)
    assert asymmetric_raised_cosine_envelope(duration - fall, duration, f, 4.0, 6.0) == pytest.approx(1.0)
    assert asymmetric_raised_cosine_envelope(duration, duration, f, 4.0, 6.0) == pytest.approx(0.0)


def test_zero_chirp_phase_is_exact_carrier_phase():
    pulse = ChirpedFluxPulse(frequency_MHz=987.5, chirp_span_kHz=0.0)
    for t in (0.0, 0.001, 0.25, 1.0):
        assert instantaneous_phase_rad(t, pulse, 1.1) == pytest.approx(
            2.0 * math.pi * pulse.frequency_MHz * t, abs=1e-12
        )


def test_linear_chirp_integral_has_requested_endpoint_frequencies():
    pulse = ChirpedFluxPulse(frequency_MHz=987.5, chirp_span_kHz=8.0)
    duration = 1.0
    eps = 1e-7
    f_start = (
        instantaneous_phase_rad(eps, pulse, duration)
        - instantaneous_phase_rad(0.0, pulse, duration)
    ) / (2.0 * math.pi * eps)
    f_end = (
        instantaneous_phase_rad(duration, pulse, duration)
        - instantaneous_phase_rad(duration - eps, pulse, duration)
    ) / (2.0 * math.pi * eps)
    assert f_start == pytest.approx(987.496, abs=2e-4)
    assert f_end == pytest.approx(987.504, abs=2e-4)


def test_overlapping_ramps_are_rejected():
    pulse = ChirpedFluxPulse(
        frequency_MHz=1000.0, duration_us=0.010,
        ramp_in_periods=6.0, ramp_out_periods=6.0,
    )
    with pytest.raises(ValueError, match="ramps overlap"):
        pulse.validate()


def test_zero_chirp_symmetric_envelope_matches_stage5_propagator():
    model = build_fixed_basis_model(charge_cutoff=8, levels_kept=3)
    pulse_old = GatePulse(
        pump_frequency_MHz=987.5,
        flux_amplitude_Phi0=0.004,
        duration_us=0.020,
        ramp_periods=2.0,
    )
    pulse_new = ChirpedFluxPulse(
        frequency_MHz=pulse_old.pump_frequency_MHz,
        fundamental_amplitude_Phi0=pulse_old.flux_amplitude_Phi0,
        duration_us=pulse_old.duration_us,
        ramp_in_periods=pulse_old.ramp_periods,
        ramp_out_periods=pulse_old.ramp_periods,
    )
    old = propagate_gate(model, pulse_old, 8, track_stride=64)
    new = propagate_chirped_gate(model, pulse_new, 8, track_stride=64)
    assert np.allclose(old["logical_matrix"], new["logical_matrix"], atol=2e-11, rtol=2e-11)
    assert new["process_overlap_after_local_Z"] == pytest.approx(
        old["projected_process_overlap_after_local_Z"], abs=2e-12
    )
