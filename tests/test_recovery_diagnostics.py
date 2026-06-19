from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_recovery_diagnostics,
    build_recovery_point_summary,
    classify_recovery_status,
    load_recovery_diagnostic_windows,
)

WINDOWS_PATH = Path("specs/backtests/recovery_diagnostic_windows.yaml")


def test_recovery_diagnostic_windows_can_be_loaded() -> None:
    windows = load_recovery_diagnostic_windows(WINDOWS_PATH)

    assert windows.version == 1
    assert windows.status == "experimental"
    assert len(windows.points) == 12
    assert any(point.expected_status == "watch_or_strong" for point in windows.points)
    assert any("修訂後歷史資料" in caveat for caveat in windows.caveats_zh)
    assert any("recovery watch 不等於正式復甦確認" in caveat for caveat in windows.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in windows.caveats_zh)


def test_recovery_status_classification() -> None:
    assert (
        classify_recovery_status(
            weighted_score=80,
            broad_group_count=3,
            high_signal_count=4,
            high_confidence_high_signal_count=4,
            policy_only_signal=False,
        )
        == "strong"
    )
    assert (
        classify_recovery_status(
            weighted_score=60,
            broad_group_count=2,
            high_signal_count=3,
            high_confidence_high_signal_count=2,
            policy_only_signal=False,
        )
        == "watch"
    )
    assert (
        classify_recovery_status(
            weighted_score=90,
            broad_group_count=1,
            high_signal_count=1,
            high_confidence_high_signal_count=1,
            policy_only_signal=True,
        )
        == "weak"
    )
    assert (
        classify_recovery_status(
            weighted_score=20,
            broad_group_count=0,
            high_signal_count=0,
            high_confidence_high_signal_count=0,
            policy_only_signal=False,
        )
        == "none"
    )


def test_recovery_point_summary_counts_groups_and_policy_only() -> None:
    groups_by_indicator = {
        "policy": "policy_support",
        "labor": "labor_reversal",
        "consumption": "consumption_recovery",
        "credit": "credit_financial_easing",
    }

    policy_only = build_recovery_point_summary([score("policy", 90, 0.9)], [], groups_by_indicator)
    strong = build_recovery_point_summary(
        [
            score("policy", 90, 0.9),
            score("labor", 85, 0.8),
            score("consumption", 82, 0.8),
            score("credit", 80, 0.8),
        ],
        [],
        groups_by_indicator,
    )

    assert policy_only["policy_only_signal"] is True
    assert policy_only["recovery_status"] == "weak"
    assert strong["broad_group_count"] == 4
    assert strong["high_signal_count"] == 4
    assert strong["labor_confirmed"] is True
    assert strong["real_activity_confirmed"] is True
    assert strong["credit_financial_confirmed"] is True
    assert strong["recovery_status"] == "strong"


def test_recovery_diagnostics_builds_summary_and_notes(tmp_path: Path) -> None:
    windows = write_windows(tmp_path)
    groups = write_groups(tmp_path)

    report = build_recovery_diagnostics(
        windows_path=windows,
        groups_path=groups,
        score_func=fake_score_func,
    )

    assert report["diagnostic_point_count"] == 4
    assert report["points_with_full_scores"] == 4
    summary = report["summary"]
    assert summary["match_count"] == 4
    assert summary["mismatch_count"] == 0
    assert summary["strong_count"] == 1
    assert summary["watch_count"] == 1
    assert summary["weak_count"] == 1
    assert summary["none_count"] == 1
    assert summary["policy_only_warning_count"] == 1
    assert summary["exogenous_shock_point_count"] == 1
    covid = next(point for point in report["points"] if point["label"] == "covid_trough_area")
    assert any("外生衝擊" in note for note in covid["notes_zh"])
    assert "不構成投資建議" in "".join(report["caveats_zh"])


def test_recovery_diagnostics_detects_unexpected_and_missed_points(tmp_path: Path) -> None:
    windows = write_windows(
        tmp_path,
        expected_for_none="watch_or_strong",
        expected_for_watch="watch_or_strong",
        expected_for_strong="weak_or_none",
    )
    groups = write_groups(tmp_path)

    report = build_recovery_diagnostics(
        windows_path=windows,
        groups_path=groups,
        score_func=fake_score_func,
    )

    summary = report["summary"]
    assert summary["unexpected_strong_points"]
    assert summary["missed_recovery_watch_points"]


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "display_name_zh": indicator_id,
        "score": value,
        "confidence": confidence,
        "reason_zh": "test",
    }


def fake_score_func(*, as_of: str, **_: object) -> dict:
    if as_of == "2009-03-31":
        scores = [score("policy", 90, 0.9)]
    elif as_of == "2009-06-30":
        scores = [score("labor", 70, 0.8), score("consumption", 72, 0.7), score("credit", 66, 0.6)]
    elif as_of == "2009-09-30":
        scores = [
            score("labor", 85, 0.8),
            score("consumption", 82, 0.8),
            score("production", 80, 0.8),
            score("credit", 78, 0.8),
        ]
    else:
        scores = [score("labor", 30, 0.8)]
    return {"scores": scores, "failures": [], "warnings": []}


def write_windows(
    tmp_path: Path,
    *,
    expected_for_none: str = "weak_or_none",
    expected_for_watch: str = "watch_or_strong",
    expected_for_strong: str = "watch_or_strong",
) -> Path:
    path = tmp_path / "windows.yaml"
    path.write_text(
        f"""
recovery_diagnostic_windows:
  version: 1
  status: test
  data_mode: revised
  objective_zh: test
  caveats_zh:
    - 使用修訂後歷史資料，不等同當時投資人可見資料。
    - recovery watch 不等於正式復甦確認。
    - policy easing 不得單獨確認 recovery。
    - 不構成投資建議。
  diagnostic_points:
    - scenario_id: global_financial_crisis
      as_of: "2008-10-31"
      label: gfc_crisis_peak
      expected_status: {expected_for_none}
      reason_zh: early
    - scenario_id: global_financial_crisis
      as_of: "2009-03-31"
      label: gfc_policy_only
      expected_status: weak_or_watch
      reason_zh: policy only
    - scenario_id: global_financial_crisis
      as_of: "2009-06-30"
      label: gfc_trough_area
      expected_status: {expected_for_watch}
      reason_zh: watch
    - scenario_id: covid_recession
      as_of: "2009-09-30"
      label: covid_trough_area
      expected_status: {expected_for_strong}
      reason_zh: shock
      caveat: exogenous_shock
""",
        encoding="utf-8",
    )
    return path


def write_groups(tmp_path: Path) -> Path:
    path = tmp_path / "groups.yaml"
    path.write_text(
        """
experimental_indicator_groups:
  policy_support:
    - policy
  labor_reversal:
    - labor
  consumption_recovery:
    - consumption
  production_recovery:
    - production
  credit_financial_easing:
    - credit
""",
        encoding="utf-8",
    )
    return path
