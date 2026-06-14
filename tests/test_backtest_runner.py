from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from business_cycle.backtests import BacktestPeriodResult, BacktestRunConfig, run_backtest
from business_cycle.backtests.runner import generate_monthly_periods
from business_cycle.backtests.specs import BacktestScenario


def scenario() -> BacktestScenario:
    return BacktestScenario(
        scenario_id="test_scenario",
        display_name_zh="測試案例",
        display_name_en="Test Scenario",
        window_start=date(2020, 1, 1),
        window_end=date(2020, 3, 31),
        focus_transition="boom_to_recession",
        baseline_phase_id="boom",
        expected_focus_zh=["測試"],
        benchmark_notes_zh="測試",
        data_mode="revised",
    )


def config(tmp_path: Path, max_periods: int | None = None) -> BacktestRunConfig:
    return BacktestRunConfig(
        scenario_id=scenario().scenario_id,
        scenario=scenario(),
        output_dir=tmp_path / "backtests",
        max_periods=max_periods,
        raw_data_dir=tmp_path / "missing_raw",
    )


def fake_period_runner(
    _config: BacktestRunConfig,
    as_of: str,
    previous_phase_id: str | None,
    _period_output_dir: Path,
) -> BacktestPeriodResult:
    current_phase_id = "recession" if as_of == "2020-01-31" else "recovery"
    return BacktestPeriodResult(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        current_phase_id=current_phase_id,
        candidate_phase_id="recession",
        decision_status="confirmed",
        confidence=0.75,
        phase_scores=[
            {
                "phase_id": "boom",
                "score": 70.0,
                "confidence": 0.8,
                "available_weight": 1.0,
                "stage_hint": "late",
            }
        ],
        indicator_summary={"total_indicators": 1, "scored_indicators": 1, "failed_indicators": 0},
        warnings=[],
        failures=[],
    )


def fake_controls_period_runner(
    config: BacktestRunConfig,
    as_of: str,
    previous_phase_id: str | None,
    _period_output_dir: Path,
) -> BacktestPeriodResult:
    assert config.transition_controls_path is not None
    return BacktestPeriodResult(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        current_phase_id="boom",
        candidate_phase_id="recession",
        decision_status="transition_watch",
        confidence=0.7,
        phase_scores=[],
        indicator_summary={"total_indicators": 1, "scored_indicators": 1, "failed_indicators": 0},
        transition_controls_enabled=True,
        transition_controls_applied=["transition_watch_required"],
        transition_controls_blocked=["transition_watch_required"],
        transition_controls_warnings=[],
    )


def test_generate_monthly_periods_uses_month_end_dates() -> None:
    periods = generate_monthly_periods(date(2020, 1, 15), date(2020, 3, 20))

    assert periods == ["2020-01-31", "2020-02-29"]


def test_generate_monthly_periods_respects_max_periods() -> None:
    periods = generate_monthly_periods(date(2020, 1, 1), date(2020, 12, 31), max_periods=2)

    assert periods == ["2020-01-31", "2020-02-29"]


def test_backtest_previous_phase_propagates_between_periods(tmp_path: Path) -> None:
    result = run_backtest(config(tmp_path, max_periods=2), period_runner=fake_period_runner)

    assert result.timeline[0].previous_phase_id == "boom"
    assert result.timeline[0].current_phase_id == "recession"
    assert result.timeline[1].previous_phase_id == "recession"
    assert result.timeline[1].current_phase_id == "recovery"


def test_backtest_writes_timeline_schema(tmp_path: Path) -> None:
    result = run_backtest(config(tmp_path, max_periods=1), period_runner=fake_period_runner)

    payload = json.loads(result.output_path.read_text(encoding="utf-8"))
    assert payload["scenario_id"] == "test_scenario"
    assert payload["display_name_zh"] == "測試案例"
    assert payload["data_mode"] == "revised"
    assert payload["period_count"] == 1
    assert payload["periods"][0]["as_of"] == "2020-01-31"
    assert payload["periods"][0]["phase_scores"][0]["phase_id"] == "boom"
    assert payload["periods"][0]["indicator_summary"]["total_indicators"] == 1
    assert "使用修訂後歷史資料。" in payload["caveats_zh"]
    assert "不構成投資建議。" in payload["caveats_zh"]
    assert payload["periods"][0]["transition_controls_enabled"] is False


def test_backtest_records_missing_raw_data_failures_without_fred_api(tmp_path: Path) -> None:
    result = run_backtest(config(tmp_path, max_periods=1))

    payload = json.loads(result.output_path.read_text(encoding="utf-8"))
    assert payload["period_count"] == 1
    assert payload["periods"][0]["indicator_summary"]["failed_indicators"] > 0
    assert payload["periods"][0]["failures"]


def test_backtest_records_transition_controls_metadata(tmp_path: Path) -> None:
    controls_path = tmp_path / "controls.yaml"
    controls_path.write_text("transition_controls: {}\n", encoding="utf-8")
    run_config = BacktestRunConfig(
        scenario_id=scenario().scenario_id,
        scenario=scenario(),
        output_dir=tmp_path / "backtests",
        max_periods=1,
        transition_controls_path=controls_path,
    )

    result = run_backtest(run_config, period_runner=fake_controls_period_runner)

    payload = json.loads(result.output_path.read_text(encoding="utf-8"))
    period = payload["periods"][0]
    assert period["transition_controls_enabled"] is True
    assert period["transition_controls_applied"] == ["transition_watch_required"]
    assert period["transition_controls_blocked"] == ["transition_watch_required"]
