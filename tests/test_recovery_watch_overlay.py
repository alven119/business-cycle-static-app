from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_recovery_watch_overlay_report,
    load_recovery_watch_overlay_experiment,
)

SPEC_PATH = Path("specs/backtests/recovery_watch_overlay_experiment.yaml")


def test_recovery_watch_overlay_spec_can_be_loaded() -> None:
    experiment = load_recovery_watch_overlay_experiment(SPEC_PATH)

    assert experiment.version == 1
    assert experiment.status == "experimental"
    caveats = "".join(experiment.caveats_zh)
    assert "修訂後歷史資料" in caveats
    assert "recovery watch 不等於正式復甦確認" in caveats
    assert "recovery watch 不是買進訊號" in caveats
    assert "不構成投資建議" in caveats


def test_recovery_watch_overlay_keeps_original_phase_and_summarizes(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path)

    report = build_recovery_watch_overlay_report(
        spec_path=spec_path,
        output_root=tmp_path,
        score_func=fake_score_func,
        timeline_loader=fake_timeline_loader,
    )

    assert report["scenario_count"] == 2
    gfc_detail = next(item for item in report["scenario_details"] if item["scenario_id"] == "global_financial_crisis")
    first_period = gfc_detail["periods"][0]
    assert first_period["original_current_phase_id"] == "recession"
    assert first_period["overlay_action"] == "watch_only"
    assert first_period["original_decision_status"] == "confirmed"

    gfc = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "global_financial_crisis")
    assert gfc["recovery_watch_count"] == 2
    assert gfc["strong_recovery_watch_count"] == 0
    assert gfc["recovery_watch_density_ratio"] == 0.6667
    assert gfc["first_recovery_watch_as_of"] == "2009-06-30"
    assert gfc["first_original_recovery_phase_as_of"] == "2009-08-31"
    assert gfc["watch_lead_or_lag_months_vs_original_recovery"] == 2
    assert gfc["longest_recovery_watch_streak_months"] == 2
    assert gfc["policy_only_blocked_count"] == 1
    assert gfc["context_gate_blocked_count"] == 0
    assert report["acceptance_summary"]["gfc_has_trough_or_recovery_watch"] is True
    assert "不構成投資建議" in "".join(report["caveats_zh"])


def test_recovery_watch_overlay_detects_excessive_watch_and_covid_caveat(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path, scenario_ids=["covid_recession", "late_cycle_2018"])

    report = build_recovery_watch_overlay_report(
        spec_path=spec_path,
        output_root=tmp_path,
        score_func=always_watch_score_func,
        timeline_loader=long_watch_timeline_loader,
    )

    late_cycle = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "late_cycle_2018")
    covid = next(item for item in report["scenario_summaries"] if item["scenario_id"] == "covid_recession")
    assert late_cycle["recovery_watch_density_ratio"] > 0.9
    assert late_cycle["longest_recovery_watch_streak_months"] > 18
    assert report["acceptance_summary"]["late_cycle_2018_excessive_recovery_watch"] is True
    assert late_cycle["acceptance_status"] == "warning"
    assert covid["acceptance_status"] == "warning"
    assert covid["exogenous_shock_caveat_count"] == 24
    assert report["acceptance_summary"]["covid_caveated_recovery_watch"] is True
    assert any("外生衝擊" in note for note in covid["notes_zh"])


def test_recovery_watch_overlay_counts_policy_and_context_blocks(tmp_path: Path) -> None:
    spec_path = write_spec(tmp_path, scenario_ids=["euro_debt_slowdown"])

    report = build_recovery_watch_overlay_report(
        spec_path=spec_path,
        output_root=tmp_path,
        score_func=policy_only_score_func,
        timeline_loader=non_recession_timeline_loader,
    )

    summary = report["scenario_summaries"][0]
    assert summary["recovery_watch_count"] == 0
    assert summary["policy_only_blocked_count"] == 2
    assert summary["context_gate_blocked_count"] == 2
    assert report["acceptance_summary"]["euro_debt_excessive_recovery_watch"] is False


def fake_score_func(*, as_of: str, **_: object) -> dict:
    if as_of in {"2009-06-30", "2009-07-31"}:
        scores = [
            score("initial_jobless_claims_peak_reversal", 82, 0.9),
            score("real_pce_bottoming", 78, 0.8),
            score("credit_spread_easing", 72, 0.7),
        ]
    else:
        scores = [score("fed_policy_easing_signal", 78, 0.8)]
    return {"scores": scores, "failures": [], "warnings": []}


def always_watch_score_func(**_: object) -> dict:
    return {
        "scores": [
            score("initial_jobless_claims_peak_reversal", 82, 0.9),
            score("real_pce_bottoming", 78, 0.8),
            score("credit_spread_easing", 72, 0.7),
        ],
        "failures": [],
    }


def policy_only_score_func(**_: object) -> dict:
    return {"scores": [score("fed_policy_easing_signal", 86, 0.9)], "failures": []}


def fake_timeline_loader(scenario_id: str) -> dict:
    periods = [
        period("2009-06-30", "recession", "confirmed", "recovery", 82),
        period("2009-07-31", "recession", "hold_current", "recovery", 75),
        period("2009-08-31", "recovery", "confirmed", "growth", 45),
    ]
    return {"scenario_id": scenario_id, "period_count": len(periods), "periods": periods}


def long_watch_timeline_loader(scenario_id: str) -> dict:
    periods = [period(f"2020-{month:02d}-28", "recession", "confirmed", "recovery", 85) for month in range(1, 13)]
    periods.extend([period(f"2021-{month:02d}-28", "recovery", "hold_current", "growth", 45) for month in range(1, 13)])
    return {"scenario_id": scenario_id, "period_count": len(periods), "periods": periods}


def non_recession_timeline_loader(scenario_id: str) -> dict:
    periods = [
        period("2011-11-30", "recovery", "hold_current", "growth", 30),
        period("2011-12-31", "recovery", "hold_current", "growth", 30),
    ]
    return {"scenario_id": scenario_id, "period_count": len(periods), "periods": periods}


def period(as_of: str, current_phase_id: str, decision_status: str, candidate_phase_id: str, recession_score: float) -> dict:
    return {
        "as_of": as_of,
        "current_phase_id": current_phase_id,
        "decision_status": decision_status,
        "candidate_phase_id": candidate_phase_id,
        "phase_scores": [{"phase_id": "recession", "score": recession_score}],
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
    window_start: "2009-06-01"
    window_end: "2009-08-31"
    focus_transition: recession_to_recovery
    baseline_phase_id: recession
    expected_focus_zh:
      - test
    benchmark_notes_zh: {"COVID 屬特殊外生衝擊。" if scenario_id == "covid_recession" else "test"}
    data_mode: revised
"""
            for scenario_id in scenarios
        ),
        encoding="utf-8",
    )
    candidate_spec = tmp_path / "candidate.yaml"
    candidate_spec.write_text("recovery_candidate_indicators: {version: 1, indicators: []}\n", encoding="utf-8")
    rule = Path("specs/backtests/recovery_watch_rule.yaml")
    refinement = write_refinement_spec(tmp_path)
    path = tmp_path / "overlay.yaml"
    path.write_text(
        f"""
recovery_watch_overlay_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 此為 experimental overlay，不代表正式模型已更新。
    - recovery watch 不等於正式復甦確認。
    - recovery watch 不是買進訊號。
    - policy easing 不得單獨確認 recovery。
    - financial easing 不得單獨確認 recovery。
    - 外生衝擊案例中，COVID 快速反彈不等同一般景氣循環復甦。
    - 不構成投資建議。
  inputs:
    scenario_spec: {catalog_path}
    recovery_candidate_spec: {candidate_spec}
    recovery_watch_rule: {rule}
    recovery_refinement_experiment: {refinement}
  overlay_policy:
    do_not_change_current_phase: true
    do_not_confirm_recovery: true
    do_not_create_portfolio_action: true
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
recovery_scoring_refinement_experiment:
  version: 1
  status: experimental
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - recovery watch 不等於正式復甦確認。
    - policy easing 不得單獨確認 recovery。
    - 不構成投資建議。
  refined_profile:
    profile_id: test
    recession_context_gate:
      enabled: true
      lookback_months: 12
      min_recession_depth_score: 60.0
    support_signal_cap:
      enabled: true
      policy_financial_only_max_status: weak
      require_labor_or_real_activity_for_watch: true
    exogenous_shock_profile:
      enabled: true
      allow_fast_trough_watch_with_caveat: true
      max_status_without_labor_confirmation: watch
  expected_refinement_outcomes: []
""",
        encoding="utf-8",
    )
    return path
