#!/usr/bin/env python3
"""Stage 6 coarse frequency/flux-amplitude/duration robustness map."""
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

from rft_qpu.stage5_gate import GatePulse, build_fixed_basis_model, propagate_gate  # noqa: E402
from rft_qpu.stage6_gate import evaluate_candidate_feasibility  # noqa: E402


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


def atomic_npz(path: Path, matrices: dict) -> None:
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(handle, **matrices)
    tmp.replace(path)


def candidate_key(frequency: float, amplitude: float, duration_offset_ps: float) -> str:
    return f"f{frequency:.12f}_a{amplitude:.10f}_t{duration_offset_ps:+.6f}ps"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-center-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--frequency-offsets-kHz", nargs="+", type=float, default=[-1.0, 0.0, 1.0])
    parser.add_argument("--amplitudes-Phi0", nargs="+", type=float, default=[0.0199, 0.0200, 0.0201])
    parser.add_argument("--duration-center-us", type=float, default=1.0625654067723154)
    parser.add_argument("--duration-offsets-ps", nargs="+", type=float, default=[-25.3165, 0.0, 25.3165])
    parser.add_argument("--steps-per-period", type=int, default=40)
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage6_robustness_sweep")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-candidates", type=int, default=None)
    parser.add_argument("--min-transfer", type=float, default=0.999)
    parser.add_argument("--max-final-leakage", type=float, default=1e-3)
    parser.add_argument("--max-coupler-population", type=float, default=0.02)
    args = parser.parse_args()

    if args.steps_per_period < 8:
        parser.error("--steps-per-period must be at least 8")
    if args.max_new_candidates is not None and args.max_new_candidates < 1:
        parser.error("--max-new-candidates must be positive")
    if not args.frequency_offsets_kHz or not args.amplitudes_Phi0 or not args.duration_offsets_ps:
        parser.error("all parameter grids must be non-empty")
    if any(a < 0 for a in args.amplitudes_Phi0):
        parser.error("flux amplitudes must be non-negative")
    if (len(set(args.frequency_offsets_kHz)) != len(args.frequency_offsets_kHz)
            or len(set(args.amplitudes_Phi0)) != len(args.amplitudes_Phi0)
            or len(set(args.duration_offsets_ps)) != len(args.duration_offsets_ps)):
        parser.error("parameter grid values must be unique")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"{args.prefix}.csv"
    json_path = args.output_dir / f"{args.prefix}.json"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    checkpoint_csv = args.output_dir / f"{args.prefix}.checkpoint.csv"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    checkpoint_matrix = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"

    config = {
        "frequency_center_MHz": args.frequency_center_MHz,
        "frequency_offsets_kHz": args.frequency_offsets_kHz,
        "amplitudes_Phi0": args.amplitudes_Phi0,
        "duration_center_us": args.duration_center_us,
        "duration_offsets_ps": args.duration_offsets_ps,
        "steps_per_period": args.steps_per_period,
        "ramp_periods": args.ramp_periods,
    }
    rows: list[dict] = []
    matrices: dict = {}
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {checkpoint_json}; pass --resume or change --prefix")
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint run configuration differs")
        rows = list(saved["candidates"])
        if not checkpoint_matrix.exists():
            parser.error("checkpoint matrix archive missing")
        with np.load(checkpoint_matrix) as archive:
            matrices = {k: archive[k].copy() for k in archive.files}
        expected = {candidate_key(float(r["frequency_MHz"]), float(r["amplitude_Phi0"]),
                                  float(r["duration_offset_ps"])) for r in rows}
        if expected != set(matrices):
            parser.error("checkpoint rows and matrices do not match")
        print(f"Resuming {len(rows)} completed candidates", flush=True)
    elif args.resume:
        parser.error("--resume requested but no checkpoint exists")

    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    total = len(args.frequency_offsets_kHz) * len(args.amplitudes_Phi0) * len(args.duration_offsets_ps)
    completed = {candidate_key(float(r["frequency_MHz"]), float(r["amplitude_Phi0"]),
                               float(r["duration_offset_ps"])) for r in rows}
    processed = 0
    context = threadpool_limits(limits=1) if threadpool_limits else nullcontext()

    def checkpoint() -> None:
        atomic_csv(checkpoint_csv, rows)
        atomic_npz(checkpoint_matrix, matrices)
        atomic_json(checkpoint_json, {
            "stage": 6, "status": "in_progress_resumable_checkpoint",
            "run_config": config, "candidate_count": len(rows),
            "total_candidate_count": total, "candidates": rows,
            "matrices_archive": checkpoint_matrix.name,
        })

    with context:
        for duration_offset_ps in args.duration_offsets_ps:
            for amplitude in args.amplitudes_Phi0:
                for frequency_offset_kHz in args.frequency_offsets_kHz:
                    frequency = args.frequency_center_MHz + frequency_offset_kHz / 1000.0
                    key = candidate_key(frequency, amplitude, duration_offset_ps)
                    if key in completed:
                        continue
                    requested_duration = args.duration_center_us + duration_offset_ps * 1e-6
                    dt = 1.0 / (frequency * args.steps_per_period)
                    n_steps = int(round(requested_duration / dt))
                    actual_duration = n_steps * dt
                    pulse = GatePulse(
                        pump_frequency_MHz=frequency,
                        flux_amplitude_Phi0=amplitude,
                        duration_us=actual_duration,
                        ramp_periods=args.ramp_periods,
                    )
                    raw = propagate_gate(model, pulse, args.steps_per_period)
                    row = {
                        "frequency_MHz": frequency,
                        "frequency_offset_kHz": frequency_offset_kHz,
                        "amplitude_Phi0": amplitude,
                        "duration_offset_ps": duration_offset_ps,
                        "requested_duration_us": requested_duration,
                        "actual_duration_us": raw["actual_duration_us"],
                        "steps_per_period": args.steps_per_period,
                        "time_steps": raw["time_steps"],
                        "A_to_B_transfer": raw["transfer_A_to_B"],
                        "B_to_A_transfer": raw["transfer_B_to_A"],
                        "process_overlap_after_local_Z": raw["projected_process_overlap_after_local_Z"],
                        "average_logical_fidelity_including_leakage": raw["average_logical_fidelity_including_leakage"],
                        "conditional_phase_rad": raw["conditional_phase_iSWAP_rad"],
                        "final_max_logical_leakage": max(raw["final_logical_leakage_by_input"]),
                        "sampled_max_logical_leakage": max(raw["max_logical_leakage_sampled_by_input"]),
                        "sampled_max_coupler_excited_probability": max(raw["max_coupler_excited_probability_sampled_by_input"]),
                        "logical_unitarity_defect": raw["logical_unitarity_defect_frobenius"],
                        "norm_error": raw["final_norm_error"],
                        "local_Z_fit_rad_canonical": np.angle(np.exp(1j * np.asarray(
                            raw["local_Z_fit_rad_global_outA_outB_inA_inB"], dtype=float))).tolist(),
                    }
                    rows.append(row)
                    matrices[key] = raw["logical_matrix"]
                    completed.add(key)
                    processed += 1
                    checkpoint()
                    print(
                        f"[{len(rows)}/{total}] f={frequency:.9f} MHz "
                        f"A={amplitude:.7f} Phi0 dtOffset={duration_offset_ps:+.3f} ps: "
                        f"Fproc={row['process_overlap_after_local_Z']:.12f}, "
                        f"A->B={row['A_to_B_transfer']:.12f}, "
                        f"phi={row['conditional_phase_rad']:.8f} rad [checkpoint saved]",
                        flush=True,
                    )
                    if args.max_new_candidates is not None and processed >= args.max_new_candidates and len(rows) < total:
                        print("Chunk limit reached; repeat same command with --resume", flush=True)
                        return

    rows.sort(key=lambda r: (float(r["duration_offset_ps"]), float(r["amplitude_Phi0"]),
                             float(r["frequency_offset_kHz"])))
    selection = evaluate_candidate_feasibility(
        rows, min_transfer=args.min_transfer,
        max_final_leakage=args.max_final_leakage,
        max_sampled_coupler_population=args.max_coupler_population,
    )
    worst = min(rows, key=lambda r: r["process_overlap_after_local_Z"])
    robustness = {
        "sampled_box_min_process_overlap": min(r["process_overlap_after_local_Z"] for r in rows),
        "sampled_box_min_A_to_B_transfer": min(r["A_to_B_transfer"] for r in rows),
        "sampled_box_min_B_to_A_transfer": min(r["B_to_A_transfer"] for r in rows),
        "sampled_box_max_final_logical_leakage": max(r["final_max_logical_leakage"] for r in rows),
        "sampled_box_max_transient_logical_leakage": max(r["sampled_max_logical_leakage"] for r in rows),
        "sampled_box_max_coupler_excited_probability": max(r["sampled_max_coupler_excited_probability"] for r in rows),
        "sampled_box_max_abs_conditional_phase_rad": max(abs(r["conditional_phase_rad"]) for r in rows),
    }
    payload = {
        "stage": 6,
        "status": "coarse_three_parameter_robustness_sweep_complete",
        "hardware_ready": False,
        "model": "125-dimensional circuit-derived fixed-DC-basis closed-system propagator",
        "run_config": config,
        "candidate_count": len(rows),
        **selection,
        "worst_process_overlap_candidate": worst,
        "sampled_box_robustness": robustness,
        "candidates": rows,
        "matrices_archive": matrix_path.name,
        "limitations": [
            "coarse search only; finalists require common-duration 120/240/480 convergence",
            "closed-system model only",
            "nominal capacitance and SQUID parameters remain assumptions",
            "no T1/T2, thermal bath, measured flux-line transfer or calibration noise",
            "sampled transient maxima depend on temporal sampling density",
        ],
    }
    atomic_csv(csv_path, rows)
    atomic_npz(matrix_path, matrices)
    atomic_json(json_path, payload)
    for path in (checkpoint_csv, checkpoint_json, checkpoint_matrix):
        path.unlink(missing_ok=True)
    print("\nCANDIDATE SELECTION:\n", json.dumps(selection, indent=2), flush=True)
    print("\nSAMPLED-BOX ROBUSTNESS:\n", json.dumps(robustness, indent=2), flush=True)
    print("Saved:", csv_path, json_path, matrix_path, flush=True)


if __name__ == "__main__":
    main()
