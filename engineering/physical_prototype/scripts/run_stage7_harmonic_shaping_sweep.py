#!/usr/bin/env python3
"""Stage-7 coarse search over second-harmonic flux-control quadratures."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from contextlib import nullcontext

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "engineering" / "physical_prototype" / "src"
sys.path.insert(0, str(SRC))

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    threadpool_limits = None

from rft_qpu.stage5_gate import build_fixed_basis_model  # noqa: E402
from rft_qpu.stage7_waveform import run_harmonic_shaping_candidate  # noqa: E402


def atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def atomic_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def atomic_npz(path: Path, matrices: dict[str, np.ndarray]) -> None:
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(handle, **matrices)
    tmp.replace(path)


def key_for(cos_amp: float, sin_amp: float) -> str:
    return f"a2c{cos_amp:+.9f}_a2s{sin_amp:+.9f}"


def feasible(row: dict, min_transfer: float, max_leakage: float,
             max_coupler: float) -> bool:
    return (
        float(row["A_to_B_transfer"]) >= min_transfer
        and float(row["B_to_A_transfer"]) >= min_transfer
        and float(row["final_max_logical_leakage"]) <= max_leakage
        and float(row["sampled_max_coupler_excited_probability"]) <= max_coupler
    )


def pareto_indices(rows: list[dict]) -> list[int]:
    """Minimize abs conditional phase and Frobenius distance; maximize Fproc."""
    front: list[int] = []
    for i, a in enumerate(rows):
        va = (abs(float(a["conditional_phase_rad"])),
              1.0 - float(a["process_overlap_after_local_Z"]),
              float(a["frobenius_distance_to_iSWAP_after_local_Z"]))
        dominated = False
        for j, b in enumerate(rows):
            if i == j:
                continue
            vb = (abs(float(b["conditional_phase_rad"])),
                  1.0 - float(b["process_overlap_after_local_Z"]),
                  float(b["frobenius_distance_to_iSWAP_after_local_Z"]))
            if all(x <= y + 1e-15 for x, y in zip(vb, va)) and any(
                x < y - 1e-15 for x, y in zip(vb, va)
            ):
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--fundamental-amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625675587737073)
    parser.add_argument("--steps-per-period", type=int, default=40)
    parser.add_argument("--second-harmonic-cos-grid", nargs="+", type=float,
                        default=[-0.0002, 0.0, 0.0002])
    parser.add_argument("--second-harmonic-sin-grid", nargs="+", type=float,
                        default=[-0.0002, 0.0, 0.0002])
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage7_harmonic_shaping")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-candidates", type=int, default=None)
    parser.add_argument("--min-transfer", type=float, default=0.999)
    parser.add_argument("--max-final-leakage", type=float, default=1e-3)
    parser.add_argument("--max-coupler-population", type=float, default=0.02)
    args = parser.parse_args()

    if args.steps_per_period < 8:
        parser.error("--steps-per-period must be >= 8")
    if args.max_new_candidates is not None and args.max_new_candidates < 1:
        parser.error("--max-new-candidates must be positive")
    if not args.second_harmonic_cos_grid or not args.second_harmonic_sin_grid:
        parser.error("both second-harmonic grids must be non-empty")
    if len(set(args.second_harmonic_cos_grid)) != len(args.second_harmonic_cos_grid):
        parser.error("cosine grid entries must be unique")
    if len(set(args.second_harmonic_sin_grid)) != len(args.second_harmonic_sin_grid):
        parser.error("sine grid entries must be unique")
    if args.frequency_MHz <= 0 or args.fundamental_amplitude_Phi0 < 0 or args.duration_us <= 0:
        parser.error("invalid fundamental pulse parameters")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"{args.prefix}.csv"
    json_path = args.output_dir / f"{args.prefix}.json"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    checkpoint_csv = args.output_dir / f"{args.prefix}.checkpoint.csv"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    checkpoint_matrix = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"

    config = {
        "frequency_MHz": args.frequency_MHz,
        "fundamental_amplitude_Phi0": args.fundamental_amplitude_Phi0,
        "duration_us": args.duration_us,
        "steps_per_period": args.steps_per_period,
        "second_harmonic_cos_grid": args.second_harmonic_cos_grid,
        "second_harmonic_sin_grid": args.second_harmonic_sin_grid,
    }
    rows: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {checkpoint_json}; pass --resume or change --prefix")
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs")
        rows = list(saved["candidates"])
        if not checkpoint_matrix.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(checkpoint_matrix) as archive:
            matrices = {k: archive[k].copy() for k in archive.files}
        expected = {key_for(float(r["second_harmonic_cos_Phi0"]),
                            float(r["second_harmonic_sin_Phi0"])) for r in rows}
        if expected != set(matrices):
            parser.error("checkpoint rows and matrices do not match")
        print(f"Resuming {len(rows)} / {len(config['second_harmonic_cos_grid']) * len(config['second_harmonic_sin_grid'])} candidates", flush=True)
    elif args.resume:
        parser.error("--resume requested but no checkpoint exists")

    context = threadpool_limits(limits=1) if threadpool_limits else nullcontext()
    processed = 0
    with context:
        model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
        print("Fixed circuit basis rebuilt; logical eigen indices:", model.logical_eigen_indices,
              "DC flux:", model.flux_dc_Phi0, flush=True)
        for a2c in args.second_harmonic_cos_grid:
            for a2s in args.second_harmonic_sin_grid:
                key = key_for(a2c, a2s)
                if key in matrices:
                    continue
                raw = run_harmonic_shaping_candidate(
                    a2c, a2s, frequency_MHz=args.frequency_MHz,
                    fundamental_amplitude_Phi0=args.fundamental_amplitude_Phi0,
                    duration_us=args.duration_us, steps_per_period=args.steps_per_period,
                    model=model,
                )
                row = {k: v for k, v in raw.items() if k != "logical_matrix"}
                row["candidate_key"] = key
                rows.append(row)
                matrices[key] = raw["logical_matrix"]
                processed += 1
                atomic_csv(checkpoint_csv, rows)
                atomic_npz(checkpoint_matrix, matrices)
                atomic_json(checkpoint_json, {
                    "stage": 7, "status": "in_progress_resumable_checkpoint",
                    "run_config": config, "candidate_count": len(rows),
                    "total_candidate_count": len(config["second_harmonic_cos_grid"]) * len(config["second_harmonic_sin_grid"]),
                    "candidates": rows, "matrices_archive": checkpoint_matrix.name,
                })
                print(
                    f"[{len(rows)}/{len(config['second_harmonic_cos_grid']) * len(config['second_harmonic_sin_grid'])}] "
                    f"A2c={a2c:+.7f} A2s={a2s:+.7f} Phi0: "
                    f"Fproc={row['process_overlap_after_local_Z']:.12f}, "
                    f"phi={row['conditional_phase_rad']:+.8f} rad, "
                    f"AB={row['A_to_B_transfer']:.12f} [checkpoint saved]",
                    flush=True,
                )
                if args.max_new_candidates is not None and processed >= args.max_new_candidates:
                    remaining = len(config['second_harmonic_cos_grid']) * len(config['second_harmonic_sin_grid']) - len(rows)
                    if remaining:
                        print("Chunk limit reached; resume with identical arguments and --resume", flush=True)
                        return

    total = len(config["second_harmonic_cos_grid"]) * len(config["second_harmonic_sin_grid"])
    if len(rows) != total:
        raise RuntimeError(f"candidate count mismatch: {len(rows)} != {total}")
    rows.sort(key=lambda r: (float(r["second_harmonic_cos_Phi0"]),
                             float(r["second_harmonic_sin_Phi0"])))
    mask = [feasible(r, args.min_transfer, args.max_final_leakage,
                     args.max_coupler_population) for r in rows]
    feasible_rows = [r for r, ok in zip(rows, mask) if ok]
    best_f = max(feasible_rows, key=lambda r: r["process_overlap_after_local_Z"]) if feasible_rows else None
    min_phase = min(feasible_rows, key=lambda r: abs(r["conditional_phase_rad"])) if feasible_rows else None
    pareto = [feasible_rows[i] for i in pareto_indices(feasible_rows)] if feasible_rows else []
    payload = {
        "stage": 7,
        "status": "second_harmonic_flux_shaping_screen_complete",
        "hardware_ready": False,
        "model": "125-dimensional circuit-derived fixed-DC-basis closed-system propagator",
        "waveform": "Phi=Phi_DC+env*(A1*cos(wt)+A2c*cos(2wt)+A2s*sin(2wt))",
        "run_config": config,
        "candidate_count": len(rows),
        "feasible_candidate_count": len(feasible_rows),
        "screening_thresholds_not_hardware_acceptance": {
            "transfer_min_each_direction": args.min_transfer,
            "final_max_logical_leakage_max": args.max_final_leakage,
            "sampled_max_coupler_excited_probability_max": args.max_coupler_population,
        },
        "best_feasible_process_overlap_candidate": best_f,
        "minimum_absolute_conditional_phase_feasible_candidate": min_phase,
        "feasible_pareto_front": pareto,
        "candidates": rows,
        "matrices_archive": matrix_path.name,
        "limitations": [
            "second-harmonic actuator is an idealized control degree of freedom; real flux-line bandwidth and calibration are not modeled",
            "coarse search; finalists require common-duration 120/240/480 convergence",
            "closed-system simulation only; no T1/T2 or thermal bath",
            "nominal capacitance and SQUID parameters are assumptions, not extracted layout data",
            "transient leakage and coupler population are sampled; extrema may be under-resolved",
        ],
    }
    atomic_csv(csv_path, rows)
    atomic_npz(matrix_path, matrices)
    atomic_json(json_path, payload)
    for p in (checkpoint_csv, checkpoint_json, checkpoint_matrix):
        p.unlink(missing_ok=True)
    print("\nFEASIBLE:", len(feasible_rows), "/", len(rows), flush=True)
    print("BEST PROCESS OVERLAP:", json.dumps(best_f, indent=2), flush=True)
    print("MIN ABS CONDITIONAL PHASE:", json.dumps(min_phase, indent=2), flush=True)
    print("Saved:", csv_path, json_path, matrix_path, flush=True)


if __name__ == "__main__":
    main()
