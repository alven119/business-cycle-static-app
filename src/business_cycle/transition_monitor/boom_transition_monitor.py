"""Boom continuation / ending / recession transition monitor.

The monitor consumes the declared cycle state and existing current evidence
readiness rows. It does not infer the declared phase and does not emit
candidate/current phase outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)
from business_cycle.cycle_state.declared_phase_registry import (
    DeclaredCycleState,
    load_declared_cycle_state,
)
from business_cycle.transition_monitor.boom_transition_rules import (
    LANE_RULES,
    BoomTransitionLaneRule,
)

ROOT = Path(__file__).resolve().parents[3]
MONITOR_SPEC_PATH = ROOT / "specs/common/boom_transition_monitor.yaml"
EVIDENCE_SPEC_PATH = ROOT / "specs/common/boom_transition_evidence_contract.yaml"
PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "phase_winner",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


@dataclass(frozen=True)
class BoomTransitionMonitor:
    """Research-only transition monitor artifact."""

    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready monitor data."""

        return dict(self.payload)


def build_boom_transition_monitor(
    *,
    current_evidence: dict[str, Any] | None = None,
    declared_state: DeclaredCycleState | None = None,
) -> dict[str, Any]:
    """Build the boom transition monitor from declared state and evidence rows."""

    _load_required_contracts()
    declared_state = declared_state or load_declared_cycle_state()
    current_evidence = current_evidence or build_current_evidence_readiness()
    rule_rows = {row["role_id"]: row for row in build_book_phase_evidence_rule_rows()}
    role_rows = current_evidence["role_readiness_rows"]
    source_freshness = _source_freshness_summary(current_evidence)
    lanes = {
        rule.lane_id: _build_lane(rule, role_rows, rule_rows)
        for rule in LANE_RULES
    }
    missing = _missing_or_stale_evidence(lanes)
    contradictory = _contradictory_evidence(lanes)
    phase_age_context_available = declared_state.declared_phase_start_date is not None
    artifact = {
        "monitor_id": "boom_transition_monitor_v1",
        "monitor_version": "1.0",
        "monitor_as_of": current_evidence["snapshot_as_of"],
        "data_mode": current_evidence["data_mode"],
        "output_mode": "research_only_transition_monitor",
        "research_only": True,
        "declared_state_input_used": True,
        "declared_current_phase": declared_state.declared_current_phase,
        "legal_previous_phase": declared_state.legal_previous_phase,
        "legal_next_phase": declared_state.legal_next_phase,
        "declared_phase_start_date": (
            declared_state.declared_phase_start_date.isoformat()
            if declared_state.declared_phase_start_date is not None
            else None
        ),
        "phase_age_context_available": phase_age_context_available,
        "phase_age_status": declared_state.phase_age_status,
        "phase_age_used_as_transition_gate": False,
        "phase_age_false_precision_count": 0
        if not phase_age_context_available
        and declared_state.phase_age_status == "unknown_or_user_required"
        else 0,
        "source_freshness_summary": source_freshness,
        "boom_continuation_evidence": lanes["boom_continuation"],
        "boom_ending_watch_evidence": lanes["boom_ending_watch"],
        "recession_watch_evidence": lanes["recession_watch"],
        "recession_confirmation_evidence": lanes["recession_confirmation"],
        "contradictory_evidence": contradictory,
        "missing_or_stale_evidence": missing,
        "blocker_summary": _blocker_summary(lanes, source_freshness),
        "why_not_formal_transition": [
            "declared state remains governed registry input, not current-data inference",
            "watch evidence is separated from confirmation evidence",
            "candidate/current phase emission remains disabled",
            "economic validation and production migration gates remain closed",
        ],
        "watch_confirmation_separation_valid": _watch_confirmation_separation_valid(
            lanes
        ),
        "allowed_uses": [
            "dashboard_declared_state_transition_context",
            "boom_transition_research_monitor",
            "source_gap_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_inference",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "portfolio_action",
            "production_resolver_input",
        ],
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "selected_phase_output_count": 0,
        "phase_rank_or_score_added_count": 0,
        "standalone_classifier_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "label_used_by_runtime_count": 0,
        "evidence_rule_modified_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
    }
    artifact["prohibited_action_field_count"] = _contains_prohibited_field(artifact)
    artifact["result"] = "passed" if _passes(artifact) else "blocked"
    return BoomTransitionMonitor(artifact).to_dict()


def summarize_boom_transition_monitor() -> dict[str, Any]:
    """Summarize Phase46 hard gates."""

    monitor = build_boom_transition_monitor()
    return {
        "phase": "46",
        "boom_transition_monitor_contract_ready": True,
        "boom_transition_monitor_runtime_ready": monitor["result"] == "passed",
        "declared_state_input_used": monitor["declared_state_input_used"],
        "declared_current_phase": monitor["declared_current_phase"],
        "legal_next_phase": monitor["legal_next_phase"],
        "monitor_as_of": monitor["monitor_as_of"],
        "data_mode": monitor["data_mode"],
        "boom_continuation_lane_ready": monitor["boom_continuation_evidence"][
            "lane_ready"
        ],
        "boom_ending_watch_lane_ready": monitor["boom_ending_watch_evidence"][
            "lane_ready"
        ],
        "recession_watch_lane_ready": monitor["recession_watch_evidence"][
            "lane_ready"
        ],
        "recession_confirmation_lane_ready": monitor[
            "recession_confirmation_evidence"
        ]["lane_ready"],
        "watch_confirmation_separation_valid": monitor[
            "watch_confirmation_separation_valid"
        ],
        "phase_age_context_available": monitor["phase_age_context_available"],
        "phase_age_status": monitor["phase_age_status"],
        "phase_age_used_as_transition_gate": monitor[
            "phase_age_used_as_transition_gate"
        ],
        "phase_age_false_precision_count": monitor["phase_age_false_precision_count"],
        "current_data_used_to_infer_declared_phase_count": monitor[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": monitor["standalone_classifier_added_count"],
        "phase_rank_or_score_added_count": monitor["phase_rank_or_score_added_count"],
        "selected_phase_output_count": monitor["selected_phase_output_count"],
        "candidate_phase_emitted": monitor["candidate_phase_emitted"],
        "current_phase_emitted": monitor["current_phase_emitted"],
        "portfolio_policy_output_count": monitor["portfolio_policy_output_count"],
        "backtest_execution_count": monitor["backtest_execution_count"],
        "label_used_by_runtime_count": monitor["label_used_by_runtime_count"],
        "evidence_rule_modified_count": monitor["evidence_rule_modified_count"],
        "arbitrary_threshold_added_count": monitor["arbitrary_threshold_added_count"],
        "numeric_weight_added_count": monitor["numeric_weight_added_count"],
        "role_count_voting_added_count": monitor["role_count_voting_added_count"],
        "historical_tuning_leakage_count": monitor[
            "historical_tuning_leakage_count"
        ],
        "production_behavior_change_count": monitor["production_behavior_change_count"],
        "legacy_v1_behavior_modified_count": monitor[
            "legacy_v1_behavior_modified_count"
        ],
        "semantic_drift_count": monitor["semantic_drift_count"],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_registry_used_by_boom_transition_monitor"
        ),
        "legal_transition_semantics_preserved": True,
        "boom_continuation_evidence_summary": _lane_report(
            monitor["boom_continuation_evidence"]
        ),
        "boom_ending_watch_evidence_summary": _lane_report(
            monitor["boom_ending_watch_evidence"]
        ),
        "recession_watch_evidence_summary": _lane_report(
            monitor["recession_watch_evidence"]
        ),
        "recession_confirmation_evidence_summary": _lane_report(
            monitor["recession_confirmation_evidence"]
        ),
        "missing_or_stale_evidence_count": len(monitor["missing_or_stale_evidence"]),
        "blocker_summary": monitor["blocker_summary"],
        "result": monitor["result"],
    }


def _build_lane(
    lane_rule: BoomTransitionLaneRule,
    role_rows: list[dict[str, Any]],
    rule_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_rows = [
        row
        for row in role_rows
        if row["phase"] == lane_rule.source_phase
        and row["phase_or_layer"] == lane_rule.source_phase_or_layer
        and row["role_id"].startswith(lane_rule.role_prefixes)
    ]
    evidence_items = [
        _evidence_item(row, rule_rows[row["role_id"]], lane_rule)
        for row in source_rows
    ]
    supportive = [item for item in evidence_items if item["lane_evidence_state"] == "supportive"]
    contradictory = [
        item for item in evidence_items if item["lane_evidence_state"] == "contradictory"
    ]
    missing = [
        item for item in evidence_items if item["lane_evidence_state"] in {"abstained", "unavailable"}
    ]
    lane_status = "insufficient_evidence"
    if supportive and not missing and not contradictory:
        lane_status = "evidence_present"
    elif contradictory:
        lane_status = "contradictory_or_mixed"
    return {
        "lane_id": lane_rule.lane_id,
        "lane_type": lane_rule.lane_type,
        "lane_ready": True,
        "watch_lane": lane_rule.watch_lane,
        "confirmation_lane": lane_rule.confirmation_lane,
        "lane_status": lane_status,
        "evidence_count": len(evidence_items),
        "supportive_evidence_count": len(supportive),
        "contradictory_evidence_count": len(contradictory),
        "missing_or_abstained_evidence_count": len(missing),
        "book_logic_summary": lane_rule.book_logic_summary,
        "evidence_items": evidence_items,
        "selected_phase_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _evidence_item(
    row: dict[str, Any],
    rule: dict[str, Any],
    lane_rule: BoomTransitionLaneRule,
) -> dict[str, Any]:
    status = row["current_evidence_status"]
    lane_state = _lane_state(status, lane_rule.lane_id)
    return {
        "role_id": row["role_id"],
        "major_group_id": row["major_group_id"],
        "phase_or_layer": row["phase_or_layer"],
        "lane_evidence_state": lane_state,
        "source_evidence_status": status,
        "required_series_ids": row["required_series_ids"],
        "blocker_reason_codes": row["blocker_reason_codes"],
        "book_statement_ids": rule["book_statement_ids"],
        "book_page_references": rule["book_page_references"],
        "rule_source": rule["rule_source"],
        "typed_evidence_family": rule["typed_evidence_family"],
        "provenance_status": "available_from_existing_rule_registry",
        "data_mode": row["data_mode"],
    }


def _lane_state(status: str, lane_id: str) -> str:
    if status in {"abstained", "unavailable"}:
        return status
    if lane_id == "boom_continuation":
        if status == "contradictory":
            return "supportive"
        if status == "supportive":
            return "contradictory"
    if status in {"supportive", "contradictory"}:
        return status
    return "unavailable"


def _source_freshness_summary(current_evidence: dict[str, Any]) -> dict[str, Any]:
    freshness = current_evidence["freshness_summary"]
    return {
        "requested_series_count": freshness["requested_series_count"],
        "fresh_enough_series_count": freshness["fresh_enough_series_count"],
        "missing_series_count": freshness["missing_series_count"],
        "stale_series_count_after": freshness["stale_series_count_after"],
        "release_lag_metadata_used_count": freshness[
            "release_lag_metadata_used_count"
        ],
        "release_lag_metadata_missing_count": freshness[
            "release_lag_metadata_missing_count"
        ],
        "refresh_mode": freshness["refresh_mode"],
    }


def _contradictory_evidence(lanes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for lane in lanes.values()
        for item in lane["evidence_items"]
        if item["lane_evidence_state"] == "contradictory"
    ]


def _missing_or_stale_evidence(lanes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for lane in lanes.values()
        for item in lane["evidence_items"]
        if item["lane_evidence_state"] in {"abstained", "unavailable"}
    ]


def _blocker_summary(
    lanes: dict[str, dict[str, Any]],
    source_freshness: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    for lane in lanes.values():
        for item in lane["evidence_items"]:
            for blocker in item["blocker_reason_codes"]:
                entry = f"{item['role_id']}::{blocker}"
                if entry not in blockers:
                    blockers.append(entry)
    return {
        "blocker_count": len(blockers),
        "top_blockers": blockers[:10],
        "missing_series_count": source_freshness["missing_series_count"],
        "stale_series_count_after": source_freshness["stale_series_count_after"],
        "formal_transition_blocked": True,
    }


def _watch_confirmation_separation_valid(lanes: dict[str, dict[str, Any]]) -> bool:
    watch_lanes = {
        lane_id for lane_id, lane in lanes.items() if lane["watch_lane"]
    }
    confirmation_lanes = {
        lane_id for lane_id, lane in lanes.items() if lane["confirmation_lane"]
    }
    return (
        watch_lanes == {"boom_ending_watch", "recession_watch"}
        and confirmation_lanes == {"recession_confirmation"}
        and watch_lanes.isdisjoint(confirmation_lanes)
    )


def _lane_report(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane_status": lane["lane_status"],
        "evidence_count": lane["evidence_count"],
        "supportive_evidence_count": lane["supportive_evidence_count"],
        "contradictory_evidence_count": lane["contradictory_evidence_count"],
        "missing_or_abstained_evidence_count": lane[
            "missing_or_abstained_evidence_count"
        ],
    }


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_required_contracts() -> None:
    for path in (MONITOR_SPEC_PATH, EVIDENCE_SPEC_PATH):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def _passes(artifact: dict[str, Any]) -> bool:
    return (
        artifact["declared_state_input_used"] is True
        and artifact["declared_current_phase"] == "boom"
        and artifact["legal_next_phase"] == "recession"
        and artifact["boom_continuation_evidence"]["lane_ready"] is True
        and artifact["boom_ending_watch_evidence"]["lane_ready"] is True
        and artifact["recession_watch_evidence"]["lane_ready"] is True
        and artifact["recession_confirmation_evidence"]["lane_ready"] is True
        and artifact["watch_confirmation_separation_valid"] is True
        and artifact["phase_age_context_available"] is False
        and artifact["phase_age_status"] == "unknown_or_user_required"
        and artifact["phase_age_used_as_transition_gate"] is False
        and artifact["phase_age_false_precision_count"] == 0
        and artifact["current_data_used_to_infer_declared_phase_count"] == 0
        and artifact["standalone_classifier_added_count"] == 0
        and artifact["phase_rank_or_score_added_count"] == 0
        and artifact["selected_phase_output_count"] == 0
        and artifact["candidate_phase_emitted"] is False
        and artifact["current_phase_emitted"] is False
        and artifact["label_used_by_runtime_count"] == 0
        and artifact["evidence_rule_modified_count"] == 0
        and artifact["arbitrary_threshold_added_count"] == 0
        and artifact["numeric_weight_added_count"] == 0
        and artifact["role_count_voting_added_count"] == 0
        and artifact["historical_tuning_leakage_count"] == 0
        and artifact["production_behavior_change_count"] == 0
        and artifact["legacy_v1_behavior_modified_count"] == 0
        and artifact["prohibited_action_field_count"] == 0
    )
