import numpy as np

from rft_qpu.graph import build_sg_graph
from rft_qpu.hamiltonian import (
    graph_hamiltonian,
    gauge_covariance_error,
    time_reversal_error,
)
from rft_qpu.su2 import random_su2, su2_rotation


def test_su2_rotations_are_unitary_and_noncommuting():
    rotations = [su2_rotation(a, np.pi / 2) for a in range(3)]
    for u in rotations:
        np.testing.assert_allclose(u.conj().T @ u, np.eye(2), atol=1e-13)
        np.testing.assert_allclose(np.linalg.det(u), 1.0, atol=1e-13)
    assert np.linalg.norm(rotations[0] @ rotations[1] - rotations[1] @ rotations[0]) > 1.0


def test_level_one_hamiltonian_is_hermitian_and_time_reversal_invariant():
    graph = build_sg_graph(1)
    H = graph_hamiltonian(graph)
    np.testing.assert_allclose(H, H.conj().T, atol=1e-13)
    assert time_reversal_error(H, graph.n_vertices) < 1e-12


def test_local_su2_gauge_covariance():
    graph = build_sg_graph(1)
    rng = np.random.default_rng(20261110)
    gauges = [random_su2(rng) for _ in range(graph.n_vertices)]
    H = graph_hamiltonian(graph)
    H_gauged = graph_hamiltonian(graph, gauge=gauges)
    assert gauge_covariance_error(H, H_gauged, gauges) < 1e-11


def test_theta_parameter_really_changes_the_operator():
    graph = build_sg_graph(1)
    H0 = graph_hamiltonian(graph, theta=0.0)
    H1 = graph_hamiltonian(graph, theta=np.pi / 2)
    assert np.linalg.norm(H0 - H1) > 0.5
