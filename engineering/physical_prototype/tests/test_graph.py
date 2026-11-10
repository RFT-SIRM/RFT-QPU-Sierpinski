import pytest

from rft_qpu.graph import build_sg_graph, expected_counts


@pytest.mark.parametrize("level", range(6))
def test_sg_counts(level):
    graph = build_sg_graph(level)
    assert (graph.n_vertices, graph.n_edges, graph.n_faces) == expected_counts(level)


def test_level_one_is_first_non_abelian_construction():
    graph = build_sg_graph(1)
    assert graph.n_vertices == 6
    assert graph.n_edges == 9
    assert graph.n_faces == 3
    assert graph.flux_edges == ((0, 1), (1, 3), (2, 4))
