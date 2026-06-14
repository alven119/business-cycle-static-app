from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from business_cycle.backtests import build_attribution_smoke_summary
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


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def attribution_payload(scenario_id: str = "scenario_a") -> dict:
    return {
        "scenario_id": scenario_id,
        "display_name_zh": f"測試案例 {scenario_id}",
        "data_mode": "revised",
        "transition_count": 1,
        "diagnostics": [
            {
                "as_of": "2020-02-29",
                "attribution_quality": "full",
                "phase_score_changes": [
                    {"phase_id": "recession", "delta": 25.0},
                    {"phase_id": "boom", "delta": -10.0},
                ],
                "top_indicator_score_changes": [
                    {"indicator_id": "initial_jobless_claims", "delta": 50.0},
                    {"indicator_id": "real_retail_sales", "delta": -8.0},
                ],
            },
            {
                "as_of": "2020-03-31",
                "attribution_quality": "partial",
                "phase_score_changes": [{"phase_id": "recovery", "delta": 12.0}],
                "top_indicator_score_changes": [{"indicator_id": "initial_jobless_claims", "delta": -7.0}],
            },
        ],
        "plausibility_warnings_linked": [
            {"as_of": "2020-02-29", "kind": "short_phase_segment", "phase_id": "recession"},
            {
                "as_of": "2020-02-29",
                "kind": "direct_confirmed_transition_without_watch",
                "phase_id": "recession",
            },
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        "warnings": [],
    }


def failing_runner(*_args, **_kwargs):  # noqa: ANN002, ANN003, ANN201
    raise RuntimeError("runner should not be called in reuse_existing tests")


def test_attribution_smoke_summary_aggregates_existing_attribution(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    write_json(output_dir / "scenario_a" / "transition_attribution.json", attribution_payload())

    summary = build_attribution_smoke_summary(
        scenarios=[scenario("scenario_a")],
        output_dir=output_dir,
        max_periods=12,
        reuse_existing=True,
        backtest_runner=failing_runner,
        report_writer=failing_runner,
        attribution_writer=failing_runner,
    )

    item = summary["scenarios"][0]
    assert summary["scenario_count"] == 1
    assert item["transition_count"] == 1
    assert item["diagnostic_count"] == 2
    assert item["attribution_quality_counts"] == {"full": 1, "partial": 1}
    assert item["top_phase_score_delta"] == {
        "as_of": "2020-02-29",
        "phase_id": "recession",
        "delta": 25.0,
    }
    assert item["top_indicator_delta"] == {
        "as_of": "2020-02-29",
        "indicator_id": "initial_jobless_claims",
        "delta": 50.0,
    }
    assert item["top_repeated_indicator_ids"][0] == "initial_jobless_claims"
    assert item["linked_plausibility_warning_count"] == 2


def test_attribution_smoke_aggregate_counts(tmp_path: Path) -> None:
    output_dir = tmp_path / "backtests"
    write_json(output_dir / "scenario_a" / "transition_attribution.json", attribution_payload("scenario_a"))
    write_json(output_dir / "scenario_b" / "transition_attribution.json", attribution_payload("scenario_b"))

    summary = build_attribution_smoke_summary(
        scenarios=[scenario("scenario_a"), scenario("scenario_b")],
        output_dir=output_dir,
        max_periods=12,
        reuse_existing=True,
        backtest_runner=failing_runner,
        report_writer=failing_runner,
        attribution_writer=failing_runner,
    )

    aggregate = summary["aggregate"]
    assert aggregate["scenario_with_attribution_count"] == 2
    assert aggregate["scenario_with_failures_count"] == 0
    assert aggregate["total_diagnostic_count"] == 4
    assert aggregate["attribution_quality_counts"] == {"full": 2, "partial": 2}
    assert aggregate["indicator_delta_frequency"] == {
        "initial_jobless_claims": 4,
        "real_retail_sales": 2,
    }
    assert aggregate["phase_delta_frequency"] == {"boom": 2, "recession": 2, "recovery": 2}
    assert aggregate["linked_plausibility_warning_kind_counts"] == {
        "direct_confirmed_transition_without_watch": 2,
        "short_phase_segment": 2,
    }
    assert "不構成投資建議。" in summary["caveats_zh"]


def test_attribution_smoke_records_scenario_failure(tmp_path: Path) -> None:
    summary = build_attribution_smoke_summary(
        scenarios=[scenario("missing")],
        output_dir=tmp_path / "backtests",
        max_periods=1,
        reuse_existing=True,
        backtest_runner=failing_runner,
        report_writer=failing_runner,
        attribution_writer=failing_runner,
    )

    item = summary["scenarios"][0]
    assert item["failure_count"] == 1
    assert item["scenario_failure"]["error_type"] == "FileNotFoundError"
    assert summary["aggregate"]["scenario_with_failures_count"] == 1
