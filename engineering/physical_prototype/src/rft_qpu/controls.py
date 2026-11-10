"""Logical-subspace projection and controllability metrics."""
from __future__ import annotations

import numpy as np

from .graph import SGGraph
from .su2 import PAULI


def local_spin_operator(n_vertices: int, vertex: int, axis: int) -> np.ndarray:
    if not 0 <= vertex < n_vertices:
        raise IndexError("vertex index out of range")
    operator = np.zeros((2 * n_vertices, 2 * n_vertices), dtype=np.complex128)
    block = slice(2 * vertex, 2 * vertex + 2)
    operator[block, block] = PAULI[axis]
    return operator


def global_spin_operator(n_vertices: int, axis: int) -> np.ndarray:
    return np.kron(np.eye(n_vertices), PAULI[axis])


def pauli_coefficient_matrix(projected: list[np.ndarray] | tuple[np.ndarray, ...]) -> np.ndarray:
    """Map physical x/y/z controls to logical Pauli coefficients.

    Row i contains Tr(P O_i P sigma_j)/2. Its singular values are invariant
    under a unitary change of basis inside the logical doublet.
    """
    result = np.zeros((len(projected), 3), dtype=float)
    for i, matrix in enumerate(projected):
        for j, sigma in enumerate(PAULI):
            result[i, j] = float(np.real(np.trace(matrix @ sigma)) / 2.0)
    return result


def analyze_control_family(
    eigenvectors: np.ndarray,
    n_vertices: int,
    vertex: int | None = None,
) -> dict:
    Q = eigenvectors[:, :2]
    if vertex is None:
        physical_ops = [global_spin_operator(n_vertices, axis) for axis in range(3)]
        label = "global"
    else:
        physical_ops = [local_spin_operator(n_vertices, vertex, axis) for axis in range(3)]
        label = f"local_vertex_{vertex}"

    projected = [Q.conj().T @ O @ Q for O in physical_ops]
    coefficients = pauli_coefficient_matrix(projected)
    singular_values = np.linalg.svd(coefficients, compute_uv=False)
    rank = int(np.linalg.matrix_rank(coefficients, tol=1e-10))
    condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float("inf")
    return {
        "family": label,
        "coefficient_matrix": coefficients,
        "singular_values": singular_values,
        "rank": rank,
        "condition_number": condition,
        "g_eff": float(singular_values[-1]),
        "projected_operators": projected,
    }


def best_local_control_site(graph: SGGraph, eigenvectors: np.ndarray) -> dict:
    reports = []
    for vertex in range(graph.n_vertices):
        report = analyze_control_family(eigenvectors, graph.n_vertices, vertex)
        report["vertex"] = vertex
        report["coordinate"] = graph.vertices[vertex]
        reports.append(report)
    return max(reports, key=lambda item: item["g_eff"])
