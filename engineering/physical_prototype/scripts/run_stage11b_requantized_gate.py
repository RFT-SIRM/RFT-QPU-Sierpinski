"""Run the initial Stage-11B gate in the re-quantized coupler basis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from rft_qpu.stage5_gate import (
    GatePulse,
    analyze_matrix_convergence,
    propagate_gate,
    richardson_extrapolate,
)
from rft_qpu.stage11b_requantization import build_requantized_model


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--charge-cutoff", type=int, default=10)
    parser.add_argument("--levels-kept", type=int, default=5)
    parser.add_argument("--bias-flux-Phi0", type=float, default=0.25934367625232047)
    parser.add_argument("--pump-frequency-MHz", type=float, default=987.6092214991908)
    parser.add_argument("--amplitude-Phi0", type=float, default=0.020)
    parser.add_argument("--duration-us", type=float, default=1.081)
    parser.add_argument("--ramp-periods", type=float, default=8.0)
    parser.add_argument("--grids", nargs="+", type=int, default=[120, 240, 480])
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "results",
    )
    parser.add_argument("--output-stem", default="stage11b_requantized_gate")
    args = parser.parse_args()

    if sorted(set(args.grids)) != sorted(args.grids) or len(args.grids) < 2:
        raise SystemExit("--grids must be unique and in increasing order")

    built = build_requantized_model(
        charge_cutoff=args.charge_cutoff,
        levels_kept=args.levels_kept,
        bias_flux_Phi0=args.bias_flux_Phi0,
    )
    pulse = GatePulse(
        pump_frequency_MHz=args.pump_frequency_MHz,
        flux_amplitude_Phi0=args.amplitude_Phi0,
        duration_us=args.duration_us,
        ramp_periods=args.ramp_periods,
    )

    grid_results = []
    matrix_data: dict[str, np.ndarray] = {}
    for grid in args.grids:
        result = propagate_gate(built.model, pulse, grid)
        grid_results.append(result)
        matrix_data[f"logical_matrix_{grid}"] = result["logical_matrix"]
        matrix_data[f"phase_corrected_matrix_{grid}"] = result["phase_corrected_matrix"]

    args.results_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = args.results_dir / f"{args.output_stem}_matrices.npz"
    json_path = args.results_dir / f"{args.output_stem}.json"
    np.savez_compressed(matrix_path, **matrix_data)

    serial_results = [
        {
            key: value
            for key, value in result.items()
            if not isinstance(value, np.ndarray)
        }
        for result in grid_results
    ]
    convergence = analyze_matrix_convergence(grid_results)
    phase_by_grid = {
        int(row["steps_per_period"]): float(row["conditional_phase_iSWAP_rad"])
        for row in serial_results
    }
    report = {
        "stage": "11B",
        "status": "requantized_full_gate_convergence_complete",
        "model": built.diagnostics,
        "pulse": {
            "bias_flux_Phi0": args.bias_flux_Phi0,
            "pump_frequency_MHz": args.pump_frequency_MHz,
            "flux_amplitude_Phi0": args.amplitude_Phi0,
            "requested_duration_us": args.duration_us,
            "ramp_periods": args.ramp_periods,
            "steps_per_period": args.grids,
        },
        "grid_results": serial_results,
        "adjacent_grid_matrix_comparisons": convergence["adjacent_grid_comparisons"],
        "richardson_conditional_phase_rad_second_order": richardson_extrapolate(
            phase_by_grid
        ),
        "matrices_archive": matrix_path.name,
        "hardware_ready": False,
        "limitations": [
            "Nominal Stage-3 capacitances and Josephson parameters are assumptions, not layout extraction.",
            "Closed-system only; no T1/T2, thermal bath, flux-line transfer, phase noise, delay, distortion or crosstalk.",
            "Transient extrema are sampled, not bounded continuously in time.",
            "This runner evaluates the supplied pulse; robust Stage-11B retuning and uncertainty sweeps remain separate work.",
            "A full-gate charge-cutoff and retained-level convergence study remains open.",
            "Numerical model outputs are not measured gate fidelity or hardware qualification.",
        ],
    }
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved: {json_path}")
    print(f"Saved: {matrix_path}")
    print(json.dumps({
        "model": built.diagnostics,
        "grid_results": serial_results,
        "matrix_convergence": convergence,
        "richardson_conditional_phase_rad_second_order":
            report["richardson_conditional_phase_rad_second_order"],
    }, indent=2))


if __name__ == "__main__":
    main()
