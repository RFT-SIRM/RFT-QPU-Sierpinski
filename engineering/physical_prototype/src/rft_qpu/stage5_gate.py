"""Stage 5 full logical-gate convergence audit for the circuit-derived coupler.

The model is rebuilt from the committed Stage-3 charge-basis circuit. The
flux-driven coupler is represented in its fixed DC local eigenbasis, and the
full 5x5x5 product Hilbert space is propagated with a symmetric Strang split.
Frequency is MHz, time is microseconds, flux is Phi_0, and hbar=1.

This is a deterministic closed-system numerical model, not hardware
qualification or an experimental gate-fidelity claim.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.linalg import eigh, expm
from scipy.optimize import brentq, least_squares

from .circuit_quantization import (
    CircuitParameters,
    build_capacitance_matrix,
    charge_operators,
    local_transmon,
    squid_parameters,
    tune_ej_for_frequency,
)


@dataclass(frozen=True)
class GatePulse:
    pump_frequency_MHz: float = 987.5136797993163
    flux_amplitude_Phi0: float = 0.020
    duration_us: float = 1.0625654067723154
    ramp_periods: float = 8.0
    phase_rad: float = 0.0

    def validate(self) -> None:
        values = (self.pump_frequency_MHz, self.flux_amplitude_Phi0,
                  self.duration_us, self.ramp_periods, self.phase_rad)
        if not all(math.isfinite(float(x)) for x in values):
            raise ValueError("pulse parameters must all be finite")
        if self.pump_frequency_MHz <= 0 or self.duration_us <= 0:
            raise ValueError("pump frequency and pulse duration must be positive")
        if self.flux_amplitude_Phi0 < 0 or self.ramp_periods < 0:
            raise ValueError("flux amplitude and ramp duration must be non-negative")


@dataclass
class FixedBasisModel:
    h_static_MHz: np.ndarray
    eigenvalues_MHz: np.ndarray
    eigenvectors: np.ndarray
    logical_basis: np.ndarray
    logical_eigen_indices: list[int]
    flux_dc_Phi0: float
    delta_h_coupler: object
    coupler_number_matrix: np.ndarray
    dimension_per_mode: int


def wrap_phase(value: float) -> float:
    """Map a phase to (-pi, pi]."""
    return float(np.angle(np.exp(1j * value)))


def iswap_target() -> np.ndarray:
    """iSWAP in logical order |00>, |10>, |01>, |11>."""
    target = np.eye(4, dtype=np.complex128)
    target[1, 1] = 0.0
    target[2, 2] = 0.0
    target[1, 2] = 1.0j
    target[2, 1] = 1.0j
    return target


def conditional_phase_invariant(matrix: np.ndarray) -> float:
    """Nonlocal iSWAP phase invariant, zero for ideal iSWAP up to local Z/global phase.

    For the dominant transitions |00>->|00>, |11>->|11>,
    |10>->|01>, |01>->|10>, the invariant is
      arg(U00) + arg(U33) - arg(U21) - arg(U12) + pi.
    """
    u = np.asarray(matrix, dtype=np.complex128)
    if u.shape != (4, 4):
        raise ValueError("logical matrix must be 4x4")
    value = (np.angle(u[0, 0]) + np.angle(u[3, 3])
             - np.angle(u[2, 1]) - np.angle(u[1, 2]) + math.pi)
    return wrap_phase(float(value))


def _local_z_diagonals(parameters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Global phase + output A/B Z + input A/B Z phase diagonals."""
    global_phase, out_a, out_b, in_a, in_b = map(float, parameters)
    d_out = np.diag(np.exp(1j * np.array([
        global_phase,
        global_phase + out_a,
        global_phase + out_b,
        global_phase + out_a + out_b,
    ])))
    d_in = np.diag(np.exp(1j * np.array([0.0, in_a, in_b, in_a + in_b])))
    return d_out, d_in


def apply_local_z(matrix: np.ndarray, parameters: np.ndarray) -> np.ndarray:
    d_out, d_in = _local_z_diagonals(parameters)
    return d_out @ np.asarray(matrix, dtype=np.complex128) @ d_in


def fit_local_z_to_target(matrix: np.ndarray, target: np.ndarray | None = None) -> dict:
    """Fit four local Z phases and a global phase by full complex matrix least squares."""
    u = np.asarray(matrix, dtype=np.complex128)
    target = iswap_target() if target is None else np.asarray(target, dtype=np.complex128)
    if u.shape != (4, 4) or target.shape != (4, 4):
        raise ValueError("source and target logical matrices must be 4x4")

    def residual(parameters: np.ndarray) -> np.ndarray:
        delta = apply_local_z(u, parameters) - target
        return np.concatenate((delta.real.ravel(), delta.imag.ravel()))

    solution = least_squares(
        residual, np.zeros(5), max_nfev=10000,
        xtol=1e-13, ftol=1e-13, gtol=1e-13,
    )
    corrected = apply_local_z(u, solution.x)
    trace_overlap = abs(np.trace(target.conj().T @ corrected))
    process_overlap = float(trace_overlap**2 / 16.0)
    projected_norm = float(np.trace(corrected.conj().T @ corrected).real)
    average_fidelity = float((projected_norm + trace_overlap**2) / 20.0)
    return {
        "phase_parameters_rad_global_outA_outB_inA_inB": solution.x.tolist(),
        "phase_parameters_deg_global_outA_outB_inA_inB": np.rad2deg(solution.x).tolist(),
        "phase_corrected_matrix": corrected,
        "projected_process_overlap": process_overlap,
        "average_logical_state_fidelity_including_leakage": average_fidelity,
        "frobenius_distance_to_iSWAP": float(np.linalg.norm(corrected - target, ord="fro")),
        "optimizer_cost": float(solution.cost),
        "optimizer_success": bool(solution.success),
    }


def fit_local_z_between_matrices(reference: np.ndarray, candidate: np.ndarray) -> dict:
    """Align candidate to reference using independent input/output local Z rotations.

    A global phase is included. This compares full complex matrices while
    quotienting out phases that are local-frame conventions.
    """
    a = np.asarray(reference, dtype=np.complex128)
    b = np.asarray(candidate, dtype=np.complex128)
    if a.shape != (4, 4) or b.shape != (4, 4):
        raise ValueError("both logical matrices must be 4x4")

    def residual(parameters: np.ndarray) -> np.ndarray:
        delta = apply_local_z(b, parameters) - a
        return np.concatenate((delta.real.ravel(), delta.imag.ravel()))

    solution = least_squares(
        residual, np.zeros(5), max_nfev=10000,
        xtol=1e-13, ftol=1e-13, gtol=1e-13,
    )
    aligned = apply_local_z(b, solution.x)
    delta = aligned - a
    return {
        "aligned_matrix": aligned,
        "phase_parameters_rad_global_outA_outB_inA_inB": solution.x.tolist(),
        "raw_frobenius_difference": float(np.linalg.norm(a - b, ord="fro")),
        "phase_aligned_frobenius_difference": float(np.linalg.norm(delta, ord="fro")),
        "phase_aligned_max_element_difference": float(np.max(np.abs(delta))),
        "optimizer_success": bool(solution.success),
    }


def build_fixed_basis_model(charge_cutoff: int = 10, levels_kept: int = 5) -> FixedBasisModel:
    """Rebuild Stage-4's fixed-DC-basis 3-mode circuit Hamiltonian.

    Uses the same charge-basis, capacitance and asymmetric-SQUID equations as
    the committed Stage-3 module. Logical dressed states are tracked by their
    maximum overlap with the bare |000>, |100>, |001>, |101> product states.
    """
    params = CircuitParameters(charge_cutoff=charge_cutoff, levels_kept=levels_kept)
    params.validate()
    capacitance, charging = build_capacitance_matrix(params)
    ec_diag = np.diag(charging)
    f_a, f_c, f_b = params.target_frequencies_MHz

    ej_a = tune_ej_for_frequency(ec_diag[0], f_a, charge_cutoff)
    ej_b = tune_ej_for_frequency(ec_diag[2], f_b, charge_cutoff)

    def coupler_f01(flux: float) -> float:
        ej_eff, phase = squid_parameters(
            flux, params.ej_c_sum_MHz, params.squid_asymmetry
        )
        energies, *_ = local_transmon(ec_diag[1], ej_eff, phase, charge_cutoff)
        return float(energies[1] - energies[0])

    flux_dc = float(brentq(lambda flux: coupler_f01(flux) - f_c,
                           0.001, 0.48, xtol=1e-12))
    ej_c_eff, phase_c = squid_parameters(
        flux_dc, params.ej_c_sum_MHz, params.squid_asymmetry
    )

    local = [
        local_transmon(ec_diag[0], ej_a, 0.0, charge_cutoff),
        local_transmon(ec_diag[1], ej_c_eff, phase_c, charge_cutoff),
        local_transmon(ec_diag[2], ej_b, 0.0, charge_cutoff),
    ]
    energies = [item[0][:levels_kept] - item[0][0] for item in local]
    number_matrices = [item[1][:levels_kept, :levels_kept] for item in local]
    identity = np.eye(levels_kept, dtype=np.complex128)
    dimension = levels_kept**3
    h_static = np.zeros((dimension, dimension), dtype=np.complex128)
    h_static += np.kron(np.kron(np.diag(energies[0]), identity), identity)
    h_static += np.kron(np.kron(identity, np.diag(energies[1])), identity)
    h_static += np.kron(np.kron(identity, identity), np.diag(energies[2]))
    for i, j in ((0, 1), (0, 2), (1, 2)):
        ops = [identity, identity, identity]
        ops[i] = number_matrices[i]
        ops[j] = number_matrices[j]
        h_static += 8.0 * charging[i, j] * np.kron(np.kron(ops[0], ops[1]), ops[2])

    eigenvalues, eigenvectors = eigh(h_static)

    def bare_index(state: tuple[int, int, int]) -> int:
        return state[0] * levels_kept**2 + state[1] * levels_kept + state[2]

    bare_states = ((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1))
    logical_indices = [
        int(np.argmax(np.abs(eigenvectors[bare_index(state), :])**2))
        for state in bare_states
    ]
    if len(set(logical_indices)) != 4:
        raise RuntimeError("dressed logical states are not uniquely tracked")
    logical_basis = eigenvectors[:, logical_indices]

    # Recover the coupler's fixed-DC charge-basis eigenvectors for projection.
    charges, _n_charge, cos_phi, sin_phi = charge_operators(charge_cutoff)
    shifted_cos = cos_phi * math.cos(phase_c) - sin_phi * math.sin(phase_c)
    h_c_dc = (4.0 * ec_diag[1] * np.diag(charges**2)
              - ej_c_eff * shifted_cos)
    _ec, v_c = eigh(h_c_dc)
    v_c = v_c[:, :levels_kept]
    cos_fixed = v_c.conj().T @ cos_phi @ v_c
    sin_fixed = v_c.conj().T @ sin_phi @ v_c
    ej0, phase0 = squid_parameters(
        flux_dc, params.ej_c_sum_MHz, params.squid_asymmetry
    )
    coeff_cos0 = -ej0 * math.cos(phase0)
    coeff_sin0 = ej0 * math.sin(phase0)

    def delta_h_coupler(flux: float) -> np.ndarray:
        ej_eff, phase = squid_parameters(
            float(flux), params.ej_c_sum_MHz, params.squid_asymmetry
        )
        coeff_cos = -ej_eff * math.cos(phase)
        coeff_sin = ej_eff * math.sin(phase)
        return ((coeff_cos - coeff_cos0) * cos_fixed
                + (coeff_sin - coeff_sin0) * sin_fixed)

    return FixedBasisModel(
        h_static_MHz=h_static,
        eigenvalues_MHz=eigenvalues,
        eigenvectors=eigenvectors,
        logical_basis=logical_basis,
        logical_eigen_indices=logical_indices,
        flux_dc_Phi0=flux_dc,
        delta_h_coupler=delta_h_coupler,
        coupler_number_matrix=number_matrices[1],
        dimension_per_mode=levels_kept,
    )


def raised_cosine_envelope(time_us: float, duration_us: float,
                           pump_frequency_MHz: float, ramp_periods: float = 8.0) -> float:
    ramp = ramp_periods / pump_frequency_MHz
    if ramp <= 0:
        return 1.0
    if time_us < ramp:
        return 0.5 * (1.0 - math.cos(math.pi * time_us / ramp))
    if time_us > duration_us - ramp:
        return 0.5 * (1.0 - math.cos(math.pi * (duration_us - time_us) / ramp))
    return 1.0


def _coupler_excited_probability(psi: np.ndarray, levels: int) -> np.ndarray:
    states = psi.reshape(levels, levels, levels, 4)
    return np.sum(np.abs(states[:, 1:, :, :])**2, axis=(0, 1, 2)).real


def propagate_gate(model: FixedBasisModel, pulse: GatePulse, steps_per_period: int,
                   track_stride: int | None = None) -> dict:
    """Propagate all four dressed logical inputs with a symmetric Strang split."""
    pulse.validate()
    if steps_per_period < 8:
        raise ValueError("steps_per_period must be at least 8")
    levels = model.dimension_per_mode
    dt = 1.0 / (pulse.pump_frequency_MHz * steps_per_period)
    steps = int(round(pulse.duration_us / dt))
    duration_actual = steps * dt
    if abs(duration_actual - pulse.duration_us) > 0.51 * dt:
        raise ValueError("duration could not be represented on this time grid")

    half_phase = np.exp(-1j * 2.0 * math.pi * model.eigenvalues_MHz * dt / 2.0)
    u_static_half = (model.eigenvectors * half_phase) @ model.eigenvectors.conj().T
    psi = model.logical_basis.copy()
    stride = track_stride if track_stride is not None else max(1, steps_per_period // 24)
    max_coupler = np.zeros(4, dtype=float)
    max_logical_leakage = np.zeros(4, dtype=float)
    max_norm_error = 0.0

    for step in range(steps):
        t_mid = (step + 0.5) * dt
        envelope = raised_cosine_envelope(
            t_mid, duration_actual, pulse.pump_frequency_MHz, pulse.ramp_periods
        )
        flux = (model.flux_dc_Phi0 + pulse.flux_amplitude_Phi0 * envelope
                * math.cos(2.0 * math.pi * pulse.pump_frequency_MHz * t_mid
                           + pulse.phase_rad))
        delta_h = model.delta_h_coupler(flux)
        u_drive = expm(-1j * 2.0 * math.pi * delta_h * dt)

        psi = u_static_half @ psi
        tensor = psi.reshape(levels, levels, levels, 4)
        tensor = np.einsum("ij,ajbk->aibk", u_drive, tensor, optimize=False)
        psi = tensor.reshape(levels**3, 4)
        psi = u_static_half @ psi

        if step % stride == 0 or step == steps - 1:
            p_c = _coupler_excited_probability(psi, levels)
            max_coupler = np.maximum(max_coupler, p_c)
            logical_projection = model.logical_basis.conj().T @ psi
            p_logical = np.sum(np.abs(logical_projection)**2, axis=0)
            max_logical_leakage = np.maximum(max_logical_leakage, 1.0 - p_logical)
            norms = np.sum(np.abs(psi)**2, axis=0)
            max_norm_error = max(max_norm_error, float(np.max(np.abs(norms - 1.0))))

    logical_matrix = model.logical_basis.conj().T @ psi
    final_norms = np.sum(np.abs(psi)**2, axis=0)
    final_leakage = 1.0 - np.sum(np.abs(logical_matrix)**2, axis=0)
    fitted = fit_local_z_to_target(logical_matrix)
    return {
        "steps_per_period": int(steps_per_period),
        "time_steps": int(steps),
        "dt_ns": float(dt * 1000.0),
        "requested_duration_us": float(pulse.duration_us),
        "actual_duration_us": float(duration_actual),
        "transfer_A_to_B": float(abs(logical_matrix[2, 1])**2),
        "transfer_B_to_A": float(abs(logical_matrix[1, 2])**2),
        "conditional_phase_iSWAP_rad": conditional_phase_invariant(logical_matrix),
        "conditional_phase_iSWAP_deg": float(math.degrees(conditional_phase_invariant(logical_matrix))),
        "final_logical_leakage_by_input": final_leakage.tolist(),
        "max_logical_leakage_sampled_by_input": max_logical_leakage.tolist(),
        "max_coupler_excited_probability_sampled_by_input": max_coupler.tolist(),
        "max_norm_error_sampled": float(max_norm_error),
        "final_norm_error": float(np.max(np.abs(final_norms - 1.0))),
        "logical_unitarity_defect_frobenius": float(
            np.linalg.norm(logical_matrix.conj().T @ logical_matrix - np.eye(4), ord="fro")
        ),
        "projected_process_overlap_after_local_Z": fitted["projected_process_overlap"],
        "average_logical_fidelity_including_leakage": fitted[
            "average_logical_state_fidelity_including_leakage"
        ],
        "frobenius_distance_corrected_matrix_to_iSWAP": fitted[
            "frobenius_distance_to_iSWAP"
        ],
        "local_Z_fit_rad_global_outA_outB_inA_inB": fitted[
            "phase_parameters_rad_global_outA_outB_inA_inB"
        ],
        "logical_matrix": logical_matrix,
        "phase_corrected_matrix": fitted["phase_corrected_matrix"],
    }


def analyze_matrix_convergence(results: list[dict]) -> dict:
    """Compare each neighbouring pair before/after local-Z phase alignment."""
    ordered = sorted(results, key=lambda row: row["steps_per_period"])
    pairs = []
    for left, right in zip(ordered[:-1], ordered[1:]):
        fit = fit_local_z_between_matrices(left["logical_matrix"], right["logical_matrix"])
        pairs.append({
            "coarse_steps_per_period": left["steps_per_period"],
            "fine_steps_per_period": right["steps_per_period"],
            "raw_frobenius_difference": fit["raw_frobenius_difference"],
            "phase_aligned_frobenius_difference": fit[
                "phase_aligned_frobenius_difference"
            ],
            "phase_aligned_max_element_difference": fit[
                "phase_aligned_max_element_difference"
            ],
            "conditional_phase_difference_rad": wrap_phase(
                conditional_phase_invariant(left["logical_matrix"])
                - conditional_phase_invariant(right["logical_matrix"])
            ),
            "phase_fit_rad_global_outA_outB_inA_inB": fit[
                "phase_parameters_rad_global_outA_outB_inA_inB"
            ],
        })
    return {"adjacent_grid_comparisons": pairs}


def richardson_extrapolate(values_by_grid: dict[int, float]) -> float | None:
    """Second-order Richardson extrapolation for grids h, h/2, h/4."""
    keys = sorted(values_by_grid)
    if len(keys) < 3 or keys[-1] != 4 * keys[0] or keys[1] != 2 * keys[0]:
        return None
    coarse, medium, fine = (values_by_grid[key] for key in keys)
    return float(fine + (fine - medium) / 3.0)
