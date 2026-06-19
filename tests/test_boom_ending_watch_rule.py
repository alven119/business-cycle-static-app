from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_boom_ending_watch_rule_report,
    classify_boom_ending_watch_status,
    load_boom_ending_watch_rule,
)

RULE_PATH = Path("specs/backtests/boom_ending_watch_rule.yaml")


def test_boom_ending_watch_rule_yaml_can_be_loaded() -> None:
    rule = load_boom_ending_watch_rule(RULE_PATH)

    assert rule.version == 1
    assert rule.status == "experimental"
    assert any("修訂後歷史資料" in caveat for caveat in rule.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in rule.caveats_zh)
    assert any("不等於 confirmed recession" in caveat for caveat in rule.caveats_zh)
    assert any("外生衝擊" in caveat for caveat in rule.caveats_zh)


def test_boom_ending_watch_rule_classifies_statuses() -> None:
    rule = load_boom_ending_watch_rule(RULE_PATH)

    assert classify_boom_ending_watch_status(summary(82, 3, 4, 4), rule) == "strong_late_cycle_warning"
    assert classify_boom_ending_watch_status(summary(65, 2, 3, 1), rule) == "watch"
    assert classify_boom_ending_watch_status(summary(50, 1, 1, 0), rule) == "weak"
    assert classify_boom_ending_watch_status(summary(40, 0, 0, 0), rule) == "none"


def test_rates_policy_cluster_can_watch_but_not_strong() -> None:
    rule = load_boom_ending_watch_rule(RULE_PATH)

    status = classify_boom_ending_watch_status(
        summary(
            weighted_score=58,
            broad_groups=1,
            high_signals=3,
            high_confidence_high_signals=3,
            rates_policy_high_signals=3,
        ),
        rule,
    )

    assert status == "watch"


def test_late_cycle_and_euro_debt_expected_watch_or_weak_not_unexpected_strong() -> None:
    rule = load_boom_ending_watch_rule(RULE_PATH)
    refinement = {
        "points": [
            point("late_cycle_2018", "2018-12-31", "late_cycle_2018_warning", summary(64, 2, 3, 1)),
            point("euro_debt_slowdown", "2011-12-31", "euro_debt_slowdown_warning", summary(48, 2, 2, 1)),
        ]
    }

    report = build_boom_ending_watch_rule_report(refinement, rule)

    assert report["summary"]["match_count"] == 2
    assert report["summary"]["unexpected_strong_points"] == []
    statuses = {item["label"]: item["experimental_watch_status"] for item in report["points"]}
    assert statuses["late_cycle_2018_warning"] == "watch"
    assert statuses["euro_debt_slowdown_warning"] == "weak"


def test_boom_ending_watch_rule_report_matches_expected() -> None:
    rule = load_boom_ending_watch_rule(RULE_PATH)
    refinement = {
        "points": [
            point("dotcom_bubble", "2000-03-31", "dotcom_market_peak_area", summary(68, 2, 3, 2)),
            point("global_financial_crisis", "2006-12-31", "gfc_yield_curve_warning", summary(64, 1, 3, 3, 3)),
            point("global_financial_crisis", "2007-12-31", "gfc_recession_window_start", summary(82, 3, 4, 4)),
            point("covid_recession", "2020-03-31", "covid_shock_recession", summary(76, 3, 4, 4)),
        ]
    }

    report = build_boom_ending_watch_rule_report(refinement, rule)

    assert report["summary"]["match_count"] == 4
    assert report["summary"]["mismatch_count"] == 0
    assert report["summary"]["strong_late_cycle_warning_count"] == 1
    assert report["summary"]["watch_count"] == 3
    assert report["summary"]["missed_watch_points"] == []
    assert "不構成投資建議" in "".join(report["caveats_zh"])


def summary(
    weighted_score: float,
    broad_groups: int,
    high_signals: int,
    high_confidence_high_signals: int,
    rates_policy_high_signals: int = 0,
) -> dict:
    return {
        "weighted_boom_ending_score": weighted_score,
        "broad_group_count": broad_groups,
        "high_signal_count": high_signals,
        "high_confidence_high_signal_count": high_confidence_high_signals,
        "rates_policy_high_signal_count": rates_policy_high_signals,
    }


def point(scenario_id: str, as_of: str, label: str, point_summary: dict) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "refined_score": point_summary["weighted_boom_ending_score"],
        "refined_broad_group_count": point_summary["broad_group_count"],
        "refined_high_signal_count": point_summary["high_signal_count"],
        "refined_high_confidence_high_signal_count": point_summary["high_confidence_high_signal_count"],
        "refined_group_summary": [
            {
                "group_id": "rates_policy",
                "high_signal_count": point_summary["rates_policy_high_signal_count"],
            }
        ],
    }
