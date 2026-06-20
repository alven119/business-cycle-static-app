"""Experimental recovery watch rule for refined recovery diagnostics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


class RecoveryWatchRuleError(ValueError):
    """Raised when recovery watch rule inputs are invalid."""


@dataclass(frozen=True)
class RecoveryWatchRule:
    """Experimental recovery watch rule."""

    version: int
    status: str
    data_mode: str
    caveats_zh: list[str]
    signal_thresholds: dict[str, float]
    context_gate: dict[str, Any]
    support_signal_cap: dict[str, Any]
    group_thresholds: dict[str, dict[str, Any]]
    required_interpretation_zh: dict[str, str]
    expected_diagnostic_outcomes: dict[str, dict[str, str]]


def load_recovery_watch_rule(path: str | Path) -> RecoveryWatchRule:
    """Load and validate recovery watch rule YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("recovery_watch_rule")
    if not isinstance(raw, dict):
        raise RecoveryWatchRuleError("recovery_watch_rule YAML must contain a mapping")
    caveats = _non_empty_str_list(raw.get("caveats_zh"), "caveats_zh")
    for required in [
        "修訂後歷史資料",
        "recovery watch 不等於正式復甦確認",
        "policy easing 不得單獨確認 recovery",
        "financial easing 不得單獨確認 recovery",
        "不構成投資建議",
    ]:
        if not any(required in caveat for caveat in caveats):
            raise RecoveryWatchRuleError(f"caveats_zh must include {required}")
    rule = RecoveryWatchRule(
        version=int(raw.get("version", 0)),
        status=str(raw.get("status", "")),
        data_mode=str(raw.get("data_mode", "")),
        caveats_zh=caveats,
        signal_thresholds=_float_mapping(raw.get("signal_thresholds"), "signal_thresholds"),
        context_gate=_mapping(raw.get("context_gate"), "context_gate"),
        support_signal_cap=_mapping(raw.get("support_signal_cap"), "support_signal_cap"),
        group_thresholds=_group_thresholds(raw.get("group_thresholds")),
        required_interpretation_zh=_str_mapping(raw.get("required_interpretation_zh"), "required_interpretation_zh"),
        expected_diagnostic_outcomes=_expected_outcomes(raw.get("expected_diagnostic_outcomes")),
    )
    _validate_rule(rule)
    return rule


def evaluate_recovery_watch(point_summary: dict[str, Any], rule: RecoveryWatchRule) -> dict[str, Any]:
    """Evaluate one refined recovery point against the experimental rule."""

    status = classify_recovery_watch_status(point_summary, rule)
    return {
        "experimental_recovery_watch_status": status,
        "reason_zh": rule.required_interpretation_zh[status],
        "rule_inputs": {
            "weighted_recovery_score": _num(point_summary.get("weighted_recovery_score")),
            "broad_group_count": int(_num(point_summary.get("broad_group_count"))),
            "high_signal_count": int(_num(point_summary.get("high_signal_count"))),
            "high_confidence_high_signal_count": int(
                _num(point_summary.get("high_confidence_high_signal_count"))
            ),
            "policy_only_signal": bool(point_summary.get("policy_only_signal")),
            "support_signal_cap_applied": bool(point_summary.get("support_signal_cap_applied")),
            "context_gate_applied": bool(point_summary.get("context_gate_applied")),
            "recession_context_detected": bool(point_summary.get("recession_context_detected")),
            "exogenous_shock_caveat": bool(point_summary.get("exogenous_shock_caveat")),
            "exogenous_shock_caveated_watch_floor": bool(
                point_summary.get("exogenous_shock_caveated_watch_floor")
            ),
            "labor_confirmed": bool(point_summary.get("labor_confirmed")),
            "real_activity_confirmed": bool(point_summary.get("real_activity_confirmed")),
            "credit_financial_confirmed": bool(point_summary.get("credit_financial_confirmed")),
        },
    }


def classify_recovery_watch_status(point_summary: dict[str, Any], rule: RecoveryWatchRule) -> str:
    """Classify experimental recovery watch status from refined diagnostics."""

    weighted_score = _num(point_summary.get("weighted_recovery_score"))
    broad_groups = _num(point_summary.get("broad_group_count"))
    high_signals = _num(point_summary.get("high_signal_count"))
    high_confidence_high_signals = _num(point_summary.get("high_confidence_high_signal_count"))
    recession_context = bool(point_summary.get("recession_context_detected"))
    exogenous_shock = bool(point_summary.get("exogenous_shock_caveat"))
    support_cap_applied = bool(point_summary.get("support_signal_cap_applied"))
    policy_only = bool(point_summary.get("policy_only_signal"))
    refined_status = str(point_summary.get("refined_status", ""))
    exogenous_watch_floor = bool(point_summary.get("exogenous_shock_caveated_watch_floor"))
    labor_confirmed = bool(point_summary.get("labor_confirmed"))
    real_activity_confirmed = bool(point_summary.get("real_activity_confirmed"))
    credit_confirmed = bool(point_summary.get("credit_financial_confirmed"))

    max_status = "strong_recovery_watch"
    if not recession_context and rule.context_gate.get("require_recession_context_for_watch", True):
        max_status = str(rule.context_gate.get("max_status_without_recession_context", "weak"))
    if support_cap_applied or policy_only:
        if exogenous_shock and exogenous_watch_floor:
            max_status = _min_status(max_status, "recovery_watch")
        else:
            max_status = _min_status(
                max_status,
                str(rule.support_signal_cap.get("policy_financial_only_max_status", "weak")),
            )
    if exogenous_shock and not (labor_confirmed and real_activity_confirmed):
        max_status = _min_status(max_status, "recovery_watch")

    strong = rule.group_thresholds["strong_recovery_watch"]
    if (
        broad_groups >= _num(strong.get("min_broad_group_count"))
        and high_confidence_high_signals >= _num(strong.get("min_high_confidence_high_signal_count"))
        and weighted_score >= _num(strong.get("min_weighted_recovery_score"))
        and (not strong.get("require_labor_confirmation") or labor_confirmed)
        and (not strong.get("require_real_activity_or_credit_confirmation") or real_activity_confirmed or credit_confirmed)
        and _status_allowed("strong_recovery_watch", max_status)
    ):
        return "strong_recovery_watch"

    watch = rule.group_thresholds["recovery_watch"]
    if (
        broad_groups >= _num(watch.get("min_broad_group_count"))
        and high_signals >= _num(watch.get("min_high_signal_count"))
        and weighted_score >= _num(watch.get("min_weighted_recovery_score"))
        and (
            not watch.get("require_labor_or_real_activity_confirmation")
            or labor_confirmed
            or real_activity_confirmed
        )
        and _status_allowed("recovery_watch", max_status)
    ):
        return "recovery_watch"
    if (
        exogenous_shock
        and exogenous_watch_floor
        and refined_status == "watch"
        and recession_context
        and weighted_score >= _num(watch.get("min_weighted_recovery_score"))
        and _status_allowed("recovery_watch", max_status)
    ):
        return "recovery_watch"

    weak = rule.group_thresholds["weak"]
    if high_signals >= _num(weak.get("min_high_signal_count")):
        return "weak"
    return "none"


def build_recovery_watch_rule_report(
    refinement_experiment_json: str | Path | dict[str, Any],
    rule: RecoveryWatchRule | str | Path,
) -> dict[str, Any]:
    """Build a recovery watch rule report from refinement experiment output."""

    refinement = _load_json_or_mapping(refinement_experiment_json)
    loaded_rule = load_recovery_watch_rule(rule) if isinstance(rule, str | Path) else rule
    points: list[dict[str, Any]] = []
    for point in refinement.get("points", []):
        if not isinstance(point, dict):
            continue
        point_summary = _point_summary(point)
        evaluation = evaluate_recovery_watch(point_summary, loaded_rule)
        expected_status = _expected_status(loaded_rule, str(point.get("scenario_id")), str(point.get("as_of")))
        experimental_status = evaluation["experimental_recovery_watch_status"]
        points.append(
            {
                "scenario_id": point.get("scenario_id"),
                "as_of": point.get("as_of"),
                "label": point.get("label"),
                "refined_status": point.get("refined_status"),
                "weighted_recovery_score": point_summary["weighted_recovery_score"],
                "broad_group_count": point_summary["broad_group_count"],
                "high_signal_count": point_summary["high_signal_count"],
                "high_confidence_high_signal_count": point_summary[
                    "high_confidence_high_signal_count"
                ],
                "policy_only_signal": point_summary["policy_only_signal"],
                "support_signal_cap_applied": point_summary["support_signal_cap_applied"],
                "context_gate_applied": point_summary["context_gate_applied"],
                "recession_context_detected": point_summary["recession_context_detected"],
                "exogenous_shock_caveat": point_summary["exogenous_shock_caveat"],
                "exogenous_shock_caveated_watch_floor": point_summary[
                    "exogenous_shock_caveated_watch_floor"
                ],
                "experimental_recovery_watch_status": experimental_status,
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


def write_recovery_watch_rule_report(output_path: str | Path, report: dict[str, Any]) -> Path:
    """Write recovery watch rule report JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _point_summary(point: dict[str, Any]) -> dict[str, Any]:
    summary = dict(point.get("candidate_summary_before_caps") or {})
    support_cap = dict(point.get("support_cap_summary") or {})
    context_gate = dict(point.get("context_gate_summary") or {})
    status_adjustments = [
        adjustment
        for adjustment in point.get("status_adjustments", [])
        if isinstance(adjustment, dict)
    ]
    return {
        "refined_status": str(point.get("refined_status", "")),
        "weighted_recovery_score": _num(summary.get("weighted_recovery_score", point.get("refined_score"))),
        "broad_group_count": int(_num(summary.get("broad_group_count"))),
        "high_signal_count": int(_num(summary.get("high_signal_count"))),
        "high_confidence_high_signal_count": int(_num(summary.get("high_confidence_high_signal_count"))),
        "policy_only_signal": bool(summary.get("policy_only_signal")),
        "labor_confirmed": bool(summary.get("labor_confirmed")),
        "real_activity_confirmed": bool(summary.get("real_activity_confirmed")),
        "credit_financial_confirmed": bool(summary.get("credit_financial_confirmed")),
        "support_signal_cap_applied": bool(
            point.get("support_signal_cap_applied")
            or support_cap.get("support_only_cap_applied")
        ),
        "context_gate_applied": bool(point.get("context_gate_applied") or context_gate.get("context_gate_applied")),
        "recession_context_detected": bool(context_gate.get("recession_context_detected")),
        "exogenous_shock_caveat": bool(context_gate.get("exogenous_shock_caveat")),
        "exogenous_shock_caveated_watch_floor": any(
            adjustment.get("kind") == "exogenous_shock_caveated_watch_floor"
            for adjustment in status_adjustments
        ),
    }


def _summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(1 for point in points if point.get("matches_expected"))
    mismatch_count = len(points) - match_count
    statuses = [str(point.get("experimental_recovery_watch_status")) for point in points]
    unexpected_strong = [
        _point_id(point)
        for point in points
        if point.get("experimental_recovery_watch_status") == "strong_recovery_watch"
        and point.get("expected_status") not in {"watch_or_strong", "strong_recovery_watch"}
    ]
    missed_watch = [
        _point_id(point)
        for point in points
        if point.get("expected_status") in {"watch_or_strong", "recovery_watch"}
        and point.get("experimental_recovery_watch_status") in {"weak", "none"}
    ]
    non_recession_watch = [
        _point_id(point)
        for point in points
        if point.get("expected_status") == "weak_or_none"
        and point.get("experimental_recovery_watch_status") in {"recovery_watch", "strong_recovery_watch"}
    ]
    return {
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "strong_recovery_watch_count": statuses.count("strong_recovery_watch"),
        "recovery_watch_count": statuses.count("recovery_watch"),
        "weak_count": statuses.count("weak"),
        "none_count": statuses.count("none"),
        "policy_only_blocked_count": sum(1 for point in points if point.get("support_signal_cap_applied")),
        "context_gate_blocked_count": sum(1 for point in points if point.get("context_gate_applied")),
        "unexpected_strong_points": unexpected_strong,
        "missed_recovery_watch_points": missed_watch,
        "non_recession_watch_points": non_recession_watch,
    }


def _expected_status(rule: RecoveryWatchRule, scenario_id: str, as_of: str) -> str | None:
    return rule.expected_diagnostic_outcomes.get(scenario_id, {}).get(as_of)


def _status_matches(status: str, expected: str) -> bool:
    if expected == "watch_or_strong":
        return status in {"recovery_watch", "strong_recovery_watch"}
    if expected == "weak_or_watch":
        return status in {"weak", "recovery_watch"}
    if expected == "weak_or_none":
        return status in {"weak", "none"}
    return status == expected


def _point_id(point: dict[str, Any]) -> str:
    return f"{point.get('scenario_id')}:{point.get('as_of')}:{point.get('label')}"


STATUS_ORDER = {"none": 0, "weak": 1, "recovery_watch": 2, "strong_recovery_watch": 3}


def _min_status(left: str, right: str) -> str:
    return left if STATUS_ORDER[left] <= STATUS_ORDER[right] else right


def _status_allowed(status: str, max_status: str) -> bool:
    return STATUS_ORDER[status] <= STATUS_ORDER[max_status]


def _validate_rule(rule: RecoveryWatchRule) -> None:
    if rule.version < 1:
        raise RecoveryWatchRuleError("version must be positive")
    for status in ("strong_recovery_watch", "recovery_watch", "weak", "none"):
        if status not in rule.required_interpretation_zh:
            raise RecoveryWatchRuleError(f"required_interpretation_zh missing {status}")
    for status in ("strong_recovery_watch", "recovery_watch", "weak"):
        if status not in rule.group_thresholds:
            raise RecoveryWatchRuleError(f"group_thresholds missing {status}")


def _load_json_or_mapping(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    path = Path(value)
    if not path.exists():
        raise RecoveryWatchRuleError(
            f"recovery refinement experiment JSON does not exist: {path}. "
            "Run scripts/run_recovery_refinement_experiment.py first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryWatchRuleError(f"recovery watch rule file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryWatchRuleError(f"Invalid YAML in recovery watch rule {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RecoveryWatchRuleError("recovery watch rule YAML must be a mapping")
    return payload


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RecoveryWatchRuleError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _group_thresholds(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise RecoveryWatchRuleError("group_thresholds must be a mapping")
    result: dict[str, dict[str, Any]] = {}
    for key, thresholds in value.items():
        if not isinstance(thresholds, dict):
            raise RecoveryWatchRuleError(f"group_thresholds.{key} must be a mapping")
        result[str(key)] = {str(field): raw for field, raw in thresholds.items()}
    return result


def _expected_outcomes(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict):
        raise RecoveryWatchRuleError("expected_diagnostic_outcomes must be a mapping")
    result: dict[str, dict[str, str]] = {}
    for scenario_id, points in value.items():
        if not isinstance(points, dict):
            raise RecoveryWatchRuleError("expected_diagnostic_outcomes scenario values must be mappings")
        result[str(scenario_id)] = {str(as_of): str(status) for as_of, status in points.items()}
    return result


def _float_mapping(value: Any, field: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise RecoveryWatchRuleError(f"{field} must be a mapping")
    return {str(key): float(raw) for key, raw in value.items()}


def _str_mapping(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise RecoveryWatchRuleError(f"{field} must be a mapping")
    return {str(key): str(raw) for key, raw in value.items()}


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RecoveryWatchRuleError(f"{field} must be a non-empty list")
    return [str(item) for item in value]


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
