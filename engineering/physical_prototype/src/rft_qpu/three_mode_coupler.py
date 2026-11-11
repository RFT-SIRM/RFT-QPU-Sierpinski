"""Three-mode Duffing-coupler model with a flux-modulated nonlinear bus.

This is an effective three-Duffing-mode model, not a circuit-quantized
capacitance/Josephson netlist. Frequencies and couplings are in MHz; time in
microseconds. The model is intended as a reproducible first engineering gate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
from typing import Iterable

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.optimize import brentq


@dataclass(frozen=True)
class ThreeModeParams:
    """Parameters of data transmon A — nonlinear coupler C — data transmon B.

    Frequencies are expressed in a common rotating frame. For the initial
    Z-link stress case, the bare data-mode separation is 985 MHz and the
    coupler is placed halfway between the two data modes.
    """

    f_a_MHz: float = 0.0
    f_c_MHz: float = -492.5
    f_b_MHz: float = -985.0
    alpha_a_MHz: float = -250.0
    alpha_c_MHz: float = -300.0
    alpha_b_MHz: float = -245.0
    g_ac_MHz: float = 100.0
    g_cb_MHz: float = 100.0
    pump_amplitude_MHz: float = 200.0
    pump_frequency_MHz: float | None = None
    pump_phase_rad: float = 0.0
    sambe_order: int = 3

    def validate(self) -> None:
        numeric = (
            self.f_a_MHz, self.f_c_MHz, self.f_b_MHz,
            self.alpha_a_MHz, self.alpha_c_MHz, self.alpha_b_MHz,
            self.g_ac_MHz, self.g_cb_MHz, self.pump_amplitude_MHz,
            self.pump_phase_rad,
        )
        if not all(math.isfinite(float(x)) for x in numeric):
            raise ValueError("all model parameters must be finite")
        if self.g_ac_MHz < 0 or self.g_cb_MHz < 0:
            raise ValueError("couplings must be non-negative")
        if self.pump_amplitude_MHz < 0:
            raise ValueError("pump amplitude must be non-negative")
        if self.sambe_order < 1:
            raise ValueError("sambe_order must be at least 1")
        if self.pump_frequency_MHz is not None and self.pump_frequency_MHz <= 0:
            raise ValueError("pump_frequency_MHz must be positive")

    @property
    def bare_difference_MHz(self) -> float:
        return abs(self.f_b_MHz - self.f_a_MHz)

    def as_dict(self) -> dict:
        result = asdict(self)
        if result["pump_frequency_MHz"] is None:
            result["pump_frequency_MHz"] = "auto-tuned"
        return result


def excitation_basis(total_excitations: int) -> list[tuple[int, int, int]]:
    """Basis |n_A,n_C,n_B> with each mode truncated to n=0,1,2."""
    if total_excitations < 0 or total_excitations > 6:
        raise ValueError("total_excitations must be between 0 and 6")
    return [
        (n_a, n_c, n_b)
        for n_a in range(3)
        for n_c in range(3)
        for n_b in range(3)
        if n_a + n_c + n_b == total_excitations
    ]


def sector_operators(
    params: ThreeModeParams,
    total_excitations: int,
) -> tuple[list[tuple[int, int, int]], np.ndarray, np.ndarray]:
    """Return bare-frame Hamiltonian H0 and coupler number operator n_C."""
    params.validate()
    basis = excitation_basis(total_excitations)
    lookup = {state: i for i, state in enumerate(basis)}
    dim = len(basis)
    h0 = np.zeros((dim, dim), dtype=np.complex128)
    n_c = np.zeros((dim, dim), dtype=np.complex128)

    for i, (n_a, n_coupler, n_b) in enumerate(basis):
        h0[i, i] = (
            params.f_a_MHz * n_a
            + params.f_c_MHz * n_coupler
            + params.f_b_MHz * n_b
            + 0.5 * params.alpha_a_MHz * n_a * (n_a - 1)
            + 0.5 * params.alpha_c_MHz * n_coupler * (n_coupler - 1)
            + 0.5 * params.alpha_b_MHz * n_b * (n_b - 1)
        )
        n_c[i, i] = n_coupler

        # Exchange A <-> C.
        for target in (
            (n_a + 1, n_coupler - 1, n_b),
            (n_a - 1, n_coupler + 1, n_b),
        ):
            if target in lookup:
                if target[0] > n_a:
                    amplitude = math.sqrt((n_a + 1) * n_coupler)
                else:
                    amplitude = math.sqrt((n_coupler + 1) * n_a)
                h0[lookup[target], i] += params.g_ac_MHz * amplitude

        # Exchange C <-> B.
        for target in (
            (n_a, n_coupler + 1, n_b - 1),
            (n_a, n_coupler - 1, n_b + 1),
        ):
            if target in lookup:
                if target[1] > n_coupler:
                    amplitude = math.sqrt((n_coupler + 1) * n_b)
                else:
                    amplitude = math.sqrt((n_b + 1) * n_coupler)
                h0[lookup[target], i] += params.g_cb_MHz * amplitude

    # Hermiticity is checked here to catch ladder-matrix assembly errors early.
    if not np.allclose(h0, h0.conj().T, atol=1e-12):
        raise ArithmeticError("assembled sector Hamiltonian is not Hermitian")
    return basis, h0, n_c


def sambe_matrix(
    params: ThreeModeParams,
    total_excitations: int,
    pump_frequency_MHz: float,
    pump_phase_rad: float | None = None,
) -> tuple[list[tuple[int, int, int]], list[int], np.ndarray]:
    """Build the truncated Sambe matrix for sinusoidal coupler-frequency drive."""
    if pump_frequency_MHz <= 0 or not math.isfinite(pump_frequency_MHz):
        raise ValueError("pump frequency must be finite and positive")
    basis, h0, n_c = sector_operators(params, total_excitations)
    phase = params.pump_phase_rad if pump_phase_rad is None else float(pump_phase_rad)
    if not math.isfinite(phase):
        raise ValueError("pump phase must be finite")
    sidebands = list(range(-params.sambe_order, params.sambe_order + 1))
    d = len(basis)
    hf = np.zeros((d * len(sidebands), d * len(sidebands)), dtype=np.complex128)
    drive_plus = 0.5 * params.pump_amplitude_MHz * np.exp(1j * phase) * n_c

    for k, m in enumerate(sidebands):
        block = slice(k * d, (k + 1) * d)
        hf[block, block] = h0 + m * pump_frequency_MHz * np.eye(d)
        if k + 1 < len(sidebands):
            next_block = slice((k + 1) * d, (k + 2) * d)
            hf[next_block, block] = drive_plus
            hf[block, next_block] = drive_plus.conj().T

    if not np.allclose(hf, hf.conj().T, atol=1e-11):
        raise ArithmeticError("Sambe matrix is not Hermitian")
    return basis, sidebands, hf


def _target_projected_effective(
    params: ThreeModeParams,
    pump_frequency_MHz: float,
    pump_phase_rad: float,
) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int, int]], list[int], list[int]]:
    basis, sidebands, hf = sambe_matrix(
        params, 1, pump_frequency_MHz, pump_phase_rad
    )
    d = len(basis)
    idx = {state: i for i, state in enumerate(basis)}
    target = [
        sidebands.index(0) * d + idx[(1, 0, 0)],
        sidebands.index(1) * d + idx[(0, 0, 1)],
    ]
    qidx = np.array([i for i in range(hf.shape[0]) if i not in target], dtype=int)
    hpp = hf[np.ix_(target, target)]
    hpq = hf[np.ix_(target, qidx)]
    hqq = hf[np.ix_(qidx, qidx)]
    eig_q = np.linalg.eigvalsh(hqq)
    if np.min(np.abs(eig_q)) < 1e-7:
        raise np.linalg.LinAlgError("reference quasienergy intersects eliminated Sambe block")
    heff = hpp + hpq @ np.linalg.solve(-hqq, hpq.conj().T)
    return heff, hf, basis, sidebands, target


def find_resonant_pump_frequency(
    params: ThreeModeParams,
    search_half_width_MHz: float = 200.0,
    samples: int = 161,
) -> tuple[float, np.ndarray]:
    """Tune pump to equality of diagonal Feshbach shifts in target subspace."""
    params.validate()
    if search_half_width_MHz <= 0 or samples < 5:
        raise ValueError("invalid pump search settings")
    center = params.bare_difference_MHz

    def imbalance(fp: float) -> float:
        heff, *_ = _target_projected_effective(params, fp, params.pump_phase_rad)
        return float(np.real(heff[0, 0] - heff[1, 1]))

    grid = np.linspace(center - search_half_width_MHz,
                       center + search_half_width_MHz, samples)
    vals: list[float] = []
    for fp in grid:
        try:
            vals.append(imbalance(float(fp)))
        except np.linalg.LinAlgError:
            vals.append(float("nan"))

    roots: list[float] = []
    for x0, x1, y0, y1 in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if not (math.isfinite(y0) and math.isfinite(y1)):
            continue
        if y0 == 0:
            roots.append(float(x0))
        elif y0 * y1 < 0:
            try:
                root = brentq(imbalance, float(x0), float(x1), xtol=1e-9)
                roots.append(float(root))
            except (ValueError, np.linalg.LinAlgError):
                continue
    if not roots:
        finite = [(abs(y), float(x)) for x, y in zip(grid, vals) if math.isfinite(y)]
        if not finite:
            raise RuntimeError("no numerically regular pump-frequency point found")
        _, fp = min(finite)
        heff, *_ = _target_projected_effective(params, fp, params.pump_phase_rad)
        return fp, heff

    fp = min(roots, key=lambda x: abs(x - center))
    heff, *_ = _target_projected_effective(params, fp, params.pump_phase_rad)
    return fp, heff


def exact_sambe_exchange(
    params: ThreeModeParams,
    pump_frequency_MHz: float,
    pump_phase_rad: float | None = None,
) -> dict:
    """Extract the resonant quasienergy splitting and effective complex phase."""
    phase = params.pump_phase_rad if pump_phase_rad is None else float(pump_phase_rad)
    heff, hf, basis, sidebands, target = _target_projected_effective(
        params, pump_frequency_MHz, phase
    )
    evals, evecs = eigh(hf)
    target_weight = np.sum(np.abs(evecs[target, :]) ** 2, axis=0)
    pick = np.argsort(target_weight)[-2:]
    pick = pick[np.argsort(evals[pick])]
    quasienergy_gap = float(evals[pick[1]] - evals[pick[0]])
    return {
        "quasienergy_pair_MHz": [float(evals[pick[0]]), float(evals[pick[1]])],
        "quasienergy_pair_target_weight": [float(target_weight[pick[0]]), float(target_weight[pick[1]])],
        "exact_sambe_exchange_MHz": 0.5 * quasienergy_gap,
        "feshbach_exchange_MHz": float(abs(heff[0, 1])),
        "feshbach_complex_exchange": {
            "real_MHz": float(heff[0, 1].real),
            "imag_MHz": float(heff[0, 1].imag),
            "phase_deg": float(np.angle(heff[0, 1], deg=True)),
        },
        "target_diagonal_shifts_MHz": [float(heff[0, 0].real), float(heff[1, 1].real)],
        "sambe_sidebands": sidebands,
        "target_basis": ["|1,0,0; m=0>", "|0,0,1; m=+1>"],
    }


def static_dressed_spectrum(params: ThreeModeParams) -> dict:
    """Track dressed |10>, |01>, and |11> energies by maximum bare overlap."""
    basis1, h1, _ = sector_operators(params, 1)
    e1, v1 = eigh(h1)
    idx_a = basis1.index((1, 0, 0))
    idx_b = basis1.index((0, 0, 1))
    state_a = int(np.argmax(np.abs(v1[idx_a, :]) ** 2))
    state_b = int(np.argmax(np.abs(v1[idx_b, :]) ** 2))

    basis2, h2, _ = sector_operators(params, 2)
    e2, v2 = eigh(h2)
    idx_ab = basis2.index((1, 0, 1))
    state_ab = int(np.argmax(np.abs(v2[idx_ab, :]) ** 2))

    overlap_a = float(abs(v1[idx_a, state_a]) ** 2)
    overlap_b = float(abs(v1[idx_b, state_b]) ** 2)
    overlap_ab = float(abs(v2[idx_ab, state_ab]) ** 2)
    zz = float(e2[state_ab] - e1[state_a] - e1[state_b])
    return {
        "dressed_E10_MHz": float(e1[state_a]),
        "dressed_E01_MHz": float(e1[state_b]),
        "dressed_E11_MHz": float(e2[state_ab]),
        "static_residual_ZZ_MHz": zz,
        "bare_state_overlap": {
            "A_single_excitation": overlap_a,
            "B_single_excitation": overlap_b,
            "AB_two_excitation": overlap_ab,
        },
        "coupler_anharmonicity_MHz": params.alpha_c_MHz,
    }


def _propagate_sector(
    params: ThreeModeParams,
    total_excitations: int,
    initial_state: tuple[int, int, int],
    end_time_us: float,
    pump_frequency_MHz: float,
    pump_phase_rad: float,
    samples: int,
    max_steps_per_period: int = 32,
) -> tuple[list[tuple[int, int, int]], np.ndarray, np.ndarray]:
    basis, h0, n_c = sector_operators(params, total_excitations)
    if initial_state not in basis:
        raise ValueError("initial state is not in the selected excitation sector")
    initial = np.zeros(len(basis), dtype=np.complex128)
    initial[basis.index(initial_state)] = 1.0
    period_us = 1.0 / pump_frequency_MHz

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        psi = y[:len(basis)] + 1j * y[len(basis):]
        h_t = h0 + params.pump_amplitude_MHz * math.cos(
            2.0 * math.pi * pump_frequency_MHz * t + pump_phase_rad
        ) * n_c
        derivative = -1j * 2.0 * math.pi * (h_t @ psi)
        return np.concatenate((derivative.real, derivative.imag))

    y0 = np.concatenate((initial.real, initial.imag))
    t_eval = np.linspace(0.0, end_time_us, max(samples, 2))
    solution = solve_ivp(
        rhs,
        (0.0, end_time_us),
        y0,
        method="DOP853",
        t_eval=t_eval,
        rtol=2e-9,
        atol=2e-11,
        max_step=period_us / max_steps_per_period,
    )
    if not solution.success:
        raise RuntimeError(f"time propagation failed: {solution.message}")
    psi = solution.y[:len(basis), :] + 1j * solution.y[len(basis):, :]
    return basis, solution.t, psi


def dynamic_gate_check(
    params: ThreeModeParams,
    pump_frequency_MHz: float,
    pump_phase_rad: float = 0.0,
    time_window_factor: float = 1.8,
) -> dict:
    """Propagate N=1 exchange and N=2 |11> spectator/leakage stress state."""
    exchange = exact_sambe_exchange(params, pump_frequency_MHz, pump_phase_rad)
    j_eff = float(exchange["exact_sambe_exchange_MHz"])
    if j_eff <= 0:
        raise RuntimeError("extracted exchange is not positive")
    nominal_swap_us = 1.0 / (4.0 * j_eff)

    basis1, times1, psi1 = _propagate_sector(
        params, 1, (1, 0, 0), nominal_swap_us * time_window_factor,
        pump_frequency_MHz, pump_phase_rad, samples=1800,
    )
    p_b = np.abs(psi1[basis1.index((0, 0, 1)), :]) ** 2
    p_c = np.abs(psi1[basis1.index((0, 1, 0)), :]) ** 2
    best = int(np.argmax(p_b))
    best_time = float(times1[best])

    basis2, times2, psi2 = _propagate_sector(
        params, 2, (1, 0, 1), best_time,
        pump_frequency_MHz, pump_phase_rad, samples=700,
    )
    final_probabilities = np.abs(psi2[:, -1]) ** 2
    logical_index = basis2.index((1, 0, 1))
    coupler_population = sum(
        n_c * final_probabilities[i] for i, (_, n_c, _) in enumerate(basis2)
    )
    high_level_population = sum(
        final_probabilities[i]
        for i, (n_a, n_c, n_b) in enumerate(basis2)
        if n_a == 2 or n_c == 2 or n_b == 2
    )
    return {
        "nominal_swap_time_from_J_us": nominal_swap_us,
        "best_dynamic_swap_time_us": best_time,
        "single_excitation_transfer_probability": float(p_b[best]),
        "single_excitation_max_coupler_population": float(np.max(p_c)),
        "single_excitation_coupler_population_at_swap": float(p_c[best]),
        "two_excitation_logical_survival_probability": float(final_probabilities[logical_index]),
        "two_excitation_leakage_probability_at_swap": float(1.0 - final_probabilities[logical_index]),
        "two_excitation_coupler_population_at_swap": float(coupler_population),
        "two_excitation_high_level_population_at_swap": float(high_level_population),
        "two_excitation_basis_populations": {
            "|200>": float(final_probabilities[basis2.index((2, 0, 0))]),
            "|110>": float(final_probabilities[basis2.index((1, 1, 0))]),
            "|101>": float(final_probabilities[basis2.index((1, 0, 1))]),
            "|020>": float(final_probabilities[basis2.index((0, 2, 0))]),
            "|011>": float(final_probabilities[basis2.index((0, 1, 1))]),
            "|002>": float(final_probabilities[basis2.index((0, 0, 2))]),
        },
    }


def analyze_three_mode_coupler(params: ThreeModeParams | None = None) -> dict:
    """Run static spectrum, Floquet extraction, phase covariance and dynamics."""
    params = params or ThreeModeParams()
    params.validate()
    pump, heff = find_resonant_pump_frequency(params)
    exact = exact_sambe_exchange(params, pump, params.pump_phase_rad)
    static = static_dressed_spectrum(params)
    dynamic = dynamic_gate_check(params, pump, params.pump_phase_rad)

    phase_map = {}
    for phase_deg in (45.0, -45.0):
        phase_exchange = exact_sambe_exchange(
            params, pump, math.radians(phase_deg)
        )
        phase_map[str(int(phase_deg))] = phase_exchange["feshbach_complex_exchange"]["phase_deg"]

    alpha_sweep = []
    for alpha_c in (-200.0, -300.0, -400.0):
        swept = replace(params, alpha_c_MHz=alpha_c)
        alpha_sweep.append({
            "alpha_c_MHz": alpha_c,
            "static_residual_ZZ_MHz": static_dressed_spectrum(swept)["static_residual_ZZ_MHz"],
        })

    return {
        "model": "three nonlinear Duffing modes with sinusoidal coupler-frequency modulation",
        "model_boundary": (
            "Effective rotating-frame model only. It is not yet a circuit-quantized capacitance/Josephson/SQUID model; "
            "the flux dependence of couplings, higher circuit modes, dissipation and calibration are omitted."
        ),
        "units": {"frequency": "MHz", "time": "microseconds", "hbar": 1.0},
        "parameters": params.as_dict(),
        "resonance": {
            "bare_data_frequency_difference_MHz": params.bare_difference_MHz,
            "dressed_resonant_pump_frequency_MHz": float(pump),
            "pump_shift_from_bare_difference_MHz": float(pump - params.bare_difference_MHz),
        },
        "effective_exchange": exact,
        "static_spectrum": static,
        "coupler_anharmonicity_sensitivity": alpha_sweep,
        "pump_phase_calibration": {
            "pump_phase_deg_to_effective_hopping_phase_deg": phase_map,
            "note": "The absolute phase offset depends on mode and hopping sign conventions; conjugation under phase reversal is the invariant check."
        },
        "dynamic_gate_check": dynamic,
        "decision": (
            "Toy-model stress test only. Do not use this parameter point for a hardware design: "
            "the predicted two-excitation leakage must be reduced with a circuit-derived model and pulse/coupler optimization."
        ),
    }
