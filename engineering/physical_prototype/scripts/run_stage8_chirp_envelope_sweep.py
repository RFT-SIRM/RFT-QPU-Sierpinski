#!/usr/bin/env python3
"""Checkpointed coarse search over linear chirp and asymmetric flux ramps."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engineering/physical_prototype/src"))

from rft_qpu.stage5_gate import build_fixed_basis_model  # noqa: E402
from rft_qpu.stage8_waveform import ChirpedFluxPulse, propagate_chirped_gate  # noqa: E402

try:
    from threadpoolctl import threadpool_limits
except ImportError:  # pragma: no cover
    from contextlib import nullcontext
    threadpool_limits = lambda limits: nullcontext()  # type: ignore


def atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def atomic_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0])
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def key_for(chirp: float, rise: float, fall: float) -> str:
    return f"chirp_{chirp:+.6f}_rise_{rise:.3f}_fall_{fall:.3f}".replace("+", "p").replace("-", "m")


def feasible(row: dict, min_transfer: float, max_leakage: float, max_coupler: float) -> bool:
    return (
        row["A_to_B_transfer"] >= min_transfer
        and row["B_to_A_transfer"] >= min_transfer
        and row["final_max_logical_leakage"] <= max_leakage
        and row["sampled_max_coupler_excited_probability"] <= max_coupler
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625675587737073)
    parser.add_argument("--steps-per-period", type=int, default=40)
    parser.add_argument("--chirp-grid-kHz", nargs="+", type=float,
                        default=[-8.0, -4.0, 0.0, 4.0, 8.0])
    parser.add_argument("--ramp-in-grid", nargs="+", type=float,
                        default=[6.0, 8.0, 10.0])
    parser.add_argument("--ramp-out-grid", nargs="+", type=float,
                        default=[6.0, 8.0, 10.0])
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage8_chirp_envelope_sweep")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-candidates", type=int, default=None)
    parser.add_argument("--min-transfer", type=float, default=0.999)
    parser.add_argument("--max-final-leakage", type=float, default=1e-3)
    parser.add_argument("--max-coupler-population", type=float, default=0.02)
    args = parser.parse_args()

    if args.steps_per_period < 8 or args.frequency_MHz <= 0 or args.duration_us <= 0:
        parser.error("invalid temporal grid, frequency, or duration")
    if args.amplitude_Phi0 < 0 or args.max_new_candidates is not None and args.max_new_candidates < 1:
        parser.error("invalid amplitude or chunk limit")
    if not args.chirp_grid_kHz or not args.ramp_in_grid or not args.ramp_out_grid:
        parser.error("chirp and ramp grids must be non-empty")
    if any(x < 0 for x in args.ramp_in_grid + args.ramp_out_grid):
        parser.error("ramp periods must be non-negative")

    candidates = [
        (float(chirp), float(rise), float(fall))
        for chirp, rise, fall in itertools.product(
            args.chirp_grid_kHz, args.ramp_in_grid, args.ramp_out_grid
        )
    ]
    total = len(candidates)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"{args.prefix}.csv"
    json_path = args.output_dir / f"{args.prefix}.json"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    cp_csv = args.output_dir / f"{args.prefix}.checkpoint.csv"
    cp_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    cp_npz = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"
    config = {
        "frequency_MHz": args.frequency_MHz,
        "amplitude_Phi0": args.amplitude_Phi0,
        "duration_us": args.duration_us,
        "steps_per_period": args.steps_per_period,
        "chirp_grid_kHz": list(args.chirp_grid_kHz),
        "ramp_in_grid": list(args.ramp_in_grid),
        "ramp_out_grid": list(args.ramp_out_grid),
    }

    rows: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if cp_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {cp_json}; pass --resume or change --prefix")
        saved = json.loads(cp_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs")
        rows = list(saved["candidates"])
        if not cp_npz.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(cp_npz) as data:
            matrices = {k: data[k].copy() for k in data.files}
        keys = {r["candidate_key"] for r in rows}
        if keys != set(matrices):
            parser.error("checkpoint rows and matrix keys do not match")
        print(f"Resuming {len(rows)}/{total} candidates", flush=True)
    elif args.resume:
        parser.error("--resume requested but checkpoint does not exist")

    processed = 0
    with threadpool_limits(limits=1):
        model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
        print("Fixed circuit basis:", model.logical_eigen_indices,
              "DC flux Phi0:", model.flux_dc_Phi0, flush=True)
        for chirp, rise, fall in candidates:
            key = key_for(chirp, rise, fall)
            if key in matrices:
                continue
            pulse = ChirpedFluxPulse(
                frequency_MHz=args.frequency_MHz,
                fundamental_amplitude_Phi0=args.amplitude_Phi0,
                duration_us=args.duration_us,
                ramp_in_periods=rise,
                ramp_out_periods=fall,
                chirp_span_kHz=chirp,
            )
            raw = propagate_chirped_gate(
                model, pulse, args.steps_per_period,
                track_stride=max(1, args.steps_per_period // 12),
            )
            row = {k: v for k, v in raw.items() if k != "logical_matrix"}
            row["candidate_key"] = key
            row["screen_feasible"] = feasible(
                row, args.min_transfer, args.max_final_leakage,
                args.max_coupler_population,
            )
            rows.append(row)
            matrices[key] = raw["logical_matrix"]
            processed += 1
            atomic_csv(cp_csv, rows)
            atomic_npz = np.savez_compressed
            temp_npz = cp_npz.with_suffix(".tmp.npz")
            atomic_npz(temp_npz, **matrices)
            temp_npz.replace(cp_npz)
            atomic_json(cp_json, {
                "stage": 8, "status": "in_progress_resumable_checkpoint",
                "run_config": config, "candidate_count": len(rows),
                "total_candidate_count": total, "candidates": rows,
                "matrices_archive": cp_npz.name,
            })
            print(
                f"[{len(rows)}/{total}] chirp={chirp:+.3f} kHz ramps={rise:.1f}/{fall:.1f} periods "
                f"F={row['process_overlap_after_local_Z']:.12f} "
                f"AB={row['A_to_B_transfer']:.12f} BA={row['B_to_A_transfer']:.12f} "
                f"phi={row['conditional_phase_rad']:+.8f} rad [checkpoint]",
                flush=True,
            )
            if args.max_new_candidates is not None and processed >= args.max_new_candidates and len(rows) < total:
                print("Chunk completed; rerun with --resume and identical arguments", flush=True)
                return

    rows.sort(key=lambda r: (r["chirp_span_kHz"], r["ramp_in_periods"], r["ramp_out_periods"]))
    feasible_rows = [r for r in rows if r["screen_feasible"]]
    best = max(feasible_rows, key=lambda r: r["process_overlap_after_local_Z"]) if feasible_rows else None
    phase_best = min(feasible_rows, key=lambda r: abs(r["conditional_phase_rad"])) if feasible_rows else None
    payload = {
        "stage": 8,
        "status": "chirped_asymmetric_envelope_screen_complete",
        "hardware_ready": False,
        "model": "125-dimensional circuit-derived fixed-DC-basis closed-system Strang propagator",
        "waveform": "Phi=Phi_DC+env_asym(t)*A*cos(theta(t)); instantaneous f sweeps linearly from f0-Deltaf/2 to f0+Deltaf/2",
        "run_config": config,
        "candidate_count": len(rows),
        "feasible_candidate_count": len(feasible_rows),
        "screening_thresholds_not_hardware_acceptance": {
            "transfer_min_each_direction": args.min_transfer,
            "final_max_logical_leakage_max": args.max_final_leakage,
            "sampled_max_coupler_population_max": args.max_coupler_population,
        },
        "best_feasible_process_overlap_candidate": best,
        "minimum_absolute_conditional_phase_candidate": phase_best,
        "candidates": rows,
        "matrices_archive": matrix_path.name,
        "limitations": [
            "closed-system model; no measured flux-line transfer, bandwidth, distortion, latency or crosstalk",
            "coarse temporal grid; finalists require common-duration 120/240/480 convergence",
            "transient population extrema are sampled and may be under-resolved",
            "nominal capacitances and SQUID parameters are assumptions rather than layout extraction",
            "no T1/T2, thermal population, quasiparticles or fabrication disorder",
        ],
    }
    atomic_csv(csv_path, rows)
    temp_npz = matrix_path.with_suffix(".tmp.npz")
    np.savez_compressed(temp_npz, **matrices)
    temp_npz.replace(matrix_path)
    atomic_json(json_path, payload)
    for path in (cp_csv, cp_json, cp_npz):
        path.unlink(missing_ok=True)
    print("\nFEASIBLE:", len(feasible_rows), "/", total, flush=True)
    print("BEST PROCESS CANDIDATE:", json.dumps(best, indent=2), flush=True)
    print("MIN ABS CONDITIONAL PHASE CANDIDATE:", json.dumps(phase_best, indent=2), flush=True)
    print("Saved:", csv_path, json_path, matrix_path, flush=True)


if __name__ == "__main__":
    main()
