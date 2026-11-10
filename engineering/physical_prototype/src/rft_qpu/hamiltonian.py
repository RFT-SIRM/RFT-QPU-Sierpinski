"""Spinor graph Hamiltonian, gauge covariance and time-reversal symmetry."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .graph import SGGraph
from .su2 import I2, PAULI, gauge_unitary, su2_rotation


@dataclass(frozen=True)
class EdgeTransport:
    a: int
    b: int
    matrix: np.ndarray
    face_index: int | None
    axis: int | None


def edge_transports(graph: SGGraph, theta: float) -> tuple[EdgeTransport, ...]:
    """Attach cyclic x/y/z SU(2) rotations to the canonical flux edges.

    The first two face vertices determine the transported edge; its endpoints
    are then ordered by canonical vertex index, matching Evgeny-Theorem.
    """
    assigned: dict[tuple[int, int], tuple[int, int]] = {}
    for face_index, edge in enumerate(graph.flux_edges):
        assigned[edge] = (face_index, face_index % 3)

    transports = []
    for a, b in graph.edges:
        if (a, b) in assigned:
            face_index, axis = assigned[(a, b)]
            matrix = su2_rotation(axis, theta)
        else:
            face_index, axis = None, None
            matrix = I2.copy()
        transports.append(EdgeTransport(a, b, matrix, face_index, axis))
    return tuple(transports)


def graph_hamiltonian(
    graph: SGGraph,
    theta: float = np.pi / 2,
    edge_weights: dict[tuple[int, int], float] | None = None,
    gauge: tuple[np.ndarray, ...] | list[np.ndarray] | None = None,
    local_fields: np.ndarray | None = None,
) -> np.ndarray:
    """Build H = D_w tensor I - sum_e w_e |a><b| tensor U_ab + h.c.

    Real positive edge weights preserve the SU(2) time-reversal structure.
    `local_fields[v, :]` adds a Zeeman-like b_v . sigma term; this deliberately
    breaks time reversal in the generic case and is used for stress testing.
    """
    n = graph.n_vertices
    if edge_weights is None:
        weights = {edge: 1.0 for edge in graph.edges}
    else:
        weights = {edge: float(edge_weights.get(edge, 1.0)) for edge in graph.edges}
        if any(value <= 0 or not np.isfinite(value) for value in weights.values()):
            raise ValueError("edge weights must be finite and strictly positive")

    if gauge is not None and len(gauge) != n:
        raise ValueError("one SU(2) gauge matrix is required per graph vertex")
    if local_fields is not None:
        local_fields = np.asarray(local_fields, dtype=float)
        if local_fields.shape != (n, 3):
            raise ValueError(f"local_fields must have shape ({n}, 3)")

    transports = edge_transports(graph, theta)
    H = np.zeros((2 * n, 2 * n), dtype=np.complex128)
    degree = np.zeros(n, dtype=float)

    for transport in transports:
        a, b = transport.a, transport.b
        w = weights[(a, b)]
        degree[a] += w
        degree[b] += w
        U = transport.matrix
        if gauge is not None:
            U = gauge[a] @ U @ gauge[b].conj().T
        sa = slice(2 * a, 2 * a + 2)
        sb = slice(2 * b, 2 * b + 2)
        H[sa, sb] -= w * U
        H[sb, sa] -= w * U.conj().T

    for vertex, d in enumerate(degree):
        block = slice(2 * vertex, 2 * vertex + 2)
        H[block, block] += d * I2
        if local_fields is not None:
            field_block = sum(local_fields[vertex, k] * PAULI[k] for k in range(3))
            H[block, block] += field_block

    return H


def time_reversal_unitary(n_vertices: int) -> np.ndarray:
    """Unitary part J of T = J K, with T^2 = -I for a spin-1/2 bundle."""
    i_sigma_y = 1j * PAULI[1]
    return np.kron(np.eye(n_vertices, dtype=np.complex128), i_sigma_y)


def gauge_covariance_error(
    H: np.ndarray,
    H_gauged: np.ndarray,
    gauges: tuple[np.ndarray, ...] | list[np.ndarray],
) -> float:
    G = gauge_unitary(gauges)
    return float(np.linalg.norm(H_gauged - G @ H @ G.conj().T, ord="fro"))


def time_reversal_error(H: np.ndarray, n_vertices: int) -> float:
    J = time_reversal_unitary(n_vertices)
    return float(np.linalg.norm(J @ H.conj() @ J.conj().T - H, ord="fro"))
