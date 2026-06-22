"""QA9 prospective protocol start semantics."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.prospective_forward_gate import (
    CANONICAL_AS_OF,
    FIRST_ELIGIBLE_OBSERVATION_PERIOD,
)


def summarize_protocol_start_semantics() -> dict[str, Any]:
    """Return registered/armed/started flags for QA9."""

    return {
        "phase": "QA9",
        "protocol_start_semantics_ready": True,
        "protocol_registered": True,
        "registry_armed": True,
        "protocol_started": False,
        "first_record_written": False,
        "real_record_count": 0,
        "metadata_only_record_count": 0,
        "candidate_record_count": 0,
        "prospective_result_inspected": False,
        "holdout_registered": False,
        "first_eligible_observation_period": FIRST_ELIGIBLE_OBSERVATION_PERIOD,
        "first_eligible_complete_as_of": CANONICAL_AS_OF,
    }
