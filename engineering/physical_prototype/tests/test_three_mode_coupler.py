import pytest
import math
import numpy as np

from rft_qpu.three_mode_coupler import (
    ThreeModeParams,
    sector_operators,
    sambe_matrix,
    find_resonant_pump_frequency,
    exact_sambe_exchange,
    static_dressed_spectrum,
)


def test_three_mode_sector_hamiltonians_are_hermitian_and_number_conserving():
    params = ThreeModeParams()
    for excitations in (1, 2):
        basis, h0, nc = sector_operators(params, excitations)
        assert h0.shape == (len(basis), len(basis))
        assert np.allclose(h0, h0.conj().T, atol=1e-12)
        assert np.allclose(nc, nc.conj().T, atol=1e-12)


def test_sambe_matrix_is_hermitian():
    params = ThreeModeParams()
    _, _, hf = sambe_matrix(params, 1, 1023.85)
    assert np.allclose(hf, hf.conj().T, atol=1e-11)


def test_pump_phase_reversal_conjugates_complex_effective_hopping():
    params = ThreeModeParams()
    pump, _ = find_resonant_pump_frequency(params)
    plus = exact_sambe_exchange(params, pump, math.radians(45))
    minus = exact_sambe_exchange(params, pump, math.radians(-45))
    j_plus = plus["feshbach_complex_exchange"]
    j_minus = minus["feshbach_complex_exchange"]
    assert j_plus["real_MHz"] == pytest.approx(j_minus["real_MHz"], abs=1e-9)
    assert j_plus["imag_MHz"] == pytest.approx(-j_minus["imag_MHz"], abs=1e-9)
    assert abs(plus["exact_sambe_exchange_MHz"] - minus["exact_sambe_exchange_MHz"]) < 1e-10


def test_coupler_anharmonicity_changes_two_excitation_dressed_spectrum():
    p1 = ThreeModeParams(alpha_c_MHz=-200.0)
    p2 = ThreeModeParams(alpha_c_MHz=-400.0)
    z1 = static_dressed_spectrum(p1)["static_residual_ZZ_MHz"]
    z2 = static_dressed_spectrum(p2)["static_residual_ZZ_MHz"]
    assert abs(z1 - z2) > 1e-5
