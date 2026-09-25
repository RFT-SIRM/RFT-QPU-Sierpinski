"""RFT-QPU-Sierpinski: minimal numerical research core."""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np

PAULI = {
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
    "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "z": np.array([[1, 0], [0, -1]], dtype=complex),
}

@dataclass(frozen=True)
class Edge:
    a: int
    b: int
    U_ab: np.ndarray

def su2_rotation(axis: str, theta: float) -> np.ndarray:
    s = PAULI[axis]
    return np.cos(theta/2)*np.eye(2) - 1j*np.sin(theta/2)*s

def graph_hamiltonian(n: int, edges: list[Edge]) -> np.ndarray:
    H = np.zeros((2*n, 2*n), complex)
    I2 = np.eye(2)
    degree = np.zeros(n)
    for e in edges:
        degree[e.a] += 1
        degree[e.b] += 1
        a = slice(2*e.a, 2*e.a+2)
        b = slice(2*e.b, 2*e.b+2)
        H[a, b] -= e.U_ab
        H[b, a] -= e.U_ab.conj().T
    for v, d in enumerate(degree):
        s = slice(2*v, 2*v+2)
        H[s, s] += d*I2
    return H

def random_su2(rng: np.random.Generator) -> np.ndarray:
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    a,b,c,d = q
    return np.array([[a+1j*b, c+1j*d],
                     [-c+1j*d, a-1j*b]], complex)

def gauge_transform_edges(edges: list[Edge], g: list[np.ndarray]) -> list[Edge]:
    return [Edge(e.a, e.b, g[e.a] @ e.U_ab @ g[e.b].conj().T) for e in edges]

def gauge_unitary(g: list[np.ndarray]) -> np.ndarray:
    G = np.zeros((2*len(g), 2*len(g)), complex)
    for v, gv in enumerate(g):
        s = slice(2*v, 2*v+2)
        G[s, s] = gv
    return G

def lowest_doublet(H: np.ndarray):
    vals, vecs = np.linalg.eigh(H)
    return vals[:2], vecs[:, :2]

def local_spin_operator(n: int, vertex: int, axis: str) -> np.ndarray:
    O = np.zeros((2*n, 2*n), complex)
    s = slice(2*vertex, 2*vertex+2)
    O[s, s] = PAULI[axis]
    return O

def project_operator(O: np.ndarray, Q: np.ndarray) -> np.ndarray:
    return Q.conj().T @ O @ Q

def gauge_invariance_check(H, H_gauge, G, atol=1e-10) -> dict:
    target = G @ H @ G.conj().T
    operator_error = np.linalg.norm(H_gauge-target)
    e0 = np.linalg.eigvalsh(H)
    e1 = np.linalg.eigvalsh(H_gauge)
    spectral_error = np.max(np.abs(e0-e1))
    return {"operator_error": float(operator_error),
            "spectral_error": float(spectral_error),
            "passed": operator_error <= atol and spectral_error <= atol}

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    edges = [Edge(0, 1, su2_rotation("x", np.pi/2))]
    H = graph_hamiltonian(2, edges)
    g = [random_su2(rng), random_su2(rng)]
    Hg = graph_hamiltonian(2, gauge_transform_edges(edges, g))
    result = gauge_invariance_check(H, Hg, gauge_unitary(g))
    print(result)
    if not result["passed"]:
        raise SystemExit("Gauge covariance check failed.")
