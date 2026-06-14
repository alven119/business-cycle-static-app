from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.backtests import build_backtest_report, write_backtest_report
from business_cycle.backtests.report import serialize_backtest_report


def timeline() -> dict:
    return {
        "scenario_id": "test_scenario",
        "display_name_zh": "測試案例",
        "window_start": "2000-01-01",
        "window_end": "2000-05-31",
        "data_mode": "revised",
        "periods": [
            period("2000-01-31", "boom", "hold_current", "recession", boom_score=70, recession_score=20),
            period("2000-02-29", "boom", "transition_watch", "recession", boom_score=65, recession_score=55),
            period(
                "2000-03-31",
                "recession",
                "confirmed",
                "recession",
                boom_score=40,
                recession_score=80,
                reason_zh="確認從榮景期轉換到衰退期。",
            ),
            period(
                "2000-04-30",
                "recession",
                "hold_current",
                "recovery",
                boom_score=30,
                recession_score=75,
                warnings=["synthetic warning"],
                failures=[{"error_type": "SyntheticFailure"}],
            ),
            {
                "as_of": "2000-05-31",
                "current_phase_id": "recovery",
                "decision_status": "confirmed",
                "candidate_phase_id": "recovery",
                "confidence": 0.66,
                "phase_scores": [],
                "warnings": [],
                "failures": [],
            },
        ],
        "caveats_zh": [
            "使用修訂後歷史資料。",
            "不等同當時投資人可見資料。",
            "不構成投資建議。",
        ],
    }


def period(
    as_of: str,
    current_phase_id: str,
    decision_status: str,
    candidate_phase_id: str,
    *,
    boom_score: float,
    recession_score: float,
    reason_zh: str | None = None,
    warnings: list[str] | None = None,
    failures: list[dict] | None = None,
) -> dict:
    return {
        "as_of": as_of,
        "current_phase_id": current_phase_id,
        "decision_status": decision_status,
        "candidate_phase_id": candidate_phase_id,
        "confidence": 0.75,
        "reason_zh": reason_zh,
        "phase_scores": [
            {
                "phase_id": "boom",
                "score": boom_score,
                "confidence": 0.8,
                "available_weight": 1.0,
                "stage_hint": None,
            },
            {
                "phase_id": "recession",
                "score": recession_score,
                "confidence": 0.7,
                "available_weight": 1.0,
                "stage_hint": None,
            },
        ],
        "warnings": warnings or [],
        "failures": failures or [],
    }


def test_phase_segments_are_grouped_by_current_phase() -> None:
    report = build_backtest_report(timeline())

    assert [(item.phase_id, item.start_as_of, item.end_as_of, item.period_count) for item in report.phase_segments] == [
        ("boom", "2000-01-31", "2000-02-29", 2),
        ("recession", "2000-03-31", "2000-04-30", 2),
        ("recovery", "2000-05-31", "2000-05-31", 1),
    ]


def test_transition_events_only_when_current_phase_changes() -> None:
    report = build_backtest_report(timeline())

    assert [(item.as_of, item.from_phase_id, item.to_phase_id) for item in report.transition_events] == [
        ("2000-03-31", "boom", "recession"),
        ("2000-05-31", "recession", "recovery"),
    ]
    assert report.transition_events[0].reason_zh == "確認從榮景期轉換到衰退期。"


def test_transition_watch_without_phase_change_is_not_transition_event() -> None:
    report = build_backtest_report(timeline())

    assert all(item.as_of != "2000-02-29" for item in report.transition_events)
    assert report.first_transition_watch_as_of == "2000-02-29"


def test_decision_status_counts_are_reported() -> None:
    report = build_backtest_report(timeline())

    assert report.decision_status_counts == {
        "hold_current": 2,
        "transition_watch": 1,
        "confirmed": 2,
    }


def test_phase_score_extrema_are_reported() -> None:
    report = build_backtest_report(timeline())
    extrema = {item.phase_id: item for item in report.phase_score_extrema}

    assert extrema["boom"].max_score == 70
    assert extrema["boom"].max_score_as_of == "2000-01-31"
    assert extrema["boom"].min_score == 30
    assert extrema["boom"].min_score_as_of == "2000-04-30"
    assert extrema["boom"].latest_score == 30
    assert extrema["boom"].latest_confidence == 0.8
    assert extrema["recession"].max_score == 80
    assert extrema["recession"].latest_score == 75


def test_recession_watch_and_current_dates_are_reported() -> None:
    report = build_backtest_report(timeline())

    assert report.first_confirmed_transition_as_of == "2000-03-31"
    assert report.first_recession_watch_as_of == "2000-02-29"
    assert report.first_recession_current_as_of == "2000-03-31"


def test_failure_and_warning_periods_are_reported() -> None:
    report = build_backtest_report(timeline())

    assert report.periods_with_failures == [{"as_of": "2000-04-30", "count": 1}]
    assert report.periods_with_warnings == [{"as_of": "2000-04-30", "count": 1}]
    assert report.failure_count == 1
    assert report.warning_count == 2
    assert "period 2000-05-31 missing phase_scores" in report.warnings


def test_empty_periods_raise_clear_error() -> None:
    payload = timeline()
    payload["periods"] = []

    with pytest.raises(ValueError, match="non-empty periods"):
        build_backtest_report(payload)


def test_missing_phase_scores_does_not_crash_and_warns() -> None:
    payload = timeline()
    payload["periods"] = [
        {
            "as_of": "2000-01-31",
            "current_phase_id": "boom",
            "decision_status": "hold_current",
            "candidate_phase_id": "recession",
            "confidence": 0.7,
            "warnings": [],
            "failures": [],
        }
    ]

    report = build_backtest_report(payload)

    assert report.phase_score_extrema == []
    assert report.warnings == ["period 2000-01-31 missing phase_scores"]


def test_write_backtest_report_writes_json(tmp_path: Path) -> None:
    timeline_path = tmp_path / "timeline.json"
    output_path = tmp_path / "report.json"
    timeline_path.write_text(json.dumps(timeline(), ensure_ascii=False), encoding="utf-8")

    written = write_backtest_report(timeline_path, output_path)

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["scenario_id"] == "test_scenario"
    assert payload["phase_segments"][0]["phase_id"] == "boom"
    assert "不構成投資建議。" in payload["caveats_zh"]
    assert serialize_backtest_report(build_backtest_report(timeline()))["scenario_id"] == "test_scenario"
