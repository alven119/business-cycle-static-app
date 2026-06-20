from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_recovery_watch_rule_report,
    classify_recovery_watch_status,
    load_recovery_watch_rule,
)

RULE_PATH = Path("specs/backtests/recovery_watch_rule.yaml")


def test_recovery_watch_rule_yaml_can_be_loaded() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    assert rule.version == 1
    assert rule.status == "experimental"
    caveats = "".join(rule.caveats_zh)
    assert "修訂後歷史資料" in caveats
    assert "recovery watch 不等於正式復甦確認" in caveats
    assert "policy easing 不得單獨確認 recovery" in caveats
    assert "financial easing 不得單獨確認 recovery" in caveats
    assert "不構成投資建議" in caveats


def test_recovery_watch_rule_classifies_statuses() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    assert classify_recovery_watch_status(summary(82, 3, 4, 4), rule) == "strong_recovery_watch"
    assert classify_recovery_watch_status(summary(66, 2, 3, 2), rule) == "recovery_watch"
    assert classify_recovery_watch_status(summary(50, 1, 1, 0), rule) == "weak"
    assert classify_recovery_watch_status(summary(40, 0, 0, 0), rule) == "none"


def test_without_recession_context_status_is_capped_at_weak() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    status = classify_recovery_watch_status(
        summary(90, 4, 5, 5, recession_context=False, context_gate_applied=True),
        rule,
    )

    assert status == "weak"


def test_policy_or_financial_only_signals_are_capped_at_weak() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    status = classify_recovery_watch_status(
        summary(
            90,
            3,
            4,
            4,
            policy_only=True,
            support_cap_applied=True,
            labor_confirmed=False,
            real_activity_confirmed=False,
            credit_confirmed=True,
        ),
        rule,
    )

    assert status == "weak"


def test_exogenous_shock_allows_caveated_watch_but_not_strong_without_labor_and_activity() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    status = classify_recovery_watch_status(
        summary(
            90,
            4,
            5,
            5,
            exogenous_shock=True,
            labor_confirmed=True,
            real_activity_confirmed=False,
            credit_confirmed=True,
        ),
        rule,
    )

    assert status == "recovery_watch"


def test_exogenous_shock_watch_floor_can_override_support_cap_but_not_strong() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)

    status = classify_recovery_watch_status(
        summary(
            62,
            2,
            2,
            1,
            exogenous_shock=True,
            support_cap_applied=True,
            labor_confirmed=False,
            real_activity_confirmed=False,
            credit_confirmed=True,
            refined_status="watch",
            exogenous_shock_watch_floor=True,
        ),
        rule,
    )

    assert status == "recovery_watch"


def test_non_recession_cases_do_not_enter_watch_or_strong() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)
    refinement = {
        "points": [
            point(
                "euro_debt_slowdown",
                "2011-12-31",
                "euro_debt_non_recession",
                summary(82, 4, 5, 4, recession_context=False, context_gate_applied=True),
            ),
            point(
                "late_cycle_2018",
                "2018-12-31",
                "late_cycle_2018_non_recession",
                summary(70, 3, 4, 2, recession_context=False, context_gate_applied=True),
            ),
        ]
    }

    report = build_recovery_watch_rule_report(refinement, rule)

    assert report["summary"]["match_count"] == 2
    assert report["summary"]["non_recession_watch_points"] == []
    statuses = {item["label"]: item["experimental_recovery_watch_status"] for item in report["points"]}
    assert statuses["euro_debt_non_recession"] == "weak"
    assert statuses["late_cycle_2018_non_recession"] == "weak"


def test_recovery_watch_report_matches_expected_outcomes() -> None:
    rule = load_recovery_watch_rule(RULE_PATH)
    refinement = {
        "points": [
            point("dotcom_bubble", "2002-03-31", "dotcom_recovery_initial", summary(68, 2, 3, 2)),
            point("global_financial_crisis", "2009-09-30", "gfc_recovery_initial", summary(82, 3, 4, 4)),
            point(
                "covid_recession",
                "2020-04-30",
                "covid_trough_area",
                summary(70, 2, 3, 2, exogenous_shock=True),
            ),
        ]
    }

    report = build_recovery_watch_rule_report(refinement, rule)

    assert report["summary"]["match_count"] == 3
    assert report["summary"]["mismatch_count"] == 0
    assert report["summary"]["missed_recovery_watch_points"] == []
    assert any(point["exogenous_shock_caveat"] for point in report["points"])
    assert "不構成投資建議" in "".join(report["caveats_zh"])


def summary(
    weighted_score: float,
    broad_groups: int,
    high_signals: int,
    high_confidence_high_signals: int,
    *,
    policy_only: bool = False,
    support_cap_applied: bool = False,
    context_gate_applied: bool = False,
    recession_context: bool = True,
    exogenous_shock: bool = False,
    labor_confirmed: bool = True,
    real_activity_confirmed: bool = True,
    credit_confirmed: bool = True,
    refined_status: str = "",
    exogenous_shock_watch_floor: bool = False,
) -> dict:
    return {
        "refined_status": refined_status,
        "weighted_recovery_score": weighted_score,
        "broad_group_count": broad_groups,
        "high_signal_count": high_signals,
        "high_confidence_high_signal_count": high_confidence_high_signals,
        "policy_only_signal": policy_only,
        "support_signal_cap_applied": support_cap_applied,
        "context_gate_applied": context_gate_applied,
        "recession_context_detected": recession_context,
        "exogenous_shock_caveat": exogenous_shock,
        "labor_confirmed": labor_confirmed,
        "real_activity_confirmed": real_activity_confirmed,
        "credit_financial_confirmed": credit_confirmed,
        "exogenous_shock_caveated_watch_floor": exogenous_shock_watch_floor,
    }


def point(scenario_id: str, as_of: str, label: str, point_summary: dict) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "refined_status": "watch",
        "candidate_summary_before_caps": {
            "weighted_recovery_score": point_summary["weighted_recovery_score"],
            "broad_group_count": point_summary["broad_group_count"],
            "high_signal_count": point_summary["high_signal_count"],
            "high_confidence_high_signal_count": point_summary["high_confidence_high_signal_count"],
            "policy_only_signal": point_summary["policy_only_signal"],
            "labor_confirmed": point_summary["labor_confirmed"],
            "real_activity_confirmed": point_summary["real_activity_confirmed"],
            "credit_financial_confirmed": point_summary["credit_financial_confirmed"],
        },
        "support_signal_cap_applied": point_summary["support_signal_cap_applied"],
        "context_gate_applied": point_summary["context_gate_applied"],
        "support_cap_summary": {
            "support_only_cap_applied": point_summary["support_signal_cap_applied"],
        },
        "context_gate_summary": {
            "recession_context_detected": point_summary["recession_context_detected"],
            "context_gate_applied": point_summary["context_gate_applied"],
            "exogenous_shock_caveat": point_summary["exogenous_shock_caveat"],
        },
    }
