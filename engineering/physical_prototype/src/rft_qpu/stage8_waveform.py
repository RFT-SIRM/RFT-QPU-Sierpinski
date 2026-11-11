"""Stage-8 chirped and asymmetric-envelope parametric-gate controls.

Closed-system, fixed-DC-basis model. Frequency is MHz, time microseconds,
flux Phi_0. This is a numerical control-space exploration, not a calibrated
flux-line waveform or experimental gate qualification.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import expm

from .stage5_gate import (
    FixedBasisModel,
    build_fixed_basis_model,
    conditional_phase_invariant,
    fit_local_z_to_target,
)


@dataclass(frozen=True)
class ChirpedFluxPulse:
    frequency_MHz: float = 987.5136797993163
    fundamental_amplitude_Phi0: float = 0.020
    duration_us: float = 1.0625675587737073
    ramp_in_periods: float = 8.0
    ramp_out_periods: float = 8.0
    chirp_span_kHz: float = 0.0
    phase_rad: float = 0.0
    second_harmonic_cos_Phi0: float = 0.0
    second_harmonic_sin_Phi0: float = 0.0

    def validate(self) -> None:
        values = (
            self.frequency_MHz, self.fundamental_amplitude_Phi0,
            self.duration_us, self.ramp_in_periods, self.ramp_out_periods,
            self.chirp_span_kHz, self.phase_rad,
            self.second_harmonic_cos_Phi0, self.second_harmonic_sin_Phi0,
        )
        if not all(math.isfinite(float(x)) for x in values):
            raise ValueError("all pulse parameters must be finite")
        if self.frequency_MHz <= 0 or self.duration_us <= 0:
            raise ValueError("frequency and duration must be positive")
        if self.fundamental_amplitude_Phi0 < 0:
            raise ValueError("fundamental amplitude must be non-negative")
        if self.ramp_in_periods < 0 or self.ramp_out_periods < 0:
            raise ValueError("ramp periods must be non-negative")
        ramp_total_us = (self.ramp_in_periods + self.ramp_out_periods) / self.frequency_MHz
        if ramp_total_us > self.duration_us:
            raise ValueError("input and output ramps overlap")


def asymmetric_raised_cosine_envelope(
    t_us: float, duration_us: float, frequency_MHz: float,
    ramp_in_periods: float, ramp_out_periods: float,
) -> float:
    """Raised-cosine rise and fall with independently selected durations."""
    rise = ramp_in_periods / frequency_MHz
    fall = ramp_out_periods / frequency_MHz
    if rise > 0.0 and t_us < rise:
        return 0.5 * (1.0 - math.cos(math.pi * t_us / rise))
    if fall > 0.0 and t_us > duration_us - fall:
        return 0.5 * (1.0 - math.cos(math.pi * (duration_us - t_us) / fall))
    return 1.0


def instantaneous_phase_rad(t_us: float, pulse: ChirpedFluxPulse, actual_duration_us: float) -> float:
    """Integrate a linear frequency sweep from f0-Delta/2 to f0+Delta/2."""
    delta_MHz = pulse.chirp_span_kHz * 1e-3
    phase_cycles = pulse.frequency_MHz * t_us + delta_MHz * (
        t_us * t_us / (2.0 * actual_duration_us) - 0.5 * t_us
    )
    return 2.0 * math.pi * phase_cycles + pulse.phase_rad


def propagate_chirped_gate(
    model: FixedBasisModel,
    pulse: ChirpedFluxPulse,
    steps_per_period: int = 40,
    track_stride: int | None = None,
) -> dict:
    """Propagate |00>, |10>, |01>, |11> using a symmetric Strang split."""
    pulse.validate()
    if steps_per_period < 8:
        raise ValueError("steps_per_period must be at least 8")
    dt = 1.0 / (pulse.frequency_MHz * steps_per_period)
    steps = int(round(pulse.duration_us / dt))
    actual_duration = steps * dt
    if abs(actual_duration - pulse.duration_us) > 0.51 * dt:
        raise ValueError("duration is not representable on this time grid")

    half_phase = np.exp(-1j * math.pi * model.eigenvalues_MHz * dt)
    u_static_half = (model.eigenvectors * half_phase) @ model.eigenvectors.conj().T
    psi = model.logical_basis.copy()
    levels = model.dimension_per_mode
    stride = track_stride if track_stride is not None else max(1, steps_per_period // 12)
    max_coupler = np.zeros(4, dtype=float)
    max_leakage = np.zeros(4, dtype=float)
    max_norm_error = 0.0

    delta_MHz = pulse.chirp_span_kHz * 1e-3
    for step in range(steps):
        t_mid = (step + 0.5) * dt
        env = asymmetric_raised_cosine_envelope(
            t_mid, actual_duration, pulse.frequency_MHz,
            pulse.ramp_in_periods, pulse.ramp_out_periods,
        )
        theta = instantaneous_phase_rad(t_mid, pulse, actual_duration)
        flux_delta = env * (
            pulse.fundamental_amplitude_Phi0 * math.cos(theta)
            + pulse.second_harmonic_cos_Phi0 * math.cos(2.0 * theta)
            + pulse.second_harmonic_sin_Phi0 * math.sin(2.0 * theta)
        )
        delta_h = model.delta_h_coupler(model.flux_dc_Phi0 + flux_delta)
        u_drive = expm(-1j * 2.0 * math.pi * delta_h * dt)
        psi = u_static_half @ psi
        tensor = psi.reshape(levels, levels, levels, 4)
        tensor = np.einsum("ij,ajbk->aibk", u_drive, tensor, optimize=False)
        psi = tensor.reshape(levels**3, 4)
        psi = u_static_half @ psi

        if step % stride == 0 or step == steps - 1:
            tensor = psi.reshape(levels, levels, levels, 4)
            p_c = np.sum(np.abs(tensor[:, 1:, :, :]) ** 2, axis=(0, 1, 2)).real
            p_logical = np.sum(np.abs(model.logical_basis.conj().T @ psi) ** 2, axis=0).real
            norms = np.sum(np.abs(psi) ** 2, axis=0).real
            max_coupler = np.maximum(max_coupler, p_c)
            max_leakage = np.maximum(max_leakage, np.maximum(0.0, 1.0 - p_logical))
            max_norm_error = max(max_norm_error, float(np.max(np.abs(norms - 1.0))))

    logical_matrix = model.logical_basis.conj().T @ psi
    final_norm = np.sum(np.abs(psi) ** 2, axis=0).real
    final_leakage = np.maximum(0.0, (1.0 - np.sum(np.abs(logical_matrix) ** 2, axis=0)).real)
    fit = fit_local_z_to_target(logical_matrix)
    inst_start = pulse.frequency_MHz - delta_MHz / 2.0
    inst_end = pulse.frequency_MHz + delta_MHz / 2.0
    return {
        "frequency_MHz": pulse.frequency_MHz,
        "fundamental_amplitude_Phi0": pulse.fundamental_amplitude_Phi0,
        "duration_requested_us": pulse.duration_us,
        "duration_actual_us": actual_duration,
        "ramp_in_periods": pulse.ramp_in_periods,
        "ramp_out_periods": pulse.ramp_out_periods,
        "chirp_span_kHz": pulse.chirp_span_kHz,
        "instantaneous_frequency_start_MHz": inst_start,
        "instantaneous_frequency_end_MHz": inst_end,
        "second_harmonic_cos_Phi0": pulse.second_harmonic_cos_Phi0,
        "second_harmonic_sin_Phi0": pulse.second_harmonic_sin_Phi0,
        "steps_per_period": int(steps_per_period),
        "time_steps": int(steps),
        "A_to_B_transfer": float(abs(logical_matrix[2, 1]) ** 2),
        "B_to_A_transfer": float(abs(logical_matrix[1, 2]) ** 2),
        "conditional_phase_rad": conditional_phase_invariant(logical_matrix),
        "final_max_logical_leakage": float(np.max(final_leakage)),
        "final_logical_leakage_by_input": final_leakage.tolist(),
        "sampled_max_logical_leakage": float(np.max(max_leakage)),
        "sampled_max_logical_leakage_by_input": max_leakage.tolist(),
        "sampled_max_coupler_excited_probability": float(np.max(max_coupler)),
        "sampled_max_coupler_excited_probability_by_input": max_coupler.tolist(),
        "norm_error": float(max(max_norm_error, np.max(np.abs(final_norm - 1.0)))),
        "logical_unitarity_defect": float(np.linalg.norm(
            logical_matrix.conj().T @ logical_matrix - np.eye(4), ord="fro"
        )),
        "process_overlap_after_local_Z": float(fit["projected_process_overlap"]),
        "average_logical_fidelity_including_leakage": float(
            fit["average_logical_state_fidelity_including_leakage"]
        ),
        "frobenius_distance_to_iSWAP_after_local_Z": float(
            fit["frobenius_distance_to_iSWAP"]
        ),
        "local_Z_fit_rad_canonical": np.angle(np.exp(1j * np.asarray(
            fit["phase_parameters_rad_global_outA_outB_inA_inB"], dtype=float
        ))).tolist(),
        "logical_matrix": logical_matrix,
    }
