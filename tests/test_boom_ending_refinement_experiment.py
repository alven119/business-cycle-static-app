from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_boom_ending_refinement_experiment,
    load_boom_ending_scoring_refinement_experiment,
)

EXPERIMENT_PATH = Path("specs/backtests/boom_ending_scoring_refinement_experiment.yaml")


def test_boom_ending_refinement_experiment_spec_can_be_loaded() -> None:
    experiment = load_boom_ending_scoring_refinement_experiment(EXPERIMENT_PATH)

    assert experiment["version"] == 1
    assert experiment["refined_profile"]["profile_id"] == "boom_ending_refined_v1"
    assert any("修訂後歷史資料" in caveat for caveat in experiment["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in experiment["caveats_zh"])


def test_boom_ending_refinement_comparison_and_expected_outcomes(tmp_path: Path) -> None:
    windows_path = write_windows(tmp_path)
    experiment_path = write_experiment(tmp_path)
    groups_path = write_groups(tmp_path)
    baseline = {
        "points": [
            baseline_point("global_financial_crisis", "2006-12-31", "gfc_yield_curve_warning", "weak", 50.0),
            baseline_point("late_cycle_2018", "2018-12-31", "late_cycle_2018_warning", "weak", 50.0),
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=tmp_path / "unused.yaml",
        cache_dir=tmp_path,
        baseline_diagnostics=baseline,
        refined_score_func=fake_refined_score_func,
    )

    points = {point["label"]: point for point in result["points"]}
    assert points["gfc_yield_curve_warning"]["baseline_status"] == "weak"
    assert points["gfc_yield_curve_warning"]["refined_status"] == "watch"
    assert points["gfc_yield_curve_warning"]["status_delta"] == "improved"
    assert points["gfc_yield_curve_warning"]["expected_result"] == "pass"
    assert points["late_cycle_2018_warning"]["refined_status"] == "strong"
    assert points["late_cycle_2018_warning"]["expected_result"] == "fail"
    assert result["baseline_lookup_warning_count"] == 0

    summary = result["summary"]
    assert summary["improved_count"] == 2
    assert summary["expected_pass_count"] == 1
    assert summary["expected_fail_count"] == 1
    assert summary["gfc_2006_improved_to_watch"] is True
    assert summary["late_cycle_2018_not_strong"] is False
    assert "boom_ending_watch_rule_thresholds" in result["refinement_candidates_still_open"]


def test_boom_ending_refinement_status_deltas_use_baseline_candidate_summary(tmp_path: Path) -> None:
    windows_path = write_delta_windows(tmp_path)
    experiment_path = write_delta_experiment(tmp_path)
    groups_path = write_groups(tmp_path)
    baseline = {
        "points": [
            baseline_point("scenario_a", "2000-01-31", "watch_to_weak", "watch", 70.0),
            baseline_point("scenario_a", "2000-02-29", "weak_to_watch", "weak", 45.0),
            baseline_point("scenario_a", "2000-03-31", "watch_to_watch", "watch", 65.0),
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=tmp_path / "unused.yaml",
        cache_dir=tmp_path,
        baseline_diagnostics=baseline,
        refined_score_func=fake_delta_refined_score_func,
    )

    points = {point["label"]: point for point in result["points"]}
    assert points["watch_to_weak"]["baseline_status"] == "watch"
    assert points["watch_to_weak"]["refined_status"] == "weak"
    assert points["watch_to_weak"]["status_delta"] == "regressed"
    assert points["weak_to_watch"]["baseline_status"] == "weak"
    assert points["weak_to_watch"]["refined_status"] == "watch"
    assert points["weak_to_watch"]["status_delta"] == "improved"
    assert points["watch_to_watch"]["baseline_status"] == "watch"
    assert points["watch_to_watch"]["refined_status"] == "watch"
    assert points["watch_to_watch"]["status_delta"] == "unchanged"
    assert result["summary"]["improved_count"] == 1
    assert result["summary"]["unchanged_count"] == 1
    assert result["summary"]["regressed_count"] == 1
    assert result["baseline_lookup_warning_count"] == 0


def test_boom_ending_refinement_warns_for_missing_baseline_status(tmp_path: Path) -> None:
    windows_path = write_delta_windows(tmp_path)
    experiment_path = write_delta_experiment(tmp_path)
    groups_path = write_groups(tmp_path)
    baseline = {
        "points": [
            {
                "scenario_id": "scenario_a",
                "as_of": "2000-01-31",
                "label": "watch_to_weak",
                "candidate_summary": {
                    "weighted_boom_ending_score": 70.0,
                    "broad_group_count": 2,
                },
            },
            baseline_point("scenario_a", "2000-02-29", "weak_to_watch", "weak", 45.0),
            baseline_point("scenario_a", "2000-03-31", "watch_to_watch", "watch", 65.0),
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=tmp_path / "unused.yaml",
        cache_dir=tmp_path,
        baseline_diagnostics=baseline,
        refined_score_func=fake_delta_refined_score_func,
    )

    assert result["baseline_lookup_warning_count"] == 1
    assert result["baseline_lookup_warnings"][0]["missing_field"] == "candidate_summary.boom_ending_status"


def test_boom_ending_refinement_warns_for_unmatched_baseline_point(tmp_path: Path) -> None:
    windows_path = write_delta_windows(tmp_path)
    experiment_path = write_delta_experiment(tmp_path)
    groups_path = write_groups(tmp_path)
    baseline = {
        "points": [
            baseline_point("scenario_a", "2000-01-31", "watch_to_weak", "watch", 70.0),
            baseline_point("scenario_a", "2000-02-29", "weak_to_watch", "weak", 45.0),
            baseline_point("scenario_a", "2000-03-31", "watch_to_watch", "watch", 65.0),
            baseline_point("scenario_a", "1999-12-31", "not_in_windows", "watch", 65.0),
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=tmp_path / "unused.yaml",
        cache_dir=tmp_path,
        baseline_diagnostics=baseline,
        refined_score_func=fake_delta_refined_score_func,
    )

    assert result["baseline_lookup_warning_count"] == 1
    assert result["baseline_lookup_warnings"][0]["unmatched_key"] is True


def test_boom_ending_refinement_retains_stronger_baseline_target_scores(tmp_path: Path) -> None:
    windows_path = write_single_window(tmp_path)
    experiment_path = write_single_experiment(tmp_path)
    groups_path = write_groups(tmp_path)
    spec_path = write_target_spec(tmp_path)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    write_series(cache_dir / "T10Y3M.csv", [1.0] * 20)
    baseline = {
        "points": [
            {
                "scenario_id": "scenario_a",
                "as_of": "2000-01-31",
                "label": "target_retention",
                "candidate_summary": {
                    "boom_ending_status": "watch",
                    "weighted_boom_ending_score": 70.0,
                    "broad_group_count": 2,
                    "high_signal_count": 3,
                    "high_confidence_high_signal_count": 1,
                },
                "top_candidate_scores": [
                    score("yield_curve_10y_3m", 80, 1.0),
                    score("credit_spread_baa_10y", 78, 0.8),
                    score("fed_policy_restrictive_pressure", 70, 0.7),
                ],
            }
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=spec_path,
        cache_dir=cache_dir,
        baseline_diagnostics=baseline,
        refined_score_func=weak_target_refined_score_func,
    )

    point = result["points"][0]
    assert point["baseline_status"] == "watch"
    assert point["refined_status"] == "watch"
    assert point["status_delta"] == "unchanged"
    target = next(item for item in point["top_refined_indicators"] if item["indicator_id"] == "yield_curve_10y_3m")
    assert target["refined_score_source"] == "baseline_retained"


def test_boom_ending_refinement_yield_curve_cluster_can_raise_watch(tmp_path: Path) -> None:
    windows_path = write_single_window(tmp_path)
    experiment_path = write_single_experiment(tmp_path)
    groups_path = write_rates_only_groups(tmp_path)
    baseline = {
        "points": [
            baseline_point("scenario_a", "2000-01-31", "target_retention", "weak", 55.0),
        ]
    }

    result = build_boom_ending_refinement_experiment(
        experiment_path=experiment_path,
        windows_path=windows_path,
        groups_path=groups_path,
        candidate_spec_path=tmp_path / "unused.yaml",
        cache_dir=tmp_path,
        baseline_diagnostics=baseline,
        refined_score_func=rates_cluster_refined_score_func,
    )

    point = result["points"][0]
    assert point["baseline_status"] == "weak"
    assert point["refined_status"] == "watch"
    assert point["status_delta"] == "improved"
    assert point["refined_status_adjustment"]["kind"] == "yield_curve_policy_cluster_watch_floor"


def baseline_point(
    scenario_id: str,
    as_of: str,
    label: str,
    status: str,
    weighted_score: float,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "label": label,
        "candidate_summary": {
            "boom_ending_status": status,
            "weighted_boom_ending_score": weighted_score,
            "broad_group_count": 1,
        },
    }


def fake_refined_score_func(*, as_of: str, **_: object) -> dict:
    if as_of == "2006-12-31":
        scores = [
            score("yield_curve_10y_3m", 82, 0.9),
            score("credit_spread_baa_10y", 78, 0.8),
            score("fed_policy_restrictive_pressure", 70, 0.7),
        ]
    else:
        scores = [
            score("yield_curve_10y_3m", 90, 0.9),
            score("credit_spread_baa_10y", 88, 0.9),
            score("fed_policy_restrictive_pressure", 85, 0.9),
            score("industrial_production_momentum_loss", 80, 0.8),
        ]
    return {"scores": scores, "failures": [], "warnings": []}


def fake_delta_refined_score_func(*, as_of: str, **_: object) -> dict:
    if as_of == "2000-01-31":
        scores = [score("yield_curve_10y_3m", 80, 0.9)]
    else:
        scores = [
            score("yield_curve_10y_3m", 82, 0.9),
            score("credit_spread_baa_10y", 78, 0.8),
            score("fed_policy_restrictive_pressure", 70, 0.7),
        ]
    return {"scores": scores, "failures": [], "warnings": []}


def weak_target_refined_score_func(**_: object) -> dict:
    return {
        "scores": [
            score("yield_curve_10y_3m", 40, 0.9),
            score("credit_spread_baa_10y", 78, 0.8),
            score("fed_policy_restrictive_pressure", 70, 0.7),
        ],
        "failures": [],
        "warnings": [],
    }


def rates_cluster_refined_score_func(**_: object) -> dict:
    return {
        "scores": [
            score("yield_curve_10y_3m", 92, 1.0),
            score("yield_curve_10y_2y", 88, 1.0),
            score("fed_policy_restrictive_pressure", 74, 1.0),
        ],
        "failures": [],
        "warnings": [],
    }


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "display_name_zh": indicator_id,
        "score": value,
        "confidence": confidence,
        "reason_zh": "test",
    }


def write_windows(tmp_path: Path) -> Path:
    path = tmp_path / "windows.yaml"
    path.write_text(
        """
boom_ending_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  scenarios:
    global_financial_crisis:
      display_name_zh: 金融海嘯
      diagnostic_points:
        - as_of: "2006-12-31"
          label: gfc_yield_curve_warning
          expected_zh: early
    late_cycle_2018:
      display_name_zh: 2018 升息與貿易戰壓力
      diagnostic_points:
        - as_of: "2018-12-31"
          label: late_cycle_2018_warning
          expected_zh: risk
""",
        encoding="utf-8",
    )
    return path


def write_single_window(tmp_path: Path) -> Path:
    path = tmp_path / "single_window.yaml"
    path.write_text(
        """
boom_ending_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  scenarios:
    scenario_a:
      display_name_zh: 測試
      diagnostic_points:
        - as_of: "2000-01-31"
          label: target_retention
          expected_zh: test
""",
        encoding="utf-8",
    )
    return path


def write_delta_windows(tmp_path: Path) -> Path:
    path = tmp_path / "delta_windows.yaml"
    path.write_text(
        """
boom_ending_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  scenarios:
    scenario_a:
      display_name_zh: 測試
      diagnostic_points:
        - as_of: "2000-01-31"
          label: watch_to_weak
          expected_zh: test
        - as_of: "2000-02-29"
          label: weak_to_watch
          expected_zh: test
        - as_of: "2000-03-31"
          label: watch_to_watch
          expected_zh: test
""",
        encoding="utf-8",
    )
    return path


def write_single_experiment(tmp_path: Path) -> Path:
    path = tmp_path / "single_experiment.yaml"
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
    profile_id: boom_ending_refined_v1
  expected_refinement_outcomes:
    - scenario_id: scenario_a
      as_of: "2000-01-31"
      expected_min_status: watch
""",
        encoding="utf-8",
    )
    return path


def write_target_spec(tmp_path: Path) -> Path:
    path = tmp_path / "target_spec.yaml"
    path.write_text(
        """
boom_ending_candidate_indicators:
  version: 1
  status: test
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - 不構成投資建議。
  indicators:
    - indicator_id: yield_curve_10y_3m
      display_name_zh: 10 年期與 3 個月期公債利差
      purpose_group: boom_ending
      provider: fred
      candidate_fred_series: [T10Y3M]
      preferred_series: T10Y3M
      transformation: [level]
      proposed_score_method: yield_curve_inversion_pressure_score
      expected_phase_impact: {boom: pressure}
      implementation_priority: high
""",
        encoding="utf-8",
    )
    return path


def write_groups(tmp_path: Path) -> Path:
    path = tmp_path / "groups.yaml"
    path.write_text(
        """
experimental_indicator_groups:
  rates_policy:
    - yield_curve_10y_3m
    - fed_policy_restrictive_pressure
  credit_financial_conditions:
    - credit_spread_baa_10y
  production:
    - industrial_production_momentum_loss
""",
        encoding="utf-8",
    )
    return path


def write_rates_only_groups(tmp_path: Path) -> Path:
    path = tmp_path / "rates_groups.yaml"
    path.write_text(
        """
experimental_indicator_groups:
  rates_policy:
    - yield_curve_10y_3m
    - yield_curve_10y_2y
    - fed_policy_restrictive_pressure
  credit_financial_conditions:
    - credit_spread_baa_10y
""",
        encoding="utf-8",
    )
    return path


def write_series(path: Path, values: list[float]) -> None:
    path.write_text(
        "date,value\n"
        + "\n".join(f"2000-{index + 1:02d}-29,{value}" for index, value in enumerate(values[:12]))
        + "\n",
        encoding="utf-8",
    )


def write_delta_experiment(tmp_path: Path) -> Path:
    path = tmp_path / "delta_experiment.yaml"
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
    profile_id: boom_ending_refined_v1
  expected_refinement_outcomes:
    - scenario_id: scenario_a
      as_of: "2000-01-31"
      expected_min_status: weak
""",
        encoding="utf-8",
    )
    return path


def write_experiment(tmp_path: Path) -> Path:
    path = tmp_path / "experiment.yaml"
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
    profile_id: boom_ending_refined_v1
  expected_refinement_outcomes:
    - scenario_id: global_financial_crisis
      as_of: "2006-12-31"
      expected_min_status: watch
    - scenario_id: late_cycle_2018
      as_of: "2018-12-31"
      expected_max_status: watch
""",
        encoding="utf-8",
    )
    return path
