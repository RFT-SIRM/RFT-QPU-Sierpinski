"""Convert dimensionless spectral separation into physical thermal scales."""
from __future__ import annotations
import math

# k_B/h in MHz/K.
KB_OVER_H_MHZ_PER_K = 20_836.619123


def gap_frequency_MHz(gap_over_J: float, J_over_2pi_MHz: float) -> float:
    return gap_over_J * J_over_2pi_MHz


def thermal_frequency_MHz(temperature_mK: float) -> float:
    if temperature_mK <= 0:
        raise ValueError("temperature must be positive")
    return KB_OVER_H_MHZ_PER_K * temperature_mK * 1e-3


def boltzmann_factor(gap_MHz: float, temperature_mK: float) -> float:
    if gap_MHz < 0:
        raise ValueError("gap must be nonnegative")
    return math.exp(-gap_MHz / thermal_frequency_MHz(temperature_mK))


def required_J_for_population(
    gap_over_J: float, temperature_mK: float, target_boltzmann_factor: float = 0.01
) -> float:
    """Return J/(2pi) in MHz needed for exp(-gap/kT) <= target.

    This is an equilibrium Boltzmann benchmark, not a prediction of actual
    chip occupation: actual transitions depend on bath coupling and spectral
    density and must be measured.
    """
    if gap_over_J <= 0:
        raise ValueError("gap_over_J must be positive")
    if not 0 < target_boltzmann_factor < 1:
        raise ValueError("target factor must lie strictly between 0 and 1")
    required_gap = -math.log(target_boltzmann_factor) * thermal_frequency_MHz(temperature_mK)
    return required_gap / gap_over_J
