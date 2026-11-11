import math

import numpy as np

from rft_qpu.stage6_gate import (
    canonicalize_local_z_fit,
    choose_common_grid_duration,
    evaluate_candidate_feasibility,
)


def test_common_duration_is_identical_on_120_240_480_grids():
    chosen = choose_common_grid_duration(
        987.5136797993163, 1.0625654067723154, [120, 240, 480]
    )
    assert chosen.gcd_steps_per_period == 120
    assert chosen.steps_by_grid == {
        120: chosen.common_ticks,
        240: 2 * chosen.common_ticks,
        480: 4 * chosen.common_ticks,
    }
    durations = [
        chosen.steps_by_grid[spp] / (987.5136797993163 * spp)
        for spp in (120, 240, 480)
    ]
    assert max(durations) - min(durations) < 1e-15
    assert abs(durations[0] - chosen.actual_duration_us) < 1e-15


def test_common_duration_uses_gcd_for_non_nested_grids():
    frequency = 1000.0
    chosen = choose_common_grid_duration(frequency, 0.1234567, [24, 40, 56])
    assert chosen.gcd_steps_per_period == 8
    durations = [chosen.steps_by_grid[spp] / (frequency * spp) for spp in (24, 40, 56)]
    assert max(durations) - min(durations) < 1e-15


def test_common_duration_rejects_invalid_grids():
    for grids in ([], [8, 8], [7, 16]):
        try:
            choose_common_grid_duration(1000.0, 1.0, grids)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid grids were accepted: {grids}")


def test_local_z_phases_are_canonicalized_without_changing_other_fields():
    original = {
        "local_Z_fit_rad_global_outA_outB_inA_inB": [0.2, 2 * math.pi + 0.3, -4 * math.pi - 0.4],
        "projected_process_overlap_after_local_Z": 0.9999,
        "other": "preserved",
    }
    fixed = canonicalize_local_z_fit(original)
    values = fixed["local_Z_fit_rad_global_outA_outB_inA_inB"]
    assert all(-math.pi - 1e-14 <= x <= math.pi + 1e-14 for x in values)
    assert fixed["projected_process_overlap_after_local_Z"] == original["projected_process_overlap_after_local_Z"]
    assert fixed["other"] == original["other"]


def _row(overlap, transfer=0.9999, leakage=1e-5, coupler=0.005):
    return {
        "process_overlap_after_local_Z": overlap,
        "A_to_B_transfer": transfer,
        "B_to_A_transfer": transfer,
        "final_max_logical_leakage": leakage,
        "sampled_max_coupler_excited_probability": coupler,
    }


def test_feasibility_selection_does_not_label_infeasible_fallback_as_feasible():
    rows = [_row(0.9999, transfer=0.98), _row(0.9998, transfer=0.97)]
    result = evaluate_candidate_feasibility(rows)
    assert result["feasible_candidate_count"] == 0
    assert result["best_sampled_feasible_candidate"] is None
    assert result["best_unfiltered_candidate"] is rows[0]


def test_feasibility_selection_returns_best_candidate_inside_constraints():
    rows = [_row(0.99999), _row(0.99995, transfer=0.98), _row(0.99997)]
    result = evaluate_candidate_feasibility(rows)
    assert result["feasible_candidate_count"] == 2
    assert result["best_sampled_feasible_candidate"] is rows[0]
    assert result["best_unfiltered_candidate"] is rows[0]
