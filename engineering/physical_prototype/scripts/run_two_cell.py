#!/usr/bin/env python3
"""Generate the two-cell logical-entangler report."""
from __future__ import annotations
import json
from pathlib import Path
from rft_qpu.two_cell import analyze_two_cell_interaction

if __name__ == "__main__":
    report = analyze_two_cell_interaction()
    path = Path("results/two_cell_entangler_report.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "data_transmons": report["n_transmons_two_cell"],
        "anchor_vertex": report["anchor_vertex"],
        "projected_ZZ_over_chi": report["effective_nonlocal_interaction_coefficient_over_chi"],
        "ideal_entangling_time_us": report["ideal_maximally_entangling_time_us"],
        "report": str(path),
    }, indent=2))
