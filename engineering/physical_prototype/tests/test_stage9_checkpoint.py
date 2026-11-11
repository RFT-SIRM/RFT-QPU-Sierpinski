from copy import deepcopy

from rft_qpu.stage9_checkpoint import checkpoint_config_differences


def sample_config():
    return {
        "bias_offset_Phi0": -0.0075,
        "bias_flux_Phi0": 0.25934367625232063,
        "static_ZZ_MHz": -0.000766699942289506,
        "static_AB_detuning_MHz": 987.673221499198,
        "pump_offset_from_static_kHz": -63.0,
        "pump_frequency_MHz": 987.610221499198,
        "amplitude_Phi0": 0.02,
        "requested_duration_us": 1.081,
        "actual_shared_duration_us": 1.0810017050174894,
        "ramp_periods": 8.0,
        "steps_per_period": [120, 240, 480],
        "steps_by_grid": {"120": 128113, "240": 256226, "480": 512452},
        "minimum_bare_overlap": 0.9942448225409911,
    }


def test_checkpoint_accepts_tiny_platform_eigensolver_roundoff():
    saved = sample_config()
    current = deepcopy(saved)
    current["bias_flux_Phi0"] += 2e-13
    current["static_ZZ_MHz"] -= 2e-12
    current["static_AB_detuning_MHz"] += 4e-10
    current["pump_frequency_MHz"] += 4e-10
    current["minimum_bare_overlap"] -= 2e-13
    assert checkpoint_config_differences(saved, current) == []


def test_checkpoint_rejects_changed_physical_controls():
    saved = sample_config()
    current = deepcopy(saved)
    current["amplitude_Phi0"] += 1e-5
    differences = checkpoint_config_differences(saved, current)
    assert any("amplitude_Phi0" in item for item in differences)


def test_checkpoint_rejects_changed_time_grid():
    saved = sample_config()
    current = deepcopy(saved)
    current["steps_by_grid"]["480"] += 1
    differences = checkpoint_config_differences(saved, current)
    assert any("steps_by_grid" in item for item in differences)


def test_checkpoint_rejects_material_spectral_drift():
    saved = sample_config()
    current = deepcopy(saved)
    current["static_ZZ_MHz"] += 1e-6
    differences = checkpoint_config_differences(saved, current)
    assert any("static_ZZ_MHz" in item for item in differences)


def test_checkpoint_rejects_missing_or_unknown_config_fields():
    saved = sample_config()
    current = deepcopy(saved)
    del current["minimum_bare_overlap"]
    differences = checkpoint_config_differences(saved, current)
    assert any("minimum_bare_overlap" in item for item in differences)
