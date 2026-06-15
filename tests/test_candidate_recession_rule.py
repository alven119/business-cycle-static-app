from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_candidate_recession_rule_report,
    classify_candidate_recession_status,
    load_candidate_recession_confirmation_rule,
)

RULE_PATH = Path("specs/backtests/candidate_recession_confirmation_rule.yaml")


def test_candidate_recession_rule_yaml_can_be_loaded() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert rule.version == 1
    assert rule.status == "experimental"
    assert any("修訂後歷史資料" in caveat for caveat in rule.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in rule.caveats_zh)


def test_candidate_recession_rule_classifies_confirmed_watch_weak_none() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert classify_candidate_recession_status(summary(82, 3, 4, 4), rule) == "confirmed"
    assert classify_candidate_recession_status(summary(65, 2, 3, 1), rule) == "watch"
    assert classify_candidate_recession_status(summary(50, 1, 1, 0), rule) == "weak"
    assert classify_candidate_recession_status(summary(40, 0, 0, 0), rule) == "none"


def test_high_weighted_score_without_breadth_cannot_confirm() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert classify_candidate_recession_status(summary(95, 1, 5, 5), rule) == "weak"


def test_late_cycle_like_point_is_weak_not_confirmed() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert classify_candidate_recession_status(summary(68.5057, 2, 2, 1), rule) == "weak"


def test_covid_2019_like_point_is_watch_not_confirmed() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert classify_candidate_recession_status(summary(61.0822, 3, 3, 1), rule) == "watch"


def test_covid_2020_and_gfc_like_points_can_confirm() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)

    assert classify_candidate_recession_status(summary(92.8883, 3, 4, 4), rule) == "confirmed"
    assert classify_candidate_recession_status(summary(98.9478, 4, 5, 4), rule) == "confirmed"


def test_candidate_recession_rule_report_matches_expected() -> None:
    rule = load_candidate_recession_confirmation_rule(RULE_PATH)
    diagnostics = {
        "points": [
            point("covid_recession", "2019-02-28", "covid_false_positive_candidate", summary(61.0822, 3, 3, 1)),
            point("covid_recession", "2020-03-31", "covid_true_recession_candidate", summary(92.8883, 3, 4, 4)),
            point("global_financial_crisis", "2008-10-31", "gfc_recession_confirmed", summary(98.9478, 4, 5, 4)),
            point("late_cycle_2018", "2018-12-31", "late_cycle_non_recession", summary(68.5057, 2, 2, 1)),
        ]
    }

    report = build_candidate_recession_rule_report(diagnostics, rule)

    assert report["summary"]["match_count"] == 4
    assert report["summary"]["mismatch_count"] == 0
    assert report["summary"]["confirmed_count"] == 2
    assert report["summary"]["watch_count"] == 1
    assert report["summary"]["weak_count"] == 1
    assert report["summary"]["false_confirmed_points"] == []


def summary(
    weighted_score: float,
    broad_groups: int,
    high_signals: int,
    high_confidence_high_signals: int,
) -> dict:
    return {
        "weighted_confirmation_score": weighted_score,
        "broad_group_count": broad_groups,
        "high_signal_count": high_signals,
        "high_confidence_high_signal_count": high_confidence_high_signals,
    }


def point(scenario_id: str, as_of: str, label: str, candidate_summary: dict) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "candidate_summary": candidate_summary,
    }
