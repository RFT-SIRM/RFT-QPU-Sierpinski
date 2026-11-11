"""Stage 11B: full gate model in the shifted, re-quantized SQUID basis."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh

from .circuit_quantization import (
    CircuitParameters,
    build_capacitance_matrix,
    local_transmon,
    squid_parameters,
    tune_ej_for_frequency,
)
from .stage5_gate import FixedBasisModel


@dataclass(frozen=True)
class RequantizedModelBuild:
    model: FixedBasisModel
    diagnostics: dict[str, object]


def build_requantized_model(
    *,
    charge_cutoff: int = 10,
    levels_kept: int = 5,
    bias_flux_Phi0: float = 0.25934367625232047,
) -> RequantizedModelBuild:
    """Rebuild the full A--coupler--B Hamiltonian at an explicit shifted flux.

    The two data-transmon bases retain the Stage-3 assumptions. The coupler is
    independently diagonalized at the supplied shifted DC flux. All three
    capacitive number-number interactions are then assembled in the new local
    product basis. Units are MHz, microseconds, and Phi_0.
    """
    if int(charge_cutoff) != charge_cutoff or int(levels_kept) != levels_kept:
        raise ValueError("charge_cutoff and levels_kept must be integers")
    params = CircuitParameters(
        charge_cutoff=int(charge_cutoff),
        levels_kept=int(levels_kept),
    )
    params.validate()
    bias = float(bias_flux_Phi0)
    if not math.isfinite(bias) or not 0.0 < bias < 0.5:
        raise ValueError("bias_flux_Phi0 must be finite and inside (0, 0.5)")

    _, charging = build_capacitance_matrix(params)
    ec_diag = np.diag(charging)
    f_a, _, f_b = params.target_frequencies_MHz
    ej_a = tune_ej_for_frequency(ec_diag[0], f_a, charge_cutoff)
    ej_b = tune_ej_for_frequency(ec_diag[2], f_b, charge_cutoff)
    ej_c, phase_c = squid_parameters(
        bias, params.ej_c_sum_MHz, params.squid_asymmetry
    )

    local_a = local_transmon(ec_diag[0], ej_a, 0.0, charge_cutoff)
    local_c = local_transmon(ec_diag[1], ej_c, phase_c, charge_cutoff)
    local_b = local_transmon(ec_diag[2], ej_b, 0.0, charge_cutoff)
    local = (local_a, local_c, local_b)

    energies = [
        point[0][:levels_kept] - point[0][0]
        for point in local
    ]
    number = [
        point[1][:levels_kept, :levels_kept]
        for point in local
    ]
    identity = np.eye(levels_kept, dtype=np.complex128)
    dimension = levels_kept ** 3
    h_static = np.zeros((dimension, dimension), dtype=np.complex128)
    h_static += np.kron(np.kron(np.diag(energies[0]), identity), identity)
    h_static += np.kron(np.kron(identity, np.diag(energies[1])), identity)
    h_static += np.kron(np.kron(identity, identity), np.diag(energies[2]))

    for i, j in ((0, 1), (0, 2), (1, 2)):
        operators = [identity, identity, identity]
        operators[i] = number[i]
        operators[j] = number[j]
        h_static += 8.0 * charging[i, j] * np.kron(
            np.kron(operators[0], operators[1]), operators[2]
        )

    hermiticity_error = float(np.max(np.abs(h_static - h_static.conj().T)))
    if hermiticity_error > 2e-10:
        raise ArithmeticError(f"static Hamiltonian is not Hermitian: {hermiticity_error}")
    eigenvalues, eigenvectors = eigh(h_static, check_finite=True)

    bare_states = {
        "ground": (0, 0, 0),
        "A_01": (1, 0, 0),
        "B_01": (0, 0, 1),
        "A1_B1": (1, 0, 1),
    }
    logical_indices: list[int] = []
    bare_overlaps: dict[str, float] = {}
    for label, state in bare_states.items():
        bare_index = state[0] * levels_kept**2 + state[1] * levels_kept + state[2]
        weights = np.abs(eigenvectors[bare_index, :]) ** 2
        index = int(np.argmax(weights))
        logical_indices.append(index)
        bare_overlaps[label] = float(weights[index])
    if len(set(logical_indices)) != 4:
        raise RuntimeError(f"logical states are not uniquely tracked: {logical_indices}")

    # local_transmon returns n, cos(phi), sin(phi) in the new coupler basis.
    coupler_number = number[1]
    coupler_cos = local_c[2][:levels_kept, :levels_kept]
    coupler_sin = local_c[3][:levels_kept, :levels_kept]
    coeff_cos_0 = -ej_c * math.cos(phase_c)
    coeff_sin_0 = ej_c * math.sin(phase_c)

    def delta_h_coupler(flux: float) -> np.ndarray:
        value = float(flux)
        if not math.isfinite(value) or not 0.0 < value < 0.5:
            raise ValueError("drive flux must be finite and inside (0, 0.5)")
        ej_value, phase_value = squid_parameters(
            value, params.ej_c_sum_MHz, params.squid_asymmetry
        )
        coeff_cos = -ej_value * math.cos(phase_value)
        coeff_sin = ej_value * math.sin(phase_value)
        return (
            (coeff_cos - coeff_cos_0) * coupler_cos
            + (coeff_sin - coeff_sin_0) * coupler_sin
        )

    model = FixedBasisModel(
        h_static_MHz=h_static,
        eigenvalues_MHz=eigenvalues,
        eigenvectors=eigenvectors,
        logical_basis=eigenvectors[:, logical_indices],
        logical_eigen_indices=logical_indices,
        flux_dc_Phi0=bias,
        delta_h_coupler=delta_h_coupler,
        coupler_number_matrix=coupler_number,
        dimension_per_mode=levels_kept,
    )

    e00, e10, e01, e11 = (float(eigenvalues[index]) for index in logical_indices)
    diagnostics: dict[str, object] = {
        "charge_cutoff": int(charge_cutoff),
        "levels_kept_per_mode": int(levels_kept),
        "product_hilbert_dimension": int(dimension),
        "bias_flux_Phi0": bias,
        "local_mode_frequencies_MHz": [
            float(point[0][1] - point[0][0]) for point in local
        ],
        "local_mode_anharmonicities_MHz": [
            float(point[0][2] - 2.0 * point[0][1] + point[0][0])
            for point in local
        ],
        "bare_state_logical_indices_ground_A_B_AB": logical_indices,
        "bare_product_overlaps": bare_overlaps,
        "minimum_bare_product_overlap": float(min(bare_overlaps.values())),
        "dressed_A_frequency_MHz": float(e10 - e00),
        "dressed_B_frequency_MHz": float(e01 - e00),
        "dressed_AB_detuning_MHz": float(abs((e10 - e00) - (e01 - e00))),
        "static_ZZ_MHz": float(e11 - e10 - e01 + e00),
        "static_hamiltonian_hermiticity_error": hermiticity_error,
        "drive_zero_at_bias_frobenius": float(
            np.linalg.norm(delta_h_coupler(bias), ord="fro")
        ),
    }
    return RequantizedModelBuild(model=model, diagnostics=diagnostics)
