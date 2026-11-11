"""Stage 11A: re-quantize the local SQUID coupler at a shifted DC flux.

This module audits the *local coupler basis* against the Stage-3 circuit
assumptions. It does not yet rebuild or propagate the full three-mode gate.
Units: MHz, fF, and flux quanta Phi_0.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import linear_sum_assignment

from .circuit_quantization import (
    CircuitParameters,
    build_capacitance_matrix,
    charge_operators,
    squid_parameters,
)


@dataclass(frozen=True)
class LocalCouplerPoint:
    flux_Phi0: float
    charge_cutoff: int
    ec_MHz: float
    ej_effective_MHz: float
    phase_offset_rad: float
    energies_MHz: np.ndarray
    eigenvectors: np.ndarray
    n_matrix: np.ndarray
    cos_matrix: np.ndarray
    sin_matrix: np.ndarray


def diagonalize_local_coupler(
    params: CircuitParameters, flux_Phi0: float, charge_cutoff: int
) -> LocalCouplerPoint:
    """Diagonalize the local SQUID-coupler Hamiltonian at an explicit flux."""
    params.validate()
    flux = float(flux_Phi0)
    if not math.isfinite(flux) or not 0.0 < flux < 0.5:
        raise ValueError("flux_Phi0 must be finite and inside (0, 0.5)")
    if int(charge_cutoff) != charge_cutoff or charge_cutoff < 4:
        raise ValueError("charge_cutoff must be an integer >= 4")

    _, ec_matrix = build_capacitance_matrix(params)
    ec_c = float(ec_matrix[1, 1])
    charges, n_op, cos_phi, sin_phi = charge_operators(int(charge_cutoff))
    ej_eff, phase = squid_parameters(
        flux, params.ej_c_sum_MHz, params.squid_asymmetry
    )
    shifted_cos = cos_phi * math.cos(phase) - sin_phi * math.sin(phase)
    h_local = 4.0 * ec_c * np.diag(charges**2) - ej_eff * shifted_cos

    hermiticity_error = float(np.max(np.abs(h_local - h_local.conj().T)))
    if hermiticity_error > 1e-10:
        raise ArithmeticError(f"local coupler Hamiltonian is not Hermitian: {hermiticity_error}")

    energies, vectors = eigh(h_local, check_finite=True)
    energies = np.asarray(energies - energies[0], dtype=float)
    n_eigen = vectors.conj().T @ n_op @ vectors
    cos_eigen = vectors.conj().T @ cos_phi @ vectors
    sin_eigen = vectors.conj().T @ sin_phi @ vectors
    return LocalCouplerPoint(
        flux_Phi0=flux,
        charge_cutoff=int(charge_cutoff),
        ec_MHz=ec_c,
        ej_effective_MHz=float(ej_eff),
        phase_offset_rad=float(phase),
        energies_MHz=energies,
        eigenvectors=vectors,
        n_matrix=n_eigen,
        cos_matrix=cos_eigen,
        sin_matrix=sin_eigen,
    )


def _align_new_basis(old: LocalCouplerPoint, new: LocalCouplerPoint):
    """Match new eigenvectors to old states and remove arbitrary eigenvector phases."""
    if old.eigenvectors.shape != new.eigenvectors.shape:
        raise ValueError("old and new bases must use the same charge cutoff")
    overlap = old.eigenvectors.conj().T @ new.eigenvectors
    probabilities = np.abs(overlap) ** 2
    rows, cols = linear_sum_assignment(-probabilities)
    new_index_for_old = np.empty(probabilities.shape[0], dtype=int)
    new_index_for_old[rows] = cols

    vectors = new.eigenvectors[:, new_index_for_old].copy()
    energies = new.energies_MHz[new_index_for_old].copy()
    matched = old.eigenvectors.conj().T @ vectors
    diagonal = np.diag(matched)
    phases = np.ones(diagonal.shape, dtype=np.complex128)
    nonzero = np.abs(diagonal) > 1e-14
    phases[nonzero] = np.conj(diagonal[nonzero]) / np.abs(diagonal[nonzero])
    vectors *= phases[np.newaxis, :]

    # Re-express operators in the reordered, phase-aligned eigenbasis.
    charges, n_op, cos_phi, sin_phi = charge_operators(old.charge_cutoff)
    n_aligned = vectors.conj().T @ n_op @ vectors
    cos_aligned = vectors.conj().T @ cos_phi @ vectors
    sin_aligned = vectors.conj().T @ sin_phi @ vectors
    aligned_overlap = old.eigenvectors.conj().T @ vectors
    state_overlap = np.abs(np.diag(aligned_overlap)) ** 2
    return {
        "new_index_for_old": new_index_for_old,
        "energies_MHz": energies,
        "eigenvectors": vectors,
        "overlap_probability_matrix": probabilities,
        "state_overlap_probability": state_overlap,
        "n_matrix": n_aligned,
        "cos_matrix": cos_aligned,
        "sin_matrix": sin_aligned,
    }


def analyze_bias_requantization(
    params: CircuitParameters,
    base_flux_Phi0: float,
    bias_offset_Phi0: float,
    charge_cutoffs: Iterable[int] = (8, 10, 12),
    levels_kept: Iterable[int] = (3, 4, 5),
):
    """Compare old and explicitly re-quantized local coupler bases."""
    base_flux = float(base_flux_Phi0)
    offset = float(bias_offset_Phi0)
    new_flux = base_flux + offset
    if not (math.isfinite(base_flux) and math.isfinite(offset)):
        raise ValueError("base flux and bias offset must be finite")
    if not 0.0 < base_flux < 0.5 or not 0.0 < new_flux < 0.5:
        raise ValueError("both base and shifted flux must lie inside (0, 0.5)")

    cutoffs = tuple(int(x) for x in charge_cutoffs)
    levels = tuple(int(x) for x in levels_kept)
    if not cutoffs or len(set(cutoffs)) != len(cutoffs) or any(x < 4 for x in cutoffs):
        raise ValueError("charge_cutoffs must be unique integers >= 4")
    if not levels or len(set(levels)) != len(levels) or any(x not in (3, 4, 5) for x in levels):
        raise ValueError("levels_kept must be unique values selected from 3, 4, 5")

    rows = []
    arrays: dict[str, np.ndarray] = {}
    spectra = {}
    for cutoff in cutoffs:
        point_params = CircuitParameters(
            target_frequencies_MHz=tuple(params.target_frequencies_MHz),
            nominal_EC_MHz=tuple(params.nominal_EC_MHz),
            c_ac_fF=params.c_ac_fF,
            c_cb_fF=params.c_cb_fF,
            c_ab_fF=params.c_ab_fF,
            ej_c_sum_MHz=params.ej_c_sum_MHz,
            squid_asymmetry=params.squid_asymmetry,
            charge_cutoff=cutoff,
            levels_kept=max(levels),
        )
        point_params.validate()
        old = diagonalize_local_coupler(point_params, base_flux, cutoff)
        new = diagonalize_local_coupler(point_params, new_flux, cutoff)
        aligned = _align_new_basis(old, new)
        spectra[cutoff] = (old, new, aligned)

        arrays[f"cutoff_{cutoff}_old_energies_MHz"] = old.energies_MHz
        arrays[f"cutoff_{cutoff}_new_energies_MHz"] = new.energies_MHz
        arrays[f"cutoff_{cutoff}_overlap_probability"] = aligned["overlap_probability_matrix"]
        for label, point, aligned_matrix in (
            ("n", old.n_matrix, aligned["n_matrix"]),
            ("cos", old.cos_matrix, aligned["cos_matrix"]),
            ("sin", old.sin_matrix, aligned["sin_matrix"]),
        ):
            arrays[f"cutoff_{cutoff}_{label}_old"] = point[:5, :5]
            arrays[f"cutoff_{cutoff}_{label}_new_aligned"] = aligned_matrix[:5, :5]

        for count in levels:
            if count > old.eigenvectors.shape[1]:
                raise ValueError(f"levels_kept={count} exceeds available basis at cutoff {cutoff}")
            old_subspace = old.eigenvectors[:, :count]
            new_subspace = aligned["eigenvectors"][:, :count]
            singular_values = np.linalg.svd(
                old_subspace.conj().T @ new_subspace, compute_uv=False
            )
            principal_min = float(np.min(singular_values))
            state_overlaps = aligned["state_overlap_probability"][:count]

            def op_diff(name: str, old_op: np.ndarray, new_op: np.ndarray):
                a = old_op[:count, :count]
                b = new_op[:count, :count]
                norm = float(np.linalg.norm(a, ord="fro"))
                diff = float(np.linalg.norm(a - b, ord="fro"))
                return diff, diff / max(norm, 1e-15)

            n_diff, n_rel = op_diff("n", old.n_matrix, aligned["n_matrix"])
            cos_diff, cos_rel = op_diff("cos", old.cos_matrix, aligned["cos_matrix"])
            sin_diff, sin_rel = op_diff("sin", old.sin_matrix, aligned["sin_matrix"])
            old_f01 = float(old.energies_MHz[1] - old.energies_MHz[0])
            new_f01 = float(aligned["energies_MHz"][1] - aligned["energies_MHz"][0])
            old_alpha = float(old.energies_MHz[2] - 2 * old.energies_MHz[1] + old.energies_MHz[0])
            new_alpha = float(
                aligned["energies_MHz"][2]
                - 2 * aligned["energies_MHz"][1]
                + aligned["energies_MHz"][0]
            )
            rows.append({
                "charge_cutoff": cutoff,
                "levels_kept": count,
                "base_flux_Phi0": base_flux,
                "shifted_flux_Phi0": new_flux,
                "bias_offset_Phi0": offset,
                "EC_c_MHz": old.ec_MHz,
                "EJ_eff_old_MHz": old.ej_effective_MHz,
                "EJ_eff_new_MHz": new.ej_effective_MHz,
                "phase_offset_old_rad": old.phase_offset_rad,
                "phase_offset_new_rad": new.phase_offset_rad,
                "old_f01_MHz": old_f01,
                "new_f01_MHz": new_f01,
                "delta_f01_MHz": new_f01 - old_f01,
                "old_anharmonicity_MHz": old_alpha,
                "new_anharmonicity_MHz": new_alpha,
                "delta_anharmonicity_MHz": new_alpha - old_alpha,
                "old_abs_n01": float(abs(old.n_matrix[0, 1])),
                "new_abs_n01": float(abs(aligned["n_matrix"][0, 1])),
                "delta_abs_n01": float(abs(aligned["n_matrix"][0, 1]) - abs(old.n_matrix[0, 1])),
                "old_abs_n12": float(abs(old.n_matrix[1, 2])),
                "new_abs_n12": float(abs(aligned["n_matrix"][1, 2])),
                "minimum_state_overlap_probability": float(np.min(state_overlaps)),
                "minimum_retained_subspace_singular_value": principal_min,
                "retained_subspace_infidelity_bound": float(max(0.0, 1.0 - principal_min**2)),
                "n_matrix_frobenius_difference": n_diff,
                "n_matrix_relative_difference": n_rel,
                "cos_matrix_frobenius_difference": cos_diff,
                "cos_matrix_relative_difference": cos_rel,
                "sin_matrix_frobenius_difference": sin_diff,
                "sin_matrix_relative_difference": sin_rel,
                "new_index_for_old_first5": aligned["new_index_for_old"][:5].tolist(),
            })

    meta = {
        "stage": 11,
        "substage": "11A_local_coupler_basis_requantization",
        "status": "local_coupler_requantization_audit_complete",
        "base_flux_Phi0": base_flux,
        "bias_offset_Phi0": offset,
        "shifted_flux_Phi0": new_flux,
        "charge_cutoffs": list(cutoffs),
        "levels_kept": list(levels),
        "model_boundary": (
            "Local SQUID-coupler charge-basis diagonalization only. The result does not yet rebuild the full "
            "three-mode driven Hamiltonian, recalculate the complete logical gate, or establish hardware readiness. "
            "Capacitances and Josephson parameters remain the declared Stage-3 assumptions."
        ),
        "basis_tracking": (
            "New eigenstates are matched to old eigenstates by maximum total squared overlap; eigenvector phases "
            "are aligned before comparing truncated operator matrices."
        ),
        "rows": rows,
    }
    return meta, arrays
