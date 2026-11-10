"""Command line entry point for reproducible prototype calculations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import analyze_level
from .disorder import run_disorder_study
from .hardware import write_hardware_package
from .thermal import (
    boltzmann_factor,
    gap_frequency_MHz,
    required_J_for_population,
    thermal_frequency_MHz,
)


def build_report(level: int, J_MHz: float, temperature_mK: float, disorder_samples: int) -> dict:
    analysis = analyze_level(level)
    gap_mhz = gap_frequency_MHz(analysis["leakage_gap_over_J"], J_MHz)
    analysis["physical_scale_assumption"] = {
        "J_over_2pi_MHz": J_MHz,
        "leakage_gap_over_2pi_MHz": gap_mhz,
        "temperature_mK": temperature_mK,
        "kBT_over_h_MHz": thermal_frequency_MHz(temperature_mK),
        "equilibrium_boltzmann_factor_benchmark": boltzmann_factor(gap_mhz, temperature_mK),
        "J_over_2pi_MHz_for_1pct_boltzmann_benchmark": required_J_for_population(analysis["leakage_gap_over_J"], temperature_mK, 0.01),
        "warning": "Boltzmann factor is a thermal-scale diagnostic, not a measured chip population or a full bath-coupling model.",
    }
    analysis["disorder_study"] = run_disorder_study(level, samples=disorder_samples)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an RFT-SG spinor qubit cell")
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--J-MHz", type=float, default=10.0, help="J/(2 pi) in MHz")
    parser.add_argument("--temperature-mK", type=float, default=10.0)
    parser.add_argument("--disorder-samples", type=int, default=250)
    parser.add_argument("--output", type=Path, default=Path("results/prototype_report.json"))
    parser.add_argument("--hardware-dir", type=Path, default=Path("hardware/generated"))
    args = parser.parse_args()

    report = build_report(args.level, args.J_MHz, args.temperature_mK, args.disorder_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_hardware_package(args.hardware_dir, args.level, J_over_2pi_MHz=args.J_MHz)
    print(json.dumps({
        "level": report["level"],
        "physical_transmons": report["n_modes"],
        "leakage_gap_over_J": report["leakage_gap_over_J"],
        "ground_doublet_splitting_over_J": report["ground_doublet_splitting_over_J"],
        "best_local_control_vertex": report["best_local_control"]["vertex"],
        "best_local_control_g_eff": report["best_local_control"]["g_eff"],
        "global_control_g_eff": report["global_control"]["g_eff"],
        "thermal_benchmark": report["physical_scale_assumption"],
        "report": str(args.output),
        "hardware_dir": str(args.hardware_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
