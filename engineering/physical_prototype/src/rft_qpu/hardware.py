"""Translate the SG SU(2) Hamiltonian into a transmon-mode coupler netlist."""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from .graph import SGGraph, build_sg_graph
from .hamiltonian import edge_transports


def transmon_id(vertex: int, spin: int) -> str:
    return f"q{vertex:02d}_{'up' if spin == 0 else 'dn'}"


def level_scale_table(max_level: int = 5) -> list[dict]:
    rows = []
    for level in range(max_level + 1):
        graph = build_sg_graph(level)
        face_count = graph.n_faces
        x_count = sum(1 for i in range(face_count) if i % 3 == 0)
        y_count = sum(1 for i in range(face_count) if i % 3 == 1)
        z_count = sum(1 for i in range(face_count) if i % 3 == 2)
        inactive_edges = graph.n_edges - face_count
        exchange_channels = (
            2 * inactive_edges + 4 * x_count + 4 * y_count + 2 * z_count
        )
        rows.append({
            "level": level,
            "graph_sites": graph.n_vertices,
            "physical_transmons": 2 * graph.n_vertices,
            "graph_edges": graph.n_edges,
            "elementary_faces": face_count,
            "x_transport_edges": x_count,
            "y_transport_edges": y_count,
            "z_transport_edges": z_count,
            "effective_exchange_channels": exchange_channels,
            "readout_resonators_target": 2 * graph.n_vertices,
        })
    return rows


def coupler_rows(graph: SGGraph, theta: float, J_over_2pi_MHz: float) -> list[dict]:
    rows = []
    degrees = graph.degrees
    for edge_index, transport in enumerate(edge_transports(graph, theta)):
        U = transport.matrix
        detuning = (degrees[transport.a] - degrees[transport.b]) * J_over_2pi_MHz
        pump_frequency = abs(detuning)
        for spin_a in range(2):
            for spin_b in range(2):
                element = U[spin_a, spin_b]
                if abs(element) < 1e-12:
                    continue
                hopping = -element
                rows.append({
                    "edge_id": f"e{edge_index:03d}",
                    "vertex_a": transport.a,
                    "vertex_b": transport.b,
                    "mode_a": transmon_id(transport.a, spin_a),
                    "mode_b": transmon_id(transport.b, spin_b),
                    "face_index": "" if transport.face_index is None else transport.face_index,
                    "axis": "identity" if transport.axis is None else ("x", "y", "z")[transport.axis],
                    "U_real": float(element.real),
                    "U_imag": float(element.imag),
                    "coupling_amplitude_MHz": float(abs(hopping) * J_over_2pi_MHz),
                    "coupling_phase_deg": float(np.angle(hopping, deg=True)),
                    "site_detuning_MHz_signed": float(detuning),
                    "pump_frequency_MHz": float(pump_frequency),
                    "drive_implementation_note": (
                        "parametric exchange: phase set by pump"
                        if pump_frequency > 1e-9
                        else (
                            "real static/on-resonance exchange"
                            if abs(hopping.imag) < 1e-12
                            else "complex resonant link needs multi-path/static-flux or auxiliary Floquet phase engineering"
                        )
                    ),
                    "J_over_2pi_MHz": float(J_over_2pi_MHz),
                })
    return rows


def site_rows(graph: SGGraph, J_over_2pi_MHz: float, common_frequency_GHz: float = 5.0) -> list[dict]:
    rows = []
    for vertex, (degree, coord) in enumerate(zip(graph.degrees, graph.vertices)):
        offset = degree * J_over_2pi_MHz / 1000.0
        rows.append({
            "vertex": vertex,
            "coordinate_x": coord[0],
            "coordinate_y": coord[1],
            "degree": degree,
            "up_transmon": transmon_id(vertex, 0),
            "down_transmon": transmon_id(vertex, 1),
            "relative_detuning_MHz": degree * J_over_2pi_MHz,
            "nominal_common_frequency_GHz": common_frequency_GHz,
            "illustrative_frequency_GHz": common_frequency_GHz + offset,
        })
    return rows


def write_csv(path: str | Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"no rows to write to {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prototype_bom(graph: SGGraph) -> list[dict]:
    transport_count = len(coupler_rows(graph, math.pi / 2, 10.0))
    return [
        {"item": "Transmon data modes", "quantity": 2 * graph.n_vertices, "purpose": "one spinor pair per SG graph vertex"},
        {"item": "Readout resonators", "quantity": 2 * graph.n_vertices, "purpose": "dispersive occupation/state readout; multiplexing to be engineered"},
        {"item": "Effective inter-site exchange channels", "quantity": transport_count, "purpose": "nonzero matrix elements of SU(2) edge transports"},
        {"item": "Intra-site spin-mixing couplers", "quantity": graph.n_vertices, "purpose": "number-conserving X/Y logical-control drive; phase sets quadrature"},
        {"item": "Differential Z-bias channels", "quantity": graph.n_vertices, "purpose": "relative up/down frequency control at each graph site"},
        {"item": "Flux-tunable coupler bias channels", "quantity": transport_count, "purpose": "per-link calibration or multiplexed pump grouping; routing not finalized"},
        {"item": "Cryogenic microwave feedline(s)", "quantity": "TBD", "purpose": "readout multiplexing and control distribution"},
        {"item": "Parametric pump channels", "quantity": "TBD", "purpose": "phase-coherent edge drives; multiplexing must be validated"},
        {"item": "Entangling inter-cell coupler module", "quantity": 0, "purpose": "not included in one-logical-qubit demonstrator; required for universal processor"},
    ]


def control_rows(graph: SGGraph, drive_frequency_MHz: float = 5.0) -> list[dict]:
    """Number-conserving intra-site spin controls for each dual-rail pair."""
    rows = []
    for vertex in range(graph.n_vertices):
        rows.append({
            "vertex": vertex,
            "mode_up": transmon_id(vertex, 0),
            "mode_down": transmon_id(vertex, 1),
            "X_control": "parametric beam-splitter, pump phase 0 deg",
            "Y_control": "same beam-splitter, pump phase +90 deg",
            "Z_control": "differential flux bias / frequency detuning",
            "illustrative_drive_Rabi_MHz": drive_frequency_MHz,
            "comment": "phase/sign convention requires cryogenic calibration",
        })
    return rows


def write_hardware_package(root: str | Path, level: int = 1, theta: float = math.pi/2, J_over_2pi_MHz: float = 10.0) -> None:
    root = Path(root)
    graph = build_sg_graph(level)
    write_csv(root / "couplers.csv", coupler_rows(graph, theta, J_over_2pi_MHz))
    write_csv(root / "site_frequency_plan.csv", site_rows(graph, J_over_2pi_MHz))
    write_csv(root / "control_channels.csv", control_rows(graph))
    write_csv(root / "bom.csv", prototype_bom(graph))
    write_csv(root / "scaling_table.csv", level_scale_table(max(5, level)))
