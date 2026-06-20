from __future__ import annotations

from business_cycle.backtests import build_recovery_attribution


def test_recovery_attribution_summary_is_built() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())

    assert attribution["point_count"] == 7
    assert attribution["mismatch_count"] == 2
    assert attribution["comparisons"]["gfc_progression"]["status_trend"] == ["weak", "watch", "watch", "strong"]
    assert any("recovery watch 不等於正式復甦確認" in caveat for caveat in attribution["caveats_zh"])
    assert any("policy easing 不得單獨確認 recovery" in caveat for caveat in attribution["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in attribution["caveats_zh"])


def test_recovery_attribution_top_positive_indicators() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())
    point = next(item for item in attribution["points"] if item["label"] == "gfc_recovery_initial")

    indicator_ids = [item["indicator_id"] for item in point["top_positive_indicators"]]
    assert indicator_ids == ["financial_stress_easing", "initial_jobless_claims_peak_reversal"]


def test_recovery_attribution_weak_but_important_indicators() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())
    point = next(item for item in attribution["points"] if item["label"] == "dotcom_recovery_initial")

    weak_ids = [item["indicator_id"] for item in point["weak_but_important_indicators"]]
    assert "initial_jobless_claims_peak_reversal" in weak_ids


def test_recovery_attribution_confirmation_flags_are_preserved() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())
    point = next(item for item in attribution["points"] if item["label"] == "gfc_recovery_initial")

    assert point["policy_only_signal"] is False
    assert point["labor_confirmed"] is True
    assert point["real_activity_confirmed"] is True
    assert point["credit_financial_confirmed"] is True


def test_recovery_attribution_false_positive_review() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())
    review = attribution["comparisons"]["false_positive_review"]

    assert review["labels"] == ["euro_debt_non_recession", "late_cycle_2018_non_recession"]
    assert review["status_trend"] == ["strong", "watch"]


def test_recovery_attribution_refinement_candidates_include_expected_items() -> None:
    attribution = build_recovery_attribution(fake_diagnostics())
    candidate_ids = [item["indicator_id"] for item in attribution["refinement_candidates"]]

    assert "financial_stress_easing" in candidate_ids
    assert "initial_jobless_claims_peak_reversal" in candidate_ids
    assert "recession_context_gate" in candidate_ids


def fake_diagnostics() -> dict:
    return {
        "data_mode": "revised",
        "points": [
            point(
                "gfc_crisis_peak",
                "2008-10-31",
                "global_financial_crisis",
                "weak",
                "weak_or_none",
                True,
                48.0,
                [score("fed_policy_easing_signal", 78, 0.9)],
                policy_only=True,
            ),
            point(
                "gfc_policy_stress_easing_but_labor_not_ready",
                "2009-03-31",
                "global_financial_crisis",
                "watch",
                "weak_or_watch",
                True,
                67.0,
                [score("financial_stress_easing", 82, 0.9), score("credit_spread_easing", 70, 0.8)],
                credit=True,
            ),
            point(
                "gfc_trough_area",
                "2009-06-30",
                "global_financial_crisis",
                "watch",
                "watch_or_strong",
                True,
                71.0,
                [score("financial_stress_easing", 80, 0.9), score("real_pce_bottoming", 68, 0.8)],
                real=True,
                credit=True,
            ),
            point(
                "gfc_recovery_initial",
                "2009-09-30",
                "global_financial_crisis",
                "strong",
                "watch_or_strong",
                True,
                86.0,
                [score("financial_stress_easing", 88, 0.9), score("initial_jobless_claims_peak_reversal", 82, 0.9)],
                labor=True,
                real=True,
                credit=True,
            ),
            point(
                "dotcom_recovery_initial",
                "2002-03-31",
                "dotcom_bubble",
                "weak",
                "watch_or_strong",
                False,
                51.0,
                [score("financial_stress_easing", 64, 0.9), score("initial_jobless_claims_peak_reversal", 42, 0.7)],
            ),
            point(
                "euro_debt_non_recession",
                "2011-12-31",
                "euro_debt_slowdown",
                "strong",
                "weak_or_none",
                False,
                83.0,
                [score("financial_stress_easing", 89, 0.9), score("credit_spread_easing", 78, 0.8)],
                credit=True,
            ),
            point(
                "late_cycle_2018_non_recession",
                "2018-12-31",
                "late_cycle_2018",
                "watch",
                "weak_or_none",
                False,
                62.0,
                [score("financial_stress_easing", 72, 0.8), score("real_retail_sales_bottoming", 50, 0.7)],
                credit=True,
            ),
        ],
        "summary": {
            "mismatch_count": 2,
            "indicators_requiring_refinement": [
                "financial_stress_easing",
                "initial_jobless_claims_peak_reversal",
            ],
        },
    }


def point(
    label: str,
    as_of: str,
    scenario_id: str,
    status: str,
    expected: str,
    matches: bool,
    weighted: float,
    scores: list[dict],
    *,
    policy_only: bool = False,
    labor: bool = False,
    real: bool = False,
    credit: bool = False,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "expected_status": expected,
        "recovery_status": status,
        "matches_expected": matches,
        "candidate_summary": {
            "weighted_recovery_score": weighted,
            "policy_only_signal": policy_only,
            "labor_confirmed": labor,
            "real_activity_confirmed": real,
            "credit_financial_confirmed": credit,
        },
        "top_positive_indicators": scores,
        "weak_but_important_indicators": [
            {
                "indicator_id": "initial_jobless_claims_peak_reversal",
                "group_id": "labor_reversal",
                "score": 42,
                "confidence": 0.7,
            }
        ],
        "group_summary": [
            {"group_id": "labor_reversal", "scored_indicator_count": 1, "high_signal_count": int(labor), "avg_score": 62, "avg_confidence": 0.8, "status": "mixed"},
            {"group_id": "credit_financial_easing", "scored_indicator_count": 1, "high_signal_count": int(credit), "avg_score": 78, "avg_confidence": 0.9, "status": "strong"},
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
