from __future__ import annotations

import json
from pathlib import Path

from business_cycle.render.dashboard import build_dashboard, build_static_site


def synthetic_snapshot() -> dict:
    return {
        "generated_at": "2026-06-14T00:00:00+00:00",
        "as_of": "2024-12-31",
        "current_phase_decision": {
            "current_phase_id": "recovery",
            "current_phase_name_zh": "復甦期",
            "decision_status": "hold_current",
            "previous_phase_id": "recovery",
            "candidate_phase_id": "growth",
            "candidate_score": 70.0,
            "candidate_confidence": 0.8,
            "current_score": 72.0,
            "confidence": 0.75,
            "allowed_next_phase_id": "growth",
            "blocked_phase_ids": [],
            "reason_zh": "synthetic reason",
            "details": {},
        },
        "phase_scores": [
            phase("growth", "成長期"),
            phase("boom", "榮景期"),
            phase("recession", "衰退期"),
            phase("recovery", "復甦期"),
        ],
        "indicator_scores": [
            {
                "indicator_id": "unemployment_rate",
                "score": 80.0,
                "confidence": 0.9,
                "as_of": "2024-12-31",
                "method": "level_percentile_score",
                "reason_zh": "失業率改善。",
                "details": {"selected_series_id": "UNRATE"},
            }
        ],
        "summary": {
            "current_phase_id": "recovery",
            "decision_status": "hold_current",
            "decision_confidence": 0.75,
        },
        "warnings": ["synthetic warning"],
        "failures": {"indicator_failures": [], "phase_failures": []},
    }


def phase(phase_id: str, name: str) -> dict:
    return {
        "phase_id": phase_id,
        "phase_name_zh": name,
        "score": 70.0,
        "confidence": 0.8,
        "available_weight": 1.0,
        "missing_indicators": [],
        "contributing_indicators": [],
        "stage_hint": "mid",
        "reason_zh": "synthetic",
        "details": {},
    }


def test_build_dashboard_generates_html() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert html.startswith("<!doctype html>")
    assert "景氣循環儀表板" in html


def test_dashboard_contains_current_phase() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "recovery" in html
    assert "復甦期" in html
    assert "hold_current" in html


def test_dashboard_contains_four_phase_scores() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "recovery" in html
    assert "growth" in html
    assert "boom" in html
    assert "recession" in html


def test_dashboard_contains_indicator_scores() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "unemployment_rate" in html
    assert "level_percentile_score" in html
    assert "UNRATE" in html


def test_dashboard_contains_warnings() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "synthetic warning" in html


def test_dashboard_contains_not_investment_advice_disclaimer() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "不構成投資建議" in html


def test_dashboard_excludes_manual_review_and_api_key() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "manual_review_required" not in html
    assert "FRED_API_KEY" not in html


def test_build_static_site_writes_index_and_snapshot(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "cycle_snapshot.json"
    snapshot_path.write_text(json.dumps(synthetic_snapshot(), ensure_ascii=False), encoding="utf-8")

    outputs = build_static_site(snapshot_path, tmp_path / "public")

    assert outputs["index_path"].exists()
    assert outputs["snapshot_path"].exists()
    assert outputs["index_path"].name == "index.html"
    assert json.loads(outputs["snapshot_path"].read_text(encoding="utf-8"))["summary"][
        "current_phase_id"
    ] == "recovery"
