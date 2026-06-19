from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_boom_ending_watch_overlay_report,
    load_boom_ending_watch_overlay_experiment,
)

SPEC_PATH = Path("specs/backtests/boom_ending_watch_overlay_experiment.yaml")


def test_boom_ending_watch_overlay_spec_can_be_loaded() -> None:
    experiment = load_boom_ending_watch_overlay_experiment(SPEC_PATH)

    assert experiment.version == 1
    assert experiment.status == "experimental"
    assert any("修訂後歷史資料" in caveat for caveat in experiment.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in experiment.caveats_zh)
    assert any("不等於 confirmed recession" in caveat for caveat in experiment.caveats_zh)
    assert any("外生衝擊" in caveat for caveat in experiment.caveats_zh)


def test_boom_ending_watch_overlay_keeps_original_phase_and_summarizes(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)

    report = build_boom_ending_watch_overlay_report(
        spec_path=spec_path,
        output_root=tmp_path,
        score_func=fake_score_func,
        timeline_loader=fake_timeline_loader,
    )

    assert report["scenario_count"] == 2
    dotcom_detail = next(item for item in report["scenario_details"] if item["scenario_id"] == "dotcom_bubble")
    first_period = dotcom_detail["periods"][0]
    assert first_period["original_current_phase_id"] == "boom"
    assert first_period["overlay_action"] == "watch_only"
    assert first_period["original_decision_status"] == "hold_current"

    dotcom = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "dotcom_bubble")
    assert dotcom["watch_count"] == 2
    assert dotcom["strong_late_cycle_warning_count"] == 0
    assert dotcom["watch_density_ratio"] == 0.6667
    assert dotcom["first_watch_as_of"] == "2000-01-31"
    assert dotcom["first_original_confirmed_recession_as_of"] == "2000-03-31"
    assert dotcom["watch_lead_time_months"] == 2
    assert dotcom["longest_watch_streak_months"] == 2
    assert report["acceptance_summary"]["dotcom_has_pre_recession_watch"] is True
    assert "不構成投資建議" in "".join(report["caveats_zh"])


def test_boom_ending_watch_overlay_detects_excessive_watch_and_covid_caveat(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path, scenario_ids=["covid_recession", "late_cycle_2018"])

    report = build_boom_ending_watch_overlay_report(
        spec_path=spec_path,
        output_root=tmp_path,
        score_func=always_watch_score_func,
        timeline_loader=long_watch_timeline_loader,
    )

    late_cycle = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "late_cycle_2018")
    covid = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "covid_recession")
    assert late_cycle["watch_density_ratio"] == 1.0
    assert late_cycle["longest_watch_streak_months"] == 24
    assert report["acceptance_summary"]["late_cycle_2018_excessive_watch"] is True
    assert late_cycle["acceptance_status"] == "warning"
    assert covid["acceptance_status"] == "warning"
    assert any("外生衝擊" in note for note in covid["notes_zh"])


def fake_score_func(*, as_of: str, **_: object) -> dict:
    if as_of in {"2000-01-31", "2000-02-29"}:
        scores = [
            score("yield_curve_10y_3m", 82, 0.9),
            score("credit_spread_baa_10y", 78, 0.8),
            score("industrial_production_momentum_loss", 72, 0.7),
        ]
    else:
        scores = [score("yield_curve_10y_3m", 40, 0.9)]
    return {"scores": scores, "failures": [], "warnings": []}


def always_watch_score_func(**_: object) -> dict:
    return {
        "scores": [
            score("yield_curve_10y_3m", 82, 0.9),
            score("credit_spread_baa_10y", 78, 0.8),
            score("industrial_production_momentum_loss", 72, 0.7),
        ],
        "failures": [],
    }


def fake_timeline_loader(scenario_id: str) -> dict:
    periods = [
        period("2000-01-31", "boom", "hold_current"),
        period("2000-02-29", "boom", "transition_watch"),
        period("2000-03-31", "recession", "confirmed"),
    ]
    return {"scenario_id": scenario_id, "period_count": len(periods), "periods": periods}


def long_watch_timeline_loader(scenario_id: str) -> dict:
    periods = [period(f"2018-{month:02d}-28", "boom", "hold_current") for month in range(1, 13)]
    periods.extend([period(f"2019-{month:02d}-28", "boom", "hold_current") for month in range(1, 13)])
    return {"scenario_id": scenario_id, "period_count": len(periods), "periods": periods}


def period(as_of: str, current_phase_id: str, decision_status: str) -> dict:
    return {
        "as_of": as_of,
        "current_phase_id": current_phase_id,
        "decision_status": decision_status,
        "candidate_phase_id": "recession",
    }


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {"indicator_id": indicator_id, "score": value, "confidence": confidence, "reason_zh": "test"}


def write_spec(tmp_path: Path, scenario_ids: list[str] | None = None) -> Path:
    scenarios = scenario_ids or ["dotcom_bubble", "global_financial_crisis"]
    catalog_path = tmp_path / "scenarios.yaml"
    catalog_path.write_text(
        "scenarios:\n"
        + "\n".join(
            f"""
  - scenario_id: {scenario_id}
    display_name_zh: {scenario_id}
    display_name_en: {scenario_id}
    window_start: "2000-01-01"
    window_end: "2000-03-31"
    focus_transition: boom_to_recession
    baseline_phase_id: boom
    expected_focus_zh:
      - test
    benchmark_notes_zh: test
    data_mode: revised
"""
            for scenario_id in scenarios
        ),
        encoding="utf-8",
    )
    candidate_spec = tmp_path / "candidate.yaml"
    candidate_spec.write_text("boom_ending_candidate_indicators: {version: 1, indicators: []}\n", encoding="utf-8")
    rule = Path("specs/backtests/boom_ending_watch_rule.yaml")
    refinement = write_refinement_spec(tmp_path)
    path = tmp_path / "overlay.yaml"
    path.write_text(
        f"""
boom_ending_watch_overlay_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為 experimental overlay，不代表正式模型已更新。
    - boom ending watch 不等於 confirmed recession。
    - 外生衝擊案例中，boom ending 指標可能是同步壓力反映，不代表事前預測。
    - 不構成投資建議。
  inputs:
    scenario_spec: {catalog_path}
    boom_ending_candidate_spec: {candidate_spec}
    boom_ending_watch_rule: {rule}
    boom_ending_refinement_experiment: {refinement}
  overlay_policy:
    do_not_change_current_phase: true
  evaluation: {{}}
  acceptance_targets: []
""",
        encoding="utf-8",
    )
    return path


def write_refinement_spec(tmp_path: Path) -> Path:
    path = tmp_path / "refinement.yaml"
    path.write_text(
        """
boom_ending_scoring_refinement_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  refined_profile:
    profile_id: test
  expected_refinement_outcomes:
    - scenario_id: dotcom_bubble
      as_of: "2000-01-31"
      expected_min_status: watch
""",
        encoding="utf-8",
    )
    return path
