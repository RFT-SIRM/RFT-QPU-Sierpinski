import math
import numpy as np

from rft_qpu.circuit_quantization import CircuitParameters, analyze_circuit_point, build_capacitance_matrix


def test_three_node_capacitance_matrix_is_positive_definite():
    c_matrix, ec_matrix = build_capacitance_matrix(CircuitParameters())
    assert min(np.linalg.eigvalsh(c_matrix)) > 0
    assert min(np.linalg.eigvalsh(ec_matrix)) > 0


def test_nominal_local_frequencies_are_exactly_calibrated():
    report = analyze_circuit_point(CircuitParameters())
    got = report["isolated_local_modes"]["computed_f01_MHz"]
    expected = [5500.0, 5007.5, 4515.0]
    assert max(abs(a-b) for a,b in zip(got, expected)) < 2e-6


def test_capacitance_derived_exchange_and_static_zz_are_finite():
    report = analyze_circuit_point(CircuitParameters())
    g = report["derived_exchange_matrix_elements_MHz"]
    spec = report["dressed_static_spectrum_MHz"]
    assert 24.0 < g["g_AC_01"] < 27.0
    assert 23.0 < g["g_CB_01"] < 26.0
    assert math.isfinite(spec["residual_static_ZZ_MHz"])
    assert abs(spec["residual_static_ZZ_MHz"]) < 0.01
    assert min(x["bare_product_overlap"] for x in spec["tracked_states"].values()) > 0.99


def test_squid_flux_calibration_gives_declared_frequency_response():
    report = analyze_circuit_point(CircuitParameters())
    flux = report["flux_to_frequency_calibration"]
    assert flux["df01_dflux_MHz_per_Phi0"] < 0
    assert flux["0.01"]["negative_peak_shift_MHz"] > 80
    assert flux["0.01"]["positive_peak_shift_MHz"] < -80
