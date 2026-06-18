from __future__ import annotations

from business_cycle.backtests import build_boom_ending_attribution


def test_boom_ending_attribution_summary_is_built() -> None:
    attribution = build_boom_ending_attribution(fake_diagnostics())

    assert attribution["point_count"] == 3
    assert attribution["comparisons"]["gfc_progression"]["status_trend"] == ["weak", "weak", "watch"]
    assert any("不構成投資建議" in caveat for caveat in attribution["caveats_zh"])


def test_boom_ending_attribution_top_positive_indicators() -> None:
    attribution = build_boom_ending_attribution(fake_diagnostics())
    point = next(item for item in attribution["points"] if item["label"] == "gfc_yield_curve_warning")

    indicator_ids = [item["indicator_id"] for item in point["top_positive_indicators"]]
    assert indicator_ids == ["yield_curve_10y_3m"]


def test_boom_ending_attribution_weak_but_important_indicators() -> None:
    attribution = build_boom_ending_attribution(fake_diagnostics())
    point = next(item for item in attribution["points"] if item["label"] == "gfc_yield_curve_warning")

    weak_ids = [item["indicator_id"] for item in point["weak_but_important_indicators"]]
    assert "credit_spread_baa_10y" in weak_ids


def test_boom_ending_attribution_refinement_candidates_include_credit_spread() -> None:
    attribution = build_boom_ending_attribution(fake_diagnostics())
    candidate_ids = [item["indicator_id"] for item in attribution["refinement_candidates"]]

    assert "credit_spread_baa_10y" in candidate_ids
    assert "yield_curve_10y_3m" in candidate_ids


def fake_diagnostics() -> dict:
    return {
        "data_mode": "revised",
        "points": [
            point("gfc_yield_curve_warning", "2006-12-31", "weak", 52.0, [score("yield_curve_10y_3m", 78, 1.0), score("credit_spread_baa_10y", 42, 0.8)]),
            point("gfc_recession_window_start", "2007-12-31", "weak", 64.0, [score("yield_curve_10y_2y", 72, 1.0), score("credit_spread_baa_10y", 45, 0.8)]),
            point("gfc_confirmed_recession", "2008-10-31", "watch", 75.0, [score("financial_conditions_tightening", 80, 0.9), score("credit_spread_baa_10y", 55, 0.9)]),
        ],
        "aggregate": {
            "candidate_indicators_requiring_refinement": ["credit_spread_baa_10y"],
        },
    }


def point(label: str, as_of: str, status: str, weighted: float, scores: list[dict]) -> dict:
    return {
        "scenario_id": "global_financial_crisis",
        "as_of": as_of,
        "label": label,
        "candidate_summary": {
            "boom_ending_status": status,
            "weighted_boom_ending_score": weighted,
        },
        "top_candidate_scores": scores,
        "group_summary": [
            {"group_id": "rates_policy", "scored_indicator_count": 1, "high_signal_count": 1, "avg_score": 78, "avg_confidence": 1, "status": "strong"},
            {"group_id": "credit_financial_conditions", "scored_indicator_count": 1, "high_signal_count": 0, "avg_score": 42, "avg_confidence": 0.8, "status": "weak"},
        ],
    }


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "display_name_zh": indicator_id,
        "score": value,
        "confidence": confidence,
        "reason_zh": "test",
    }
