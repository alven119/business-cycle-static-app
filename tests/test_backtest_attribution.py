from __future__ import annotations

import json
from pathlib import Path

from business_cycle.backtests import build_transition_attribution


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def timeline_payload() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "data_mode": "revised",
        "periods": [
            period("2020-01-31", "boom", "hold_current", recession=40.0, boom=70.0),
            period("2020-02-29", "recession", "confirmed", recession=65.0, boom=50.0),
            period("2020-03-31", "recovery", "confirmed", recession=45.0, boom=55.0),
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def period(as_of: str, phase_id: str, status: str, *, recession: float, boom: float) -> dict:
    return {
        "as_of": as_of,
        "current_phase_id": phase_id,
        "decision_status": status,
        "candidate_phase_id": "recession",
        "confidence": 0.7,
        "phase_scores": [
            {"phase_id": "boom", "score": boom, "confidence": 0.7},
            {"phase_id": "recession", "score": recession, "confidence": 0.8},
        ],
        "warnings": [],
        "failures": [],
    }


def report_payload() -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "display_name_zh": "金融海嘯",
        "data_mode": "revised",
        "transition_events": [
            {
                "as_of": "2020-02-29",
                "from_phase_id": "boom",
                "to_phase_id": "recession",
                "decision_status": "confirmed",
                "confidence": 0.72,
                "candidate_phase_id": "recession",
            }
        ],
        "plausibility_warnings": [
            {"kind": "short_phase_segment", "as_of": "2020-02-29", "phase_id": "recession"},
            {"kind": "rapid_round_trip", "as_of": "2020-03-31", "phase_id": "recovery"},
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def write_intermediate(root: Path) -> None:
    write_json(
        root / "2020-01-31" / "indicator_scores.json",
        {
            "results": [
                {"indicator_id": "initial_jobless_claims", "score": 20.0, "confidence": 0.9},
                {"indicator_id": "real_retail_sales", "score": 80.0, "confidence": 0.8},
            ]
        },
    )
    write_json(
        root / "2020-02-29" / "indicator_scores.json",
        {
            "results": [
                {
                    "indicator_id": "initial_jobless_claims",
                    "score": 70.0,
                    "confidence": 0.9,
                    "reason_zh": "初領失業救濟金轉弱。",
                },
                {
                    "indicator_id": "real_retail_sales",
                    "score": 75.0,
                    "confidence": 0.8,
                    "reason_zh": "零售銷售放緩。",
                },
            ]
        },
    )
    write_json(
        root / "2020-02-29" / "phase_scores.json",
        {
            "results": [
                {
                    "phase_id": "recession",
                    "contributing_indicators": [
                        {
                            "indicator_id": "initial_jobless_claims",
                            "phase_signal_score": 70.0,
                            "confidence": 0.9,
                            "weight": 0.3,
                            "weighted_contribution": 21.0,
                            "role": "core",
                            "signal_transform": "as_is",
                        }
                    ],
                }
            ]
        },
    )


def build_payload(tmp_path: Path) -> dict:
    timeline_path = write_json(tmp_path / "timeline.json", timeline_payload())
    report_path = write_json(tmp_path / "report.json", report_payload())
    intermediate_dir = tmp_path / "intermediate"
    write_intermediate(intermediate_dir)
    return build_transition_attribution(
        timeline_path=timeline_path,
        report_path=report_path,
        intermediate_dir=intermediate_dir,
    )


def test_transition_attribution_calculates_phase_score_changes(tmp_path: Path) -> None:
    payload = build_payload(tmp_path)

    diagnostic = payload["diagnostics"][0]
    assert diagnostic["event_type"] == "transition_event"
    assert diagnostic["phase_score_changes"][0]["phase_id"] == "recession"
    assert diagnostic["phase_score_changes"][0]["delta"] == 25.0
    assert diagnostic["attribution_quality"] == "full"


def test_transition_warning_links_and_unlinked_warning_diagnostic(tmp_path: Path) -> None:
    payload = build_payload(tmp_path)

    assert payload["plausibility_warnings_linked"] == [
        {"as_of": "2020-02-29", "kind": "short_phase_segment", "phase_id": "recession"}
    ]
    assert payload["diagnostics"][0]["plausibility_warnings"][0]["kind"] == "short_phase_segment"
    assert payload["diagnostics"][1]["event_type"] == "plausibility_warning"
    assert payload["diagnostics"][1]["plausibility_warnings"][0]["kind"] == "rapid_round_trip"


def test_indicator_score_delta_is_included(tmp_path: Path) -> None:
    payload = build_payload(tmp_path)

    changes = payload["diagnostics"][0]["top_indicator_score_changes"]
    assert changes[0]["indicator_id"] == "initial_jobless_claims"
    assert changes[0]["delta"] == 50.0
    assert changes[0]["reason_zh"] == "初領失業救濟金轉弱。"


def test_missing_previous_period_is_limited_and_warns(tmp_path: Path) -> None:
    timeline = timeline_payload()
    report = report_payload()
    report["transition_events"][0]["as_of"] = "2020-01-31"
    timeline_path = write_json(tmp_path / "timeline.json", timeline)
    report_path = write_json(tmp_path / "report.json", report)

    payload = build_transition_attribution(
        timeline_path=timeline_path,
        report_path=report_path,
        intermediate_dir=tmp_path / "missing_intermediate",
    )

    assert payload["diagnostics"][0]["previous_as_of"] is None
    assert payload["diagnostics"][0]["attribution_quality"] == "limited"
    assert any("missing previous period" in warning for warning in payload["warnings"])


def test_missing_intermediate_files_do_not_crash(tmp_path: Path) -> None:
    timeline_path = write_json(tmp_path / "timeline.json", timeline_payload())
    report_path = write_json(tmp_path / "report.json", report_payload())

    payload = build_transition_attribution(
        timeline_path=timeline_path,
        report_path=report_path,
        intermediate_dir=tmp_path / "missing_intermediate",
    )

    assert payload["diagnostics"][0]["phase_score_changes"]
    assert payload["diagnostics"][0]["top_indicator_score_changes"] == []
    assert any("missing intermediate output" in warning for warning in payload["warnings"])


def test_missing_contribution_schema_falls_back_with_warning(tmp_path: Path) -> None:
    timeline_path = write_json(tmp_path / "timeline.json", timeline_payload())
    report_path = write_json(tmp_path / "report.json", report_payload())
    intermediate_dir = tmp_path / "intermediate"
    write_intermediate(intermediate_dir)
    write_json(intermediate_dir / "2020-02-29" / "phase_scores.json", {"results": [{"phase_id": "recession"}]})

    payload = build_transition_attribution(
        timeline_path=timeline_path,
        report_path=report_path,
        intermediate_dir=intermediate_dir,
    )

    assert payload["diagnostics"][0]["top_candidate_phase_evidence"] == []
    assert any("does not include per-indicator contribution details" in warning for warning in payload["warnings"])


def test_attribution_output_contains_caveats(tmp_path: Path) -> None:
    payload = build_payload(tmp_path)

    assert "使用修訂後歷史資料。" in payload["caveats_zh"]
    assert "不構成投資建議。" in payload["caveats_zh"]
