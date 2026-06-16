from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_boom_ending_diagnostics,
    build_boom_ending_group_summary,
    build_boom_ending_point_summary,
    is_boom_ending_high_signal,
    is_boom_ending_strong_signal,
    load_boom_ending_diagnostic_windows,
)

WINDOWS_PATH = Path("specs/backtests/boom_ending_diagnostic_windows.yaml")


def test_boom_ending_diagnostic_windows_can_be_loaded() -> None:
    windows = load_boom_ending_diagnostic_windows(WINDOWS_PATH)

    assert windows.version == 1
    assert windows.data_mode == "revised"
    assert len(windows.points) == 9
    assert any("修訂後歷史資料" in caveat for caveat in windows.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in windows.caveats_zh)


def test_boom_ending_signal_helpers() -> None:
    assert is_boom_ending_high_signal({"score": 65, "confidence": 0.5})
    assert is_boom_ending_strong_signal({"score": 75, "confidence": 0.7})
    assert not is_boom_ending_high_signal({"score": 80, "confidence": 0.3})
    assert not is_boom_ending_strong_signal({"score": 70, "confidence": 0.9})


def test_boom_ending_point_summary_statuses() -> None:
    groups_by_indicator = {
        "a": "rates_policy",
        "b": "credit_financial_conditions",
        "c": "production",
        "d": "employment",
    }
    scores = [
        score("a", 80, 0.9),
        score("b", 78, 0.8),
        score("c", 76, 0.75),
        score("d", 74, 0.9),
    ]

    summary = build_boom_ending_point_summary(scores, [], groups_by_indicator)

    assert summary["high_signal_count"] == 4
    assert summary["high_confidence_high_signal_count"] == 3
    assert summary["broad_group_count"] == 4
    assert summary["boom_ending_status"] == "watch"


def test_boom_ending_group_summary_is_computed() -> None:
    groups = {
        "rates_policy": ["a", "b"],
        "production": ["c"],
    }
    scores = [score("a", 80, 0.9), score("b", 40, 0.9), score("c", 70, 0.8)]

    summary = build_boom_ending_group_summary(scores, groups)

    rates = next(item for item in summary if item["group_id"] == "rates_policy")
    production = next(item for item in summary if item["group_id"] == "production")
    assert rates["scored_indicator_count"] == 2
    assert rates["high_signal_count"] == 1
    assert rates["status"] == "mixed"
    assert production["high_signal_count"] == 1


def test_boom_ending_diagnostics_builds_gfc_comparison(tmp_path: Path) -> None:
    windows_path = write_windows(tmp_path)
    groups_path = write_groups(tmp_path)

    diagnostics = build_boom_ending_diagnostics(
        windows_path=windows_path,
        groups_path=groups_path,
        score_func=fake_score_func,
    )

    assert diagnostics["diagnostic_point_count"] == 2
    comparison = diagnostics["comparisons"]["gfc_2006_vs_2008"]
    assert comparison["score_delta"] > 0
    assert comparison["group_breadth_delta"] > 0
    assert diagnostics["aggregate"]["points_with_full_scores"] == 2
    assert "不構成投資建議" in "".join(diagnostics["caveats_zh"])


def score(indicator_id: str, value: float, confidence: float) -> dict:
    return {
        "indicator_id": indicator_id,
        "display_name_zh": indicator_id,
        "score": value,
        "confidence": confidence,
        "reason_zh": "test",
    }


def fake_score_func(*, as_of: str, **_: object) -> dict:
    if as_of == "2006-12-31":
        scores = [score("a", 55, 0.8), score("b", 45, 0.8), score("c", 40, 0.8)]
    else:
        scores = [score("a", 80, 0.9), score("b", 78, 0.8), score("c", 76, 0.75)]
    return {
        "scores": scores,
        "failures": [],
        "warnings": [],
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
        - as_of: "2008-10-31"
          label: gfc_confirmed_recession
          expected_zh: strong
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
    - a
  credit_financial_conditions:
    - b
  production:
    - c
""",
        encoding="utf-8",
    )
    return path
