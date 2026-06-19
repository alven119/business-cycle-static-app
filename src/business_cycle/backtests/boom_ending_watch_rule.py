"""Experimental boom-ending watch rule for refined candidate diagnostics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


class BoomEndingWatchRuleError(ValueError):
    """Raised when boom-ending watch rule inputs are invalid."""


@dataclass(frozen=True)
class BoomEndingWatchRule:
    """Experimental boom-ending watch rule."""

    version: int
    status: str
    data_mode: str
    caveats_zh: list[str]
    signal_thresholds: dict[str, float]
    group_thresholds: dict[str, dict[str, float]]
    required_interpretation_zh: dict[str, str]
    expected_diagnostic_outcomes: dict[str, dict[str, str]]


def load_boom_ending_watch_rule(path: str | Path) -> BoomEndingWatchRule:
    """Load and validate boom-ending watch rule YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("boom_ending_watch_rule")
    if not isinstance(raw, dict):
        raise BoomEndingWatchRuleError("boom_ending_watch_rule YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise BoomEndingWatchRuleError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BoomEndingWatchRuleError("caveats_zh must include no-investment-advice caveat")
    if not any("不等於 confirmed recession" in caveat for caveat in caveats):
        raise BoomEndingWatchRuleError("caveats_zh must state boom ending watch is not confirmed recession")
    if not any("外生衝擊" in caveat for caveat in caveats):
        raise BoomEndingWatchRuleError("caveats_zh must include exogenous shock caveat")

    rule = BoomEndingWatchRule(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        caveats_zh=caveats,
        signal_thresholds=_float_mapping(raw.get("signal_thresholds"), "signal_thresholds"),
        group_thresholds=_group_thresholds(raw.get("group_thresholds")),
        required_interpretation_zh=_str_mapping(raw.get("required_interpretation_zh"), "required_interpretation_zh"),
        expected_diagnostic_outcomes=_expected_outcomes(raw.get("expected_diagnostic_outcomes")),
    )
    _validate_rule(rule)
    return rule


def evaluate_boom_ending_watch(point_summary: dict[str, Any], rule: BoomEndingWatchRule) -> dict[str, Any]:
    """Evaluate one refined boom-ending point against the experimental rule."""

    status = classify_boom_ending_watch_status(point_summary, rule)
    return {
        "experimental_watch_status": status,
        "reason_zh": rule.required_interpretation_zh[status],
        "rule_inputs": {
            "weighted_boom_ending_score": _num(point_summary.get("weighted_boom_ending_score")),
            "broad_group_count": int(_num(point_summary.get("broad_group_count"))),
            "high_signal_count": int(_num(point_summary.get("high_signal_count"))),
            "high_confidence_high_signal_count": int(
                _num(point_summary.get("high_confidence_high_signal_count"))
            ),
            "rates_policy_high_signal_count": int(_num(point_summary.get("rates_policy_high_signal_count"))),
        },
    }


def classify_boom_ending_watch_status(point_summary: dict[str, Any], rule: BoomEndingWatchRule) -> str:
    """Classify boom-ending watch status from refined diagnostics."""

    weighted_score = _num(point_summary.get("weighted_boom_ending_score"))
    broad_groups = _num(point_summary.get("broad_group_count"))
    high_signals = _num(point_summary.get("high_signal_count"))
    high_confidence_high_signals = _num(point_summary.get("high_confidence_high_signal_count"))
    rates_policy_high_signals = _num(point_summary.get("rates_policy_high_signal_count"))

    strong = rule.group_thresholds["strong_late_cycle_warning"]
    if (
        broad_groups >= strong["min_broad_group_count"]
        and high_confidence_high_signals >= strong["min_high_confidence_high_signal_count"]
        and weighted_score >= strong["min_weighted_boom_ending_score"]
    ):
        return "strong_late_cycle_warning"

    watch = rule.group_thresholds["watch"]
    if (
        broad_groups >= watch["min_broad_group_count"]
        and high_signals >= watch["min_high_signal_count"]
        and weighted_score >= watch["min_weighted_boom_ending_score"]
    ):
        return "watch"

    rates_cluster = rule.group_thresholds["rates_policy_cluster_watch"]
    if (
        rates_policy_high_signals >= rates_cluster["min_rates_policy_high_signal_count"]
        and weighted_score >= rates_cluster["min_weighted_boom_ending_score"]
    ):
        return "watch"

    weak = rule.group_thresholds["weak"]
    if high_signals >= weak["min_high_signal_count"]:
        return "weak"
    return "none"


def build_boom_ending_watch_rule_report(
    refinement_experiment_json: str | Path | dict[str, Any],
    rule: BoomEndingWatchRule | str | Path,
) -> dict[str, Any]:
    """Build a boom-ending watch rule report from refinement experiment output."""

    refinement = _load_json_or_mapping(refinement_experiment_json)
    loaded_rule = load_boom_ending_watch_rule(rule) if isinstance(rule, str | Path) else rule
    points: list[dict[str, Any]] = []
    for point in refinement.get("points", []):
        if not isinstance(point, dict):
            continue
        point_summary = _point_summary(point)
        evaluation = evaluate_boom_ending_watch(point_summary, loaded_rule)
        expected_status = _expected_status(loaded_rule, str(point.get("scenario_id")), str(point.get("as_of")))
        experimental_status = evaluation["experimental_watch_status"]
        points.append(
            {
                "scenario_id": point.get("scenario_id"),
                "as_of": point.get("as_of"),
                "label": point.get("label"),
                "refined_status": point.get("refined_status"),
                "weighted_boom_ending_score": point_summary["weighted_boom_ending_score"],
                "broad_group_count": point_summary["broad_group_count"],
                "high_signal_count": point_summary["high_signal_count"],
                "high_confidence_high_signal_count": point_summary["high_confidence_high_signal_count"],
                "rates_policy_high_signal_count": point_summary["rates_policy_high_signal_count"],
                "experimental_watch_status": experimental_status,
                "expected_status": expected_status,
                "matches_expected": expected_status is None or _status_matches(experimental_status, expected_status),
                "reason_zh": evaluation["reason_zh"],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rule_version": loaded_rule.version,
        "data_mode": loaded_rule.data_mode,
        "point_count": len(points),
        "points": points,
        "summary": _summary(points),
        "caveats_zh": loaded_rule.caveats_zh,
    }


def write_boom_ending_watch_rule_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write boom-ending watch rule report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _point_summary(point: dict[str, Any]) -> dict[str, Any]:
    rates_policy_high_signal_count = 0
    for group in point.get("refined_group_summary", []):
        if isinstance(group, dict) and group.get("group_id") == "rates_policy":
            rates_policy_high_signal_count = int(_num(group.get("high_signal_count")))
            break
    return {
        "weighted_boom_ending_score": _num(point.get("refined_score")),
        "broad_group_count": int(_num(point.get("refined_broad_group_count"))),
        "high_signal_count": int(_num(point.get("refined_high_signal_count"))),
        "high_confidence_high_signal_count": int(_num(point.get("refined_high_confidence_high_signal_count"))),
        "rates_policy_high_signal_count": rates_policy_high_signal_count,
    }


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(1 for point in points if point.get("matches_expected"))
    mismatch_count = len(points) - match_count
    statuses = [str(point.get("experimental_watch_status")) for point in points]
    unexpected_strong = [
        _point_id(point)
        for point in points
        if point.get("experimental_watch_status") == "strong_late_cycle_warning"
        and point.get("expected_status") not in {"watch_or_strong", "strong_late_cycle_warning"}
    ]
    missed_watch = [
        _point_id(point)
        for point in points
        if point.get("expected_status") in {"watch", "watch_or_strong"}
        and point.get("experimental_watch_status") in {"weak", "none"}
    ]
    return {
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "strong_late_cycle_warning_count": statuses.count("strong_late_cycle_warning"),
        "watch_count": statuses.count("watch"),
        "weak_count": statuses.count("weak"),
        "none_count": statuses.count("none"),
        "unexpected_strong_points": unexpected_strong,
        "missed_watch_points": missed_watch,
    }


def _expected_status(rule: BoomEndingWatchRule, scenario_id: str, as_of: str) -> str | None:
    return rule.expected_diagnostic_outcomes.get(scenario_id, {}).get(as_of)


def _status_matches(status: str, expected: str) -> bool:
    if expected == "watch_or_strong":
        return status in {"watch", "strong_late_cycle_warning"}
    if expected == "weak_or_watch":
        return status in {"weak", "watch"}
    return status == expected


def _point_id(point: dict[str, Any]) -> str:
    return f"{point.get('scenario_id')}:{point.get('as_of')}:{point.get('label')}"


def _validate_rule(rule: BoomEndingWatchRule) -> None:
    if rule.version < 1:
        raise BoomEndingWatchRuleError("version must be positive")
    for status in ("strong_late_cycle_warning", "watch", "weak", "none"):
        if status not in rule.required_interpretation_zh:
            raise BoomEndingWatchRuleError(f"required_interpretation_zh missing {status}")
    for status in ("strong_late_cycle_warning", "watch", "rates_policy_cluster_watch", "weak"):
        if status not in rule.group_thresholds:
            raise BoomEndingWatchRuleError(f"group_thresholds missing {status}")


def _load_json_or_mapping(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    path = Path(value)
    if not path.exists():
        raise BoomEndingWatchRuleError(
            f"boom ending refinement experiment JSON does not exist: {path}. "
            "Run scripts/run_boom_ending_refinement_experiment.py first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BoomEndingWatchRuleError(f"boom ending watch rule file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BoomEndingWatchRuleError(f"Invalid YAML in boom ending watch rule {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BoomEndingWatchRuleError("boom ending watch rule YAML must be a mapping")
    return payload


def _group_thresholds(value: Any) -> dict[str, dict[str, float]]:
    if not isinstance(value, dict):
        raise BoomEndingWatchRuleError("group_thresholds must be a mapping")
    result: dict[str, dict[str, float]] = {}
    for key, thresholds in value.items():
        if not isinstance(thresholds, dict):
            raise BoomEndingWatchRuleError(f"group_thresholds.{key} must be a mapping")
        result[str(key)] = {
            str(field): float(raw)
            for field, raw in thresholds.items()
            if isinstance(raw, int | float)
        }
    return result


def _expected_outcomes(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict):
        raise BoomEndingWatchRuleError("expected_diagnostic_outcomes must be a mapping")
    result: dict[str, dict[str, str]] = {}
    for scenario_id, points in value.items():
        if not isinstance(points, dict):
            raise BoomEndingWatchRuleError("expected_diagnostic_outcomes scenario values must be mappings")
        result[str(scenario_id)] = {str(as_of): str(status) for as_of, status in points.items()}
    return result


def _float_mapping(value: Any, field: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise BoomEndingWatchRuleError(f"{field} must be a mapping")
    return {str(key): float(raw) for key, raw in value.items()}


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise BoomEndingWatchRuleError(f"{field} must be a mapping")
    return {str(key): str(raw) for key, raw in value.items()}


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BoomEndingWatchRuleError(f"{field} must be a non-empty list")
    return [str(item) for item in value]


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
