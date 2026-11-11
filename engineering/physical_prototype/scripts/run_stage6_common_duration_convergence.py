#!/usr/bin/env python3
"""Stage 6 convergence audit using one exactly shared physical pulse duration."""
from __future__ import annotations

import argparse
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

from rft_qpu.stage5_gate import (  # noqa: E402
    GatePulse, analyze_matrix_convergence, build_fixed_basis_model,
    conditional_phase_invariant, propagate_gate, richardson_extrapolate,
)
from rft_qpu.stage6_gate import (  # noqa: E402
    canonicalize_local_z_fit, choose_common_grid_duration,
)


def atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def atomic_npz(path: Path, results: list[dict]) -> None:
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(
            handle,
            **{f"U_{r['steps_per_period']}": r["logical_matrix"] for r in results},
            **{f"Ucorr_{r['steps_per_period']}": r["phase_corrected_matrix"] for r in results},
        )
    tmp.replace(path)


def summary_rows(results: list[dict]) -> list[dict]:
    return [{k: v for k, v in row.items()
             if k not in ("logical_matrix", "phase_corrected_matrix")}
            for row in results]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps-per-period", nargs="+", type=int, default=[120, 240, 480])
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625654067723154,
                        help="requested pulse duration; snapped once to common grid")
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage6_common_duration_convergence")
    parser.add_argument("--track-stride", type=int, default=0)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-grids", type=int, default=None)
    args = parser.parse_args()

    if not args.steps_per_period or any(x < 8 for x in args.steps_per_period):
        parser.error("each time grid must contain at least 8 steps per period")
    if len(set(args.steps_per_period)) != len(args.steps_per_period):
        parser.error("time grids must be unique")
    if args.max_new_grids is not None and args.max_new_grids < 1:
        parser.error("--max-new-grids must be positive")
    if args.track_stride < 0:
        parser.error("--track-stride cannot be negative")

    duration = choose_common_grid_duration(
        args.frequency_MHz, args.duration_us, args.steps_per_period
    )
    pulse = GatePulse(
        pump_frequency_MHz=args.frequency_MHz,
        flux_amplitude_Phi0=args.amplitude_Phi0,
        duration_us=duration.actual_duration_us,
        ramp_periods=args.ramp_periods,
    )
    config = {
        "steps_per_period": args.steps_per_period,
        "frequency_MHz": args.frequency_MHz,
        "amplitude_Phi0": args.amplitude_Phi0,
        "requested_duration_us": args.duration_us,
        "common_actual_duration_us": duration.actual_duration_us,
        "gcd_steps_per_period": duration.gcd_steps_per_period,
        "common_ticks": duration.common_ticks,
        "steps_by_grid": {str(k): v for k, v in duration.steps_by_grid.items()},
        "ramp_periods": args.ramp_periods,
        "track_stride": args.track_stride,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    md_path = args.output_dir / f"{args.prefix}.md"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    checkpoint_matrix = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"

    results: list[dict] = []
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {checkpoint_json}; use --resume or a new --prefix")
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint settings differ; resume with identical settings")
        if not checkpoint_matrix.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(checkpoint_matrix) as archive:
            for row in saved["grid_results"]:
                spp = int(row["steps_per_period"])
                if f"U_{spp}" not in archive or f"Ucorr_{spp}" not in archive:
                    parser.error(f"checkpoint missing matrix for grid {spp}")
                restored = dict(row)
                restored["logical_matrix"] = archive[f"U_{spp}"].copy()
                restored["phase_corrected_matrix"] = archive[f"Ucorr_{spp}"].copy()
                results.append(restored)
        print(f"Resuming {len(results)}/{len(args.steps_per_period)} grids", flush=True)
    elif args.resume:
        parser.error("--resume requested but no checkpoint exists")

    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    print("Static circuit basis:", model.logical_eigen_indices,
          "DC flux Phi0:", model.flux_dc_Phi0, flush=True)
    context = threadpool_limits(limits=1) if threadpool_limits else nullcontext()

    def save_checkpoint() -> None:
        atomic_npz(checkpoint_matrix, results)
        atomic_json(checkpoint_json, {
            "stage": 6, "status": "in_progress_resumable_checkpoint",
            "run_config": config, "grid_results": summary_rows(results),
            "matrix_archive": checkpoint_matrix.name,
        })

    done = {int(x["steps_per_period"]) for x in results}
    new_count = 0
    with context:
        for spp in args.steps_per_period:
            if spp in done:
                continue
            print(f"Propagating {spp} steps/period; shared duration={pulse.duration_us:.15f} us", flush=True)
            row = propagate_gate(
                model, pulse, spp,
                track_stride=args.track_stride if args.track_stride > 0 else None,
            )
            if abs(row["actual_duration_us"] - duration.actual_duration_us) > 1e-12:
                raise ArithmeticError("propagator changed the shared physical pulse duration")
            row = canonicalize_local_z_fit(row)
            results.append(row)
            done.add(spp)
            new_count += 1
            save_checkpoint()
            print(
                f"  A->B={row['transfer_A_to_B']:.12f}; "
                f"Fproc={row['projected_process_overlap_after_local_Z']:.12f}; "
                f"phi={row['conditional_phase_iSWAP_rad']:.10g} rad; "
                f"actual T={row['actual_duration_us']:.15f} us [checkpoint saved]",
                flush=True,
            )
            if args.max_new_grids is not None and new_count >= args.max_new_grids and len(done) < len(args.steps_per_period):
                print("Chunk limit reached; resume with identical arguments plus --resume", flush=True)
                return

    results.sort(key=lambda x: int(x["steps_per_period"]))
    convergence = analyze_matrix_convergence(results)
    for pair in convergence["adjacent_grid_comparisons"]:
        key = "phase_fit_rad_global_outA_outB_inA_inB"
        if key in pair:
            pair[key] = np.angle(np.exp(1j * np.asarray(pair[key], dtype=float))).tolist()
    metric_names = (
        "transfer_A_to_B", "transfer_B_to_A", "conditional_phase_iSWAP_rad",
        "projected_process_overlap_after_local_Z", "average_logical_fidelity_including_leakage",
    )
    richardson = {
        name: richardson_extrapolate({int(r["steps_per_period"]): float(r[name]) for r in results})
        for name in metric_names
    }
    payload = {
        "stage": 6,
        "status": "fixed_physical_duration_full_matrix_convergence",
        "hardware_ready": False,
        "model": {
            "logical_dimension": 4,
            "product_hilbert_dimension": 125,
            "logical_eigen_indices": model.logical_eigen_indices,
            "dc_flux_Phi0": model.flux_dc_Phi0,
            "propagator": "symmetric Strang split in fixed-DC circuit-derived basis",
        },
        "duration_quantization": config,
        "pulse": {
            "pump_frequency_MHz": pulse.pump_frequency_MHz,
            "flux_amplitude_Phi0": pulse.flux_amplitude_Phi0,
            "actual_shared_duration_us": pulse.duration_us,
            "ramp_periods": pulse.ramp_periods,
        },
        "grid_results": summary_rows(results),
        "matrix_convergence": convergence,
        "second_order_richardson_extrapolation": richardson,
        "matrix_archive": matrix_path.name,
        "limitations": [
            "closed-system calculation only",
            "nominal capacitance and SQUID values remain assumptions, not extracted layout data",
            "no flux-line transfer, crosstalk, T1/T2, thermal bath or calibration noise",
            "sampled transient peak metrics depend on track_stride",
        ],
    }
    atomic_npz(matrix_path, results)
    atomic_json(json_path, payload)

    lines = [
        "# Stage 6 — full-gate convergence at a shared physical duration", "",
        "All time grids use exactly the same physical pulse duration; only the integration step changes.", "",
        f"- Requested duration: {duration.requested_duration_us:.15f} us",
        f"- Shared actual duration: {duration.actual_duration_us:.15f} us",
        f"- Common GCD steps per period: {duration.gcd_steps_per_period}",
        f"- Grids: {', '.join(map(str, args.steps_per_period))}", "",
        "| Grid | Actual duration (us) | A→B transfer | Process overlap | Conditional phase (rad) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['steps_per_period']} | {r['actual_duration_us']:.15f} | "
            f"{r['transfer_A_to_B']:.12f} | {r['projected_process_overlap_after_local_Z']:.12f} | "
            f"{r['conditional_phase_iSWAP_rad']:.10g} |"
        )
    lines += ["", "## Full-matrix phase alignment", ""]
    for pair in convergence["adjacent_grid_comparisons"]:
        lines.append(
            f"- {pair['coarse_steps_per_period']}→{pair['fine_steps_per_period']}: "
            f"raw Frobenius {pair['raw_frobenius_difference']:.10g}; "
            f"after independent local-Z/global-phase alignment "
            f"{pair['phase_aligned_frobenius_difference']:.10g}; "
            f"max element {pair['phase_aligned_max_element_difference']:.10g}."
        )
    lines += ["", "## Richardson extrapolation", ""]
    for name, value in richardson.items():
        lines.append(f"- {name}: {value if value is not None else 'not available'}")
    lines += ["", "## Evidence boundary", "", "No experimental or hardware-qualified gate fidelity is claimed."]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    checkpoint_json.unlink(missing_ok=True)
    checkpoint_matrix.unlink(missing_ok=True)
    print("Saved:", json_path, matrix_path, md_path, flush=True)
    print("Shared actual duration:", duration.actual_duration_us, "us", flush=True)


if __name__ == "__main__":
    main()
