"""Research assistant for declared phase-start context.

This module researches candidate start-date context for the declared boom
state. It does not write the declared registry, infer the current phase, or
emit candidate/current phase outputs.
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
from business_cycle.transition_monitor.boom_transition_monitor import (
    build_boom_transition_monitor,
)

ROOT = Path(__file__).resolve().parents[3]
ASSISTANT_SPEC_PATH = ROOT / "specs/common/phase_start_research_assistant.yaml"
HYPOTHESIS_SPEC_PATH = ROOT / "specs/common/phase_start_research_hypotheses.yaml"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_winner",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}

PHASE48_PRIORITY_ROLE_IDS = (
    "boom_claims_u_shape",
    "boom_retail_sales_vs_broad_pce",
    "boom_private_investment",
    "recession_employment_confirmation",
    "recession_consumption_confirmation",
)


@dataclass(frozen=True)
class PhaseStartResearchAssistantArtifact:
    """JSON-ready Phase47 research artifact."""

    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a stable artifact dictionary."""

        return dict(self.payload)


def build_phase_start_research_assistant(
    *,
    current_evidence: dict[str, Any] | None = None,
    declared_state: DeclaredCycleState | None = None,
    boom_monitor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the Phase47 research assistant artifact."""

    _load_required_contracts()
    declared_state = declared_state or load_declared_cycle_state()
    current_evidence = current_evidence or build_current_evidence_readiness()
    boom_monitor = boom_monitor or build_boom_transition_monitor(
        current_evidence=current_evidence,
        declared_state=declared_state,
    )
    rule_rows = build_book_phase_evidence_rule_rows()
    role_rows = current_evidence["role_readiness_rows"]
    hypotheses = [
        _user_prior_hypothesis(declared_state, current_evidence, rule_rows),
        _evidence_based_hypothesis(declared_state, current_evidence, rule_rows, role_rows),
    ]
    phase48_plan = build_phase48_boom_monitor_evidence_wiring_plan(
        current_evidence=current_evidence,
        boom_monitor=boom_monitor,
        rule_rows=rule_rows,
    )
    artifact = {
        "assistant_id": "phase_start_research_assistant_v1",
        "assistant_version": "1.0",
        "output_mode": "research_only_phase_start_context",
        "declared_current_phase": declared_state.declared_current_phase,
        "declared_phase_start_date_current_value": (
            declared_state.declared_phase_start_date.isoformat()
            if declared_state.declared_phase_start_date is not None
            else None
        ),
        "declared_phase_start_date_unchanged": True,
        "phase_age_status_current_value": declared_state.phase_age_status,
        "legal_previous_phase": declared_state.legal_previous_phase,
        "legal_next_phase": declared_state.legal_next_phase,
        "hypothesis_count": len(hypotheses),
        "user_prior_hypothesis_present": any(
            item["hypothesis_id"] == "user_prior_hypothesis"
            for item in hypotheses
        ),
        "evidence_based_hypothesis_present": any(
            item["hypothesis_id"] == "evidence_based_research_hypothesis"
            for item in hypotheses
        ),
        "hypotheses": hypotheses,
        "missing_evidence_summary": _missing_evidence_summary(hypotheses),
        "source_provenance_summary": _source_provenance_summary(current_evidence),
        "book_traceability_summary": _book_traceability_summary(rule_rows),
        "phase48_boom_monitor_evidence_wiring_plan": phase48_plan,
        "phase48_boom_monitor_evidence_wiring_plan_ready": phase48_plan[
            "phase48_boom_monitor_evidence_wiring_plan_ready"
        ],
        "phase48_plan_governance_only": False,
        "top_phase48_evidence_wiring_priorities": phase48_plan[
            "highest_product_value_evidence_to_wire_first"
        ],
        "user_confirmation_required": True,
        "registry_write_allowed": False,
        "declared_registry_modified": False,
        "phase_age_used_as_transition_gate": False,
        "false_precision_start_date_count": _false_precision_start_date_count(
            hypotheses
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "selected_phase_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "label_used_by_runtime_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "phase_start_research_context_added_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "allowed_uses": [
            "research_candidate_declared_phase_start_context",
            "dashboard_phase_age_context_review",
            "phase48_evidence_wiring_planning",
        ],
        "prohibited_uses": [
            "declared_registry_auto_write",
            "formal_current_phase_inference",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "portfolio_action",
            "production_resolver_input",
        ],
    }
    artifact["prohibited_action_field_count"] = _contains_prohibited_field(artifact)
    artifact["result"] = "passed" if _passes(artifact) else "blocked"
    return PhaseStartResearchAssistantArtifact(artifact).to_dict()


def summarize_phase_start_research_assistant() -> dict[str, Any]:
    """Return Phase47 hard-gate summary."""

    artifact = build_phase_start_research_assistant()
    user_hypothesis = _hypothesis_by_id(artifact, "user_prior_hypothesis")
    evidence_hypothesis = _hypothesis_by_id(
        artifact,
        "evidence_based_research_hypothesis",
    )
    return {
        "phase": "47",
        "phase_start_research_assistant_contract_ready": True,
        "phase_start_research_assistant_runtime_ready": artifact["result"] == "passed",
        "declared_current_phase": artifact["declared_current_phase"],
        "declared_phase_start_date_current_value": artifact[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_unchanged": artifact[
            "declared_phase_start_date_unchanged"
        ],
        "phase_age_status_current_value": artifact["phase_age_status_current_value"],
        "legal_next_phase": artifact["legal_next_phase"],
        "hypothesis_count": artifact["hypothesis_count"],
        "user_prior_hypothesis_present": artifact["user_prior_hypothesis_present"],
        "evidence_based_hypothesis_present": artifact[
            "evidence_based_hypothesis_present"
        ],
        "user_prior_hypothesis_summary": _hypothesis_summary(user_hypothesis),
        "evidence_based_hypothesis_summary": _hypothesis_summary(evidence_hypothesis),
        "false_precision_start_date_count": artifact[
            "false_precision_start_date_count"
        ],
        "user_confirmation_required": artifact["user_confirmation_required"],
        "registry_write_allowed": artifact["registry_write_allowed"],
        "declared_registry_modified": artifact["declared_registry_modified"],
        "phase_age_used_as_transition_gate": artifact[
            "phase_age_used_as_transition_gate"
        ],
        "missing_evidence_summary": artifact["missing_evidence_summary"],
        "source_provenance_summary": artifact["source_provenance_summary"],
        "book_traceability_summary": artifact["book_traceability_summary"],
        "phase48_boom_monitor_evidence_wiring_plan_ready": artifact[
            "phase48_boom_monitor_evidence_wiring_plan_ready"
        ],
        "top_phase48_evidence_wiring_priorities": artifact[
            "top_phase48_evidence_wiring_priorities"
        ],
        "phase48_plan_governance_only": artifact["phase48_plan_governance_only"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "selected_phase_output_count": artifact["selected_phase_output_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "arbitrary_threshold_added_count": artifact[
            "arbitrary_threshold_added_count"
        ],
        "numeric_weight_added_count": artifact["numeric_weight_added_count"],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "historical_tuning_leakage_count": artifact[
            "historical_tuning_leakage_count"
        ],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": artifact[
            "legacy_v1_behavior_modified_count"
        ],
        "portfolio_policy_output_count": artifact["portfolio_policy_output_count"],
        "backtest_execution_count": artifact["backtest_execution_count"],
        "label_used_by_runtime_count": artifact["label_used_by_runtime_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": artifact[
            "legal_transition_semantics_preserved"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "result": artifact["result"],
    }


def build_phase48_boom_monitor_evidence_wiring_plan(
    *,
    current_evidence: dict[str, Any] | None = None,
    boom_monitor: dict[str, Any] | None = None,
    rule_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a machine-readable Phase48 evidence wiring plan."""

    current_evidence = current_evidence or build_current_evidence_readiness()
    boom_monitor = boom_monitor or build_boom_transition_monitor(
        current_evidence=current_evidence
    )
    rule_by_role = {
        row["role_id"]: row
        for row in (rule_rows or build_book_phase_evidence_rule_rows())
    }
    role_rows = {
        row["role_id"]: row
        for row in current_evidence["role_readiness_rows"]
    }
    lane_inputs = []
    for lane_key, lane_mapping in (
        ("boom_continuation", "boom_continuation_evidence"),
        ("boom_ending_watch", "boom_ending_watch_evidence"),
        ("recession_watch", "recession_watch_evidence"),
        ("recession_confirmation", "recession_confirmation_evidence"),
    ):
        lane = boom_monitor[lane_mapping]
        for item in lane["evidence_items"]:
            role_id = item["role_id"]
            role = role_rows[role_id]
            rule = rule_by_role[role_id]
            lane_inputs.append(
                {
                    "role_id": role_id,
                    "source_availability_status": _source_availability_status(role),
                    "data_mode_support": role["data_mode"],
                    "transformation_needed": rule["required_transformation"],
                    "rule_readiness": rule["evaluator_status"],
                    "lane_mapping": lane_key,
                    "watch_vs_confirmation_semantics": _watch_confirmation_semantics(
                        lane
                    ),
                    "blocker": role["blocker_reason_codes"] or [],
                }
            )
    priorities = [
        item
        for item in lane_inputs
        if item["role_id"] in PHASE48_PRIORITY_ROLE_IDS
    ]
    return {
        "phase48_boom_monitor_evidence_wiring_plan_ready": True,
        "plan_version": "phase48_boom_monitor_evidence_wiring_plan_v1",
        "boom_continuation_candidate_inputs": _lane_inputs(
            lane_inputs,
            "boom_continuation",
        ),
        "boom_ending_watch_candidate_inputs": _lane_inputs(
            lane_inputs,
            "boom_ending_watch",
        ),
        "recession_watch_candidate_inputs": _lane_inputs(
            lane_inputs,
            "recession_watch",
        ),
        "recession_confirmation_candidate_inputs": _lane_inputs(
            lane_inputs,
            "recession_confirmation",
        ),
        "highest_product_value_evidence_to_wire_first": priorities,
        "prioritization_policy": (
            "prioritize roles that explain boom weakening and recession confirmation "
            "for the declared boom to recession legal transition; no phase ranking "
            "or score is introduced"
        ),
        "governance_only": False,
    }


def _user_prior_hypothesis(
    declared_state: DeclaredCycleState,
    current_evidence: dict[str, Any],
    rule_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "hypothesis_id": "user_prior_hypothesis",
        "hypothesis_source": "user_provided",
        "candidate_start_date_or_window": (
            "user_provided_window: boom may have started before mid-2025; "
            "April-May 2026 may be a recovery-to-boom transition revision window"
        ),
        "hypothesis_status": "user_input_unverified",
        "supporting_evidence": [],
        "contradictory_evidence": [],
        "missing_evidence": _role_missing_evidence(current_evidence, ("growth", "boom"))[:8],
        "freshness_or_release_lag_caveats": _freshness_caveats(current_evidence),
        "source_provenance": _source_provenance_summary(current_evidence),
        "book_traceability": _traceability(rule_rows, ("growth_indicators", "boom_ending_indicators")),
        "user_confirmation_required": True,
        "registry_write_allowed": False,
        "phase_age_used_as_transition_gate": False,
        "false_precision_flag": False,
        "declared_current_phase_context": declared_state.declared_current_phase,
    }


def _evidence_based_hypothesis(
    declared_state: DeclaredCycleState,
    current_evidence: dict[str, Any],
    rule_rows: list[dict[str, Any]],
    role_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    supporting = [
        _role_evidence_summary(row)
        for row in role_rows
        if row["phase"] in {"growth", "boom"} and row["supportive"]
    ]
    contradictory = [
        _role_evidence_summary(row)
        for row in role_rows
        if row["phase"] in {"growth", "boom"} and row["contradictory"]
    ]
    missing = _role_missing_evidence(current_evidence, ("growth", "boom"))
    has_supported_window = bool(supporting) and not missing and not contradictory
    return {
        "hypothesis_id": "evidence_based_research_hypothesis",
        "hypothesis_source": "existing_macro_evidence_contracts",
        "candidate_start_date_or_window": None if not has_supported_window else "review_required",
        "hypothesis_status": (
            "needs_user_review" if has_supported_window else "insufficient_evidence"
        ),
        "supporting_evidence": supporting,
        "contradictory_evidence": contradictory,
        "missing_evidence": missing[:16],
        "freshness_or_release_lag_caveats": _freshness_caveats(current_evidence),
        "source_provenance": _source_provenance_summary(current_evidence),
        "book_traceability": _traceability(rule_rows, ("growth_indicators", "boom_ending_indicators")),
        "user_confirmation_required": True,
        "registry_write_allowed": False,
        "phase_age_used_as_transition_gate": False,
        "false_precision_flag": False,
        "declared_current_phase_context": declared_state.declared_current_phase,
    }


def _role_missing_evidence(
    current_evidence: dict[str, Any],
    phases: tuple[str, ...],
) -> list[dict[str, Any]]:
    return [
        {
            "role_id": row["role_id"],
            "phase": row["phase"],
            "major_group_id": row["major_group_id"],
            "required_series_ids": row["required_series_ids"],
            "blocker_reason_codes": row["blocker_reason_codes"],
            "evidence_status": row["current_evidence_status"],
            "observation_only": row["observation_only"],
        }
        for row in current_evidence["role_readiness_rows"]
        if row["phase"] in phases and (row["unavailable"] or row["observation_only"])
    ]


def _role_evidence_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "role_id": row["role_id"],
        "phase": row["phase"],
        "major_group_id": row["major_group_id"],
        "evidence_status": row["current_evidence_status"],
        "required_series_ids": row["required_series_ids"],
    }


def _freshness_caveats(current_evidence: dict[str, Any]) -> list[str]:
    freshness = current_evidence["freshness_summary"]
    caveats = [
        f"data_mode={current_evidence['data_mode']}",
        f"refresh_mode={current_evidence['refresh_mode']}",
        "latest revised/current metadata is not strict point-in-time evidence",
    ]
    if freshness["missing_series_count"]:
        caveats.append(f"missing_series_count={freshness['missing_series_count']}")
    if freshness["stale_series_count_after"]:
        caveats.append(
            f"stale_series_count_after={freshness['stale_series_count_after']}"
        )
    return caveats


def _source_provenance_summary(current_evidence: dict[str, Any]) -> dict[str, Any]:
    freshness = current_evidence["freshness_summary"]
    return {
        "snapshot_as_of": current_evidence["snapshot_as_of"],
        "data_mode": current_evidence["data_mode"],
        "refresh_mode": current_evidence["refresh_mode"],
        "model_id": current_evidence["model_id"],
        "freeze_id": current_evidence["freeze_id"],
        "requested_series_count": freshness["requested_series_count"],
        "fresh_enough_series_count": freshness["fresh_enough_series_count"],
        "missing_series_count": freshness["missing_series_count"],
        "release_lag_metadata_used_count": freshness[
            "release_lag_metadata_used_count"
        ],
    }


def _book_traceability_summary(rule_rows: list[dict[str, Any]]) -> dict[str, Any]:
    traceability = _traceability(
        rule_rows,
        ("growth_indicators", "boom_ending_indicators"),
    )
    return {
        "statement_id_count": len(traceability["book_statement_ids"]),
        "page_reference_count": len(traceability["book_page_references"]),
        "book_statement_ids": traceability["book_statement_ids"][:10],
        "book_page_references": traceability["book_page_references"],
    }


def _traceability(
    rule_rows: list[dict[str, Any]],
    layers: tuple[str, ...],
) -> dict[str, Any]:
    statement_ids: list[str] = []
    page_refs: list[str] = []
    for row in rule_rows:
        if row["phase_or_layer"] not in layers:
            continue
        for statement_id in row["book_statement_ids"]:
            if statement_id not in statement_ids:
                statement_ids.append(statement_id)
        for page_ref in row["book_page_references"]:
            if page_ref not in page_refs:
                page_refs.append(page_ref)
    return {
        "book_statement_ids": statement_ids,
        "book_page_references": page_refs,
    }


def _missing_evidence_summary(hypotheses: list[dict[str, Any]]) -> dict[str, Any]:
    missing_by_role: dict[str, dict[str, Any]] = {}
    for hypothesis in hypotheses:
        for item in hypothesis["missing_evidence"]:
            missing_by_role.setdefault(item["role_id"], item)
    return {
        "missing_evidence_count": len(missing_by_role),
        "top_missing_roles": list(missing_by_role.values())[:10],
    }


def _hypothesis_by_id(artifact: dict[str, Any], hypothesis_id: str) -> dict[str, Any]:
    for hypothesis in artifact["hypotheses"]:
        if hypothesis["hypothesis_id"] == hypothesis_id:
            return hypothesis
    raise KeyError(hypothesis_id)


def _hypothesis_summary(hypothesis: dict[str, Any]) -> dict[str, Any]:
    return {
        "hypothesis_id": hypothesis["hypothesis_id"],
        "hypothesis_source": hypothesis["hypothesis_source"],
        "candidate_start_date_or_window": hypothesis[
            "candidate_start_date_or_window"
        ],
        "hypothesis_status": hypothesis["hypothesis_status"],
        "supporting_evidence_count": len(hypothesis["supporting_evidence"]),
        "contradictory_evidence_count": len(hypothesis["contradictory_evidence"]),
        "missing_evidence_count": len(hypothesis["missing_evidence"]),
        "user_confirmation_required": hypothesis["user_confirmation_required"],
        "registry_write_allowed": hypothesis["registry_write_allowed"],
    }


def _source_availability_status(role: dict[str, Any]) -> str:
    if role["current_phase_evidence_output_available"]:
        return "available_for_current_research"
    if role["blocker_reason_codes"]:
        return "blocked_or_missing"
    return "unavailable_or_abstained"


def _watch_confirmation_semantics(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "confirmation_lane_not_watch"
    if lane["watch_lane"]:
        return "watch_lane_not_confirmation"
    return "continuation_context_not_transition_confirmation"


def _lane_inputs(
    lane_inputs: list[dict[str, Any]],
    lane_id: str,
) -> list[dict[str, Any]]:
    return [item for item in lane_inputs if item["lane_mapping"] == lane_id]


def _false_precision_start_date_count(hypotheses: list[dict[str, Any]]) -> int:
    return sum(
        bool(item["false_precision_flag"])
        for item in hypotheses
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_required_contracts() -> None:
    for path in (ASSISTANT_SPEC_PATH, HYPOTHESIS_SPEC_PATH):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def _passes(artifact: dict[str, Any]) -> bool:
    return (
        artifact["declared_current_phase"] == "boom"
        and artifact["declared_phase_start_date_unchanged"] is True
        and artifact["registry_write_allowed"] is False
        and artifact["user_confirmation_required"] is True
        and artifact["hypothesis_count"] >= 2
        and artifact["user_prior_hypothesis_present"] is True
        and artifact["evidence_based_hypothesis_present"] is True
        and artifact["false_precision_start_date_count"] == 0
        and artifact["phase_age_used_as_transition_gate"] is False
        and artifact["current_data_used_to_infer_declared_phase_count"] == 0
        and artifact["standalone_classifier_added_count"] == 0
        and artifact["phase_rank_or_score_added_count"] == 0
        and artifact["selected_phase_output_count"] == 0
        and artifact["candidate_phase_emitted"] is False
        and artifact["current_phase_emitted"] is False
        and artifact["portfolio_policy_output_count"] == 0
        and artifact["backtest_execution_count"] == 0
        and artifact["label_used_by_runtime_count"] == 0
        and artifact["arbitrary_threshold_added_count"] == 0
        and artifact["numeric_weight_added_count"] == 0
        and artifact["role_count_voting_added_count"] == 0
        and artifact["historical_tuning_leakage_count"] == 0
        and artifact["production_behavior_change_count"] == 0
        and artifact["legacy_v1_behavior_modified_count"] == 0
        and artifact["semantic_drift_count"] == 0
        and artifact["product_doctrine_alignment_status"] == "aligned"
        and artifact["cycle_state_machine_alignment_status"]
        == "phase_start_research_context_added_registry_unchanged"
        and artifact["legal_transition_semantics_preserved"] is True
        and artifact["phase48_boom_monitor_evidence_wiring_plan_ready"] is True
        and artifact["phase48_plan_governance_only"] is False
        and artifact["prohibited_action_field_count"] == 0
    )
