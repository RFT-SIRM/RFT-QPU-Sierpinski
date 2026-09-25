import numpy as np

from qpu_core import (
    Edge,
    gauge_invariance_check,
    gauge_transform_edges,
    gauge_unitary,
    graph_hamiltonian,
    random_su2,
    su2_rotation,
)


def test_su2_rotation_is_unitary():
    u = su2_rotation("y", np.pi / 2)
    np.testing.assert_allclose(u.conj().T @ u, np.eye(2), atol=1e-12)
    np.testing.assert_allclose(np.linalg.det(u), 1.0, atol=1e-12)


def test_gauge_covariance_two_site():
    rng = np.random.default_rng(7)
    edges = [Edge(0, 1, su2_rotation("x", np.pi / 2))]
    h = graph_hamiltonian(2, edges)
    g = [random_su2(rng), random_su2(rng)]
    hg = graph_hamiltonian(2, gauge_transform_edges(edges, g))
    result = gauge_invariance_check(h, hg, gauge_unitary(g))
    assert result["passed"]
