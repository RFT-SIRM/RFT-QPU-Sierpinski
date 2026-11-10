"""Spectral, projected-control and device-scale analysis."""
from __future__ import annotations

import numpy as np

from .controls import analyze_control_family, best_local_control_site
from .graph import SGGraph, build_sg_graph
from .hamiltonian import graph_hamiltonian, time_reversal_error


def analyze_level(level: int, theta: float = np.pi / 2) -> dict:
    graph = build_sg_graph(level)
    H = graph_hamiltonian(graph, theta=theta)
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    if len(eigenvalues) < 4:
        raise ValueError("at least two Kramers pairs are required")

    ground_split = float(eigenvalues[1] - eigenvalues[0])
    leakage_gap = float(eigenvalues[2] - eigenvalues[1])
    global_controls = analyze_control_family(eigenvectors, graph.n_vertices)
    local_controls = best_local_control_site(graph, eigenvectors)
    weights = [
        float(np.trace(
            eigenvectors[2*v:2*v+2, :2]
            @ eigenvectors[2*v:2*v+2, :2].conj().T
        ).real / 2.0)
        for v in range(graph.n_vertices)
    ]

    return {
        "level": level,
        "theta_rad": float(theta),
        "n_vertices": graph.n_vertices,
        "n_edges": graph.n_edges,
        "n_faces": graph.n_faces,
        "n_modes": 2 * graph.n_vertices,
        "degrees": list(graph.degrees),
        "lowest_eigenvalues": [float(value) for value in eigenvalues[:8]],
        "ground_doublet_splitting_over_J": ground_split,
        "leakage_gap_over_J": leakage_gap,
        "time_reversal_error_fro": time_reversal_error(H, graph.n_vertices),
        "global_control": {
            "coefficient_matrix": global_controls["coefficient_matrix"].tolist(),
            "singular_values": global_controls["singular_values"].tolist(),
            "rank": global_controls["rank"],
            "condition_number": global_controls["condition_number"],
            "g_eff": global_controls["g_eff"],
        },
        "best_local_control": {
            "vertex": local_controls["vertex"],
            "coordinate": list(local_controls["coordinate"]),
            "coefficient_matrix": local_controls["coefficient_matrix"].tolist(),
            "singular_values": local_controls["singular_values"].tolist(),
            "rank": local_controls["rank"],
            "condition_number": local_controls["condition_number"],
            "g_eff": local_controls["g_eff"],
        },
        "logical_ground_doublet_vertex_weights": weights,
    }
