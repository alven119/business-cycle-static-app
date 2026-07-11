"""Read-only prospective validation calendar state for the private NAS."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.pre_registered_validation import (
    summarize_pre_registered_validation_protocol,
)
from business_cycle.audits.phase126_nas_v1_operational_acceptance_closure import (
    summarize_phase126_nas_v1_operational_acceptance_closure,
)
from business_cycle.audits.prospective_protocol_start_semantics import (
    summarize_protocol_start_semantics,
)
from business_cycle.audits.prospective_wait_state import (
    summarize_prospective_wait_state,
)
from business_cycle.audits.qa12_common import current_utc_date
from business_cycle.shadow_model.manual_start_gate import summarize_manual_start_gate
from business_cycle.shadow_model.prospective_period_manifest import (
    summarize_first_period_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_prospective_validation_wait_state_contract.yaml"
)


def load_nas_prospective_validation_wait_state_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_prospective_validation_wait_state_contract"])


def build_nas_prospective_validation_wait_state(
    *,
    clock: datetime | date | None = None,
    phase126_acceptance_status: dict[str, Any] | None = None,
    registry_metadata: dict[str, Any] | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build calendar/readiness diagnostics without reading validation results."""

    contract = load_nas_prospective_validation_wait_state_contract(contract_path)
    today = current_utc_date(clock)
    wait = summarize_prospective_wait_state(clock=today)
    manual = summarize_manual_start_gate(clock=today)
    protocol = summarize_protocol_start_semantics()
    preregistered = summarize_pre_registered_validation_protocol()
    manifest = summarize_first_period_manifest()
    acceptance = phase126_acceptance_status or (
        summarize_phase126_nas_v1_operational_acceptance_closure()["artifact"]
    )
    registry = registry_metadata or {}
    record_count = int(registry.get("real_registry_record_count", 0))
    write_count = int(registry.get("real_registry_write_attempt_count", 0))
    evaluation_months = int(registry.get("evaluation_month_count", 0))
    complete_dates = int(registry.get("complete_strict_date_count", 0))
    transition_events = int(registry.get("unseen_transition_event_count", 0))
    stress_events = int(
        registry.get("unseen_non_recession_stress_event_count", 0)
    )
    earliest_append = date.fromisoformat(manifest["earliest_possible_manual_append_at"])
    seal_ready = (
        protocol["protocol_started"]
        and evaluation_months >= int(contract["minimum_evaluation_months"])
        and complete_dates >= int(contract["minimum_complete_strict_dates"])
        and transition_events > 0
        and stress_events > 0
        and bool(registry.get("independent_validation_passed", False))
    )
    state: dict[str, Any] = {
        "phase": 127,
        "artifact_id": "phase127_nas_prospective_validation_calendar_wait_state",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "current_utc_date": today.isoformat(),
        "observation_period": contract["observation_period"],
        "canonical_as_of": contract["canonical_as_of"],
        "earliest_possible_manual_append_at": earliest_append.isoformat(),
        "current_wait_state": wait["current_wait_state"],
        "canonical_as_of_reached": manual["canonical_as_of_reached"],
        "earliest_manual_append_reached": today >= earliest_append,
        "phase126_acceptance_dependency_ready": bool(
            acceptance.get("nas_v1_operational_acceptance_passed", False)
        ),
        "protocol_registered": protocol["protocol_registered"],
        "registry_armed": protocol["registry_armed"],
        "protocol_started": protocol["protocol_started"],
        "evaluation_month_count": evaluation_months,
        "minimum_evaluation_months": int(contract["minimum_evaluation_months"]),
        "complete_strict_date_count": complete_dates,
        "minimum_complete_strict_dates": int(
            contract["minimum_complete_strict_dates"]
        ),
        "unseen_transition_event_count": transition_events,
        "unseen_non_recession_stress_event_count": stress_events,
        "prospective_registry_record_count": record_count,
        "real_registry_write_attempt_count": write_count,
        "prospective_result_inspected": protocol["prospective_result_inspected"],
        "manual_start_allowed_now": manual["manual_start_allowed_now"],
        "explicit_user_command_required": manual["explicit_user_command_required"],
        "automatic_start_path_count": manual["automatic_start_path_count"],
        "calendar_gate_bypass_count": 0,
        "parameter_change_resets_evaluation_window": preregistered[
            "parameter_change_resets_holdout"
        ],
        "prior_records_retained_after_reset": True,
        "prospective_wait_state_contract_ready": _contract_ready(contract),
        "prospective_validation_seal_ready": seal_ready,
        "formal_production_validated": False,
        "economic_validation_status": "not_started",
        "recommended_next_action": "WAIT_FOR_FIRST_ELIGIBLE_AS_OF",
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "private_nas_calendar_gate_review",
            "prospective_input_progress_review",
            "registry_metadata_review",
        ],
        "prohibited_uses": [
            "automatic_registry_append",
            "prospective_result_inspection",
            "rule_tuning",
            "candidate_phase_selection",
            "formal_production_validation_claim",
        ],
        "trust_metadata": {
            "registry_metadata_only": True,
            "validation_result_payload_read": False,
            "registry_write_attempted": False,
            "calendar_gate_bypass_allowed": False,
            "qa12_manifest_hash": manifest["manifest_hash"],
        },
    }
    state["result"] = "passed" if _passes(state, contract["hard_gates"]) else "blocked"
    return state


def summarize_nas_prospective_validation_wait_state(
    *, clock: datetime | date | None = None
) -> dict[str, Any]:
    return build_nas_prospective_validation_wait_state(clock=clock)


def _contract_ready(contract: dict[str, Any]) -> bool:
    calendar = contract["calendar_policy"]
    validation = contract["validation_policy"]
    output = contract["output_policy"]
    return (
        contract["status"] == "active_calendar_wait_contract"
        and calendar["bypass_allowed"] is False
        and calendar["automatic_start_allowed"] is False
        and calendar["automatic_registry_append_allowed"] is False
        and calendar["explicit_user_command_required"] is True
        and validation["result_inspection_before_gate_allowed"] is False
        and validation["rule_tuning_from_results_allowed"] is False
        and validation["parameter_change_resets_evaluation_window"] is True
        and output["registry_metadata_only"] is True
        and output["candidate_phase_emission_allowed"] is False
        and output["current_phase_emission_allowed"] is False
    )


def _passes(state: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(state.get(key) == value for key, value in expected.items())
