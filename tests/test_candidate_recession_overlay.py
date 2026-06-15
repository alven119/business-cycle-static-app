from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_candidate_recession_overlay_report,
    load_candidate_recession_overlay_experiment,
)

SPEC_PATH = Path("specs/backtests/candidate_recession_overlay_experiment.yaml")


def test_candidate_recession_overlay_spec_can_be_loaded() -> None:
    spec = load_candidate_recession_overlay_experiment(SPEC_PATH)

    assert spec.version == 1
    assert spec.status == "experimental"
    assert spec.overlay_policy["target_phase"] == "recession"
    assert any("修訂後歷史資料" in caveat for caveat in spec.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in spec.caveats_zh)


def test_candidate_overlay_actions_and_summary() -> None:
    report = build_candidate_recession_overlay_report(
        timeline_loader=fake_timeline_loader,
        score_func=fake_score_func,
    )

    covid = scenario_detail(report, "covid_recession")
    actions = {period["as_of"]: period["overlay_action"] for period in covid["periods"]}
    assert actions["2019-02-28"] == "downgrade_confirmed_to_watch"
    assert actions["2020-03-31"] == "confirm_supported"

    gfc = scenario_detail(report, "global_financial_crisis")
    assert gfc["periods"][0]["overlay_action"] == "confirm_supported"

    dotcom = scenario_detail(report, "dotcom_bubble")
    assert dotcom["periods"][0]["overlay_action"] == "candidate_watch_only"

    euro = scenario_detail(report, "euro_debt_slowdown")
    assert euro["periods"][0]["overlay_action"] == "no_action"

    summaries = {item["scenario_id"]: item for item in report["scenario_summaries"]}
    assert summaries["covid_recession"]["downgraded_confirmed_count"] == 1
    assert summaries["covid_recession"]["candidate_supported_confirmed_count"] == 1
    assert summaries["global_financial_crisis"]["candidate_supported_confirmed_count"] == 1
    assert summaries["late_cycle_2018"]["first_overlay_confirmed_recession_as_of"] is None
    assert report["acceptance_summary"]["blocked_covid_2019_false_confirmed"] is True
    assert report["acceptance_summary"]["kept_gfc_confirmed"] is True
    assert report["acceptance_summary"]["out_of_sample_false_confirmed_count"] == 0


def test_candidate_overlay_missing_candidate_data_does_not_crash() -> None:
    report = build_candidate_recession_overlay_report(
        timeline_loader=lambda _scenario_id: {"periods": [period("2020-01-31", "boom", "confirmed", "recession")]},
        score_func=missing_score_func,
    )

    first_period = report["scenario_details"][0]["periods"][0]
    assert first_period["overlay_action"] == "missing_candidate_data"
    assert first_period["candidate_recession_status"] == "missing"


def test_candidate_overlay_caveats_are_present() -> None:
    report = build_candidate_recession_overlay_report(
        timeline_loader=fake_timeline_loader,
        score_func=fake_score_func,
    )

    assert any("修訂後歷史資料" in caveat for caveat in report["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in report["caveats_zh"])


def scenario_detail(report: dict, scenario_id: str) -> dict:
    return next(item for item in report["scenario_details"] if item["scenario_id"] == scenario_id)


def fake_timeline_loader(scenario_id: str) -> dict:
    timelines = {
        "covid_recession": {
            "periods": [
                period("2019-02-28", "recession", "confirmed", "recession", previous_phase_id="boom"),
                period("2020-03-31", "recession", "confirmed", "recession", previous_phase_id="boom"),
            ]
        },
        "global_financial_crisis": {
            "periods": [period("2008-10-31", "recession", "confirmed", "recession")]
        },
        "dotcom_bubble": {
            "periods": [period("2001-01-31", "boom", "hold_current", "recession")]
        },
        "euro_debt_slowdown": {
            "periods": [period("2011-12-31", "growth", "hold_current", "growth")]
        },
        "late_cycle_2018": {
            "periods": [period("2018-12-31", "growth", "hold_current", "boom")]
        },
    }
    return timelines[scenario_id]


def period(
    as_of: str,
    current_phase_id: str,
    decision_status: str,
    candidate_phase_id: str,
    previous_phase_id: str = "boom",
) -> dict:
    return {
        "as_of": as_of,
        "previous_phase_id": previous_phase_id,
        "current_phase_id": current_phase_id,
        "decision_status": decision_status,
        "candidate_phase_id": candidate_phase_id,
    }


def fake_score_func(*, as_of: str, **_: object) -> dict:
    if as_of in {"2020-03-31", "2008-10-31"}:
        scores = [
            score("continuing_jobless_claims", 90, 0.9),
            score("insured_unemployment_rate", 90, 0.9),
            score("industrial_production", 90, 0.9),
            score("financial_stress_index", 90, 0.9),
        ]
    elif as_of in {"2019-02-28", "2001-01-31"}:
        scores = [
            score("continuing_jobless_claims", 80, 0.9),
            score("industrial_production", 75, 0.6),
            score("credit_spread_baa_aaa", 70, 0.6),
        ]
    else:
        scores = [score("continuing_jobless_claims", 70, 0.6)]
    return {"scores": scores, "failures": [], "warnings": []}


def missing_score_func(**_: object) -> dict:
    return {"scores": [], "failures": [{"error_type": "MissingRawCsv"}], "warnings": []}


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "score": value,
        "confidence": confidence,
        "display_name_zh": indicator_id,
        "reason_zh": "test",
    }
