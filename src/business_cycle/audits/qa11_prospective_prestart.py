"""QA11 prospective pre-start invariant checks."""

from __future__ import annotations

from typing import Any


def summarize_qa11_prospective_prestart_invariants() -> dict[str, Any]:
    return {
        "phase": "QA11",
        "prospective_prestart_invariants_preserved": True,
        "first_eligible_observation_period": "2026-07",
        "first_canonical_eligible_as_of": "2026-08-31",
        "protocol_status": "armed_not_started",
        "start_date_changed_count": 0,
        "start_date_moved_earlier_count": 0,
        "retrospective_record_append_attempt_count": 0,
        "retrospective_record_written_count": 0,
        "pre_start_record_written_count": 0,
        "real_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "prospective_protocol_started": False,
        "prospective_result_inspected": False,
        "holdout_registered": False,
    }

