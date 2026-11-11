#!/usr/bin/env python3
"""Run the Stage 11A local SQUID-coupler re-quantization audit."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from rft_qpu.circuit_quantization import CircuitParameters
from rft_qpu.stage11_requantization import analyze_bias_requantization


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage3-report", type=Path,
        default=Path("engineering/physical_prototype/results/three_node_circuit_static_stage3.json"),
    )
    parser.add_argument("--bias-offset-Phi0", type=float, default=-0.0075)
    parser.add_argument("--charge-cutoffs", nargs="+", type=int, default=[8, 10, 12])
    parser.add_argument("--levels-kept", nargs="+", type=int, default=[3, 4, 5])
    parser.add_argument("--output-dir", type=Path, default=Path("engineering/physical_prototype/results"))
    parser.add_argument("--prefix", default="stage11_local_coupler_requantization")
    args = parser.parse_args()

    raw = json.loads(args.stage3_report.read_text(encoding="utf-8"))
    assumptions = raw["nominal_assumptions"]
    nominal = raw["nominal_point"]
    base_flux = float(nominal["isolated_local_modes"]["SQUID_DC_flux_Phi0"])
    params = CircuitParameters(
        target_frequencies_MHz=tuple(assumptions["target_frequencies_MHz"]),
        nominal_EC_MHz=tuple(assumptions["nominal_EC_MHz"]),
        c_ac_fF=float(assumptions["C_AC_fF"]),
        c_cb_fF=float(assumptions["C_CB_fF"]),
        c_ab_fF=float(assumptions["C_AB_parasitic_fF"]),
        ej_c_sum_MHz=float(assumptions["EJ_C_sum_over_h_MHz"]),
        squid_asymmetry=float(assumptions["SQUID_asymmetry"]),
        charge_cutoff=max(args.charge_cutoffs),
        levels_kept=max(args.levels_kept),
    )

    report, arrays = analyze_bias_requantization(
        params,
        base_flux_Phi0=base_flux,
        bias_offset_Phi0=args.bias_offset_Phi0,
        charge_cutoffs=args.charge_cutoffs,
        levels_kept=args.levels_kept,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.prefix}.json"
    csv_path = args.output_dir / f"{args.prefix}.csv"
    npz_path = args.output_dir / f"{args.prefix}_matrices.npz"
    md_path = args.output_dir / f"{args.prefix}.md"

    json_path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(report["rows"][0]))
        writer.writeheader()
        writer.writerows(report["rows"])
    np.savez_compressed(npz_path, **arrays)

    lines = [
        "# Stage 11A — local SQUID-coupler re-quantization",
        "",
        f"- Base flux: `{report['base_flux_Phi0']:.15f} Phi0`",
        f"- Bias offset: `{report['bias_offset_Phi0']:+.8f} Phi0`",
        f"- Re-quantized flux: `{report['shifted_flux_Phi0']:.15f} Phi0`",
        f"- Charge cutoffs: `{report['charge_cutoffs']}`",
        f"- Retained local levels: `{report['levels_kept']}`",
        "",
        "| Cutoff | Levels | old f01 (MHz) | new f01 (MHz) | Δf01 (MHz) | min state overlap | min subspace σ | Δ|n01| |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['charge_cutoff']} | {row['levels_kept']} | {row['old_f01_MHz']:.9f} "
            f"| {row['new_f01_MHz']:.9f} | {row['delta_f01_MHz']:+.9f} "
            f"| {row['minimum_state_overlap_probability']:.9f} "
            f"| {row['minimum_retained_subspace_singular_value']:.9f} "
            f"| {row['delta_abs_n01']:+.9e} |"
        )
    lines += [
        "",
        "## Scope and limitations",
        report["model_boundary"],
        "",
        "The aligned operator matrices and overlap matrices are in the companion NPZ. This audit is a prerequisite "
        "to, not a substitute for, rebuilding and converging the full driven three-mode logical gate in the new basis.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Base flux: {base_flux:.15f} Phi0")
    print(f"Shifted flux: {report['shifted_flux_Phi0']:.15f} Phi0")
    for row in report["rows"]:
        if row["levels_kept"] == max(args.levels_kept):
            print(
                f"cutoff={row['charge_cutoff']} levels={row['levels_kept']} "
                f"f01: {row['old_f01_MHz']:.9f}->{row['new_f01_MHz']:.9f} MHz "
                f"min_overlap={row['minimum_state_overlap_probability']:.9f} "
                f"min_subspace_sigma={row['minimum_retained_subspace_singular_value']:.9f}"
            )
    print("Saved:", json_path, csv_path, npz_path, md_path)


if __name__ == "__main__":
    main()
