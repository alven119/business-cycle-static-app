from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    BacktestScenarioError,
    get_scenario,
    load_backtest_scenario_catalog,
    load_backtest_scenarios,
)

SCENARIOS_PATH = Path("specs/backtests/scenarios.yaml")


def write_scenarios(path: Path, scenario_blocks: str) -> Path:
    path.write_text(f"scenarios:\n{scenario_blocks}", encoding="utf-8")
    return path


def scenario_yaml(
    scenario_id: str = "test_scenario",
    *,
    window_start: str = "2000-01-01",
    window_end: str = "2001-12-31",
    baseline_phase_id: str = "boom",
    data_mode: str = "revised",
) -> str:
    return f"""  - scenario_id: {scenario_id}
    display_name_zh: 測試案例
    display_name_en: Test Scenario
    window_start: "{window_start}"
    window_end: "{window_end}"
    focus_transition: boom_to_recession
    baseline_phase_id: {baseline_phase_id}
    expected_focus_zh:
      - 測試觀察重點
    benchmark_notes_zh: 測試備註
    data_mode: {data_mode}
"""


def test_scenarios_yaml_can_be_loaded() -> None:
    scenarios = load_backtest_scenarios(SCENARIOS_PATH)

    assert [scenario.scenario_id for scenario in scenarios] == [
        "dotcom_bubble",
        "global_financial_crisis",
        "covid_recession",
        "euro_debt_slowdown",
        "late_cycle_2018",
    ]


def test_scenario_ids_are_unique() -> None:
    scenarios = load_backtest_scenarios(SCENARIOS_PATH)

    scenario_ids = [scenario.scenario_id for scenario in scenarios]
    assert len(scenario_ids) == len(set(scenario_ids))


def test_windows_baseline_and_data_mode_are_valid() -> None:
    scenarios = load_backtest_scenarios(SCENARIOS_PATH)

    for scenario in scenarios:
        assert scenario.window_start <= scenario.window_end
        assert scenario.baseline_phase_id in {"recovery", "growth", "boom", "recession"}
        assert scenario.data_mode == "revised"


def test_unsupported_data_mode_raises_clear_error(tmp_path: Path) -> None:
    path = write_scenarios(tmp_path / "scenarios.yaml", scenario_yaml(data_mode="realtime_vintage"))

    with pytest.raises(BacktestScenarioError, match="unsupported data_mode"):
        load_backtest_scenario_catalog(path)


def test_duplicate_scenario_id_raises_clear_error(tmp_path: Path) -> None:
    path = write_scenarios(
        tmp_path / "scenarios.yaml",
        scenario_yaml("duplicate") + scenario_yaml("duplicate"),
    )

    with pytest.raises(BacktestScenarioError, match="Duplicate scenario_id"):
        load_backtest_scenario_catalog(path)


def test_invalid_window_order_raises_clear_error(tmp_path: Path) -> None:
    path = write_scenarios(
        tmp_path / "scenarios.yaml",
        scenario_yaml(window_start="2002-01-01", window_end="2001-01-01"),
    )

    with pytest.raises(BacktestScenarioError, match="window_start"):
        load_backtest_scenario_catalog(path)


def test_get_scenario_returns_requested_scenario() -> None:
    catalog = load_backtest_scenario_catalog(SCENARIOS_PATH)

    scenario = get_scenario(catalog, "global_financial_crisis")

    assert scenario.display_name_zh == "金融海嘯"
    assert scenario.baseline_phase_id == "boom"


def test_get_missing_scenario_raises_clear_error() -> None:
    catalog = load_backtest_scenario_catalog(SCENARIOS_PATH)

    with pytest.raises(BacktestScenarioError, match="Unknown scenario_id"):
        get_scenario(catalog, "missing")
