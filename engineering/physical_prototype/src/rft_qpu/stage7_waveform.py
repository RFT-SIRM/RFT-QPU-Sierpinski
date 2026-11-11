"""Stage-7 harmonic flux-waveform shaping in the circuit-derived SQUID model.

A second-harmonic component is added as an independent control quadrature:
  Phi(t) = Phi_DC + env(t) * [A1 cos(wt) + A2c cos(2wt) + A2s sin(2wt)].
All quantities use MHz, microseconds, and Phi_0. Closed-system exploration
only; the extra harmonic is not assumed to be available from real hardware.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import expm

from .stage5_gate import (
    FixedBasisModel,
    GatePulse,
    build_fixed_basis_model,
    conditional_phase_invariant,
    fit_local_z_to_target,
    raised_cosine_envelope,
)


@dataclass(frozen=True)
class HarmonicFluxPulse:
    frequency_MHz: float = 987.5136797993163
    fundamental_amplitude_Phi0: float = 0.020
    second_harmonic_cos_Phi0: float = 0.0
    second_harmonic_sin_Phi0: float = 0.0
    duration_us: float = 1.0625675587737073
    ramp_periods: float = 8.0
    phase_rad: float = 0.0

    def validate(self) -> None:
        values = (
            self.frequency_MHz, self.fundamental_amplitude_Phi0,
            self.second_harmonic_cos_Phi0, self.second_harmonic_sin_Phi0,
            self.duration_us, self.ramp_periods, self.phase_rad,
        )
        if not all(math.isfinite(float(v)) for v in values):
            raise ValueError("pulse parameters must be finite")
        if self.frequency_MHz <= 0 or self.duration_us <= 0:
            raise ValueError("frequency and duration must be positive")
        if self.fundamental_amplitude_Phi0 < 0 or self.ramp_periods < 0:
            raise ValueError("fundamental amplitude and ramp must be non-negative")


def propagate_harmonic_flux_gate(
    model: FixedBasisModel,
    pulse: HarmonicFluxPulse,
    steps_per_period: int = 40,
    track_stride: int | None = None,
) -> dict:
    """Propagate all four logical inputs with a two-quadrature 2w flux term."""
    pulse.validate()
    if steps_per_period < 8:
        raise ValueError("steps_per_period must be >= 8")
    dt = 1.0 / (pulse.frequency_MHz * steps_per_period)
    steps = int(round(pulse.duration_us / dt))
    duration = steps * dt
    if abs(duration - pulse.duration_us) > 0.51 * dt:
        raise ValueError("requested duration not representable on this time grid")
    half_phase = np.exp(-1j * 2.0 * math.pi * model.eigenvalues_MHz * dt / 2.0)
    u_static_half = (model.eigenvectors * half_phase) @ model.eigenvectors.conj().T
    psi = model.logical_basis.copy()
    levels = model.dimension_per_mode
    stride = track_stride if track_stride is not None else max(1, steps_per_period // 24)
    max_coupler = np.zeros(4, dtype=float)
    max_logical_leak = np.zeros(4, dtype=float)
    max_norm_error = 0.0

    for step in range(steps):
        t_mid = (step + 0.5) * dt
        env = raised_cosine_envelope(
            t_mid, duration, pulse.frequency_MHz, pulse.ramp_periods
        )
        theta = 2.0 * math.pi * pulse.frequency_MHz * t_mid + pulse.phase_rad
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
        psi = tensor.reshape(levels ** 3, 4)
        psi = u_static_half @ psi
        if step % stride == 0 or step == steps - 1:
            p_c = np.sum(np.abs(psi.reshape(levels, levels, levels, 4)[:, 1:, :, :]) ** 2,
                         axis=(0, 1, 2))
            p_logical = np.sum(np.abs(model.logical_basis.conj().T @ psi) ** 2, axis=0)
            norms = np.sum(np.abs(psi) ** 2, axis=0)
            max_coupler = np.maximum(max_coupler, p_c.real)
            max_logical_leak = np.maximum(max_logical_leak, 1.0 - p_logical.real)
            max_norm_error = max(max_norm_error, float(np.max(np.abs(norms - 1.0))))

    logical_matrix = model.logical_basis.conj().T @ psi
    final_norms = np.sum(np.abs(psi) ** 2, axis=0)
    leakage = (1.0 - np.sum(np.abs(logical_matrix) ** 2, axis=0)).real
    fit = fit_local_z_to_target(logical_matrix)
    return {
        "frequency_MHz": float(pulse.frequency_MHz),
        "fundamental_amplitude_Phi0": float(pulse.fundamental_amplitude_Phi0),
        "second_harmonic_cos_Phi0": float(pulse.second_harmonic_cos_Phi0),
        "second_harmonic_sin_Phi0": float(pulse.second_harmonic_sin_Phi0),
        "second_harmonic_magnitude_Phi0": float(math.hypot(
            pulse.second_harmonic_cos_Phi0, pulse.second_harmonic_sin_Phi0
        )),
        "second_harmonic_phase_rad": float(math.atan2(
            pulse.second_harmonic_sin_Phi0, pulse.second_harmonic_cos_Phi0
        )),
        "requested_duration_us": float(pulse.duration_us),
        "actual_duration_us": float(duration),
        "steps_per_period": int(steps_per_period),
        "time_steps": int(steps),
        "A_to_B_transfer": float(abs(logical_matrix[2, 1]) ** 2),
        "B_to_A_transfer": float(abs(logical_matrix[1, 2]) ** 2),
        "conditional_phase_rad": conditional_phase_invariant(logical_matrix),
        "final_max_logical_leakage": float(np.max(leakage)),
        "final_logical_leakage_by_input": leakage.tolist(),
        "sampled_max_logical_leakage": float(np.max(max_logical_leak)),
        "sampled_max_logical_leakage_by_input": max_logical_leak.tolist(),
        "sampled_max_coupler_excited_probability": float(np.max(max_coupler)),
        "sampled_max_coupler_excited_probability_by_input": max_coupler.tolist(),
        "logical_unitarity_defect": float(np.linalg.norm(
            logical_matrix.conj().T @ logical_matrix - np.eye(4), ord="fro"
        )),
        "norm_error": float(max(
            max_norm_error, np.max(np.abs(final_norms - 1.0))
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


def run_harmonic_shaping_candidate(
    second_harmonic_cos_Phi0: float,
    second_harmonic_sin_Phi0: float,
    *,
    frequency_MHz: float = 987.5136797993163,
    fundamental_amplitude_Phi0: float = 0.020,
    duration_us: float = 1.0625675587737073,
    steps_per_period: int = 40,
    model: FixedBasisModel | None = None,
) -> dict:
    model = model or build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    pulse = HarmonicFluxPulse(
        frequency_MHz=frequency_MHz,
        fundamental_amplitude_Phi0=fundamental_amplitude_Phi0,
        second_harmonic_cos_Phi0=second_harmonic_cos_Phi0,
        second_harmonic_sin_Phi0=second_harmonic_sin_Phi0,
        duration_us=duration_us,
    )
    return propagate_harmonic_flux_gate(model, pulse, steps_per_period)
