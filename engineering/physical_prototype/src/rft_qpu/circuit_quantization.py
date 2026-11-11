"""Charge-basis quantization for a three-node transmon--SQUID--transmon circuit.

Frequency units are MHz, capacitances are fF, and magnetic flux is in Phi_0.
This module encodes a declared nominal circuit scenario; it is not a layout
extraction, driven-gate simulation, or fabrication-qualified design.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.constants import elementary_charge as E_CHARGE, Planck as PLANCK
from scipy.linalg import eigh
from scipy.optimize import brentq


@dataclass(frozen=True)
class CircuitParameters:
    target_frequencies_MHz: tuple[float, float, float] = (5500.0, 5007.5, 4515.0)
    nominal_EC_MHz: tuple[float, float, float] = (250.0, 300.0, 250.0)
    c_ac_fF: float = 0.70
    c_cb_fF: float = 0.75
    c_ab_fF: float = 0.03
    ej_c_sum_MHz: float = 18000.0
    squid_asymmetry: float = 0.05
    charge_cutoff: int = 8
    levels_kept: int = 3

    def validate(self) -> None:
        values = (
            *self.target_frequencies_MHz, *self.nominal_EC_MHz,
            self.c_ac_fF, self.c_cb_fF, self.c_ab_fF,
            self.ej_c_sum_MHz, self.squid_asymmetry,
        )
        if not all(math.isfinite(float(x)) for x in values):
            raise ValueError("all circuit parameters must be finite")
        if any(x <= 0 for x in self.target_frequencies_MHz + self.nominal_EC_MHz):
            raise ValueError("target frequencies and nominal EC values must be positive")
        if min(self.c_ac_fF, self.c_cb_fF, self.c_ab_fF) < 0:
            raise ValueError("mutual capacitances must be non-negative")
        if self.ej_c_sum_MHz <= 0 or not 0 <= self.squid_asymmetry < 1:
            raise ValueError("invalid SQUID Josephson energy or asymmetry")
        if self.charge_cutoff < 4 or not 3 <= self.levels_kept <= 5:
            raise ValueError("charge_cutoff must be >=4 and levels_kept in [3,5]")


def charge_operators(charge_cutoff: int):
    charges = np.arange(-charge_cutoff, charge_cutoff + 1, dtype=float)
    dim = len(charges)
    n_op = np.diag(charges)
    shift = np.zeros((dim, dim), dtype=np.complex128)
    for index in range(dim - 1):
        shift[index + 1, index] = 1.0
    cos_phi = (shift + shift.conj().T) / 2.0
    sin_phi = (shift - shift.conj().T) / (2.0j)
    return charges, n_op, cos_phi, sin_phi


def squid_parameters(flux_fraction: float, ej_sum_MHz: float, asymmetry: float):
    theta = math.pi * flux_fraction
    scale = math.sqrt(math.cos(theta) ** 2 + asymmetry**2 * math.sin(theta) ** 2)
    ej_eff = ej_sum_MHz * scale
    phase_offset = math.atan2(asymmetry * math.sin(theta), math.cos(theta))
    return ej_eff, phase_offset


def local_transmon(ec_MHz: float, ej_MHz: float, phase_offset: float, cutoff: int):
    charges, n_op, cos_phi, sin_phi = charge_operators(cutoff)
    shifted_cos = cos_phi * math.cos(phase_offset) - sin_phi * math.sin(phase_offset)
    h_local = 4.0 * ec_MHz * np.diag(charges**2) - ej_MHz * shifted_cos
    energies, vectors = eigh(h_local)
    return (
        energies,
        vectors.conj().T @ n_op @ vectors,
        vectors.conj().T @ cos_phi @ vectors,
        vectors.conj().T @ sin_phi @ vectors,
    )


def exact_local_f01(ec_MHz: float, ej_MHz: float, phase_offset: float, cutoff: int) -> float:
    energies, *_ = local_transmon(ec_MHz, ej_MHz, phase_offset, cutoff)
    return float(energies[1] - energies[0])


def tune_ej_for_frequency(ec_MHz: float, target_MHz: float, cutoff: int) -> float:
    lower = target_MHz + ec_MHz
    upper = 3.0 * (target_MHz + ec_MHz) ** 2 / (8.0 * ec_MHz)
    return float(brentq(
        lambda ej: exact_local_f01(ec_MHz, ej, 0.0, cutoff) - target_MHz,
        lower, upper, xtol=1e-8,
    ))


def build_capacitance_matrix(params: CircuitParameters):
    c_ground_fF = np.array([
        E_CHARGE**2 / (2.0 * PLANCK * ec * 1e6) * 1e15
        for ec in params.nominal_EC_MHz
    ])
    capacitance_fF = np.diag(c_ground_fF.copy())
    for i, j, value in (
        (0, 1, params.c_ac_fF),
        (1, 2, params.c_cb_fF),
        (0, 2, params.c_ab_fF),
    ):
        capacitance_fF[i, i] += value
        capacitance_fF[j, j] += value
        capacitance_fF[i, j] -= value
        capacitance_fF[j, i] -= value
    c_eigenvalues = np.linalg.eigvalsh(capacitance_fF)
    if c_eigenvalues[0] <= 0:
        raise ValueError("capacitance matrix is not positive definite")
    ec_matrix_MHz = (
        E_CHARGE**2 / (2.0 * PLANCK)
        * np.linalg.inv(capacitance_fF * 1e-15) / 1e6
    )
    return capacitance_fF, ec_matrix_MHz


def analyze_circuit_point(params: CircuitParameters, *, include_flux_calibration: bool = True) -> dict:
    params.validate()
    c_matrix, ec_matrix = build_capacitance_matrix(params)
    ec_diagonal = np.diag(ec_matrix)
    f_a, f_c, f_b = params.target_frequencies_MHz
    ej_a = tune_ej_for_frequency(ec_diagonal[0], f_a, params.charge_cutoff)
    ej_b = tune_ej_for_frequency(ec_diagonal[2], f_b, params.charge_cutoff)

    def coupler_frequency(flux_fraction: float) -> float:
        ej_eff, phase = squid_parameters(
            flux_fraction, params.ej_c_sum_MHz, params.squid_asymmetry
        )
        return exact_local_f01(ec_diagonal[1], ej_eff, phase, params.charge_cutoff)

    flux_dc = float(brentq(
        lambda flux: coupler_frequency(flux) - f_c,
        0.001, 0.48, xtol=1e-12,
    ))
    ej_c_eff, phase_c = squid_parameters(
        flux_dc, params.ej_c_sum_MHz, params.squid_asymmetry
    )

    local = [
        local_transmon(ec_diagonal[0], ej_a, 0.0, params.charge_cutoff),
        local_transmon(ec_diagonal[1], ej_c_eff, phase_c, params.charge_cutoff),
        local_transmon(ec_diagonal[2], ej_b, 0.0, params.charge_cutoff),
    ]
    n_levels = params.levels_kept
    local_energies = [item[0][:n_levels] - item[0][0] for item in local]
    local_n = [item[1][:n_levels, :n_levels] for item in local]
    eye = np.eye(n_levels, dtype=np.complex128)
    dim = n_levels**3
    hamiltonian = np.zeros((dim, dim), dtype=np.complex128)

    def index(state):
        return state[0] * n_levels**2 + state[1] * n_levels + state[2]

    for na in range(n_levels):
        for nc in range(n_levels):
            for nb in range(n_levels):
                i = index((na, nc, nb))
                hamiltonian[i, i] = (
                    local_energies[0][na] + local_energies[1][nc] + local_energies[2][nb]
                )
    for i, j in ((0, 1), (0, 2), (1, 2)):
        ops = [eye, eye, eye]
        ops[i] = local_n[i]
        ops[j] = local_n[j]
        hamiltonian += 8.0 * ec_matrix[i, j] * np.kron(np.kron(ops[0], ops[1]), ops[2])

    dressed_energies, dressed_vectors = eigh(hamiltonian)
    tracked_states = {}
    bare_states = {
        "ground": (0, 0, 0),
        "A_01": (1, 0, 0),
        "B_01": (0, 0, 1),
        "A1_B1": (1, 0, 1),
    }
    for label, bare_state in bare_states.items():
        bare_index = index(bare_state)
        overlaps = np.abs(dressed_vectors[bare_index, :]) ** 2
        eig_index = int(np.argmax(overlaps))
        tracked_states[label] = {
            "eigen_index": eig_index,
            "energy_MHz": float(dressed_energies[eig_index]),
            "bare_product_overlap": float(overlaps[eig_index]),
        }

    e00 = tracked_states["ground"]["energy_MHz"]
    e10 = tracked_states["A_01"]["energy_MHz"]
    e01 = tracked_states["B_01"]["energy_MHz"]
    e11 = tracked_states["A1_B1"]["energy_MHz"]
    residual_zz = e11 - e10 - e01 + e00

    n01 = [abs(float(np.real_if_close(item[1][0, 1]))) for item in local]
    g_ac = 8.0 * ec_matrix[0, 1] * n01[0] * n01[1]
    g_cb = 8.0 * ec_matrix[1, 2] * n01[1] * n01[2]
    g_ab = 8.0 * ec_matrix[0, 2] * n01[0] * n01[2]
    local_frequencies = [float(item[0][1] - item[0][0]) for item in local]
    local_anharmonicities = [
        float(item[0][2] - 2.0 * item[0][1] + item[0][0]) for item in local
    ]

    flux_report = {}
    if include_flux_calibration:
        delta = 1e-4
        derivative = (
            coupler_frequency(flux_dc + delta) - coupler_frequency(flux_dc - delta)
        ) / (2.0 * delta)
        for flux_amplitude in (0.005, 0.01, 0.02, 0.03):
            f_low = coupler_frequency(flux_dc - flux_amplitude)
            f_high = coupler_frequency(flux_dc + flux_amplitude)
            flux_report[str(flux_amplitude)] = {
                "flux_amplitude_Phi0": flux_amplitude,
                "frequency_at_negative_peak_MHz": f_low,
                "frequency_at_positive_peak_MHz": f_high,
                "negative_peak_shift_MHz": f_low - f_c,
                "positive_peak_shift_MHz": f_high - f_c,
            }
        flux_report["df01_dflux_MHz_per_Phi0"] = float(derivative)

    return {
        "capacitances_fF": {
            "C_matrix": c_matrix.tolist(),
            "C_AC": params.c_ac_fF,
            "C_CB": params.c_cb_fF,
            "C_AB_parasitic": params.c_ab_fF,
        },
        "charging_matrix_MHz": ec_matrix.tolist(),
        "charging_energy_diagonal_MHz": ec_diagonal.tolist(),
        "isolated_local_modes": {
            "target_f01_MHz": list(params.target_frequencies_MHz),
            "computed_f01_MHz": local_frequencies,
            "anharmonicity_MHz": local_anharmonicities,
            "EJ_over_h_MHz": [float(ej_a), float(ej_c_eff), float(ej_b)],
            "EJ_C_sum_over_h_MHz": params.ej_c_sum_MHz,
            "SQUID_asymmetry": params.squid_asymmetry,
            "SQUID_DC_flux_Phi0": flux_dc,
            "SQUID_phase_offset_rad": phase_c,
        },
        "derived_exchange_matrix_elements_MHz": {
            "g_AC_01": float(g_ac),
            "g_CB_01": float(g_cb),
            "g_AB_direct_01": float(g_ab),
            "definition": "8 * E_C,ij/h * |<0|n_i|1>| * |<0|n_j|1>|; rotating-wave matrix element estimate",
        },
        "dressed_static_spectrum_MHz": {
            "A_transition_MHz": e10 - e00,
            "B_transition_MHz": e01 - e00,
            "dressed_A_B_detuning_MHz": abs(e10 - e01),
            "residual_static_ZZ_MHz": float(residual_zz),
            "tracked_states": tracked_states,
        },
        "flux_to_frequency_calibration": flux_report,
        "truncation": {
            "charge_cutoff": params.charge_cutoff,
            "local_levels_kept": params.levels_kept,
            "product_hilbert_dimension": dim,
        },
    }


def scan_capacitances(base: CircuitParameters, values: tuple[float, ...] = (0.40, 0.55, 0.70, 0.85, 1.00, 1.15)) -> list[dict]:
    rows = []
    for c_ac in values:
        for c_cb in values:
            params = CircuitParameters(
                target_frequencies_MHz=base.target_frequencies_MHz,
                nominal_EC_MHz=base.nominal_EC_MHz,
                c_ac_fF=c_ac,
                c_cb_fF=c_cb,
                c_ab_fF=base.c_ab_fF,
                ej_c_sum_MHz=base.ej_c_sum_MHz,
                squid_asymmetry=base.squid_asymmetry,
                charge_cutoff=base.charge_cutoff,
                levels_kept=base.levels_kept,
            )
            point = analyze_circuit_point(params, include_flux_calibration=False)
            rows.append({
                "C_AC_fF": c_ac,
                "C_CB_fF": c_cb,
                "g_AC_01_MHz": point["derived_exchange_matrix_elements_MHz"]["g_AC_01"],
                "g_CB_01_MHz": point["derived_exchange_matrix_elements_MHz"]["g_CB_01"],
                "g_AB_direct_01_MHz": point["derived_exchange_matrix_elements_MHz"]["g_AB_direct_01"],
                "dressed_A_B_detuning_MHz": point["dressed_static_spectrum_MHz"]["dressed_A_B_detuning_MHz"],
                "residual_static_ZZ_MHz": point["dressed_static_spectrum_MHz"]["residual_static_ZZ_MHz"],
                "minimum_bare_product_overlap": min(
                    item["bare_product_overlap"]
                    for item in point["dressed_static_spectrum_MHz"]["tracked_states"].values()
                ),
            })
    return rows
