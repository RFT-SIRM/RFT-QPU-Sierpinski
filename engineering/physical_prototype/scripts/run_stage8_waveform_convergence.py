#!/usr/bin/env python3
"""High-resolution common-duration convergence for a Stage-8 chirped pulse."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engineering/physical_prototype/src"))

from rft_qpu.stage5_gate import (  # noqa: E402
    analyze_matrix_convergence,
    build_fixed_basis_model,
    richardson_extrapolate,
)
from rft_qpu.stage6_gate import choose_common_grid_duration  # noqa: E402
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625675587737073)
    parser.add_argument("--ramp-in-periods", type=float, default=8.0)
    parser.add_argument("--ramp-out-periods", type=float, default=8.0)
    parser.add_argument("--chirp-span-kHz", type=float, default=0.0)
    parser.add_argument("--steps-per-period", nargs="+", type=int, default=[120, 240, 480])
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage8_waveform_convergence")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-grids", type=int, default=None)
    args = parser.parse_args()

    if args.frequency_MHz <= 0 or args.duration_us <= 0 or args.amplitude_Phi0 < 0:
        parser.error("invalid frequency, duration or amplitude")
    if len(args.steps_per_period) < 3 or len(set(args.steps_per_period)) != len(args.steps_per_period):
        parser.error("provide at least three unique grids")
    if args.max_new_grids is not None and args.max_new_grids < 1:
        parser.error("--max-new-grids must be positive")

    common = choose_common_grid_duration(
        args.frequency_MHz, args.duration_us, args.steps_per_period
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    md_path = args.output_dir / f"{args.prefix}.md"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    cp_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    cp_npz = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"
    config = {
        "frequency_MHz": args.frequency_MHz,
        "amplitude_Phi0": args.amplitude_Phi0,
        "requested_duration_us": args.duration_us,
        "actual_shared_duration_us": common.actual_duration_us,
        "ramp_in_periods": args.ramp_in_periods,
        "ramp_out_periods": args.ramp_out_periods,
        "chirp_span_kHz": args.chirp_span_kHz,
        "steps_per_period": list(args.steps_per_period),
        "steps_by_grid": {str(k): v for k, v in common.steps_by_grid.items()},
    }

    rows: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if cp_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {cp_json}; pass --resume or change --prefix")
        saved = json.loads(cp_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs")
        rows = list(saved["grid_results"])
        if not cp_npz.exists():
            parser.error("checkpoint matrices are missing")
        with np.load(cp_npz) as data:
            matrices = {k: data[k].copy() for k in data.files}
        if {str(r["steps_per_period"]) for r in rows} != set(matrices):
            parser.error("checkpoint result and matrix grids differ")
        print(f"Resuming {len(rows)}/{len(args.steps_per_period)} completed grids", flush=True)
    elif args.resume:
        parser.error("--resume requested without checkpoint")

    with threadpool_limits(limits=1):
        model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
        print("Fixed circuit basis:", model.logical_eigen_indices,
              "DC flux:", model.flux_dc_Phi0, flush=True)
        processed = 0
        for spp in args.steps_per_period:
            key = str(spp)
            if key in matrices:
                continue
            pulse = ChirpedFluxPulse(
                frequency_MHz=args.frequency_MHz,
                fundamental_amplitude_Phi0=args.amplitude_Phi0,
                duration_us=common.actual_duration_us,
                ramp_in_periods=args.ramp_in_periods,
                ramp_out_periods=args.ramp_out_periods,
                chirp_span_kHz=args.chirp_span_kHz,
            )
            result = propagate_chirped_gate(
                model, pulse, spp, track_stride=max(1, spp // 24)
            )
            matrix = result.pop("logical_matrix")
            result["steps_by_common_duration_grid"] = common.steps_by_grid[spp]
            rows.append(result)
            matrices[key] = matrix
            processed += 1
            tmp_npz = cp_npz.with_suffix(".tmp.npz")
            np.savez_compressed(tmp_npz, **matrices)
            tmp_npz.replace(cp_npz)
            atomic_json(cp_json, {
                "stage": 8, "status": "in_progress_resumable_checkpoint",
                "run_config": config, "grid_results": rows,
                "completed_grids": len(rows),
            })
            print(
                f"[{len(rows)}/{len(args.steps_per_period)}] {spp} steps/period "
                f"AB={result['A_to_B_transfer']:.12f} F={result['process_overlap_after_local_Z']:.12f} "
                f"phi={result['conditional_phase_rad']:+.10f} T={result['duration_actual_us']:.15f} us [checkpoint]",
                flush=True,
            )
            if args.max_new_grids is not None and processed >= args.max_new_grids and len(rows) < len(args.steps_per_period):
                print("Chunk completed; resume with identical arguments and --resume", flush=True)
                return

    rows.sort(key=lambda row: row["steps_per_period"])
    matrix_rows = [
        {"steps_per_period": row["steps_per_period"], "logical_matrix": matrices[str(row["steps_per_period"])]}
        for row in rows
    ]
    convergence = analyze_matrix_convergence(matrix_rows)
    phases = {int(r["steps_per_period"]): float(r["conditional_phase_rad"]) for r in rows}
    payload = {
        "stage": 8,
        "status": "chirped_asymmetric_envelope_common_duration_convergence_complete",
        "hardware_ready": False,
        "model": "125-dimensional circuit-derived fixed-DC-basis closed-system Strang propagator",
        "parameters": config,
        "grid_results": rows,
        "adjacent_grid_matrix_comparisons": convergence["adjacent_grid_comparisons"],
        "richardson_conditional_phase_rad_second_order": richardson_extrapolate(phases),
        "matrices_archive": matrix_path.name,
        "limitations": [
            "common physical duration is enforced across grids; remaining error is temporal integration and sampled extrema",
            "the pulse waveform is idealized and is not passed through a measured flux-line transfer function",
            "closed-system model only; no T1/T2 or thermal bath",
            "nominal circuit capacitances and SQUID parameters are assumptions, not layout extraction",
        ],
    }
    atomic_json(json_path, payload)
    tmp_npz = matrix_path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp_npz, **matrices)
    tmp_npz.replace(matrix_path)
    lines = [
        "# Stage 8 — chirped/asymmetric pulse convergence", "",
        "Status: closed-system numerical convergence check; not hardware qualification.", "",
        f"Shared physical duration: {common.actual_duration_us:.15f} us", "",
        "| Grid (steps/period) | A→B | B→A | Process overlap | Conditional phase (rad) | Final leakage max | Sampled coupler max |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['steps_per_period']} | {r['A_to_B_transfer']:.12f} | {r['B_to_A_transfer']:.12f} "
            f"| {r['process_overlap_after_local_Z']:.12f} | {r['conditional_phase_rad']:.10f} "
            f"| {r['final_max_logical_leakage']:.3e} | {r['sampled_max_coupler_excited_probability']:.6f} |"
        )
    lines += ["", "## Adjacent-grid full-matrix comparison", ""]
    for p in convergence["adjacent_grid_comparisons"]:
        lines.append(
            f"- {p['coarse_steps_per_period']}→{p['fine_steps_per_period']}: raw Frobenius "
            f"{p['raw_frobenius_difference']:.6e}; after independent input/output local-Z alignment "
            f"{p['phase_aligned_frobenius_difference']:.6e}; max element "
            f"{p['phase_aligned_max_element_difference']:.6e}."
        )
    lines += ["", f"Second-order Richardson conditional phase: {payload['richardson_conditional_phase_rad_second_order']}", ""]
    lines += ["## Evidence boundary", "", *[f"- {x}" for x in payload["limitations"]], ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    for path in (cp_json, cp_npz):
        path.unlink(missing_ok=True)
    print("Saved:", json_path, md_path, matrix_path, flush=True)
    print("Richardson phase:", payload["richardson_conditional_phase_rad_second_order"], flush=True)


if __name__ == "__main__":
    main()
