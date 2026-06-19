"""Diagnostics for experimental recovery candidate indicators."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.backtests.boom_ending_diagnostics import load_experimental_indicator_groups
from business_cycle.backtests.recovery_candidates import score_recovery_candidate_indicators

HIGH_SIGNAL_SCORE = 65.0
HIGH_SIGNAL_CONFIDENCE = 0.5
STRONG_SIGNAL_SCORE = 75.0
STRONG_SIGNAL_CONFIDENCE = 0.7

DEFAULT_WINDOWS_PATH = Path("specs/backtests/recovery_diagnostic_windows.yaml")
DEFAULT_CANDIDATE_SPEC_PATH = Path("specs/backtests/recovery_candidate_indicators.yaml")
DEFAULT_GROUPS_PATH = Path("specs/common/experimental_indicator_groups.yaml")
DEFAULT_CACHE_DIR = Path("data/raw/fred")
DEFAULT_OUTPUT_PATH = Path(
    "data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json"
)

ScoreFunction = Callable[..., dict[str, Any]]


class RecoveryDiagnosticsError(ValueError):
    """Raised when recovery diagnostics cannot be built."""


@dataclass(frozen=True)
class RecoveryDiagnosticPoint:
    """One scenario/as-of recovery diagnostic point."""

    scenario_id: str
    as_of: str
    label: str
    expected_status: str
    reason_zh: str
    caveat: str | None


@dataclass(frozen=True)
class RecoveryDiagnosticWindows:
    """Recovery diagnostic windows spec."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    points: list[RecoveryDiagnosticPoint]


def load_recovery_diagnostic_windows(path: str | Path = DEFAULT_WINDOWS_PATH) -> RecoveryDiagnosticWindows:
    """Load and validate recovery diagnostic windows."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("recovery_diagnostic_windows")
    if not isinstance(raw, dict):
        raise RecoveryDiagnosticsError("recovery_diagnostic_windows YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise RecoveryDiagnosticsError("caveats_zh must include revised data caveat")
    if not any("recovery watch 不等於正式復甦確認" in caveat for caveat in caveats):
        raise RecoveryDiagnosticsError("caveats_zh must state recovery watch is not formal recovery confirmation")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise RecoveryDiagnosticsError("caveats_zh must include no-investment-advice caveat")
    return RecoveryDiagnosticWindows(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        objective_zh=str(raw.get("objective_zh", "")),
        caveats_zh=caveats,
        points=_points_from_list(raw.get("diagnostic_points")),
    )


def is_recovery_high_signal(score: dict[str, Any]) -> bool:
    """Return whether a candidate score is a high recovery signal."""

    return _num(score.get("score")) >= HIGH_SIGNAL_SCORE and _num(score.get("confidence")) >= HIGH_SIGNAL_CONFIDENCE


def is_recovery_strong_signal(score: dict[str, Any]) -> bool:
    """Return whether a candidate score is a strong high-confidence recovery signal."""

    return _num(score.get("score")) >= STRONG_SIGNAL_SCORE and _num(score.get("confidence")) >= STRONG_SIGNAL_CONFIDENCE


def build_recovery_point_summary(
    scores: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    groups_by_indicator: dict[str, str],
) -> dict[str, Any]:
    """Build deterministic point-level recovery summary."""

    high_scores = [score for score in scores if is_recovery_high_signal(score)]
    strong_scores = [score for score in scores if is_recovery_strong_signal(score)]
    high_groups = {
        groups_by_indicator.get(str(score.get("indicator_id")))
        for score in high_scores
        if groups_by_indicator.get(str(score.get("indicator_id")))
    }
    non_policy_groups = {group for group in high_groups if group != "policy_support"}
    weighted_score = _weighted_recovery_score(scores)
    policy_only_signal = bool(high_scores) and not non_policy_groups
    labor_confirmed = "labor_reversal" in high_groups
    real_activity_confirmed = bool(high_groups & {"consumption_recovery", "production_recovery"})
    credit_financial_confirmed = "credit_financial_easing" in high_groups
    status = classify_recovery_status(
        weighted_score=weighted_score,
        broad_group_count=len(high_groups),
        high_signal_count=len(high_scores),
        high_confidence_high_signal_count=len(strong_scores),
        policy_only_signal=policy_only_signal,
    )
    return {
        "total_candidates": len(scores) + len(failures),
        "scored_candidates": len(scores),
        "failed_candidates": len(failures),
        "weighted_recovery_score": weighted_score,
        "broad_group_count": len(high_groups),
        "high_signal_count": len(high_scores),
        "high_confidence_high_signal_count": len(strong_scores),
        "policy_only_signal": policy_only_signal,
        "labor_confirmed": labor_confirmed,
        "real_activity_confirmed": real_activity_confirmed,
        "credit_financial_confirmed": credit_financial_confirmed,
        "recovery_status": status,
    }


def classify_recovery_status(
    *,
    weighted_score: float,
    broad_group_count: int,
    high_signal_count: int,
    high_confidence_high_signal_count: int,
    policy_only_signal: bool,
) -> str:
    """Classify recovery diagnostics status from point summary fields."""

    if policy_only_signal:
        return "weak"
    if broad_group_count >= 3 and high_confidence_high_signal_count >= 4 and weighted_score >= 75.0:
        return "strong"
    if broad_group_count >= 2 and high_signal_count >= 3 and weighted_score >= 55.0:
        return "watch"
    if high_signal_count >= 1:
        return "weak"
    return "none"


def build_recovery_group_summary(scores: list[dict[str, Any]], groups: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Build group-level recovery candidate score summaries."""

    scores_by_indicator = {str(score.get("indicator_id")): score for score in scores}
    summaries: list[dict[str, Any]] = []
    recovery_groups = {
        "labor_reversal",
        "consumption_recovery",
        "production_recovery",
        "credit_financial_easing",
        "policy_support",
    }
    for group_id, indicator_ids in groups.items():
        if group_id not in recovery_groups:
            continue
        group_scores = [
            scores_by_indicator[indicator_id]
            for indicator_id in indicator_ids
            if indicator_id in scores_by_indicator
        ]
        high_signal_count = sum(1 for score in group_scores if is_recovery_high_signal(score))
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


def build_recovery_diagnostics(
    *,
    spec_path: str | Path = DEFAULT_CANDIDATE_SPEC_PATH,
    windows_path: str | Path = DEFAULT_WINDOWS_PATH,
    groups_path: str | Path = DEFAULT_GROUPS_PATH,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    output_path: str | Path | None = None,
    score_func: ScoreFunction | None = None,
) -> dict[str, Any]:
    """Build recovery diagnostics across configured scenario points."""

    windows = load_recovery_diagnostic_windows(windows_path)
    groups = load_experimental_indicator_groups(groups_path)
    groups_by_indicator = _groups_by_indicator(groups)
    scorer = score_func or score_recovery_candidate_indicators
    points: list[dict[str, Any]] = []

    for point in windows.points:
        score_payload = scorer(as_of=point.as_of, cache_dir=cache_dir, spec_path=spec_path)
        scores = list(score_payload.get("scores", []))
        failures = list(score_payload.get("failures", []))
        summary = build_recovery_point_summary(scores, failures, groups_by_indicator)
        expected = point.expected_status
        status = summary["recovery_status"]
        warnings = list(score_payload.get("warnings", []))
        if summary["policy_only_signal"]:
            warnings.append("policy_only_signal: policy easing cannot confirm recovery by itself")
        notes = _diagnostic_notes(point, summary, failures)
        record = {
            "scenario_id": point.scenario_id,
            "as_of": point.as_of,
            "label": point.label,
            "expected_status": expected,
            "recovery_status": status,
            "matches_expected": _status_matches(status, expected),
            "candidate_summary": summary,
            "group_summary": build_recovery_group_summary(scores, groups),
            "top_positive_indicators": _top_candidate_scores(scores),
            "weak_but_important_indicators": _weak_but_important_indicators(scores, groups_by_indicator),
            "warnings": warnings,
            "notes_zh": notes,
            "reason_zh": point.reason_zh,
            "failures": failures,
        }
        points.append(record)

    report = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "data_mode": windows.data_mode,
        "diagnostic_point_count": len(points),
        "points_with_full_scores": sum(1 for point in points if point["candidate_summary"]["failed_candidates"] == 0),
        "points_with_missing_scores": sum(1 for point in points if point["candidate_summary"]["failed_candidates"] > 0),
        "points": points,
        "summary": _summary(points),
        "caveats_zh": windows.caveats_zh,
    }
    if output_path is not None:
        write_recovery_diagnostics(output_path, report)
    return report


def write_recovery_diagnostics(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write recovery diagnostics JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _points_from_list(raw_points: Any) -> list[RecoveryDiagnosticPoint]:
    if not isinstance(raw_points, list) or not raw_points:
        raise RecoveryDiagnosticsError("diagnostic_points must be a non-empty list")
    points: list[RecoveryDiagnosticPoint] = []
    for point in raw_points:
        if not isinstance(point, dict):
            raise RecoveryDiagnosticsError("diagnostic_points entries must be mappings")
        points.append(
            RecoveryDiagnosticPoint(
                scenario_id=str(point.get("scenario_id") or ""),
                as_of=str(point.get("as_of") or ""),
                label=str(point.get("label") or ""),
                expected_status=str(point.get("expected_status") or ""),
                reason_zh=str(point.get("reason_zh") or ""),
                caveat=str(point["caveat"]) if point.get("caveat") else None,
            )
        )
    if any(not point.scenario_id or not point.as_of or not point.label for point in points):
        raise RecoveryDiagnosticsError("diagnostic_points entries must include scenario_id, as_of, and label")
    return points


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(point["recovery_status"]) for point in points]
    unexpected_strong = [
        _point_id(point)
        for point in points
        if point["recovery_status"] == "strong"
        and point["expected_status"] in {"weak_or_none", "weak_or_watch"}
    ]
    missed_watch = [
        _point_id(point)
        for point in points
        if point["expected_status"] == "watch_or_strong"
        and point["recovery_status"] in {"weak", "none"}
    ]
    indicators_requiring_refinement = _indicators_requiring_refinement(points)
    return {
        "match_count": sum(1 for point in points if point["matches_expected"]),
        "mismatch_count": sum(1 for point in points if not point["matches_expected"]),
        "strong_count": statuses.count("strong"),
        "watch_count": statuses.count("watch"),
        "weak_count": statuses.count("weak"),
        "none_count": statuses.count("none"),
        "policy_only_warning_count": sum(
            1 for point in points if point["candidate_summary"]["policy_only_signal"]
        ),
        "exogenous_shock_point_count": sum(
            1 for point in points if any("外生衝擊" in note for note in point["notes_zh"])
        ),
        "unexpected_strong_points": unexpected_strong,
        "missed_recovery_watch_points": missed_watch,
        "indicators_requiring_refinement": indicators_requiring_refinement,
    }


def _status_matches(status: str, expected: str) -> bool:
    if expected == "watch_or_strong":
        return status in {"watch", "strong"}
    if expected == "weak_or_watch":
        return status in {"weak", "watch"}
    if expected == "weak_or_none":
        return status in {"weak", "none"}
    return status == expected


def _indicators_requiring_refinement(points: list[dict[str, Any]]) -> list[str]:
    flagged: list[str] = []
    for point in points:
        if point["expected_status"] == "weak_or_none" and point["recovery_status"] == "strong":
            for score in point["top_positive_indicators"]:
                indicator_id = str(score.get("indicator_id"))
                if indicator_id not in flagged:
                    flagged.append(indicator_id)
    return flagged


def _weak_but_important_indicators(
    scores: list[dict[str, Any]],
    groups_by_indicator: dict[str, str],
) -> list[dict[str, Any]]:
    important_groups = {"labor_reversal", "consumption_recovery", "production_recovery"}
    items: list[dict[str, Any]] = []
    for score in scores:
        group = groups_by_indicator.get(str(score.get("indicator_id")))
        if group in important_groups and not is_recovery_high_signal(score):
            items.append(
                {
                    "indicator_id": score.get("indicator_id"),
                    "group_id": group,
                    "score": score.get("score"),
                    "confidence": score.get("confidence"),
                }
            )
    return items[:5]


def _diagnostic_notes(
    point: RecoveryDiagnosticPoint,
    summary: dict[str, Any],
    failures: list[dict[str, Any]],
) -> list[str]:
    notes = ["此診斷只解釋 recovery candidate indicators，不會修改正式模型判斷。"]
    if failures:
        notes.append("部分 candidate indicators 缺少本機 cache 或 scoring failure，需先補齊資料再解讀。")
    if summary["policy_only_signal"]:
        notes.append("policy easing 只能作為 support signal，不得單獨確認 recovery。")
    if point.caveat == "exogenous_shock":
        notes.append("外生衝擊案例中，COVID 快速反彈不等同一般景氣循環復甦。")
    if summary["recovery_status"] in {"watch", "strong"}:
        notes.append("recovery watch 不等於正式復甦確認。")
    return notes


def _weighted_recovery_score(scores: list[dict[str, Any]]) -> float:
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


def _group_status(high_signal_count: int, scored_count: int, avg_score: float) -> str:
    if scored_count == 0:
        return "missing"
    if high_signal_count >= 2 or avg_score >= 70.0:
        return "strong"
    if high_signal_count == 1 or avg_score >= 55.0:
        return "mixed"
    return "weak"


def _groups_by_indicator(groups: dict[str, list[str]]) -> dict[str, str]:
    return {indicator_id: group_id for group_id, indicator_ids in groups.items() for indicator_id in indicator_ids}


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def _point_id(point: dict[str, Any]) -> str:
    return f"{point.get('scenario_id')}:{point.get('as_of')}:{point.get('label')}"


def _num(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryDiagnosticsError(f"Recovery diagnostics file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryDiagnosticsError(f"Invalid YAML in recovery diagnostics file {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryDiagnosticsError("Recovery diagnostics YAML must be a mapping")
    return payload


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RecoveryDiagnosticsError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise RecoveryDiagnosticsError(f"{field} entries must be non-empty")
    return items
