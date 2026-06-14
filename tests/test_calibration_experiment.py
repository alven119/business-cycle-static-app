from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from business_cycle.backtests import (
    BacktestRunConfig,
    BacktestRunResult,
    build_calibration_experiment_summary,
)
from business_cycle.backtests.specs import BacktestScenario


def scenario(scenario_id: str = "global_financial_crisis") -> BacktestScenario:
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
        timeline=[],
        output_path=output_path,
        warnings=[],
        failures=[],
    )


def fake_report_writer(timeline_path: str | Path, output_path: str | Path) -> Path:
    timeline = Path(timeline_path)
    scenario_id = timeline.parent.name
    is_experiment = "experiment" in timeline.parts
    baseline_values = {
        "global_financial_crisis": (6, 2, 3, "2020-02-29"),
        "late_cycle_2018": (0, 0, 1, None),
        "regression_case": (1, 1, 1, None),
    }
    experiment_values = {
        "global_financial_crisis": (2, 1, 1, None),
        "late_cycle_2018": (0, 0, 1, "2020-02-29"),
        "regression_case": (3, 1, 2, None),
    }
    warning_count, transition_count, segment_count, first_recession = (
        experiment_values if is_experiment else baseline_values
    )[scenario_id]
    report = {
        "scenario_id": scenario_id,
        "display_name_zh": f"測試案例 {scenario_id}",
        "plausibility_warning_count": warning_count,
        "transition_events": [{"as_of": "2020-02-29"}] * transition_count,
        "first_recession_current_as_of": first_recession,
        "phase_segments": [{"phase_id": "boom"}] * segment_count,
        "failure_count": 0,
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return output


def fake_attribution_writer(**kwargs) -> Path:  # noqa: ANN003
    output = Path(kwargs["output_path"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("{}", encoding="utf-8")
    return output


def failing_runner(_config: BacktestRunConfig) -> BacktestRunResult:
    raise RuntimeError("synthetic failure")


def test_calibration_experiment_summary_compares_baseline_and_experiment(tmp_path: Path) -> None:
    summary = build_calibration_experiment_summary(
        experiment_id="test",
        scenarios=[scenario("global_financial_crisis")],
        experiment_root=tmp_path / "calibration" / "test",
        controls_config_path=Path("controls.yaml"),
        max_periods=12,
        out_of_sample_scenarios=set(),
        backtest_runner=fake_runner,
        report_writer=fake_report_writer,
        attribution_writer=fake_attribution_writer,
    )

    item = summary["scenarios"][0]
    assert item["baseline"]["plausibility_warning_count"] == 6
    assert item["experiment"]["plausibility_warning_count"] == 2
    assert item["delta"]["plausibility_warning_count"] == -4
    assert item["acceptance_checks"]["reduced_warnings"] is True
    assert summary["aggregate"]["delta_total_plausibility_warning_count"] == -4
    assert summary["aggregate"]["scenario_improved_count"] == 1
    assert summary["aggregate"]["scenario_regressed_count"] == 0
    assert "不構成投資建議。" in summary["caveats_zh"]


def test_calibration_experiment_detects_regression(tmp_path: Path) -> None:
    summary = build_calibration_experiment_summary(
        experiment_id="test",
        scenarios=[scenario("regression_case")],
        experiment_root=tmp_path / "calibration" / "test",
        controls_config_path=Path("controls.yaml"),
        max_periods=12,
        out_of_sample_scenarios=set(),
        backtest_runner=fake_runner,
        report_writer=fake_report_writer,
        attribution_writer=fake_attribution_writer,
    )

    assert summary["aggregate"]["scenario_improved_count"] == 0
    assert summary["aggregate"]["scenario_regressed_count"] == 1


def test_out_of_sample_false_recession_check(tmp_path: Path) -> None:
    summary = build_calibration_experiment_summary(
        experiment_id="test",
        scenarios=[scenario("late_cycle_2018")],
        experiment_root=tmp_path / "calibration" / "test",
        controls_config_path=Path("controls.yaml"),
        max_periods=12,
        out_of_sample_scenarios={"late_cycle_2018"},
        backtest_runner=fake_runner,
        report_writer=fake_report_writer,
        attribution_writer=fake_attribution_writer,
    )

    checks = summary["scenarios"][0]["acceptance_checks"]
    assert checks["no_new_false_recession_for_out_of_sample"] is False


def test_calibration_experiment_records_scenario_failure(tmp_path: Path) -> None:
    summary = build_calibration_experiment_summary(
        experiment_id="test",
        scenarios=[scenario("global_financial_crisis")],
        experiment_root=tmp_path / "calibration" / "test",
        controls_config_path=Path("controls.yaml"),
        max_periods=12,
        out_of_sample_scenarios=set(),
        backtest_runner=failing_runner,
        report_writer=fake_report_writer,
        attribution_writer=fake_attribution_writer,
    )

    item = summary["scenarios"][0]
    assert item["failure_count"] == 1
    assert item["scenario_failure"]["error_type"] == "RuntimeError"
    assert summary["aggregate"]["scenario_with_failures_count"] == 1
