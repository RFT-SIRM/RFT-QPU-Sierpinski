#!/usr/bin/env python3
"""Coarse three-parameter iSWAP sweep with full four-state process metrics."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from contextlib import nullcontext

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "engineering" / "physical_prototype" / "src"
sys.path.insert(0, str(SRC))

try:
    from threadpoolctl import threadpool_limits
except ImportError:
    threadpool_limits = None

from rft_qpu.stage5_gate import GatePulse, build_fixed_basis_model, propagate_gate  # noqa: E402


def _candidate_key(frequency: float, amplitude: float, duration_offset: int) -> str:
    return f"f{frequency:.9f}_a{amplitude:.6f}_d{duration_offset:+d}"


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def _write_npz(path: Path, matrices: dict[str, object]) -> None:
    import numpy as np
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(handle, **matrices)
    tmp.replace(path)


def _write_json(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def main() -> None:
    import numpy as np

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-center-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--frequency-offsets-kHz", nargs="+", type=float,
                        default=[-0.5, 0.0, 0.5])
    parser.add_argument("--amplitudes-Phi0", nargs="+", type=float,
                        default=[0.0199, 0.0200, 0.0201])
    parser.add_argument("--duration-center-us", type=float, default=1.0625654067723154)
    parser.add_argument("--duration-offset-steps", nargs="+", type=int,
                        default=[-2, 0, 2],
                        help="offsets in steps at the requested steps-per-period grid")
    parser.add_argument("--steps-per-period", type=int, default=40,
                        help="coarse grid for the design-space sweep; confirm finalists at 240/480")
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage5_full_gate_sweep")
    parser.add_argument("--resume", action="store_true",
                        help="resume an interrupted sweep from its atomic checkpoint")
    parser.add_argument("--max-new-candidates", type=int, default=None,
                        help="optional chunk limit; checkpoint is retained for a later --resume")
    args = parser.parse_args()

    if args.steps_per_period < 8:
        parser.error("--steps-per-period must be at least 8")
    if args.max_new_candidates is not None and args.max_new_candidates < 1:
        parser.error("--max-new-candidates must be positive")
    if not args.frequency_offsets_kHz or not args.amplitudes_Phi0 or not args.duration_offset_steps:
        parser.error("frequency, amplitude and duration grids must be non-empty")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"{args.prefix}.csv"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    json_path = args.output_dir / f"{args.prefix}.json"
    checkpoint_csv = args.output_dir / f"{args.prefix}.checkpoint.csv"
    checkpoint_matrix = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"

    config = {
        "frequency_center_MHz": args.frequency_center_MHz,
        "frequency_offsets_kHz": args.frequency_offsets_kHz,
        "amplitudes_Phi0": args.amplitudes_Phi0,
        "duration_center_us": args.duration_center_us,
        "duration_offset_steps": args.duration_offset_steps,
        "steps_per_period": args.steps_per_period,
        "ramp_periods": args.ramp_periods,
    }

    rows: list[dict] = []
    matrices: dict[str, object] = {}
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(
                f"checkpoint exists at {checkpoint_json}; rerun with --resume "
                "or choose a different --prefix"
            )
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs; use the original grid or a new --prefix")
        rows = list(saved.get("candidates", []))
        if checkpoint_matrix.exists():
            with np.load(checkpoint_matrix) as archive:
                matrices = {key: archive[key].copy() for key in archive.files}
        completed = {_candidate_key(
            float(row["frequency_MHz"]), float(row["amplitude_Phi0"]),
            int(row["duration_offset_steps"])
        ) for row in rows}
        if completed != set(matrices):
            parser.error("checkpoint CSV/JSON and matrix archive are inconsistent")
        print(f"Resuming checkpoint: {len(completed)} of "
              f"{len(args.frequency_offsets_kHz) * len(args.amplitudes_Phi0) * len(args.duration_offset_steps)} "
              "candidates already complete", flush=True)
    else:
        if args.resume:
            parser.error(f"--resume requested but no checkpoint exists at {checkpoint_json}")
        completed = set()

    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    print("Built 125-dimensional circuit model; logical indices:",
          model.logical_eigen_indices, flush=True)

    total = (len(args.frequency_offsets_kHz) * len(args.amplitudes_Phi0)
             * len(args.duration_offset_steps))
    remaining = total - len(completed)
    processed_this_call = 0
    context = threadpool_limits(limits=1) if threadpool_limits else nullcontext()

    def checkpoint() -> None:
        _write_csv(checkpoint_csv, rows)
        _write_npz(checkpoint_matrix, matrices)
        _write_json(checkpoint_json, {
            "stage": 5,
            "status": "in_progress_resumable_checkpoint",
            "hardware_ready": False,
            "run_config": config,
            "candidate_count": len(rows),
            "total_candidate_count": total,
            "candidates": rows,
            "matrices_archive": checkpoint_matrix.name,
        })

    with context:
        for duration_offset in args.duration_offset_steps:
            for amplitude in args.amplitudes_Phi0:
                for frequency_offset in args.frequency_offsets_kHz:
                    frequency = args.frequency_center_MHz + frequency_offset / 1000.0
                    key = _candidate_key(frequency, amplitude, duration_offset)
                    if key in completed:
                        continue
                    dt = 1.0 / (frequency * args.steps_per_period)
                    requested_duration = (
                        args.duration_center_us + duration_offset
                        / (args.frequency_center_MHz * args.steps_per_period)
                    )
                    n_steps = int(round(requested_duration / dt))
                    actual_duration = n_steps * dt
                    pulse = GatePulse(
                        pump_frequency_MHz=frequency,
                        flux_amplitude_Phi0=amplitude,
                        duration_us=actual_duration,
                        ramp_periods=args.ramp_periods,
                    )
                    result = propagate_gate(model, pulse, args.steps_per_period)
                    row = {
                        "frequency_MHz": frequency,
                        "frequency_offset_kHz": frequency_offset,
                        "amplitude_Phi0": amplitude,
                        "duration_offset_steps": duration_offset,
                        "duration_us": result["actual_duration_us"],
                        "steps_per_period": args.steps_per_period,
                        "A_to_B_transfer": result["transfer_A_to_B"],
                        "B_to_A_transfer": result["transfer_B_to_A"],
                        "process_overlap_after_local_Z": result[
                            "projected_process_overlap_after_local_Z"
                        ],
                        "average_logical_fidelity_including_leakage": result[
                            "average_logical_fidelity_including_leakage"
                        ],
                        "conditional_phase_rad": result["conditional_phase_iSWAP_rad"],
                        "final_max_logical_leakage": max(result[
                            "final_logical_leakage_by_input"
                        ]),
                        "sampled_max_logical_leakage": max(result[
                            "max_logical_leakage_sampled_by_input"
                        ]),
                        "sampled_max_coupler_excited_probability": max(result[
                            "max_coupler_excited_probability_sampled_by_input"
                        ]),
                        "logical_unitarity_defect": result[
                            "logical_unitarity_defect_frobenius"
                        ],
                        "norm_error": result["final_norm_error"],
                    }
                    rows.append(row)
                    matrices[key] = result["logical_matrix"]
                    completed.add(key)
                    processed_this_call += 1
                    checkpoint()
                    run = len(completed)
                    print(
                        f"[{run}/{total}] f={frequency:.9f} MHz "
                        f"A={amplitude:.6f} Phi0 dStep={duration_offset:+d}: "
                        f"Fproc={row['process_overlap_after_local_Z']:.12f}, "
                        f"A->B={row['A_to_B_transfer']:.12f}, "
                        f"phi={row['conditional_phase_rad']:.8f} rad "
                        "[checkpoint saved]",
                        flush=True,
                    )
                    if (args.max_new_candidates is not None
                            and processed_this_call >= args.max_new_candidates
                            and len(completed) < total):
                        print("Chunk limit reached; progress is safely checkpointed.")
                        print("Resume with the same arguments plus --resume.")
                        return

    rows.sort(key=lambda r: (
        int(r["duration_offset_steps"]), float(r["amplitude_Phi0"]),
        float(r["frequency_offset_kHz"]),
    ))
    feasible = [r for r in rows if
                r["A_to_B_transfer"] >= 0.999
                and r["B_to_A_transfer"] >= 0.999
                and r["final_max_logical_leakage"] <= 1e-3
                and r["sampled_max_coupler_excited_probability"] <= 0.02]
    best = max(feasible or rows, key=lambda r: r["process_overlap_after_local_Z"])
    worst = min(rows, key=lambda r: r["process_overlap_after_local_Z"])
    centre_frequency = args.frequency_center_MHz
    centre_amplitude = min(args.amplitudes_Phi0, key=lambda x: abs(x - 0.020))
    centre_duration_offset = min(args.duration_offset_steps, key=abs)
    centre = min(rows, key=lambda r: (
        abs(r["frequency_MHz"] - centre_frequency),
        abs(r["amplitude_Phi0"] - centre_amplitude),
        abs(r["duration_offset_steps"] - centre_duration_offset),
    ))

    robustness = {
        "sampled_box_min_process_overlap": worst["process_overlap_after_local_Z"],
        "sampled_box_max_final_logical_leakage": max(r["final_max_logical_leakage"] for r in rows),
        "sampled_box_max_coupler_excited_probability": max(
            r["sampled_max_coupler_excited_probability"] for r in rows
        ),
        "sampled_box_min_A_to_B_transfer": min(r["A_to_B_transfer"] for r in rows),
    }

    _write_csv(csv_path, rows)
    _write_npz(matrix_path, matrices)
    payload = {
        "stage": 5,
        "status": "coarse_three_parameter_full_gate_sweep_complete",
        "hardware_ready": False,
        "model_dimension": 125,
        "logical_eigen_indices": model.logical_eigen_indices,
        **config,
        "feasibility_screen": {
            "A_to_B_and_B_to_A_transfer_min": 0.999,
            "final_max_logical_leakage_max": 1e-3,
            "sampled_max_coupler_excited_probability_max": 0.02,
            "note": "engineering screening thresholds only; not hardware acceptance limits",
        },
        "candidate_count": len(rows),
        "feasible_candidate_count": len(feasible),
        "nominal_center_candidate": centre,
        "best_sampled_feasible_candidate": best,
        "worst_candidate": worst,
        "sampled_box_robustness": robustness,
        "candidates": rows,
        "matrices_archive": matrix_path.name,
        "limitations": [
            "coarse search only; finalists require 120/240/480 convergence",
            "closed-system model only",
            "no measured flux-line transfer, T1/T2, thermal population or calibration noise",
            "sampled maximum leakage/coupler occupancy depends on time sampling",
            "nominal capacitances and SQUID parameters are assumptions, not extracted layout data",
        ],
    }
    _write_json(json_path, payload)
    for checkpoint_path in (checkpoint_csv, checkpoint_matrix, checkpoint_json):
        checkpoint_path.unlink(missing_ok=True)

    print("\nBEST SAMPLED FEASIBLE CANDIDATE:")
    print(json.dumps(best, indent=2))
    print("\nSAMPLED BOX ROBUSTNESS:")
    print(json.dumps(robustness, indent=2))
    print("Saved:", csv_path)
    print("Saved:", json_path)
    print("Saved:", matrix_path)


if __name__ == "__main__":
    main()
