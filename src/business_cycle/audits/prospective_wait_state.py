"""QA12 prospective wait-state governance."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from business_cycle.audits.qa12_common import (
    CANONICAL_AS_OF,
    CANONICAL_AS_OF_DATE,
    OBSERVATION_PERIOD_START,
    current_utc_date,
)
from business_cycle.shadow_model.prospective_period_manifest import (
    summarize_first_period_manifest,
)


def summarize_prospective_wait_state(
    *,
    clock: datetime | date | None = None,
) -> dict[str, Any]:
    today = current_utc_date(clock)
    manifest = summarize_first_period_manifest()
    if today < OBSERVATION_PERIOD_START:
        state = "pre_period"
    elif today < CANONICAL_AS_OF_DATE:
        state = "awaiting_canonical_as_of"
    else:
        state = "awaiting_late_releases"
    return {
        "phase": "QA12",
        "wait_state_governance_ready": True,
        "current_wait_state": state,
        "next_check_date": CANONICAL_AS_OF,
        "earliest_possible_manual_append_at": manifest[
            "earliest_possible_manual_append_at"
        ],
        "qa13_allowed_now": False,
        "qa13_earliest_as_of": CANONICAL_AS_OF,
        "real_registry_append_allowed_now": False,
        "candidate_monitoring_allowed_now": False,
        "allowed_development_while_waiting": [
            "source_adapter_maintenance",
            "data_contract_remediation",
            "fixture_improvements",
            "documentation",
        ],
        "prohibited_actions_while_waiting": [
            "real_prospective_append",
            "candidate_monitoring",
            "result_inspection",
            "rule_tuning",
        ],
    }
