"""Load backtest scenario specs from YAML."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.specs import (
    BacktestScenario,
    BacktestScenarioCatalog,
    BacktestScenarioError,
)

REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "display_name_zh",
    "display_name_en",
    "window_start",
    "window_end",
    "focus_transition",
    "baseline_phase_id",
    "expected_focus_zh",
    "benchmark_notes_zh",
    "data_mode",
)


def load_backtest_scenarios(path: str | Path) -> list[BacktestScenario]:
    """Load validated backtest scenarios from YAML."""

    return load_backtest_scenario_catalog(path).scenarios


def load_backtest_scenario_catalog(path: str | Path) -> BacktestScenarioCatalog:
    """Load a validated backtest scenario catalog from YAML."""

    payload = _load_yaml_mapping(path)
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise BacktestScenarioError("Backtest scenario YAML must contain a non-empty scenarios list")
    return BacktestScenarioCatalog([_scenario_from_mapping(item) for item in scenarios])


def get_scenario(catalog: BacktestScenarioCatalog, scenario_id: str) -> BacktestScenario:
    """Return one scenario by id."""

    scenarios_by_id = catalog.by_id()
    try:
        return scenarios_by_id[scenario_id]
    except KeyError as exc:
        raise BacktestScenarioError(f"Unknown scenario_id: {scenario_id}") from exc


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BacktestScenarioError(f"Backtest scenario file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BacktestScenarioError(f"Invalid YAML in backtest scenario file {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BacktestScenarioError("Backtest scenario YAML must be a mapping")
    return payload


def _scenario_from_mapping(value: Any) -> BacktestScenario:
    if not isinstance(value, dict):
        raise BacktestScenarioError("Each backtest scenario must be a mapping")
    missing = [field for field in REQUIRED_SCENARIO_FIELDS if field not in value]
    if missing:
        raise BacktestScenarioError(
            f"Backtest scenario missing required field(s): {', '.join(missing)}"
        )
    expected_focus = value["expected_focus_zh"]
    if not isinstance(expected_focus, list) or not expected_focus:
        raise BacktestScenarioError("expected_focus_zh must be a non-empty list")
    return BacktestScenario(
        scenario_id=str(value["scenario_id"]),
        display_name_zh=str(value["display_name_zh"]),
        display_name_en=str(value["display_name_en"]),
        window_start=_parse_date(value["window_start"], "window_start"),
        window_end=_parse_date(value["window_end"], "window_end"),
        focus_transition=str(value["focus_transition"]),
        baseline_phase_id=str(value["baseline_phase_id"]),
        expected_focus_zh=[str(item) for item in expected_focus],
        benchmark_notes_zh=str(value["benchmark_notes_zh"]),
        data_mode=str(value["data_mode"]),
    )


def _parse_date(value: Any, field: str) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise BacktestScenarioError(f"{field} must be a YYYY-MM-DD string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise BacktestScenarioError(f"{field} must be a valid YYYY-MM-DD date") from exc
