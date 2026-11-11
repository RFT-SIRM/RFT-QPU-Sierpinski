import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from run_three_mode_optimization import (  # noqa: E402
    DYNAMIC_CANDIDATES,
    build_static_grid,
    run_dynamic_shortlist,
)
from rft_qpu.three_mode_coupler import ThreeModeParams


def test_static_optimizer_grid_is_deterministic_and_has_72_points():
    rows = build_static_grid(ThreeModeParams())
    assert len(rows) == 72
    assert rows[0]["alpha_c_MHz"] == -200.0
    assert rows[-1]["alpha_c_MHz"] == -400.0
    assert all(row["target_weight_min"] > 0.98 for row in rows)


def test_dynamic_shortlist_is_explicit_and_limited():
    assert len(DYNAMIC_CANDIDATES) == 6
    assert run_dynamic_shortlist(limit=0) == []


def test_sambe_order_four_exchange_is_converged_for_shortlisted_point():
    from dataclasses import replace
    from rft_qpu.three_mode_coupler import exact_sambe_exchange, find_resonant_pump_frequency

    base = ThreeModeParams(g_ac_MHz=25.0, g_cb_MHz=25.0, pump_amplitude_MHz=350.0)
    p4 = replace(base, sambe_order=4)
    p5 = replace(base, sambe_order=5)
    f4, _ = find_resonant_pump_frequency(p4, search_half_width_MHz=60.0, samples=61)
    f5, _ = find_resonant_pump_frequency(p5, search_half_width_MHz=60.0, samples=61)
    j4 = exact_sambe_exchange(p4, f4)["exact_sambe_exchange_MHz"]
    j5 = exact_sambe_exchange(p5, f5)["exact_sambe_exchange_MHz"]
    assert abs(j5 - j4) < 2e-6
