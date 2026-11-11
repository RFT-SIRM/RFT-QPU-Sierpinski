#!/usr/bin/env python3
"""Run the first explicit three-mode nonlinear-coupler stress calculation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from rft_qpu.three_mode_coupler import ThreeModeParams, analyze_three_mode_coupler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/three_mode_coupler_stage1.json"))
    parser.add_argument("--g-MHz", type=float, default=100.0)
    parser.add_argument("--pump-amplitude-MHz", type=float, default=200.0)
    parser.add_argument("--coupler-offset-MHz", type=float, default=-492.5)
    parser.add_argument("--alpha-c-MHz", type=float, default=-300.0)
    parser.add_argument("--phase-deg", type=float, default=0.0)
    args = parser.parse_args()
    params = ThreeModeParams(
        f_a_MHz=0.0,
        f_c_MHz=args.coupler_offset_MHz,
        f_b_MHz=-985.0,
        g_ac_MHz=args.g_MHz,
        g_cb_MHz=args.g_MHz,
        pump_amplitude_MHz=args.pump_amplitude_MHz,
        alpha_c_MHz=args.alpha_c_MHz,
        pump_phase_rad=args.phase_deg * 3.141592653589793 / 180.0,
    )
    report = analyze_three_mode_coupler(params)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "bare_difference_MHz": report["resonance"]["bare_data_frequency_difference_MHz"],
        "dressed_pump_MHz": report["resonance"]["dressed_resonant_pump_frequency_MHz"],
        "J_eff_MHz": report["effective_exchange"]["exact_sambe_exchange_MHz"],
        "static_ZZ_MHz": report["static_spectrum"]["static_residual_ZZ_MHz"],
        "dynamic_transfer_probability": report["dynamic_gate_check"]["single_excitation_transfer_probability"],
        "dynamic_max_coupler_population": report["dynamic_gate_check"]["single_excitation_max_coupler_population"],
        "two_excitation_leakage": report["dynamic_gate_check"]["two_excitation_leakage_probability_at_swap"],
        "warning": report["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
