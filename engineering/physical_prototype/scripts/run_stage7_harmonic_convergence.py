#!/usr/bin/env python3
"""Converge one Stage-7 second-harmonic flux waveform on a shared duration.

Each completed grid is checkpointed. If interrupted, rerun with --resume and
identical physical/grid arguments; already completed grids are not repeated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "engineering" / "physical_prototype" / "src"
sys.path.insert(0, str(SRC))

from rft_qpu.stage5_gate import build_fixed_basis_model, fit_local_z_between_matrices  # noqa: E402
from rft_qpu.stage6_gate import choose_common_grid_duration  # noqa: E402
from rft_qpu.stage7_waveform import run_harmonic_shaping_candidate  # noqa: E402


def wrap_phase(x: float) -> float:
    return float(np.angle(np.exp(1j * x)))


def atomic_json(path: Path, payload: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def atomic_npz(path: Path, matrices: dict[str, np.ndarray]) -> None:
    tmp = path.with_name(path.stem + ".tmp" + path.suffix)
    with tmp.open("wb") as handle:
        np.savez_compressed(handle, **matrices)
    tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frequency-MHz", type=float, default=987.5136797993163)
    parser.add_argument("--fundamental-amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.0625675587737073)
    parser.add_argument("--second-harmonic-cos-Phi0", type=float, default=0.0002)
    parser.add_argument("--second-harmonic-sin-Phi0", type=float, default=0.0)
    parser.add_argument("--steps-per-period", nargs="+", type=int, default=[120, 240, 480])
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "engineering/physical_prototype/results")
    parser.add_argument("--prefix", default="stage7_harmonic_convergence")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-grids", type=int, default=None)
    args = parser.parse_args()

    grids = sorted(args.steps_per_period)
    if not grids or any(g < 8 for g in grids) or len(set(grids)) != len(grids):
        parser.error("--steps-per-period must contain unique integers >= 8")
    if args.max_new_grids is not None and args.max_new_grids < 1:
        parser.error("--max-new-grids must be positive")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    md_path = args.output_dir / f"{args.prefix}.md"
    npz_path = args.output_dir / f"{args.prefix}_matrices.npz"
    checkpoint_json = args.output_dir / f"{args.prefix}.checkpoint.json"
    checkpoint_npz = args.output_dir / f"{args.prefix}.checkpoint_matrices.npz"

    common = choose_common_grid_duration(args.frequency_MHz, args.duration_us, grids)
    config = {
        "frequency_MHz": args.frequency_MHz,
        "fundamental_amplitude_Phi0": args.fundamental_amplitude_Phi0,
        "second_harmonic_cos_Phi0": args.second_harmonic_cos_Phi0,
        "second_harmonic_sin_Phi0": args.second_harmonic_sin_Phi0,
        "requested_duration_us": args.duration_us,
        "actual_shared_duration_us": common.actual_duration_us,
        "steps_per_period": grids,
        "step_counts": {str(k): v for k, v in common.steps_by_grid.items()},
    }
    results: list[dict] = []
    matrices: dict[str, np.ndarray] = {}
    if checkpoint_json.exists():
        if not args.resume:
            parser.error(f"checkpoint exists: {checkpoint_json}; pass --resume or use another prefix")
        saved = json.loads(checkpoint_json.read_text(encoding="utf-8"))
        if saved.get("run_config") != config:
            parser.error("checkpoint configuration differs from this run")
        results = list(saved.get("grid_results", []))
        if not checkpoint_npz.exists():
            parser.error("checkpoint matrix archive is missing")
        with np.load(checkpoint_npz) as archive:
            matrices = {k: archive[k].copy() for k in archive.files}
        expected = {f"logical_matrix_steps_{int(r['steps_per_period'])}" for r in results}
        if expected != set(matrices):
            parser.error("checkpoint grid results and matrices do not match")
        print(f"Resuming {len(results)}/{len(grids)} completed grids", flush=True)
    elif args.resume:
        parser.error("--resume requested but no checkpoint exists")

    completed = {int(r["steps_per_period"]) for r in results}
    model = build_fixed_basis_model(charge_cutoff=10, levels_kept=5)
    processed = 0
    for spp in grids:
        if spp in completed:
            continue
        result = run_harmonic_shaping_candidate(
            args.second_harmonic_cos_Phi0,
            args.second_harmonic_sin_Phi0,
            frequency_MHz=args.frequency_MHz,
            fundamental_amplitude_Phi0=args.fundamental_amplitude_Phi0,
            duration_us=common.actual_duration_us,
            steps_per_period=spp,
            model=model,
        )
        matrix = result.pop("logical_matrix")
        if abs(result["actual_duration_us"] - common.actual_duration_us) > 1e-13:
            raise ArithmeticError("actual duration differs from shared duration")
        matrices[f"logical_matrix_steps_{spp}"] = matrix
        results.append(result)
        completed.add(spp)
        processed += 1
        atomic_npz(checkpoint_npz, matrices)
        atomic_json(checkpoint_json, {
            "stage": 7,
            "status": "in_progress_resumable_checkpoint",
            "run_config": config,
            "completed_grids": sorted(completed),
            "grid_results": results,
            "matrices_archive": checkpoint_npz.name,
        })
        print(
            f"[{len(completed)}/{len(grids)}] {spp} steps/period: "
            f"A->B={result['A_to_B_transfer']:.12f}, "
            f"Fproc={result['process_overlap_after_local_Z']:.12f}, "
            f"phi={result['conditional_phase_rad']:+.10f} rad, "
            f"T={result['actual_duration_us']:.15f} us [checkpoint saved]",
            flush=True,
        )
        if args.max_new_grids is not None and processed >= args.max_new_grids and len(completed) < len(grids):
            print("Grid chunk completed; rerun with --resume and identical parameters.", flush=True)
            return

    results.sort(key=lambda r: int(r["steps_per_period"]))
    comparisons = []
    for coarse, fine in zip(results[:-1], results[1:]):
        left = matrices[f"logical_matrix_steps_{coarse['steps_per_period']}"]
        right = matrices[f"logical_matrix_steps_{fine['steps_per_period']}"]
        aligned = fit_local_z_between_matrices(left, right)
        comparisons.append({
            "coarse_steps_per_period": coarse["steps_per_period"],
            "fine_steps_per_period": fine["steps_per_period"],
            "raw_frobenius_difference": aligned["raw_frobenius_difference"],
            "phase_aligned_frobenius_difference": aligned["phase_aligned_frobenius_difference"],
            "phase_aligned_max_element_difference": aligned["phase_aligned_max_element_difference"],
            "conditional_phase_difference_rad": wrap_phase(
                coarse["conditional_phase_rad"] - fine["conditional_phase_rad"]
            ),
            "phase_fit_rad_global_outA_outB_inA_inB": aligned[
                "phase_parameters_rad_global_outA_outB_inA_inB"
            ],
        })

    values = {int(r["steps_per_period"]): float(r["conditional_phase_rad"]) for r in results}
    richardson = None
    if len(grids) == 3 and grids[1] == 2 * grids[0] and grids[2] == 4 * grids[0]:
        richardson = float(values[grids[2]] + (values[grids[2]] - values[grids[1]]) / 3.0)

    payload = {
        "stage": 7,
        "status": "second_harmonic_candidate_common_duration_convergence_complete",
        "hardware_ready": False,
        "model": "125-dimensional circuit-derived fixed-DC-basis closed-system propagator",
        "waveform": "Phi=Phi_DC+env*(A1*cos(wt)+A2c*cos(2wt)+A2s*sin(2wt))",
        "parameters": config,
        "grid_results": results,
        "adjacent_grid_matrix_comparisons": comparisons,
        "richardson_conditional_phase_rad_second_order": richardson,
        "matrices_archive": npz_path.name,
        "limitations": [
            "closed-system model only; no dissipation, T1/T2 or thermal bath",
            "nominal circuit parameters are assumptions, not layout extracted",
            "second-harmonic flux control is idealized; actuator bandwidth and transfer function omitted",
            "sampled transient leakage and coupler population may under-resolve extrema",
        ],
    }
    atomic_npz(npz_path, matrices)
    atomic_json(json_path, payload)

    lines = [
        "# Stage 7 harmonic waveform convergence",
        "",
        f"- Frequency: {args.frequency_MHz:.12f} MHz",
        f"- Fundamental amplitude: {args.fundamental_amplitude_Phi0:.9f} Phi0",
        f"- Second harmonic (cos, sin): ({args.second_harmonic_cos_Phi0:+.9f}, {args.second_harmonic_sin_Phi0:+.9f}) Phi0",
        f"- Shared physical duration: {common.actual_duration_us:.15f} us",
        "",
        "| Steps/period | Transfer A->B | Process overlap | Conditional phase (rad) | Final leakage |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['steps_per_period']} | {r['A_to_B_transfer']:.12f} | "
            f"{r['process_overlap_after_local_Z']:.12f} | {r['conditional_phase_rad']:.10f} | "
            f"{r['final_max_logical_leakage']:.3e} |"
        )
    lines += ["", "## Full-matrix comparison", ""]
    for c in comparisons:
        lines.append(
            f"- {c['coarse_steps_per_period']} -> {c['fine_steps_per_period']}: raw Frobenius "
            f"{c['raw_frobenius_difference']:.6e}; phase-aligned Frobenius "
            f"{c['phase_aligned_frobenius_difference']:.6e}; max element "
            f"{c['phase_aligned_max_element_difference']:.6e}; conditional-phase difference "
            f"{c['conditional_phase_difference_rad']:.6e} rad"
        )
    lines += ["", f"Second-order Richardson phase estimate: {richardson}", "",
              "This is a closed-system model result, not an experimental gate fidelity or hardware release signoff.", ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    for p in (checkpoint_json, checkpoint_npz):
        p.unlink(missing_ok=True)
    print("Saved:", json_path, md_path, npz_path, flush=True)


if __name__ == "__main__":
    main()
