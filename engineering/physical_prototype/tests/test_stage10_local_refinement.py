import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def test_stage10_local_scan_contains_nine_feasible_points_and_expected_best():
    report = json.loads((RESULTS / "stage10_bias_refine_40grid.json").read_text())
    assert report["candidate_count"] == 9
    assert report["feasible_candidate_count"] == 9
    best = report["best_feasible_process_overlap_candidate"]
    assert best["bias_offset_Phi0"] == -0.0075
    assert best["pump_offset_from_static_kHz"] == -64.0
    assert best["duration_requested_us"] == 1.081
    assert best["process_overlap_after_local_Z"] > 0.999995
    assert best["A_to_B_transfer"] > 0.99999


def test_stage10_candidate_is_either_resumable_or_complete():
    checkpoint_path = RESULTS / "stage10_bias_refined_candidate.checkpoint.json"
    checkpoint_matrix_path = RESULTS / "stage10_bias_refined_candidate.checkpoint_matrices.npz"
    final_path = RESULTS / "stage10_bias_refined_candidate.json"
    final_matrix_path = RESULTS / "stage10_bias_refined_candidate_matrices.npz"

    if final_path.exists():
        report = json.loads(final_path.read_text())
        assert report["status"] == "bias_shifted_full_gate_common_duration_convergence_complete"
        assert len(report["grid_results"]) == 3
        with np.load(final_matrix_path) as matrices:
            assert set(matrices.files) == {"120", "240", "480"}
            assert all(matrices[key].shape == (4, 4) for key in matrices.files)
    else:
        checkpoint = json.loads(checkpoint_path.read_text())
        assert checkpoint["status"] == "in_progress_resumable_checkpoint"
        assert checkpoint["completed_grids"] == 1
        assert checkpoint["grid_results"][0]["steps_per_period"] == 120
        with np.load(checkpoint_matrix_path) as matrices:
            assert set(matrices.files) == {"120"}
            assert matrices["120"].shape == (4, 4)
