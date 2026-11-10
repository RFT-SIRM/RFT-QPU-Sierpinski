import numpy as np

from rft_qpu.analysis import analyze_level
from rft_qpu.graph import build_sg_graph
from rft_qpu.hamiltonian import graph_hamiltonian


def test_level_one_ground_state_is_kramers_doublet_with_resolved_gap():
    H = graph_hamiltonian(build_sg_graph(1))
    values = np.linalg.eigvalsh(H)
    assert abs(values[1] - values[0]) < 1e-10
    assert abs((values[2] - values[1]) - 1.39371269308684) < 1e-10


def test_projected_global_and_local_controls_are_full_rank():
    report = analyze_level(1)
    assert report["global_control"]["rank"] == 3
    assert report["best_local_control"]["rank"] == 3
    assert abs(report["best_local_control"]["g_eff"] - 0.17704330851508) < 1e-10
    assert report["best_local_control"]["vertex"] == 5
    assert report["best_local_control"]["coordinate"] == [0.0, 1.0]


def test_level_five_reproduces_repository_control_scale():
    report = analyze_level(5)
    assert abs(report["best_local_control"]["g_eff"] - 0.0150851774268) < 2e-10
