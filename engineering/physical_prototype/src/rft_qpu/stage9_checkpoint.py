"""Strict-but-portable compatibility checks for Stage 9 resume checkpoints.

User-controlled physical inputs and discrete grids must match exactly. Derived
floating-point diagnostics are compared with tight tolerances because LAPACK,
BLAS and platform implementations can differ by a few ulps.
"""
from __future__ import annotations

import math
from typing import Any

EXACT_FIELDS = (
    "bias_offset_Phi0",
    "pump_offset_from_static_kHz",
    "amplitude_Phi0",
    "requested_duration_us",
    "ramp_periods",
    "steps_per_period",
    "steps_by_grid",
)

# Per-field tolerances are deliberately tight. In particular, pulse duration
# is much more tightly bounded than eigensolver-derived spectral diagnostics.
DERIVED_TOLERANCES = {
    "bias_flux_Phi0": (1e-10, 1e-11),
    "static_ZZ_MHz": (1e-9, 1e-11),
    "static_AB_detuning_MHz": (1e-9, 1e-10),
    "pump_frequency_MHz": (1e-9, 1e-10),
    "actual_shared_duration_us": (1e-13, 1e-13),
    "minimum_bare_overlap": (1e-10, 1e-11),
}


def checkpoint_config_differences(saved: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Describe incompatible resume settings; return [] when safe to resume.

    Explicit physical controls and temporal-grid definitions are exact-match
    requirements. Only derived floating-point values tolerate numerical noise.
    Unknown or missing fields are rejected rather than silently ignored.
    """
    differences: list[str] = []
    all_fields = set(saved) | set(current)
    known_fields = set(EXACT_FIELDS) | set(DERIVED_TOLERANCES)
    for field in sorted(all_fields - known_fields):
        if saved.get(field) != current.get(field):
            differences.append(f"{field}: unknown/mismatched field")
    for field in EXACT_FIELDS:
        if field not in saved or field not in current:
            differences.append(f"{field}: missing from saved or current configuration")
        elif saved[field] != current[field]:
            differences.append(f"{field}: saved={saved[field]!r}, current={current[field]!r}")
    for field, (rel_tol, abs_tol) in DERIVED_TOLERANCES.items():
        if field not in saved or field not in current:
            differences.append(f"{field}: missing from saved or current configuration")
            continue
        try:
            a, b = float(saved[field]), float(current[field])
        except (TypeError, ValueError):
            differences.append(f"{field}: non-numeric derived value")
            continue
        if not (math.isfinite(a) and math.isfinite(b)):
            differences.append(f"{field}: non-finite derived value")
        elif not math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol):
            differences.append(
                f"{field}: saved={a:.17g}, current={b:.17g}, "
                f"allowed abs/rel={abs_tol:g}/{rel_tol:g}"
            )
    return differences
