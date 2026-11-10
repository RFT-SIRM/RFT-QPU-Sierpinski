import math
import pytest
from rft_qpu.floquet_audit import audit_floquet_collisions
from rft_qpu.graph import build_sg_graph
from rft_qpu.hardware import coupler_rows

def test_level1_screen_detects_exact_cross_edge_qutrit_collision():
 rows=coupler_rows(build_sg_graph(1),math.pi/2,10.0)
 report=audit_floquet_collisions(rows)
 assert report["input"]["edge_count"]==9
 assert report["input"]["effective_channel_count"]==22
 assert report["summary"]["primary_component_minimum_margin_MHz"]==pytest.approx(0.0)
 assert report["summary"]["primary_component_warning_count"]>0
 assert any(x["source"]=="e002" and x["victim_edge"]=="e000" and
            x["transition"]=="N2_11_to_20" and x["collision_margin_MHz"]==0
            for x in report["worst_primary_collisions"])

def test_harmonic_and_intermodulation_are_explicitly_conditional():
 rows=coupler_rows(build_sg_graph(1),math.pi/2,10.0)
 report=audit_floquet_collisions(rows)
 assert report["is_full_floquet_solution"] is False
 assert report["is_transition_probability"] is False
 assert report["summary"]["all_component_warning_count"]>=report["summary"]["primary_component_warning_count"]
 assert any("conditional" in x["component_assumption"] for x in report["worst_all_collisions"])

def test_empty_input_rejected():
 with pytest.raises(ValueError,match="must not be empty"): audit_floquet_collisions([])
