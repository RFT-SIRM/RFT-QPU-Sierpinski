#!/usr/bin/env python3
"""Reproduce the static charge-basis three-node SQUID-coupler study."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

from rft_qpu.circuit_quantization import CircuitParameters, analyze_circuit_point, scan_capacitances


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/three_node_circuit_static_stage3.json"))
    parser.add_argument("--scan", action="store_true", help="include the 36-point mutual-capacitance scan")
    parser.add_argument("--c-ac-fF", type=float, default=0.70)
    parser.add_argument("--c-cb-fF", type=float, default=0.75)
    parser.add_argument("--c-ab-fF", type=float, default=0.03)
    parser.add_argument("--charge-cutoff", type=int, default=8)
    parser.add_argument("--levels-kept", type=int, default=3)
    args = parser.parse_args()

    params = CircuitParameters(
        c_ac_fF=args.c_ac_fF,
        c_cb_fF=args.c_cb_fF,
        c_ab_fF=args.c_ab_fF,
        charge_cutoff=args.charge_cutoff,
        levels_kept=args.levels_kept,
    )
    nominal = analyze_circuit_point(params)
    scan = scan_capacitances(params) if args.scan else []
    report = {
        "title": "Circuit-quantized three-node static model — Stage 3",
        "model_boundary": (
            "Charge-basis quantization of three capacitively coupled Josephson modes with an asymmetric SQUID coupler. "
            "Capacitances and Josephson energies are declared assumptions, not extracted layout values. "
            "No driven-gate fidelity, dissipation, flux-line transfer, or fabrication disorder is included."
        ),
        "nominal_assumptions": {
            "target_frequencies_MHz": list(params.target_frequencies_MHz),
            "nominal_EC_MHz": list(params.nominal_EC_MHz),
            "C_AC_fF": params.c_ac_fF,
            "C_CB_fF": params.c_cb_fF,
            "C_AB_parasitic_fF": params.c_ab_fF,
            "EJ_C_sum_over_h_MHz": params.ej_c_sum_MHz,
            "SQUID_asymmetry": params.squid_asymmetry,
        },
        "nominal_point": nominal,
        "capacitance_scan": scan,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    csv_path = args.output.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        rows = scan or [{
            "C_AC_fF": params.c_ac_fF,
            "C_CB_fF": params.c_cb_fF,
            "g_AC_01_MHz": nominal["derived_exchange_matrix_elements_MHz"]["g_AC_01"],
            "g_CB_01_MHz": nominal["derived_exchange_matrix_elements_MHz"]["g_CB_01"],
            "g_AB_direct_01_MHz": nominal["derived_exchange_matrix_elements_MHz"]["g_AB_direct_01"],
            "dressed_A_B_detuning_MHz": nominal["dressed_static_spectrum_MHz"]["dressed_A_B_detuning_MHz"],
            "residual_static_ZZ_MHz": nominal["dressed_static_spectrum_MHz"]["residual_static_ZZ_MHz"],
            "minimum_bare_product_overlap": min(x["bare_product_overlap"] for x in nominal["dressed_static_spectrum_MHz"]["tracked_states"].values()),
        }]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    modes = nominal["isolated_local_modes"]
    derived = nominal["derived_exchange_matrix_elements_MHz"]
    dressed = nominal["dressed_static_spectrum_MHz"]
    print(json.dumps({
        "output": str(args.output),
        "csv": str(csv_path),
        "scan_points": len(scan),
        "computed_f01_MHz": modes["computed_f01_MHz"],
        "anharmonicity_MHz": modes["anharmonicity_MHz"],
        "squid_dc_flux_Phi0": modes["SQUID_DC_flux_Phi0"],
        "g_AC_01_MHz": derived["g_AC_01"],
        "g_CB_01_MHz": derived["g_CB_01"],
        "g_AB_direct_01_MHz": derived["g_AB_direct_01"],
        "dressed_AB_detuning_MHz": dressed["dressed_A_B_detuning_MHz"],
        "residual_static_ZZ_MHz": dressed["residual_static_ZZ_MHz"],
        "model_boundary": report["model_boundary"],
    }, indent=2))


if __name__ == "__main__":
    main()
