"""Phase 48 boom-to-recession transition evidence evaluators.

These evaluators adapt existing current evidence readiness rows into
transition-lane diagnostics. They do not infer the declared phase, emit a
candidate/current phase, or promote watch evidence into confirmation.
"""

from __future__ import annotations

from typing import Any

from business_cycle.transition_monitor.boom_transition_rules import (
    BoomTransitionLaneRule,
)


def evaluate_boom_transition_evidence(
    *,
    role_row: dict[str, Any],
    rule_row: dict[str, Any],
    role_contract: dict[str, Any],
    lane_rule: BoomTransitionLaneRule,
) -> dict[str, Any]:
    """Evaluate one priority role for one boom transition lane."""

    source_status = str(role_row["current_evidence_status"])
    blockers = list(role_row["blocker_reason_codes"])
    evaluator_runtime_ready = (
        rule_row["evaluator_status"] == "implemented_phase_evidence"
    )
    evidence_available = bool(role_row["current_phase_evidence_output_available"])
    explicit_abstention = (
        source_status in {"abstained", "unavailable"}
        or bool(blockers)
        or not evidence_available
    )
    lane_state = (
        "abstained"
        if explicit_abstention
        else _lane_state(source_status, lane_rule.lane_id)
    )
    if lane_rule.confirmation_lane and role_contract["role_id"].startswith("boom_"):
        lane_state = "abstained"
        explicit_abstention = True
        blockers.append("boom_watch_role_not_confirmation_input")

    return {
        "role_id": role_row["role_id"],
        "major_group_id": role_row["major_group_id"],
        "phase_or_layer": role_row["phase_or_layer"],
        "lane_id": lane_rule.lane_id,
        "lane_evidence_state": lane_state,
        "source_evidence_status": source_status,
        "source_availability_status": _source_availability_status(role_row),
        "required_series_ids": role_row["required_series_ids"],
        "contextual_series_ids": list(role_contract.get("contextual_series_ids", [])),
        "required_transformation": rule_row["required_transformation"],
        "transformation_semantics": role_contract["transformation_semantics"],
        "blocker_reason_codes": _dedupe(blockers),
        "book_statement_ids": rule_row["book_statement_ids"],
        "book_page_references": rule_row["book_page_references"],
        "book_logic_summary": role_contract["book_logic_summary"],
        "rule_source": rule_row["rule_source"],
        "typed_evidence_family": rule_row["typed_evidence_family"],
        "evaluator_runtime_ready": evaluator_runtime_ready,
        "evaluator_runtime_status": _runtime_status(
            evaluator_runtime_ready=evaluator_runtime_ready,
            evidence_available=evidence_available,
            explicit_abstention=explicit_abstention,
        ),
        "phase_evidence_output_available": evidence_available,
        "explicit_abstention": explicit_abstention,
        "watch_vs_confirmation_semantics": _watch_confirmation_semantics(lane_rule),
        "watch_evidence_promoted_to_confirmation": False,
        "confirmation_derived_from_watch_only": False,
        "smoothing_only_used_as_evidence": False,
        "raw_direction_alone_used_as_turning_point": False,
        "missing_treated_as_neutral": False,
        "missing_treated_as_zero": False,
        "proxy_fallback_used": False,
        "revised_fallback_used_for_point_in_time": False,
        "arbitrary_threshold_used": False,
        "numeric_weight_used": False,
        "role_count_voting_used": False,
        "historical_label_tuning_used": False,
        "market_return_tuning_used": False,
        "provenance_status": "available_from_existing_rule_registry",
        "data_mode": role_row["data_mode"],
        "wired_by_phase48": True,
    }


def _lane_state(status: str, lane_id: str) -> str:
    if lane_id == "boom_continuation":
        if status == "contradictory":
            return "supportive"
        if status == "supportive":
            return "contradictory"
    if status in {"supportive", "contradictory"}:
        return status
    return "abstained"


def _source_availability_status(role_row: dict[str, Any]) -> str:
    if role_row["current_phase_evidence_output_available"]:
        return "available_for_current_research"
    if role_row["blocker_reason_codes"]:
        return "blocked_or_missing"
    return "unavailable_or_abstained"


def _runtime_status(
    *,
    evaluator_runtime_ready: bool,
    evidence_available: bool,
    explicit_abstention: bool,
) -> str:
    if not evaluator_runtime_ready:
        return "blocked_rule_not_operational"
    if explicit_abstention:
        return "runtime_ready_explicit_abstention"
    if evidence_available:
        return "runtime_ready_evidence_available"
    return "runtime_ready_unavailable"


def _watch_confirmation_semantics(lane_rule: BoomTransitionLaneRule) -> str:
    if lane_rule.confirmation_lane:
        return "confirmation_lane_not_watch"
    if lane_rule.watch_lane:
        return "watch_lane_not_confirmation"
    return "continuation_context_not_transition_confirmation"


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped
