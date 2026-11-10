"""Small-device disorder studies separating TR-preserving and TR-breaking noise."""
from __future__ import annotations

import numpy as np

from .graph import build_sg_graph
from .hamiltonian import graph_hamiltonian


def run_disorder_study(
    level: int = 1,
    samples: int = 250,
    edge_fractional_disorder: tuple[float, ...] = (0.01, 0.05, 0.10),
    time_reversal_breaking_field: tuple[float, ...] = (1e-3, 1e-2, 5e-2),
    seed: int = 1234,
) -> dict:
    graph = build_sg_graph(level)
    rng = np.random.default_rng(seed)
    base_H = graph_hamiltonian(graph)
    result = {"level": level, "samples": samples, "seed": seed, "edge_weight_disorder": [], "TR_breaking_local_z_field": []}

    for amplitude in edge_fractional_disorder:
        gaps = []
        splittings = []
        for _ in range(samples):
            weights = {
                edge: float(1.0 + rng.uniform(-amplitude, amplitude))
                for edge in graph.edges
            }
            values = np.linalg.eigvalsh(graph_hamiltonian(graph, edge_weights=weights))
            splittings.append(float(values[1] - values[0]))
            gaps.append(float(values[2] - values[1]))
        result["edge_weight_disorder"].append({
            "fractional_amplitude": amplitude,
            "ground_splitting_max_over_J": max(splittings),
            "leakage_gap_min_over_J": min(gaps),
            "leakage_gap_median_over_J": float(np.median(gaps)),
            "leakage_gap_max_over_J": max(gaps),
        })

    for amplitude in time_reversal_breaking_field:
        splittings = []
        for _ in range(samples):
            fields = np.zeros((graph.n_vertices, 3), dtype=float)
            fields[:, 2] = rng.normal(0.0, amplitude, graph.n_vertices)
            values = np.linalg.eigvalsh(graph_hamiltonian(graph, local_fields=fields))
            splittings.append(float(values[1] - values[0]))
        result["TR_breaking_local_z_field"].append({
            "field_sigma_over_J": amplitude,
            "ground_splitting_mean_over_J": float(np.mean(splittings)),
            "ground_splitting_max_over_J": max(splittings),
        })

    result["base_leakage_gap_over_J"] = float(np.linalg.eigvalsh(base_H)[2] - np.linalg.eigvalsh(base_H)[1])
    return result
