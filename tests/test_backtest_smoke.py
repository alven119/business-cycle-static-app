from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from business_cycle.backtests import (
    BacktestPeriodResult,
    BacktestRunConfig,
    BacktestRunResult,
    build_backtest_smoke_summary,
    run_backtest_smoke,
)
from business_cycle.backtests.specs import BacktestScenario


def scenario(scenario_id: str = "scenario_a") -> BacktestScenario:
    return BacktestScenario(
        scenario_id=scenario_id,
        display_name_zh=f"測試案例 {scenario_id}",
        display_name_en="Test Scenario",
        window_start=date(2020, 1, 1),
        window_end=date(2020, 12, 31),
        focus_transition="boom_to_recession",
        baseline_phase_id="boom",
        expected_focus_zh=["測試"],
        benchmark_notes_zh="測試",
        data_mode="revised",
    )


def fake_runner(config: BacktestRunConfig) -> BacktestRunResult:
    output_path = Path(config.output_dir) / config.scenario_id / "timeline.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("{}", encoding="utf-8")
    return BacktestRunResult(
        scenario_id=config.scenario_id,
        display_name_zh=config.scenario.display_name_zh,
        window_start=config.scenario.window_start.isoformat(),
        window_end=config.scenario.window_end.isoformat(),
        data_mode=config.data_mode,
        generated_at="2026-06-14T00:00:00+00:00",
        period_count=config.max_periods or 0,
        timeline=[
            BacktestPeriodResult(
                as_of="2020-01-31",
                previous_phase_id="boom",
                current_phase_id="boom",
                candidate_phase_id="recession",
                decision_status="hold_current",
                confidence=0.7,
                phase_scores=[],
                indicator_summary={"total_indicators": 1, "scored_indicators": 1, "failed_indicators": 0},
            )
        ],
        output_path=output_path,
        warnings=[],
        failures=[],
    )


def fake_report_writer(timeline_path: str | Path, output_path: str | Path) -> Path:
    timeline = Path(timeline_path)
    scenario_id = timeline.parent.name
    warning_count = 2 if scenario_id == "scenario_a" else 0
    report = {
        "scenario_id": scenario_id,
        "display_name_zh": f"測試案例 {scenario_id}",
        "data_mode": "revised",
        "window_start": "2020-01-01",
        "window_end": "2020-12-31",
        "period_count": 2,
        "phase_segments": [{"phase_id": "boom"}, {"phase_id": "recession"}],
        "transition_events": [{"as_of": "2020-02-29"}],
        "first_transition_watch_as_of": None,
        "first_recession_watch_as_of": "2020-02-29",
        "first_recession_current_as_of": "2020-02-29",
        "plausibility_warning_count": warning_count,
        "plausibility_warnings": [
            {"kind": "short_phase_segment"},
            {"kind": "rapid_round_trip"},
        ][:warning_count],
        "failure_count": 0,
        "warning_count": 0,
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return output


def failing_runner(_config: BacktestRunConfig) -> BacktestRunResult:
    raise RuntimeError("synthetic scenario failure")


def test_build_backtest_smoke_summary_aggregates_scenarios(tmp_path: Path) -> None:
    summary = build_backtest_smoke_summary(
        scenarios=[scenario("scenario_a"), scenario("scenario_b")],
        output_dir=tmp_path / "backtests",
        max_periods=2,
        backtest_runner=fake_runner,
        report_writer=fake_report_writer,
    )

    assert summary["scenario_count"] == 2
    assert summary["data_mode"] == "revised"
    assert summary["max_periods"] == 2
    assert summary["aggregate"]["scenario_with_plausibility_warnings_count"] == 1
    assert summary["aggregate"]["total_plausibility_warning_count"] == 2
    assert summary["aggregate"]["warning_kind_counts"] == {
        "rapid_round_trip": 1,
        "short_phase_segment": 1,
    }
    assert "使用修訂後歷史資料。" in summary["caveats_zh"]
    assert "不構成投資建議。" in summary["caveats_zh"]


def test_build_backtest_smoke_summary_records_scenario_failure(tmp_path: Path) -> None:
    summary = build_backtest_smoke_summary(
        scenarios=[scenario("scenario_a")],
        output_dir=tmp_path / "backtests",
        max_periods=1,
        backtest_runner=failing_runner,
        report_writer=fake_report_writer,
    )

    item = summary["scenarios"][0]
    assert item["failure_count"] == 1
    assert item["scenario_failure"]["error_type"] == "RuntimeError"
    assert "synthetic scenario failure" in item["scenario_failure"]["message"]
    assert summary["aggregate"]["scenario_with_failures_count"] == 1


def test_run_backtest_smoke_writes_output_for_fake_catalog(tmp_path: Path) -> None:
    scenario_path = tmp_path / "scenarios.yaml"
    scenario_path.write_text(
        """
scenarios:
  - scenario_id: scenario_a
    display_name_zh: 測試案例
    display_name_en: Test Scenario
    window_start: "2020-01-01"
    window_end: "2020-12-31"
    focus_transition: boom_to_recession
    baseline_phase_id: boom
    expected_focus_zh:
      - 測試
    benchmark_notes_zh: 測試
    data_mode: revised
""",
        encoding="utf-8",
    )
    output_path = tmp_path / "smoke_summary.json"

    summary = run_backtest_smoke(
        catalog_path=scenario_path,
        output_dir=tmp_path / "backtests",
        output_path=output_path,
        max_periods=1,
        backtest_runner=fake_runner,
        report_writer=fake_report_writer,
    )

    assert summary["scenario_count"] == 1
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["scenarios"][0]["scenario_id"] == "scenario_a"
