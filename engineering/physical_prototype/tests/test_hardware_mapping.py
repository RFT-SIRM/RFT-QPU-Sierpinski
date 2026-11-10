from rft_qpu.graph import build_sg_graph
from rft_qpu.hardware import coupler_rows, level_scale_table, site_rows


def test_level_one_hardware_mapping_has_12_transmons_and_22_exchange_channels():
    graph = build_sg_graph(1)
    rows = coupler_rows(graph, 3.141592653589793 / 2, 10.0)
    assert graph.n_vertices * 2 == 12
    assert len(rows) == 22
    assert {row["axis"] for row in rows} == {"identity", "x", "y", "z"}
    assert all(row["coupling_amplitude_MHz"] > 0 for row in rows)


def test_site_frequency_plan_tracks_graph_degree():
    rows = site_rows(build_sg_graph(1), 10.0)
    assert [row["degree"] for row in rows] == [2, 4, 4, 2, 4, 2]
    assert [row["relative_detuning_MHz"] for row in rows] == [20, 40, 40, 20, 40, 20]


def test_level_five_scaling_reference():
    row = level_scale_table(5)[5]
    assert row["physical_transmons"] == 732
    assert row["graph_edges"] == 729
    assert row["effective_exchange_channels"] == 1782
