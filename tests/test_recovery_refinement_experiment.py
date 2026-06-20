from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_recovery_refinement_experiment,
    load_recovery_diagnostic_windows,
    load_recovery_scoring_refinement_experiment,
)

EXPERIMENT_PATH = Path("specs/backtests/recovery_scoring_refinement_experiment.yaml")
WINDOWS_PATH = Path("specs/backtests/recovery_diagnostic_windows.yaml")


def test_recovery_refinement_experiment_spec_can_be_loaded() -> None:
    experiment = load_recovery_scoring_refinement_experiment(EXPERIMENT_PATH)

    assert experiment["version"] == 1
    assert experiment["refined_profile"]["profile_id"] == "recovery_refined_v1"


def test_recovery_refinement_experiment_compares_baseline_and_refined() -> None:
    report = build_recovery_refinement_experiment(
        experiment_path=EXPERIMENT_PATH,
        windows_path=WINDOWS_PATH,
        baseline_diagnostics=fake_baseline(),
        refined_score_func=fake_refined_scores,
    )
    summary = report["summary"]

    assert report["baseline_lookup_warning_count"] == 0
    assert summary["euro_debt_false_strong_fixed"] is True
    assert summary["late_cycle_2018_false_watch_fixed"] is True
    assert summary["gfc_trough_watch_preserved"] is True
    assert summary["dotcom_recovery_watch_improved"] is True
    assert summary["policy_only_strong_blocked"] is True
    assert point(report, "euro_debt_non_recession")["baseline_status"] == "strong"
    assert point(report, "euro_debt_non_recession")["refined_status"] == "weak"
    assert point(report, "euro_debt_non_recession")["status_delta"] == "improved"
    assert point(report, "dotcom_recovery_initial")["baseline_status"] == "weak"
    assert point(report, "dotcom_recovery_initial")["refined_status"] == "watch"
    assert any("recovery watch 不等於正式復甦確認" in caveat for caveat in report["caveats_zh"])
    assert any("policy easing 不得單獨確認 recovery" in caveat for caveat in report["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in report["caveats_zh"])


def test_recovery_refinement_experiment_records_baseline_warnings() -> None:
    baseline = fake_baseline()
    baseline["points"][0].pop("candidate_summary")

    report = build_recovery_refinement_experiment(
        experiment_path=EXPERIMENT_PATH,
        windows_path=WINDOWS_PATH,
        baseline_diagnostics=baseline,
        refined_score_func=fake_refined_scores,
    )

    assert report["baseline_lookup_warning_count"] > 0


def fake_baseline() -> dict:
    windows = load_recovery_diagnostic_windows(WINDOWS_PATH)
    statuses = {
        "dotcom_recovery_initial": "weak",
        "euro_debt_non_recession": "strong",
        "late_cycle_2018_non_recession": "watch",
    }
    points = []
    for item in windows.points:
        status = statuses.get(item.label, "watch" if item.expected_status != "weak_or_none" else "weak")
        points.append(
            {
                "scenario_id": item.scenario_id,
                "as_of": item.as_of,
                "label": item.label,
                "recovery_status": status,
                "candidate_summary": {
                    "weighted_recovery_score": 80.0 if status == "strong" else 60.0,
                },
            }
        )
    return {"data_mode": "revised", "points": points}


def fake_refined_scores(**_: object) -> dict:
    return {
        "scores": [
            score("initial_jobless_claims_peak_reversal", 82, 0.9),
            score("real_retail_sales_bottoming", 78, 0.8),
            score("financial_stress_easing", 80, 0.9),
            score("fed_policy_easing_signal", 90, 0.6),
        ],
        "failures": [],
        "warnings": [],
    }


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "score": value,
        "confidence": confidence,
        "reason_zh": "test",
    }


def point(report: dict, label: str) -> dict:
    return next(item for item in report["points"] if item["label"] == label)
