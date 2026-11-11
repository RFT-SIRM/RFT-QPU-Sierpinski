#!/usr/bin/env python3
"""Checkpointed search over a small static SQUID bias offset and full-gate settings."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engineering/physical_prototype/src"))

from rft_qpu.stage5_gate import build_fixed_basis_model, GatePulse, propagate_gate  # noqa: E402
from rft_qpu.stage9_bias import build_bias_shifted_model  # noqa: E402

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
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def candidate_key(bias: float, pump_offset: float, duration: float) -> str:
    return f"b{bias:+.6f}_df{pump_offset:+.3f}_T{duration:.9f}".replace("+", "p").replace("-", "m")


def is_feasible(row: dict, min_transfer: float, max_leakage: float,
                max_coupler: float) -> bool:
    return (
        row["A_to_B_transfer"] >= min_transfer
        and row["B_to_A_transfer"] >= min_transfer
        and row["final_max_logical_leakage"] <= max_leakage
        and row["sampled_max_coupler_population"] <= max_coupler
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bias-offsets-Phi0", nargs="+", type=float,
                        default=[-0.0065, -0.0075, -0.0085])
    parser.add_argument("--pump-offset-from-static-kHz", nargs="+", type=float,
                        default=[-64.0, -63.0, -62.0])
    parser.add_argument("--durations-us", nargs="+", type=float,
                        default=[1.080, 1.081, 1.082])
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--steps-per-period", type=int, default=40)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage9_bias_scan")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-candidates", type=int, default=None)
    parser.add_argument("--min-transfer", type=float, default=0.999)
    parser.add_argument("--max-final-leakage", type=float, default=1e-3)
    parser.add_argument("--max-coupler-population", type=float, default=0.02)
    args = parser.parse_args()

    if args.steps_per_period < 8 or args.amplitude_Phi0 < 0:
        parser.error("invalid temporal grid or flux amplitude")
    if args.ramp_periods < 0 or args.max_new_candidates is not None and args.max_new_candidates < 1:
        parser.error("invalid ramp or candidate chunk limit")
    if not args.bias_offsets_Phi0 or not args.pump_offset_from_static_kHz or not args.durations_us:
        parser.error("parameter grids must be non-empty")
    if any(x <= 0 for x in args.durations_us):
        parser.error("durations must be positive")

    candidates = list(itertools.product(
        map(float, args.bias_offsets_Phi0),
        map(float, args.pump_offset_from_static_kHz),
        map(float, args.durations_us),
    ))
    total = len(candidates)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"{args.prefix}.csv"
    json_path = args.output_dir / f"{args.prefix}.json"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    cp_csv = args.output_dir / f"{args.prefix}.checkpoint.csv"
    cp_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    cp_npz = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"
    config = {
        "bias_offsets_Phi0": list(args.bias_offsets_Phi0),
        "pump_offset_from_static_kHz": list(args.pump_offset_from_static_kHz),
        "durations_us": list(args.durations_us),
        "amplitude_Phi0": args.amplitude_Phi0,
        "ramp_periods": args.ramp_periods,
        "steps_per_period": args.steps_per_period,
    }

    rows: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if cp_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {cp_json}; pass --resume or use another prefix")
        saved = json.loads(cp_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs")
        rows = list(saved["candidates"])
        if not cp_npz.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(cp_npz) as data:
            matrices = {k: data[k].copy() for k in data.files}
        if {r["candidate_key"] for r in rows} != set(matrices):
            parser.error("checkpoint rows and matrix keys differ")
        print(f"Resuming {len(rows)}/{total} candidates", flush=True)
    elif args.resume:
        parser.error("--resume requested but no checkpoint exists")

    with threadpool_limits(limits=1):
        base = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
        bias_models = {}
        processed = 0
        for offset, pump_offset_kHz, duration in candidates:
            key = candidate_key(offset, pump_offset_kHz, duration)
            if key in matrices:
                continue
            if offset not in bias_models:
                bias_models[offset] = build_bias_shifted_model(base, offset)
            shifted = bias_models[offset]
            pump_frequency = shifted.dressed_AB_detuning_MHz + pump_offset_kHz * 1e-3
            pulse = GatePulse(
                pump_frequency_MHz=pump_frequency,
                flux_amplitude_Phi0=args.amplitude_Phi0,
                duration_us=duration,
                ramp_periods=args.ramp_periods,
            )
            raw = propagate_gate(
                shifted.model, pulse, args.steps_per_period,
                track_stride=max(1, args.steps_per_period // 24),
            )
            matrix = raw.pop("logical_matrix")
            raw.pop("phase_corrected_matrix", None)
            row = {
                "candidate_key": key,
                "bias_offset_Phi0": offset,
                "bias_flux_Phi0": shifted.bias_flux_Phi0,
                "static_ZZ_MHz": shifted.static_ZZ_MHz,
                "static_AB_detuning_MHz": shifted.dressed_AB_detuning_MHz,
                "minimum_bare_overlap": shifted.minimum_bare_overlap,
                "pump_offset_from_static_kHz": pump_offset_kHz,
                "pump_frequency_MHz": pump_frequency,
                "duration_requested_us": duration,
                "actual_duration_us": raw["actual_duration_us"],
                "A_to_B_transfer": raw["transfer_A_to_B"],
                "B_to_A_transfer": raw["transfer_B_to_A"],
                "conditional_phase_rad": raw["conditional_phase_iSWAP_rad"],
                "final_max_logical_leakage": max(raw["final_logical_leakage_by_input"]),
                "sampled_max_logical_leakage": max(raw["max_logical_leakage_sampled_by_input"]),
                "sampled_max_coupler_population": max(raw["max_coupler_excited_probability_sampled_by_input"]),
                "logical_unitarity_defect": raw["logical_unitarity_defect_frobenius"],
                "norm_error": raw["final_norm_error"],
                "process_overlap_after_local_Z": raw["projected_process_overlap_after_local_Z"],
                "average_fidelity_including_leakage": raw["average_logical_fidelity_including_leakage"],
                "local_Z_fit_rad": raw["local_Z_fit_rad_global_outA_outB_inA_inB"],
            }
            row["screen_feasible"] = is_feasible(
                row, args.min_transfer, args.max_final_leakage,
                args.max_coupler_population,
            )
            rows.append(row)
            matrices[key] = matrix
            processed += 1
            atomic_csv(cp_csv, rows)
            tmp_npz = cp_npz.with_suffix(".tmp.npz")
            np.savez_compressed(tmp_npz, **matrices)
            tmp_npz.replace(cp_npz)
            atomic_json(cp_json, {
                "stage": 9, "status": "in_progress_resumable_checkpoint",
                "run_config": config, "candidate_count": len(rows),
                "total_candidate_count": total, "candidates": rows,
                "matrices_archive": cp_npz.name,
            })
            print(
                f"[{len(rows)}/{total}] biasOff={offset:+.5f} Phi0 "
                f"df={pump_offset_kHz:+.2f} kHz T={duration:.9f} us "
                f"F={row['process_overlap_after_local_Z']:.12f} "
                f"AB={row['A_to_B_transfer']:.12f} BA={row['B_to_A_transfer']:.12f} "
                f"phi={row['conditional_phase_rad']:+.8f} ZZ={row['static_ZZ_MHz']:+.7f} [checkpoint]",
                flush=True,
            )
            if args.max_new_candidates is not None and processed >= args.max_new_candidates and len(rows) < total:
                print("Chunk completed; rerun with --resume and identical parameters", flush=True)
                return

    rows.sort(key=lambda row: (row["bias_offset_Phi0"], row["pump_offset_from_static_kHz"], row["duration_requested_us"]))
    feasible = [row for row in rows if row["screen_feasible"]]
    best_f = max(feasible, key=lambda r: r["process_overlap_after_local_Z"]) if feasible else None
    best_phase = min(feasible, key=lambda r: abs(r["conditional_phase_rad"])) if feasible else None
    payload = {
        "stage": 9,
        "status": "static_bias_offset_parametric_gate_scan_complete",
        "hardware_ready": False,
        "model": "125-dimensional fixed-local-basis circuit-derived closed-system propagator",
        "run_config": config,
        "candidate_count": len(rows),
        "feasible_candidate_count": len(feasible),
        "screening_thresholds_not_hardware_acceptance": {
            "min_transfer_each_direction": args.min_transfer,
            "max_final_logical_leakage": args.max_final_leakage,
            "max_sampled_coupler_population": args.max_coupler_population,
        },
        "best_feasible_process_overlap_candidate": best_f,
        "minimum_absolute_conditional_phase_candidate": best_phase,
        "candidates": rows,
        "matrices_archive": matrix_path.name,
        "limitations": [
            "bias shift is evaluated in the Stage-5 fixed 5-level coupler basis; excluded local coupler levels are not re-quantized",
            "coarse temporal grid; finalists require common-duration 120/240/480 convergence",
            "no measured flux-line calibration, bandwidth, delay, distortion or crosstalk",
            "closed-system only; no T1/T2, thermal population, quasiparticles or fabrication disorder",
            "nominal capacitances and SQUID parameters remain assumptions, not layout extraction",
        ],
    }
    atomic_csv(csv_path, rows)
    tmp_npz = matrix_path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp_npz, **matrices)
    tmp_npz.replace(matrix_path)
    atomic_json(json_path, payload)
    for path in (cp_csv, cp_json, cp_npz):
        path.unlink(missing_ok=True)
    print("\nFEASIBLE:", len(feasible), "/", total, flush=True)
    print("BEST PROCESS OVERLAP:", json.dumps(best_f, indent=2), flush=True)
    print("MINIMUM ABS CONDITIONAL PHASE:", json.dumps(best_phase, indent=2), flush=True)
    print("Saved:", csv_path, json_path, matrix_path, flush=True)


if __name__ == "__main__":
    main()
