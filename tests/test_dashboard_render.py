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
            "reason_zh": "維持榮景期，因為允許的下一階段衰退期尚未提供足夠的轉換證據。",
            "details": {
                "previous_phase_source": "cycle_context",
                "cycle_context": {
                    "baseline_phase_id": "boom",
                    "baseline_phase_name_zh": "榮景期",
                    "baseline_stage_note_zh": "榮景期第一年剛結束",
                    "source_type": "user_provided_author_assessment",
                    "source_note_zh": "根據使用者提供之作者近期敘述，作為 state machine 的外部基準情境；模型仍以資料分數檢查是否維持或轉換。",
                    "use_as_default_previous_phase": True,
                },
            },
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
    assert '<html lang="zh-Hant-TW">' in html
    assert "景氣循環儀表板" in html


def test_dashboard_contains_current_phase() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "復甦期" in html
    assert "維持目前階段" in html
    assert "榮景期第一年剛結束" in html
    assert "維持 boom" not in html
    assert "recession 尚未" not in html


def test_dashboard_contains_four_phase_scores() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "復甦期" in html
    assert "成長期" in html
    assert "榮景期" in html
    assert "衰退期" in html
    assert "可用權重" in html
    assert "資料信心" in html


def test_dashboard_contains_indicator_scores() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "失業率" in html
    assert "歷史分位數評分" in html
    assert "UNRATE" in html
    assert "<h3>unemployment_rate</h3>" not in html


def test_dashboard_contains_warnings() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "synthetic warning" in html


def test_dashboard_contains_not_investment_advice_disclaimer() -> None:
    html = build_dashboard(synthetic_snapshot())

    assert "不構成投資建議" in html


def test_dashboard_excludes_manual_review_and_api_key() -> None:
    html = build_dashboard(synthetic_snapshot())

    forbidden_manual_review_field = "manual_review" + "_required"
    assert forbidden_manual_review_field not in html
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
