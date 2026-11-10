"""Projected two-cell interaction: the first step beyond one logical qubit."""
from __future__ import annotations

import numpy as np

from .analysis import analyze_level
from .controls import local_spin_operator
from .graph import build_sg_graph
from .hamiltonian import graph_hamiltonian
from .su2 import PAULI


def _pauli_vector(matrix: np.ndarray) -> np.ndarray:
    return np.array([float(np.real(np.trace(matrix @ sigma)) / 2.0) for sigma in PAULI])


def analyze_two_cell_interaction(
    level: int = 1,
    anchor_vertex: int | None = None,
    chi_over_J_values: tuple[float, ...] = (0.01, 0.05, 0.10),
    chi_over_2pi_MHz: float = 10.0,
) -> dict:
    """Project a differential-density ZZ coupler between two identical cells.

    Each cell carries one excitation. The inter-cell term is

        H_AB / hbar = chi * S_z(A,v) * S_z(B,w),
        S_z(v) = (n_v_up - n_v_down)/2.

    This preserves the excitation number in each cell. The effective
    two-logical-qubit term is calculated directly in the product doublet.
    """
    graph = build_sg_graph(level)
    H = graph_hamiltonian(graph)
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    P = eigenvectors[:, :2]

    if anchor_vertex is None:
        anchor_vertex = analyze_level(level)["best_local_control"]["vertex"]
    if not 0 <= anchor_vertex < graph.n_vertices:
        raise ValueError("anchor_vertex out of range")

    O_z = local_spin_operator(graph.n_vertices, anchor_vertex, 2)
    S_z = O_z / 2.0
    projected_S_z = P.conj().T @ S_z @ P
    projected_vector = _pauli_vector(projected_S_z)
    control_strength = float(2.0 * np.linalg.norm(projected_vector))
    effective_interaction_scale = float(np.linalg.norm(projected_vector) ** 2)

    product_basis = np.kron(P, P)
    product_projector = product_basis @ product_basis.conj().T
    interaction_unit = np.kron(S_z, S_z)
    projected_unit_interaction = product_basis.conj().T @ interaction_unit @ product_basis
    projected_spectrum = np.linalg.eigvalsh(projected_unit_interaction)

    identity2 = np.eye(2, dtype=np.complex128)
    cell_identity = np.eye(H.shape[0], dtype=np.complex128)
    scenarios = []
    for chi_over_J in chi_over_J_values:
        H_int = chi_over_J * interaction_unit
        full_H = np.kron(H, cell_identity) + np.kron(cell_identity, H) + H_int
        full_values = np.linalg.eigvalsh(full_H)
        leakage_coupling = float(
            np.linalg.norm((np.eye(full_H.shape[0]) - product_projector) @ H_int @ product_basis, ord=2)
        )
        scenarios.append({
            "chi_over_J": float(chi_over_J),
            "lowest_four_eigenvalues_over_J": [float(x) for x in full_values[:4]],
            "gap_after_logical_quartet_over_J": float(full_values[4] - full_values[3]),
            "off_subspace_coupling_norm_over_J": leakage_coupling,
        })

    # H_L/hbar = chi * |c|^2/4 * (sigma_z tensor sigma_z).
    # A maximally-entangling ZZ phase is pi/4, so t = pi/(4 J_ZZ)
    # = 1/(2 * (chi/2pi) * |c|^2).
    chi_hz = chi_over_2pi_MHz * 1e6
    gate_time_seconds = 1.0 / (2.0 * chi_hz * effective_interaction_scale)

    return {
        "level": level,
        "n_transmons_per_cell": 2 * graph.n_vertices,
        "n_transmons_two_cell": 4 * graph.n_vertices,
        "anchor_vertex": anchor_vertex,
        "anchor_coordinate": list(graph.vertices[anchor_vertex]),
        "local_projected_Sz_matrix": [
            [[float(x.real), float(x.imag)] for x in row] for row in projected_S_z
        ],
        "logical_Ising_axis_A": projected_vector.tolist(),
        "logical_Ising_axis_B": projected_vector.tolist(),
        "local_control_g_eff_for_Oz": control_strength,
        "projected_interaction_eigenvalues_at_chi_over_J_1": [float(x) for x in projected_spectrum],
        "effective_nonlocal_interaction_coefficient_over_chi": effective_interaction_scale,
        "chi_over_2pi_MHz_assumption": chi_over_2pi_MHz,
        "ideal_maximally_entangling_time_us": gate_time_seconds * 1e6,
        "chi_sweep": scenarios,
        "warning": "The differential cross-Kerr coupler is a proposed primitive. The projected model is numerical; the physical four-channel circuit and open-system gate are not validated.",
    }
