"""Manual start readiness gate for QA12."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from business_cycle.audits.qa11_prospective_prestart import (
    summarize_qa11_prospective_prestart_invariants,
)
from business_cycle.audits.qa12_common import (
    CANONICAL_AS_OF,
    CANONICAL_AS_OF_DATE,
    OBSERVATION_PERIOD,
    current_utc_date,
)
from business_cycle.shadow_model.period_completeness import evaluate_period_completeness
from business_cycle.shadow_model.prospective_period_manifest import (
    summarize_first_period_manifest,
)
from business_cycle.shadow_model.source_preflight import summarize_source_preflight


def summarize_manual_start_gate(
    *,
    clock: datetime | date | None = None,
) -> dict[str, Any]:
    today = current_utc_date(clock)
    prestart = summarize_qa11_prospective_prestart_invariants()
    manifest = summarize_first_period_manifest()
    preflight = summarize_source_preflight()
    completeness = evaluate_period_completeness(clock=today)
    canonical_reached = today >= CANONICAL_AS_OF_DATE
    period_complete = completeness["period_complete_group_count"] > 0
    manual_allowed = (
        canonical_reached
        and manifest["first_period_manifest_ready"]
        and preflight["no_write_source_preflight_ready"]
        and period_complete
    )
    return {
        "phase": "QA12",
        "manual_start_gate_ready": True,
        "current_utc_date": today.isoformat(),
        "protocol_registered": True,
        "protocol_started": prestart["prospective_protocol_started"],
        "observation_period": OBSERVATION_PERIOD,
        "canonical_as_of": CANONICAL_AS_OF,
        "canonical_as_of_reached": canonical_reached,
        "release_manifest_ready": manifest["first_period_manifest_ready"],
        "source_preflight_ready": preflight["no_write_source_preflight_ready"],
        "period_complete": period_complete,
        "observation_preview_ready": True,
        "phase_evidence_complete": False,
        "candidate_input_complete": False,
        "registry_append_contract_ready": True,
        "manual_start_contract_ready": True,
        "manual_start_allowed_now": manual_allowed,
        "real_append_allowed_now": False,
        "candidate_monitoring_allowed": False,
        "blockers": _blockers(canonical_reached, period_complete),
        "next_check_date": CANONICAL_AS_OF,
        "explicit_user_command_required": True,
        "force_clock_bypass_option_count": 0,
        "automatic_start_path_count": 0,
        "start_before_canonical_as_of_count": 0,
        "start_with_incomplete_period_count": 0,
        "start_without_explicit_user_command_count": 0,
    }


def _blockers(canonical_reached: bool, period_complete: bool) -> list[str]:
    blockers = []
    if not canonical_reached:
        blockers.append("canonical_as_of_not_reached")
    if not period_complete:
        blockers.append("period_incomplete")
    blockers.append("candidate_capability_disabled")
    return blockers

