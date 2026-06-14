from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.backtests import (
    CalibrationPlanError,
    load_backtest_scenarios,
    load_calibration_plan,
    validate_calibration_plan,
)

CALIBRATION_PLAN_PATH = Path("specs/backtests/calibration_plan.yaml")
SCENARIOS_PATH = Path("specs/backtests/scenarios.yaml")


def test_calibration_plan_yaml_can_be_loaded() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)

    assert plan.version == 1
    assert plan.status == "draft"
    assert "不直接修改模型" in plan.objective_zh
    validate_calibration_plan(plan)


def test_calibration_plan_contains_required_caveats() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in plan.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in plan.caveats_zh)
    assert any("不得只針對單一歷史案例最佳化" in caveat for caveat in plan.caveats_zh)


def test_calibration_plan_diagnosed_issues_and_actions() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)
    issues = {issue["issue_id"]: issue for issue in plan.diagnosed_issues}

    assert set(issues) == {
        "direct_confirmed_without_watch",
        "short_phase_segment",
        "rapid_round_trip",
        "concentrated_indicator_delta",
        "incomplete_book_indicator_coverage",
    }
    assert "require_transition_watch_before_confirmed" in issues[
        "direct_confirmed_without_watch"
    ]["proposed_actions"]
    assert "add_group_breadth_rule" in issues["concentrated_indicator_delta"]["proposed_actions"]


def test_calibration_plan_candidate_controls_are_machine_readable() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)
    controls = plan.candidate_model_controls

    assert controls["confirmation_period"]["initial_candidates"] == [2, 3]
    assert controls["transition_watch_required"]["initial_value"] is True
    assert controls["hysteresis_margin"]["initial_candidates"] == [5, 10, 15]
    assert "confirmation_period" in controls
    assert "breadth_confirmation" in controls
    assert "hysteresis_margin" in controls
    assert "employment" in controls["breadth_confirmation"]["groups"]
    assert "initial_jobless_claims" in controls["indicator_smoothing"]["candidate_indicators"]


def test_calibration_plan_scenario_split_and_acceptance_criteria() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)

    assert plan.calibration_scenarios["in_sample"] == [
        "dotcom_bubble",
        "global_financial_crisis",
        "covid_recession",
    ]
    assert plan.calibration_scenarios["out_of_sample"] == [
        "euro_debt_slowdown",
        "late_cycle_2018",
    ]
    criteria = {item["criterion_id"]: item for item in plan.acceptance_criteria}
    assert criteria["preserve_non_recession_cases"]["target"] == "no_new_false_recession"
    assert criteria["keep_revised_data_caveat"]["target"] == "required"


def test_calibration_plan_scenarios_exist_in_catalog() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)
    known_scenario_ids = {scenario.scenario_id for scenario in load_backtest_scenarios(SCENARIOS_PATH)}
    plan_scenario_ids = set(plan.calibration_scenarios["in_sample"]) | set(
        plan.calibration_scenarios["out_of_sample"]
    )

    assert plan_scenario_ids <= known_scenario_ids


def test_calibration_plan_next_phases_are_declared() -> None:
    plan = load_calibration_plan(CALIBRATION_PLAN_PATH)

    assert [phase["phase_id"] for phase in plan.next_phases] == ["7B", "7C", "7D"]


def test_calibration_plan_missing_caveat_raises(tmp_path: Path) -> None:
    path = tmp_path / "calibration_plan.yaml"
    path.write_text(
        """
calibration_plan:
  version: 1
  status: draft
  objective_zh: 測試
  caveats_zh:
    - 使用修訂後歷史資料。
  diagnosed_issues:
    - issue_id: issue
      display_name_zh: 測試
      evidence_zh: 測試
      likely_causes_zh:
        - 測試
      proposed_actions:
        - action
  candidate_model_controls:
    control:
      description_zh: 測試
  calibration_scenarios:
    in_sample:
      - a
    out_of_sample:
      - b
  acceptance_criteria:
    - criterion_id: criterion
      description_zh: 測試
      target: required
  next_phases:
    - phase_id: 7B
      title: 測試
""",
        encoding="utf-8",
    )

    with pytest.raises(CalibrationPlanError, match="no-investment-advice"):
        load_calibration_plan(path)


def test_calibration_plan_overlapping_scenario_split_raises(tmp_path: Path) -> None:
    path = tmp_path / "calibration_plan.yaml"
    payload = CALIBRATION_PLAN_PATH.read_text(encoding="utf-8").replace(
        "out_of_sample:\n      - euro_debt_slowdown",
        "out_of_sample:\n      - dotcom_bubble",
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(CalibrationPlanError, match="must not overlap"):
        load_calibration_plan(path)


def test_calibration_plan_duplicate_issue_id_raises(tmp_path: Path) -> None:
    path = tmp_path / "calibration_plan.yaml"
    payload = CALIBRATION_PLAN_PATH.read_text(encoding="utf-8").replace(
        "issue_id: short_phase_segment",
        "issue_id: direct_confirmed_without_watch",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(CalibrationPlanError, match="duplicate issue_id"):
        load_calibration_plan(path)


def test_calibration_plan_duplicate_acceptance_criterion_id_raises(tmp_path: Path) -> None:
    path = tmp_path / "calibration_plan.yaml"
    payload = CALIBRATION_PLAN_PATH.read_text(encoding="utf-8").replace(
        "criterion_id: reduce_short_segments",
        "criterion_id: no_direct_confirmed_without_watch",
        1,
    )
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(CalibrationPlanError, match="duplicate criterion_id"):
        load_calibration_plan(path)
