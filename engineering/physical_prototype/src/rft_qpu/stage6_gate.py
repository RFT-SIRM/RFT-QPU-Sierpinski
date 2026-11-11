"""Stage 6 helpers for fixed-duration convergence and robust gate screening."""
from __future__ import annotations

from dataclasses import dataclass
import math
from functools import reduce
from math import gcd
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class CommonDuration:
    requested_duration_us: float
    actual_duration_us: float
    gcd_steps_per_period: int
    common_ticks: int
    steps_by_grid: dict[int, int]


def choose_common_grid_duration(
    frequency_MHz: float,
    requested_duration_us: float,
    steps_per_period: Iterable[int],
) -> CommonDuration:
    """Snap once to a duration exactly representable on every requested grid.

    With frequency in MHz and time in microseconds, one pump period is
    1/frequency microseconds. The GCD grid is the coarsest time lattice shared
    by all requested steps-per-period grids. Each grid is an integer multiple
    of that lattice, so the physical pulse duration is identical on every grid.
    """
    grids = tuple(int(x) for x in steps_per_period)
    if not math.isfinite(frequency_MHz) or frequency_MHz <= 0:
        raise ValueError("frequency_MHz must be finite and positive")
    if not math.isfinite(requested_duration_us) or requested_duration_us <= 0:
        raise ValueError("requested_duration_us must be finite and positive")
    if not grids or any(x < 8 for x in grids) or len(set(grids)) != len(grids):
        raise ValueError("steps_per_period must be unique integers >= 8")

    common_spp = reduce(gcd, grids)
    ticks = int(round(requested_duration_us * frequency_MHz * common_spp))
    actual = ticks / (frequency_MHz * common_spp)
    steps: dict[int, int] = {}
    for spp in grids:
        n = ticks * (spp // common_spp)
        reconstructed = n / (frequency_MHz * spp)
        if abs(reconstructed - actual) > 1e-13:
            raise ArithmeticError("common duration is not exactly representable on a requested grid")
        steps[spp] = n
    return CommonDuration(
        requested_duration_us=float(requested_duration_us),
        actual_duration_us=float(actual),
        gcd_steps_per_period=common_spp,
        common_ticks=ticks,
        steps_by_grid=steps,
    )


def canonicalize_local_z_fit(result: dict) -> dict:
    """Return equivalent local-Z fit angles in the canonical (-pi, pi] range.

    The corrected matrix and fidelity metrics do not change. This only removes
    arbitrary integer multiples of 2*pi from the reported phase parameters.
    """
    out = dict(result)
    key = "local_Z_fit_rad_global_outA_outB_inA_inB"
    if key in out:
        phases = np.asarray(out[key], dtype=float)
        out[key] = np.angle(np.exp(1j * phases)).tolist()
    return out


def evaluate_candidate_feasibility(
    rows: list[dict],
    *,
    min_transfer: float = 0.999,
    max_final_leakage: float = 1e-3,
    max_sampled_coupler_population: float = 0.02,
) -> dict:
    """Select best feasible row without silently relabelling an infeasible row."""
    if not rows:
        raise ValueError("candidate list must not be empty")
    feasible = [
        row for row in rows
        if float(row["A_to_B_transfer"]) >= min_transfer
        and float(row["B_to_A_transfer"]) >= min_transfer
        and float(row["final_max_logical_leakage"]) <= max_final_leakage
        and float(row["sampled_max_coupler_excited_probability"]) <= max_sampled_coupler_population
    ]
    best_any = max(rows, key=lambda r: float(r["process_overlap_after_local_Z"]))
    best_feasible = (
        max(feasible, key=lambda r: float(r["process_overlap_after_local_Z"]))
        if feasible else None
    )
    return {
        "feasible_candidate_count": len(feasible),
        "best_sampled_feasible_candidate": best_feasible,
        "best_unfiltered_candidate": best_any,
        "feasibility_thresholds": {
            "transfer_min_each_direction": min_transfer,
            "final_max_logical_leakage_max": max_final_leakage,
            "sampled_max_coupler_population_max": max_sampled_coupler_population,
        },
    }
