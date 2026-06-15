"""Experimental recession confirmation rule for candidate indicators."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


class CandidateRecessionRuleError(ValueError):
    """Raised when candidate recession rule inputs are invalid."""


@dataclass(frozen=True)
class CandidateRecessionConfirmationRule:
    """Experimental recession confirmation rule."""

    version: int
    status: str
    data_mode: str
    caveats_zh: list[str]
    signal_thresholds: dict[str, float]
    group_thresholds: dict[str, dict[str, float]]
    required_interpretation_zh: dict[str, str]
    expected_diagnostic_outcomes: dict[str, dict[str, str]]


def load_candidate_recession_confirmation_rule(
    path: str | Path,
) -> CandidateRecessionConfirmationRule:
    """Load and validate candidate recession confirmation rule YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("candidate_recession_confirmation_rule")
    if not isinstance(raw, dict):
        raise CandidateRecessionRuleError("candidate_recession_confirmation_rule YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise CandidateRecessionRuleError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CandidateRecessionRuleError("caveats_zh must include no-investment-advice caveat")

    rule = CandidateRecessionConfirmationRule(
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


def evaluate_candidate_recession_confirmation(
    point_summary: dict[str, Any],
    rule: CandidateRecessionConfirmationRule,
) -> dict[str, Any]:
    """Evaluate one candidate diagnostics point against the experimental rule."""

    status = classify_candidate_recession_status(point_summary, rule)
    reason = rule.required_interpretation_zh[status]
    return {
        "experimental_status": status,
        "reason_zh": reason,
        "rule_inputs": {
            "weighted_confirmation_score": _num(point_summary.get("weighted_confirmation_score")),
            "broad_group_count": int(_num(point_summary.get("broad_group_count"))),
            "high_signal_count": int(_num(point_summary.get("high_signal_count"))),
            "high_confidence_high_signal_count": int(
                _num(point_summary.get("high_confidence_high_signal_count"))
            ),
        },
    }


def classify_candidate_recession_status(
    point_summary: dict[str, Any],
    rule: CandidateRecessionConfirmationRule,
) -> str:
    """Classify candidate recession confirmation status."""

    weighted_score = _num(point_summary.get("weighted_confirmation_score"))
    broad_groups = _num(point_summary.get("broad_group_count"))
    high_signals = _num(point_summary.get("high_signal_count"))
    high_confidence_high_signals = _num(point_summary.get("high_confidence_high_signal_count"))

    confirmed = rule.group_thresholds["confirmed"]
    if (
        broad_groups >= confirmed["min_broad_group_count"]
        and high_confidence_high_signals >= confirmed["min_high_confidence_high_signal_count"]
        and weighted_score >= confirmed["min_weighted_confirmation_score"]
    ):
        return "confirmed"

    watch = rule.group_thresholds["watch"]
    if (
        broad_groups >= watch["min_broad_group_count"]
        and high_signals >= watch["min_high_signal_count"]
        and weighted_score >= watch["min_weighted_confirmation_score"]
    ):
        return "watch"

    weak = rule.group_thresholds["weak"]
    if high_signals >= weak["min_high_signal_count"]:
        return "weak"
    return "none"


def build_candidate_recession_rule_report(
    diagnostics_json: str | Path | dict[str, Any],
    rule: CandidateRecessionConfirmationRule | str | Path,
) -> dict[str, Any]:
    """Build a rule report from candidate recession diagnostics."""

    diagnostics = _load_json_or_mapping(diagnostics_json)
    loaded_rule = (
        load_candidate_recession_confirmation_rule(rule)
        if isinstance(rule, str | Path)
        else rule
    )
    points: list[dict[str, Any]] = []
    for point in diagnostics.get("points", []):
        if not isinstance(point, dict):
            continue
        summary = dict(point.get("candidate_summary") or {})
        evaluation = evaluate_candidate_recession_confirmation(summary, loaded_rule)
        expected_status = _expected_status(loaded_rule, str(point.get("scenario_id")), str(point.get("as_of")))
        experimental_status = evaluation["experimental_status"]
        points.append(
            {
                "scenario_id": point.get("scenario_id"),
                "as_of": point.get("as_of"),
                "label": point.get("label"),
                "weighted_confirmation_score": summary.get("weighted_confirmation_score"),
                "broad_group_count": summary.get("broad_group_count"),
                "high_signal_count": summary.get("high_signal_count"),
                "high_confidence_high_signal_count": summary.get("high_confidence_high_signal_count"),
                "experimental_status": experimental_status,
                "expected_status": expected_status,
                "matches_expected": expected_status is None or experimental_status == expected_status,
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


def write_candidate_recession_rule_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write candidate recession rule report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(1 for point in points if point.get("matches_expected"))
    mismatch_count = len(points) - match_count
    statuses = [str(point.get("experimental_status")) for point in points]
    false_confirmed = [
        _point_id(point)
        for point in points
        if point.get("experimental_status") == "confirmed"
        and point.get("expected_status") in {"watch", "weak", "none"}
    ]
    missed_confirmed = [
        _point_id(point)
        for point in points
        if point.get("expected_status") == "confirmed"
        and point.get("experimental_status") != "confirmed"
    ]
    return {
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "confirmed_count": statuses.count("confirmed"),
        "watch_count": statuses.count("watch"),
        "weak_count": statuses.count("weak"),
        "none_count": statuses.count("none"),
        "false_confirmed_points": false_confirmed,
        "missed_confirmed_points": missed_confirmed,
    }


def _expected_status(
    rule: CandidateRecessionConfirmationRule,
    scenario_id: str,
    as_of: str,
) -> str | None:
    return rule.expected_diagnostic_outcomes.get(scenario_id, {}).get(as_of)


def _point_id(point: dict[str, Any]) -> str:
    return f"{point.get('scenario_id')}:{point.get('as_of')}:{point.get('label')}"


def _validate_rule(rule: CandidateRecessionConfirmationRule) -> None:
    if rule.version < 1:
        raise CandidateRecessionRuleError("version must be positive")
    for status in ("confirmed", "watch", "weak", "none"):
        if status not in rule.required_interpretation_zh:
            raise CandidateRecessionRuleError(f"required_interpretation_zh missing {status}")
    for status in ("confirmed", "watch", "weak"):
        if status not in rule.group_thresholds:
            raise CandidateRecessionRuleError(f"group_thresholds missing {status}")


def _load_json_or_mapping(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    path = Path(value)
    if not path.exists():
        raise CandidateRecessionRuleError(
            f"candidate recession diagnostics JSON does not exist: {path}. "
            "Run scripts/run_candidate_recession_diagnostics.py first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CandidateRecessionRuleError(f"candidate recession rule file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateRecessionRuleError(f"Invalid YAML in candidate recession rule {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CandidateRecessionRuleError("candidate recession rule YAML must be a mapping")
    return payload


def _group_thresholds(value: Any) -> dict[str, dict[str, float]]:
    if not isinstance(value, dict):
        raise CandidateRecessionRuleError("group_thresholds must be a mapping")
    result: dict[str, dict[str, float]] = {}
    for key, thresholds in value.items():
        result[str(key)] = _float_mapping(thresholds, f"group_thresholds.{key}")
    return result


def _expected_outcomes(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict):
        raise CandidateRecessionRuleError("expected_diagnostic_outcomes must be a mapping")
    result: dict[str, dict[str, str]] = {}
    for scenario_id, outcomes in value.items():
        if not isinstance(outcomes, dict):
            raise CandidateRecessionRuleError("expected_diagnostic_outcomes scenario entries must be mappings")
        result[str(scenario_id)] = {str(as_of): str(status) for as_of, status in outcomes.items()}
    return result


def _float_mapping(value: Any, field: str) -> dict[str, float]:
    if not isinstance(value, dict) or not value:
        raise CandidateRecessionRuleError(f"{field} must be a non-empty mapping")
    return {str(key): float(raw_value) for key, raw_value in value.items()}


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict) or not value:
        raise CandidateRecessionRuleError(f"{field} must be a non-empty mapping")
    return {str(key): str(raw_value) for key, raw_value in value.items()}


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionRuleError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CandidateRecessionRuleError(f"{field} entries must be non-empty")
    return items


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
