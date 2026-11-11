#!/usr/bin/env python3
"""High-resolution common-duration convergence for a shifted-SQUID-bias gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "engineering/physical_prototype/src"))

from rft_qpu.stage5_gate import (  # noqa: E402
    GatePulse,
    analyze_matrix_convergence,
    build_fixed_basis_model,
    propagate_gate,
    richardson_extrapolate,
)
from rft_qpu.stage6_gate import choose_common_grid_duration  # noqa: E402
from rft_qpu.stage9_bias import build_bias_shifted_model  # noqa: E402
from rft_qpu.stage9_checkpoint import checkpoint_config_differences  # noqa: E402

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
    parser.add_argument("--bias-offset-Phi0", type=float, required=True)
    parser.add_argument("--pump-offset-from-static-kHz", type=float, required=True)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, required=True)
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--steps-per-period", nargs="+", type=int, default=[120, 240, 480])
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage9_bias_convergence")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-grids", type=int, default=None)
    args = parser.parse_args()

    if args.duration_us <= 0 or args.amplitude_Phi0 < 0 or args.ramp_periods < 0:
        parser.error("invalid duration, amplitude or ramp")
    if len(args.steps_per_period) < 3 or len(set(args.steps_per_period)) != len(args.steps_per_period):
        parser.error("provide at least three unique temporal grids")
    if args.max_new_grids is not None and args.max_new_grids < 1:
        parser.error("--max-new-grids must be positive")

    base = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    shifted = build_bias_shifted_model(base, args.bias_offset_Phi0)
    pump_frequency = shifted.dressed_AB_detuning_MHz + args.pump_offset_from_static_kHz * 1e-3
    common = choose_common_grid_duration(
        pump_frequency, args.duration_us, args.steps_per_period
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    md_path = args.output_dir / f"{args.prefix}.md"
    matrix_path = args.output_dir / f"{args.prefix}_matrices.npz"
    cp_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    cp_npz = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"
    config = {
        "bias_offset_Phi0": args.bias_offset_Phi0,
        "bias_flux_Phi0": shifted.bias_flux_Phi0,
        "static_ZZ_MHz": shifted.static_ZZ_MHz,
        "static_AB_detuning_MHz": shifted.dressed_AB_detuning_MHz,
        "pump_offset_from_static_kHz": args.pump_offset_from_static_kHz,
        "pump_frequency_MHz": pump_frequency,
        "amplitude_Phi0": args.amplitude_Phi0,
        "requested_duration_us": args.duration_us,
        "actual_shared_duration_us": common.actual_duration_us,
        "ramp_periods": args.ramp_periods,
        "steps_per_period": list(args.steps_per_period),
        "steps_by_grid": {str(k): v for k, v in common.steps_by_grid.items()},
        "minimum_bare_overlap": shifted.minimum_bare_overlap,
    }
    rows: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if cp_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {cp_json}; pass --resume or use another prefix")
        saved = json.loads(cp_json.read_text(encoding="utf-8"))
        differences = checkpoint_config_differences(saved.get("run_config", {}), config)
        if differences:
            detail = "\n  - ".join(differences)
            parser.error("checkpoint configuration differs beyond safe resume tolerances:\n  - " + detail)
        else:
            print("Checkpoint configuration verified (exact physical inputs; derived values within tight numeric tolerances).", flush=True)
        rows = list(saved["grid_results"])
        if not cp_npz.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(cp_npz) as data:
            matrices = {k: data[k].copy() for k in data.files}
        if {str(r["steps_per_period"]) for r in rows} != set(matrices):
            parser.error("checkpoint grids and matrices differ")
        print(f"Resuming {len(rows)}/{len(args.steps_per_period)} grids", flush=True)
    elif args.resume:
        parser.error("--resume requested without checkpoint")

    with threadpool_limits(limits=1):
        processed = 0
        for spp in args.steps_per_period:
            key = str(spp)
            if key in matrices:
                continue
            pulse = GatePulse(
                pump_frequency_MHz=pump_frequency,
                flux_amplitude_Phi0=args.amplitude_Phi0,
                duration_us=common.actual_duration_us,
                ramp_periods=args.ramp_periods,
            )
            result = propagate_gate(
                shifted.model, pulse, spp, track_stride=max(1, spp // 24)
            )
            matrix = result.pop("logical_matrix")
            result.pop("phase_corrected_matrix", None)
            result["steps_by_common_duration_grid"] = common.steps_by_grid[spp]
            rows.append(result)
            matrices[key] = matrix
            processed += 1
            tmp_npz = cp_npz.with_suffix(".tmp.npz")
            np.savez_compressed(tmp_npz, **matrices)
            tmp_npz.replace(cp_npz)
            atomic_json(cp_json, {
                "stage": 9, "status": "in_progress_resumable_checkpoint",
                "run_config": config, "grid_results": rows,
                "completed_grids": len(rows),
            })
            print(
                f"[{len(rows)}/{len(args.steps_per_period)}] {spp} steps/period "
                f"F={result['projected_process_overlap_after_local_Z']:.12f} "
                f"AB={result['transfer_A_to_B']:.12f} BA={result['transfer_B_to_A']:.12f} "
                f"phi={result['conditional_phase_iSWAP_rad']:+.10f} rad "
                f"T={result['actual_duration_us']:.15f} us [checkpoint]",
                flush=True,
            )
            if args.max_new_grids is not None and processed >= args.max_new_grids and len(rows) < len(args.steps_per_period):
                print("Chunk completed; rerun with --resume and identical arguments", flush=True)
                return

    rows.sort(key=lambda r: r["steps_per_period"])
    matrix_rows = [
        {"steps_per_period": r["steps_per_period"], "logical_matrix": matrices[str(r["steps_per_period"])]}
        for r in rows
    ]
    conv = analyze_matrix_convergence(matrix_rows)["adjacent_grid_comparisons"]
    phases = {int(r["steps_per_period"]): float(r["conditional_phase_iSWAP_rad"]) for r in rows}
    payload = {
        "stage": 9,
        "status": "bias_shifted_full_gate_common_duration_convergence_complete",
        "hardware_ready": False,
        "model": "125-dimensional fixed-local-basis circuit-derived closed-system Strang propagator",
        "parameters": config,
        "grid_results": rows,
        "adjacent_grid_matrix_comparisons": conv,
        "richardson_conditional_phase_rad_second_order": richardson_extrapolate(phases),
        "matrices_archive": matrix_path.name,
        "limitations": [
            "DC bias shift is projected into the retained Stage-5 local 5-level coupler basis",
            "common physical duration is enforced across grids",
            "transient extrema are sampled rather than proven continuous-time extrema",
            "no measured flux-line transfer function, bandwidth, delay, distortion or crosstalk",
            "closed-system only; no T1/T2 or thermal bath",
            "nominal capacitances and SQUID parameters remain assumptions, not layout extraction",
        ],
    }
    atomic_json(json_path, payload)
    md = [
        "# Stage 9 — bias-shifted gate convergence", "",
        "Status: closed-system numerical convergence check, not hardware qualification.", "",
        f"Bias offset: {args.bias_offset_Phi0:+.7f} Phi0; absolute bias: {shifted.bias_flux_Phi0:.12f} Phi0.",
        f"Static ZZ: {shifted.static_ZZ_MHz:+.9f} MHz; static A-B detuning: {shifted.dressed_AB_detuning_MHz:.9f} MHz.",
        f"Pump: {pump_frequency:.12f} MHz; common pulse duration: {common.actual_duration_us:.15f} us.",
        f"Minimum tracked bare overlap: {shifted.minimum_bare_overlap:.9f}.", "",
        "| Grid | A→B | B→A | Process overlap | Conditional phase (rad) | Final leakage max | Coupler sampled max |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['steps_per_period']} | {r['transfer_A_to_B']:.12f} | {r['transfer_B_to_A']:.12f} "
            f"| {r['projected_process_overlap_after_local_Z']:.12f} | {r['conditional_phase_iSWAP_rad']:.10f} "
            f"| {max(r['final_logical_leakage_by_input']):.3e} | {max(r['max_coupler_excited_probability_sampled_by_input']):.6f} |"
        )
    md += ["", "## Full logical matrix convergence", ""]
    for p in conv:
        md.append(
            f"- {p['coarse_steps_per_period']}→{p['fine_steps_per_period']}: raw Frobenius "
            f"{p['raw_frobenius_difference']:.6e}; after local-Z frame alignment "
            f"{p['phase_aligned_frobenius_difference']:.6e}; max element "
            f"{p['phase_aligned_max_element_difference']:.6e}."
        )
    md += ["", f"Richardson conditional phase estimate: {payload['richardson_conditional_phase_rad_second_order']}", ""]
    md += ["## Limitations", "", *[f"- {x}" for x in payload["limitations"]], ""]
    md_path.write_text("\n".join(md), encoding="utf-8")
    tmp_npz = matrix_path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp_npz, **matrices)
    tmp_npz.replace(matrix_path)
    for p in (cp_json, cp_npz):
        p.unlink(missing_ok=True)
    print("Saved:", json_path, md_path, matrix_path, flush=True)
    print("Richardson phase:", payload["richardson_conditional_phase_rad_second_order"], flush=True)


if __name__ == "__main__":
    main()
