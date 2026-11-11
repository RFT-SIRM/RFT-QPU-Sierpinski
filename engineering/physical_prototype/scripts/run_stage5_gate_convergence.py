#!/usr/bin/env python3
"""Reproduce Stage 4 and audit full-matrix phase convergence (Stage 5)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from contextlib import nullcontext

try:
    from threadpoolctl import threadpool_limits
except ImportError:  # optional acceleration / predictable BLAS threading
    threadpool_limits = None

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "engineering" / "physical_prototype" / "src"
sys.path.insert(0, str(SRC))

from rft_qpu.stage5_gate import (  # noqa: E402
    GatePulse,
    analyze_matrix_convergence,
    build_fixed_basis_model,
    conditional_phase_invariant,
    propagate_gate,
    richardson_extrapolate,
)



def _write_json_atomic(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def _write_matrix_archive(path: Path, results: list[dict]) -> None:
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(
            handle,
            **{f"U_{r['steps_per_period']}": r["logical_matrix"] for r in results},
            **{f"Ucorr_{r['steps_per_period']}": r["phase_corrected_matrix"] for r in results},
        )
    tmp.replace(path)


def _summary_rows(results: list[dict]) -> list[dict]:
    return [
        {k: v for k, v in r.items()
         if k not in ("logical_matrix", "phase_corrected_matrix")}
        for r in results
    ]

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps-per-period", nargs="+", type=int,
                        default=[120, 240, 480],
                        help="time grids; 120/240/480 reproduces the Stage-4 convergence pair")
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625654067723154)
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage5_gate_convergence")
    parser.add_argument("--track-stride", type=int, default=0,
                        help="sample dynamics every N steps; 0 uses ~24 samples per pump period")
    parser.add_argument("--resume", action="store_true",
                        help="resume an interrupted grid sequence from its atomic checkpoint")
    parser.add_argument("--max-new-grids", type=int, default=None,
                        help="optional chunk limit; use --resume to continue the remaining grids")
    args = parser.parse_args()

    if not args.steps_per_period or any(x < 8 for x in args.steps_per_period):
        parser.error("each time grid must contain at least 8 steps per period")
    if len(set(args.steps_per_period)) != len(args.steps_per_period):
        parser.error("time grids must be unique")
    if args.max_new_grids is not None and args.max_new_grids < 1:
        parser.error("--max-new-grids must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pulse = GatePulse(
        pump_frequency_MHz=args.frequency_MHz,
        flux_amplitude_Phi0=args.amplitude_Phi0,
        duration_us=args.duration_us,
        ramp_periods=args.ramp_periods,
    )
    config = {
        "steps_per_period": args.steps_per_period,
        "frequency_MHz": args.frequency_MHz,
        "amplitude_Phi0": args.amplitude_Phi0,
        "duration_us": args.duration_us,
        "ramp_periods": args.ramp_periods,
        "track_stride": args.track_stride,
    }
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    json_path = args.output_dir / f"{args.prefix}.json"
    md_path = args.output_dir / f"{args.prefix}.md"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    checkpoint_matrix = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"

    raw_results: list[dict] = []
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(
                f"checkpoint exists at {checkpoint_json}; rerun with --resume "
                "or choose another --prefix"
            )
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs; use original settings or a new --prefix")
        if not checkpoint_matrix.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(checkpoint_matrix) as archive:
            for row in saved.get("grid_results", []):
                result = dict(row)
                spp = int(result["steps_per_period"])
                if f"U_{spp}" not in archive or f"Ucorr_{spp}" not in archive:
                    parser.error(f"checkpoint matrix missing for {spp} steps/period")
                result["logical_matrix"] = archive[f"U_{spp}"].copy()
                result["phase_corrected_matrix"] = archive[f"Ucorr_{spp}"].copy()
                raw_results.append(result)
        print(f"Resuming: {len(raw_results)} of {len(args.steps_per_period)} grids complete",
              flush=True)
    elif args.resume:
        parser.error(f"--resume requested but no checkpoint exists at {checkpoint_json}")

    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    print("Static circuit basis ready:", model.logical_eigen_indices,
          "DC flux Phi0=", model.flux_dc_Phi0, flush=True)

    thread_context = threadpool_limits(limits=1) if threadpool_limits else nullcontext()

    def checkpoint() -> None:
        _write_matrix_archive(checkpoint_matrix, raw_results)
        _write_json_atomic(checkpoint_json, {
            "stage": 5,
            "status": "in_progress_resumable_checkpoint",
            "run_config": config,
            "grid_results": _summary_rows(raw_results),
            "matrix_archive": checkpoint_matrix.name,
        })

    done = {int(r["steps_per_period"]) for r in raw_results}
    processed_this_call = 0
    with thread_context:
        for spp in args.steps_per_period:
            if spp in done:
                continue
            print(f"Propagating {spp} steps/period...", flush=True)
            result = propagate_gate(
                model, pulse, spp,
                track_stride=(args.track_stride if args.track_stride > 0 else None),
            )
            raw_results.append(result)
            done.add(spp)
            processed_this_call += 1
            checkpoint()
            print(
                f"  A->B={result['transfer_A_to_B']:.12f}; "
                f"Fproc={result['projected_process_overlap_after_local_Z']:.12f}; "
                f"phi={result['conditional_phase_iSWAP_rad']:.10g} rad; "
                f"unitarity={result['logical_unitarity_defect_frobenius']:.3e} "
                "[checkpoint saved]",
                flush=True,
            )
            if (args.max_new_grids is not None
                    and processed_this_call >= args.max_new_grids
                    and len(done) < len(args.steps_per_period)):
                print("Grid chunk limit reached; progress is safely checkpointed.")
                print("Resume with the same arguments plus --resume.")
                return

    raw_results.sort(key=lambda r: int(r["steps_per_period"]))
    convergence = analyze_matrix_convergence(raw_results)
    metric_names = (
        "transfer_A_to_B", "transfer_B_to_A", "conditional_phase_iSWAP_rad",
        "projected_process_overlap_after_local_Z",
        "average_logical_fidelity_including_leakage",
    )
    grids = [r["steps_per_period"] for r in raw_results]
    richardson = {}
    for name in metric_names:
        values = {r["steps_per_period"]: float(r[name]) for r in raw_results}
        richardson[name] = richardson_extrapolate(values)

    _write_matrix_archive(matrix_path, raw_results)
    json_results = _summary_rows(raw_results)
    payload = {
        "stage": 5,
        "status": "reconstructed_full_matrix_phase_convergence_audit",
        "hardware_ready": False,
        "model": {
            "basis": "charge-basis-calibrated fixed-DC local eigenbasis; product dimension 5x5x5",
            "logical_eigen_indices": model.logical_eigen_indices,
            "dc_flux_Phi0": model.flux_dc_Phi0,
            "propagator": "symmetric Strang split; static H half steps and exact 5x5 local coupler drive exponential",
            "frequency_units": "MHz",
            "time_units": "microseconds",
            "flux_units": "Phi0",
        },
        "pulse": {
            "pump_frequency_MHz": pulse.pump_frequency_MHz,
            "flux_amplitude_Phi0": pulse.flux_amplitude_Phi0,
            "requested_duration_us": pulse.duration_us,
            "ramp_periods": pulse.ramp_periods,
            "envelope": "raised_cosine",
        },
        "grid_results": json_results,
        "matrix_convergence": convergence,
        "second_order_richardson_extrapolation": richardson,
        "matrix_archive": matrix_path.name,
        "conditional_phase_definition": (
            "wrap(arg(U00)+arg(U33)-arg(U21)-arg(U12)+pi); invariant under independent local Z and global phases"
        ),
        "limitations": [
            "closed-system simulation only",
            "no T1/T2, thermal bath, flux-line transfer, crosstalk or calibration noise",
            "capacitance and SQUID parameters remain declared assumptions, not extracted layout values",
            "sampled peak coupler/leakage values depend on track_stride",
        ],
    }
    _write_json_atomic(json_path, payload)

    lines = [
        "# Stage 5 — full logical-matrix convergence",
        "",
        "This is a reproducible closed-system calculation, not a hardware qualification.",
        "",
        f"- Pump: {pulse.pump_frequency_MHz:.12f} MHz",
        f"- Flux amplitude: {pulse.flux_amplitude_Phi0:.8f} Phi0",
        f"- Requested duration: {pulse.duration_us:.12f} us",
        f"- Time grids: {', '.join(map(str, grids))} steps per pump period",
        "",
        "| Grid | A→B transfer | Process overlap after local Z | Conditional phase (rad) | Logical unitarity defect |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in raw_results:
        lines.append(
            f"| {r['steps_per_period']} | {r['transfer_A_to_B']:.12f} | "
            f"{r['projected_process_overlap_after_local_Z']:.12f} | "
            f"{r['conditional_phase_iSWAP_rad']:.10g} | "
            f"{r['logical_unitarity_defect_frobenius']:.3e} |"
        )
    lines += ["", "## Full matrix comparison", ""]
    for p in convergence["adjacent_grid_comparisons"]:
        lines.append(
            f"- {p['coarse_steps_per_period']}→{p['fine_steps_per_period']}: "
            f"raw Frobenius `{p['raw_frobenius_difference']:.10g}`, "
            f"after independent local-Z/global phase alignment "
            f"`{p['phase_aligned_frobenius_difference']:.10g}`, "
            f"max element `{p['phase_aligned_max_element_difference']:.10g}`."
        )
    lines += ["", "## Richardson estimates", ""]
    for key, value in richardson.items():
        lines.append(f"- {key}: {value if value is not None else 'not available'}")
    lines += [
        "", "## Evidence boundary", "",
        "No experimental gate fidelity is claimed. The source circuit remains a nominal assumption set. "
        "Open-system, flux-line, calibration, fabrication and spectator-channel effects remain outstanding.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for checkpoint_path in (checkpoint_json, checkpoint_matrix):
        checkpoint_path.unlink(missing_ok=True)

    print("Saved:", json_path)
    print("Saved:", matrix_path)
    print("Saved:", md_path)
    print("iSWAP conditional phase (finest grid):",
          conditional_phase_invariant(raw_results[-1]["logical_matrix"]), "rad")


if __name__ == "__main__":
    main()
