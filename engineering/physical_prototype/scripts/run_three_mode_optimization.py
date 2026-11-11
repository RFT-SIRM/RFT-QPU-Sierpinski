#!/usr/bin/env python3
"""Two-stage design-space scan for the effective three-mode coupler model."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from dataclasses import replace

from rft_qpu.three_mode_coupler import (
    ThreeModeParams,
    dynamic_gate_check,
    exact_sambe_exchange,
    find_resonant_pump_frequency,
    static_dressed_spectrum,
)

G_VALUES = (20.0, 25.0, 30.0, 35.0)
PUMP_AMPLITUDES_MHZ = (150.0, 200.0, 250.0, 300.0, 350.0, 400.0)
COUPLER_ANHARMONICITIES_MHZ = (-200.0, -300.0, -400.0)

# Selected points span the speed/leakage trade-off rather than assuming one
# scalar objective. The scan can be reproduced with --dynamic-limit 6.
DYNAMIC_CANDIDATES = (
    (20.0, 400.0),
    (25.0, 300.0),
    (25.0, 350.0),
    (25.0, 400.0),
    (30.0, 200.0),
    (30.0, 300.0),
)


def build_static_grid(base: ThreeModeParams | None = None) -> list[dict]:
    base = base or ThreeModeParams()
    rows: list[dict] = []
    for alpha_c in COUPLER_ANHARMONICITIES_MHZ:
        for g in G_VALUES:
            for pump_amplitude in PUMP_AMPLITUDES_MHZ:
                p = replace(
                    base,
                    g_ac_MHz=g,
                    g_cb_MHz=g,
                    pump_amplitude_MHz=pump_amplitude,
                    alpha_c_MHz=alpha_c,
                    sambe_order=4,
                )
                pump, _ = find_resonant_pump_frequency(
                    p, search_half_width_MHz=80.0, samples=41
                )
                exchange = exact_sambe_exchange(p, pump)
                static = static_dressed_spectrum(p)
                rows.append({
                    "g_ac_MHz": g,
                    "g_cb_MHz": g,
                    "pump_amplitude_MHz": pump_amplitude,
                    "alpha_c_MHz": alpha_c,
                    "pump_frequency_MHz": pump,
                    "J_eff_MHz": exchange["exact_sambe_exchange_MHz"],
                    "target_weight_min": min(exchange["quasienergy_pair_target_weight"]),
                    "static_ZZ_MHz": static["static_residual_ZZ_MHz"],
                    "bare_AB_overlap_N2": static["bare_state_overlap"]["AB_two_excitation"],
                })
    return rows


def run_dynamic_shortlist(
    base: ThreeModeParams | None = None,
    limit: int = len(DYNAMIC_CANDIDATES),
) -> list[dict]:
    base = base or ThreeModeParams()
    if limit < 0:
        raise ValueError("dynamic limit must be non-negative")
    rows: list[dict] = []
    for g, amplitude in DYNAMIC_CANDIDATES[:limit]:
        p = replace(
            base,
            g_ac_MHz=g,
            g_cb_MHz=g,
            pump_amplitude_MHz=amplitude,
            sambe_order=4,
        )
        pump, _ = find_resonant_pump_frequency(
            p, search_half_width_MHz=80.0, samples=81
        )
        exchange = exact_sambe_exchange(p, pump)
        static = static_dressed_spectrum(p)
        dynamic = dynamic_gate_check(p, pump)
        rows.append({
            "g_ac_MHz": g,
            "g_cb_MHz": g,
            "pump_amplitude_MHz": amplitude,
            "alpha_c_MHz": p.alpha_c_MHz,
            "pump_frequency_MHz": pump,
            "J_eff_MHz": exchange["exact_sambe_exchange_MHz"],
            "static_ZZ_MHz": static["static_residual_ZZ_MHz"],
            "N1_transfer_probability": dynamic["single_excitation_transfer_probability"],
            "N1_max_coupler_population": dynamic["single_excitation_max_coupler_population"],
            "N2_leakage_probability": dynamic["two_excitation_leakage_probability_at_swap"],
            "N2_coupler_population_at_swap": dynamic["two_excitation_coupler_population_at_swap"],
            "N2_high_level_population_at_swap": dynamic["two_excitation_high_level_population_at_swap"],
            "best_swap_time_ns": dynamic["best_dynamic_swap_time_us"] * 1000.0,
            "N2_logical_survival_probability": dynamic["two_excitation_logical_survival_probability"],
        })
    return rows



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/three_mode_optimization_stage2.json"),
    )
    parser.add_argument(
        "--dynamic-limit", type=int, default=6,
        help="number of shortlisted candidates for time-domain N=1/N=2 propagation",
    )
    parser.add_argument("--static-only", action="store_true", help="run only the 72-point static grid")
    args = parser.parse_args()

    static_rows = build_static_grid()
    dynamic_rows = [] if args.static_only else run_dynamic_shortlist(limit=args.dynamic_limit)
    report = {
        "title": "Three-mode effective coupler parameter scan — stage 2",
        "model": "three nonlinear Duffing modes with sinusoidal coupler-frequency modulation",
        "model_boundary": (
            "Exploratory effective model only. No capacitance matrix, Josephson/SQUID potential, "
            "flux-to-frequency calibration, dissipation, device yield, or measured transfer function is included."
        ),
        "units": {"frequency": "MHz", "time": "microseconds"},
        "scan": {
            "g_values_MHz": [20, 25, 30, 35],
            "pump_amplitudes_MHz": [150, 200, 250, 300, 350, 400],
            "coupler_anharmonicities_MHz": [-200, -300, -400],
            "static_grid_size": len(static_rows),
            "sambe_order": 4,
            "resonance_search_half_width_MHz": 80.0,
            "resonance_search_samples": 41,
        },
        "screening_thresholds_not_hardware_acceptance": {
            "N1_transfer_probability_min": 0.999,
            "N2_leakage_probability_max": 0.01,
            "N1_max_coupler_population_max": 0.02,
            "absolute_static_ZZ_MHz_max": 0.005,
        },
        "static_grid": static_rows,
        "dynamic_validation": dynamic_rows,
        "decision": (
            "No globally optimal or hardware-qualified point is claimed. The scan identifies a Pareto-like "
            "trade-off; the preferred point must be revisited with a circuit-quantized SQUID model and "
            "a flux-calibrated pulse waveform."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    csv_path = args.output.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        if static_rows:
            writer = csv.DictWriter(f, fieldnames=list(static_rows[0]))
            writer.writeheader()
            writer.writerows(static_rows)

    dynamic_csv_path = args.output.with_name(args.output.stem + "_dynamic.csv")
    with dynamic_csv_path.open("w", newline="", encoding="utf-8") as f:
        if dynamic_rows:
            writer = csv.DictWriter(f, fieldnames=list(dynamic_rows[0]))
            writer.writeheader()
            writer.writerows(dynamic_rows)

    print(json.dumps({
        "output": str(args.output),
        "static_csv": str(csv_path),
        "dynamic_csv": str(dynamic_csv_path),
        "static_candidates": len(static_rows),
        "dynamic_candidates": len(dynamic_rows),
        "best_J_eff_static_MHz": max(r["J_eff_MHz"] for r in static_rows),
        "model_boundary": report["model_boundary"],
    }, indent=2))


if __name__ == "__main__":
    main()
