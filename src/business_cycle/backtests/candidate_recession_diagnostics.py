"""Diagnostics for experimental recession confirmation candidate indicators."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.candidate_indicators import score_candidate_indicators

HIGH_SIGNAL_SCORE = 65.0
HIGH_SIGNAL_CONFIDENCE = 0.5
STRONG_SIGNAL_SCORE = 75.0
STRONG_SIGNAL_CONFIDENCE = 0.7

DEFAULT_WINDOWS_PATH = Path("specs/backtests/candidate_recession_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/recession_confirmation_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")

ScoreFunction = Callable[..., dict[str, Any]]


class CandidateRecessionDiagnosticsError(ValueError):
    """Raised when candidate recession diagnostics cannot be built."""


@dataclass(frozen=True)
class CandidateDiagnosticPoint:
    """One scenario/as-of diagnostic point."""

    scenario_id: str
    display_name_zh: str
    as_of: str
    label: str
    expected_zh: str


@dataclass(frozen=True)
class CandidateRecessionDiagnosticWindows:
    """Candidate diagnostics window spec."""

    version: int
    status: str
    data_mode: str
    caveats_zh: list[str]
    points: list[CandidateDiagnosticPoint]


def load_candidate_recession_diagnostic_windows(
    path: str | Path = DEFAULT_WINDOWS_PATH,
) -> CandidateRecessionDiagnosticWindows:
    """Load and validate candidate recession diagnostics windows."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("candidate_recession_diagnostic_windows")
    if not isinstance(raw, dict):
        raise CandidateRecessionDiagnosticsError(
            "candidate_recession_diagnostic_windows YAML must contain a mapping"
        )
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise CandidateRecessionDiagnosticsError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CandidateRecessionDiagnosticsError("caveats_zh must include no-investment-advice caveat")
    points = _points_from_scenarios(raw.get("scenarios"))
    return CandidateRecessionDiagnosticWindows(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        caveats_zh=caveats,
        points=points,
    )


def build_candidate_point_summary(
    scores: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    groups_by_indicator: dict[str, str],
) -> dict[str, Any]:
    """Build deterministic point-level summary from candidate scores."""

    high_scores = [score for score in scores if is_high_signal(score)]
    strong_scores = [score for score in scores if is_strong_signal(score)]
    high_groups = {
        groups_by_indicator.get(str(score.get("indicator_id")))
        for score in high_scores
        if groups_by_indicator.get(str(score.get("indicator_id")))
    }
    weighted_confirmation_score = _weighted_confirmation_score(scores)
    status = _confirmation_status(
        broad_group_count=len(high_groups),
        high_signal_count=len(high_scores),
        high_confidence_high_signal_count=len(strong_scores),
    )
    return {
        "total_candidates": len(scores) + len(failures),
        "scored_candidates": len(scores),
        "failed_candidates": len(failures),
        "high_signal_count": len(high_scores),
        "high_confidence_high_signal_count": len(strong_scores),
        "broad_group_count": len(high_groups),
        "weighted_confirmation_score": weighted_confirmation_score,
        "recession_confirmation_status": status,
    }


def build_group_summary(
    scores: list[dict[str, Any]],
    groups: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Build group-level candidate score summaries."""

    scores_by_indicator = {str(score.get("indicator_id")): score for score in scores}
    summaries: list[dict[str, Any]] = []
    for group_id, indicator_ids in groups.items():
        group_scores = [scores_by_indicator[indicator_id] for indicator_id in indicator_ids if indicator_id in scores_by_indicator]
        high_signal_count = sum(1 for score in group_scores if is_high_signal(score))
        avg_score = _average([_num(score.get("score")) for score in group_scores])
        avg_confidence = _average([_num(score.get("confidence")) for score in group_scores])
        summaries.append(
            {
                "group_id": group_id,
                "scored_indicator_count": len(group_scores),
                "high_signal_count": high_signal_count,
                "avg_score": avg_score,
                "avg_confidence": avg_confidence,
                "status": _group_status(high_signal_count, len(group_scores), avg_score),
            }
        )
    return summaries


def is_high_signal(score: dict[str, Any]) -> bool:
    """Return whether a candidate score is a high recession-confirmation signal."""

    return _num(score.get("score")) >= HIGH_SIGNAL_SCORE and _num(score.get("confidence")) >= HIGH_SIGNAL_CONFIDENCE


def is_strong_signal(score: dict[str, Any]) -> bool:
    """Return whether a candidate score is a strong high-confidence signal."""

    return _num(score.get("score")) >= STRONG_SIGNAL_SCORE and _num(score.get("confidence")) >= STRONG_SIGNAL_CONFIDENCE


def build_candidate_recession_diagnostics(
    *,
    windows_path: str | Path = DEFAULT_WINDOWS_PATH,
    candidate_spec_path: str | Path = DEFAULT_CANDIDATE_SPEC_PATH,
    groups_path: str | Path = DEFAULT_GROUPS_PATH,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    score_func: ScoreFunction | None = None,
) -> dict[str, Any]:
    """Build candidate recession diagnostics across configured scenario points."""

    windows = load_candidate_recession_diagnostic_windows(windows_path)
    groups = load_experimental_indicator_groups(groups_path)
    groups_by_indicator = _groups_by_indicator(groups)
    scorer = score_func or score_candidate_indicators
    points: list[dict[str, Any]] = []

    for point in windows.points:
        score_payload = scorer(
            as_of=point.as_of,
            cache_dir=cache_dir,
            spec_path=candidate_spec_path,
        )
        scores = list(score_payload.get("scores", []))
        failures = list(score_payload.get("failures", []))
        point_summary = build_candidate_point_summary(scores, failures, groups_by_indicator)
        group_summary = build_group_summary(scores, groups)
        points.append(
            {
                "scenario_id": point.scenario_id,
                "display_name_zh": point.display_name_zh,
                "as_of": point.as_of,
                "label": point.label,
                "candidate_summary": point_summary,
                "group_summary": group_summary,
                "top_candidate_scores": _top_candidate_scores(scores),
                "expected_zh": point.expected_zh,
                "diagnostic_notes_zh": _diagnostic_notes(point_summary, failures),
                "failures": failures,
                "warnings": list(score_payload.get("warnings", [])),
            }
        )

    comparisons = _build_comparisons(points)
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data_mode": windows.data_mode,
        "diagnostic_point_count": len(points),
        "points": points,
        "comparisons": comparisons,
        "aggregate": _aggregate(points),
        "caveats_zh": windows.caveats_zh,
    }


def write_candidate_recession_diagnostics(
    output_path: str | Path,
    diagnostics: dict[str, Any],
) -> Path:
    """Write candidate recession diagnostics JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_experimental_indicator_groups(path: str | Path = DEFAULT_GROUPS_PATH) -> dict[str, list[str]]:
    """Load experimental indicator group mapping."""

    payload = _load_yaml_mapping(path)
    raw_groups = payload.get("experimental_indicator_groups")
    if not isinstance(raw_groups, dict):
        raise CandidateRecessionDiagnosticsError("experimental_indicator_groups YAML must contain a mapping")
    groups: dict[str, list[str]] = {}
    for group_id, indicators in raw_groups.items():
        groups[str(group_id)] = _non_empty_str_list(indicators, f"experimental_indicator_groups.{group_id}")
    return groups


def _points_from_scenarios(raw_scenarios: Any) -> list[CandidateDiagnosticPoint]:
    if not isinstance(raw_scenarios, dict) or not raw_scenarios:
        raise CandidateRecessionDiagnosticsError("scenarios must be a non-empty mapping")
    points: list[CandidateDiagnosticPoint] = []
    for scenario_id, scenario in raw_scenarios.items():
        if not isinstance(scenario, dict):
            raise CandidateRecessionDiagnosticsError("scenario entries must be mappings")
        display_name_zh = str(scenario.get("display_name_zh") or "")
        raw_points = scenario.get("diagnostic_points")
        if not isinstance(raw_points, list) or not raw_points:
            raise CandidateRecessionDiagnosticsError(f"scenario {scenario_id} diagnostic_points must be non-empty")
        for point in raw_points:
            if not isinstance(point, dict):
                raise CandidateRecessionDiagnosticsError(f"scenario {scenario_id} diagnostic_points entries must be mappings")
            points.append(
                CandidateDiagnosticPoint(
                    scenario_id=str(scenario_id),
                    display_name_zh=display_name_zh,
                    as_of=str(point.get("as_of") or ""),
                    label=str(point.get("label") or ""),
                    expected_zh=str(point.get("expected_zh") or ""),
                )
            )
    if any(not point.as_of or not point.label for point in points):
        raise CandidateRecessionDiagnosticsError("diagnostic points must include as_of and label")
    return points


def _build_comparisons(points: list[dict[str, Any]]) -> dict[str, Any]:
    by_label = {str(point["label"]): point for point in points}
    comparisons: dict[str, Any] = {}
    false_point = by_label.get("covid_false_positive_candidate")
    true_point = by_label.get("covid_true_recession_candidate")
    if false_point and true_point:
        false_summary = false_point["candidate_summary"]
        true_summary = true_point["candidate_summary"]
        comparisons["covid_2019_vs_2020"] = {
            "false_positive_as_of": false_point["as_of"],
            "true_recession_as_of": true_point["as_of"],
            "score_delta": round(
                true_summary["weighted_confirmation_score"] - false_summary["weighted_confirmation_score"],
                4,
            ),
            "group_breadth_delta": true_summary["broad_group_count"] - false_summary["broad_group_count"],
            "interpretation_zh": "比較 COVID 2019 early false recession 與 2020 真實衝擊期間的候選指標廣度與分數差異。",
        }
    return comparisons


def _aggregate(points: list[dict[str, Any]]) -> dict[str, Any]:
    full_scores = [point for point in points if point["candidate_summary"]["failed_candidates"] == 0]
    missing_scores = [point for point in points if point["candidate_summary"]["failed_candidates"] > 0]
    useful = _useful_candidate_indicators(points)
    refinement = _indicators_requiring_refinement(points, useful)
    return {
        "points_with_full_scores": len(full_scores),
        "points_with_missing_scores": len(missing_scores),
        "candidate_indicators_useful_for_discrimination": useful,
        "candidate_indicators_requiring_refinement": refinement,
    }


def _useful_candidate_indicators(points: list[dict[str, Any]]) -> list[str]:
    by_label = {str(point["label"]): point for point in points}
    weak = by_label.get("covid_false_positive_candidate", {})
    strong_points = [
        by_label.get("covid_true_recession_candidate", {}),
        by_label.get("covid_shock_confirmation", {}),
        by_label.get("gfc_recession_confirmed", {}),
        by_label.get("dotcom_recession_window", {}),
    ]
    weak_scores = {score["indicator_id"]: score for score in weak.get("top_candidate_scores", [])}
    useful: list[str] = []
    for point in strong_points:
        for score in point.get("top_candidate_scores", []):
            indicator_id = str(score.get("indicator_id"))
            weak_score = _num(weak_scores.get(indicator_id, {}).get("score"))
            if is_high_signal(score) and _num(score.get("score")) - weak_score >= 10.0 and indicator_id not in useful:
                useful.append(indicator_id)
    return useful


def _indicators_requiring_refinement(points: list[dict[str, Any]], useful: list[str]) -> list[str]:
    non_recession_labels = {
        "covid_false_positive_candidate",
        "euro_debt_non_recession",
        "late_cycle_non_recession",
    }
    flagged: list[str] = []
    for point in points:
        if point["label"] not in non_recession_labels:
            continue
        for score in point.get("top_candidate_scores", []):
            indicator_id = str(score.get("indicator_id"))
            if is_strong_signal(score) and indicator_id not in useful and indicator_id not in flagged:
                flagged.append(indicator_id)
    return flagged


def _confirmation_status(
    *,
    broad_group_count: int,
    high_signal_count: int,
    high_confidence_high_signal_count: int,
) -> str:
    if broad_group_count >= 3 and high_confidence_high_signal_count >= 4:
        return "strong"
    if broad_group_count >= 2 and high_signal_count >= 3:
        return "partial"
    if high_signal_count > 0:
        return "weak"
    return "none"


def _group_status(high_signal_count: int, scored_count: int, avg_score: float) -> str:
    if scored_count == 0:
        return "missing"
    if high_signal_count >= 2 or avg_score >= 70.0:
        return "strong"
    if high_signal_count == 1 or avg_score >= 55.0:
        return "mixed"
    return "weak"


def _weighted_confirmation_score(scores: list[dict[str, Any]]) -> float:
    weighted_values: list[float] = []
    weights: list[float] = []
    for score in scores:
        value = _num(score.get("score"))
        confidence = _num(score.get("confidence"))
        weighted_values.append(value * confidence)
        weights.append(confidence)
    if not weights or sum(weights) == 0:
        return 0.0
    return round(sum(weighted_values) / sum(weights), 4)


def _top_candidate_scores(scores: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    sorted_scores = sorted(
        scores,
        key=lambda score: (_num(score.get("score")), _num(score.get("confidence"))),
        reverse=True,
    )
    return [
        {
            "indicator_id": score.get("indicator_id"),
            "display_name_zh": score.get("display_name_zh"),
            "score": score.get("score"),
            "confidence": score.get("confidence"),
            "reason_zh": score.get("reason_zh"),
        }
        for score in sorted_scores[:limit]
    ]


def _diagnostic_notes(summary: dict[str, Any], failures: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = ["此診斷只解釋 candidate indicators，不會修改正式模型判斷。"]
    if failures:
        notes.append("部分 candidate indicators 缺少本機 cache 或 scoring failure，需先補齊資料再解讀。")
    if summary["recession_confirmation_status"] == "strong":
        notes.append("候選指標呈現廣泛且高信心的衰退確認訊號。")
    elif summary["recession_confirmation_status"] == "partial":
        notes.append("候選指標呈現部分衰退確認訊號，仍需搭配正式 state machine 與其他資料。")
    return notes


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for group_id, indicators in groups.items():
        for indicator_id in indicators:
            mapping[indicator_id] = group_id
    return mapping


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CandidateRecessionDiagnosticsError(f"Candidate recession diagnostics file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateRecessionDiagnosticsError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CandidateRecessionDiagnosticsError("YAML must be a mapping")
    return payload


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionDiagnosticsError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CandidateRecessionDiagnosticsError(f"{field} entries must be non-empty")
    return items
