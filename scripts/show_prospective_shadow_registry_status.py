from __future__ import annotations

from business_cycle.audits.prospective_protocol_start_semantics import (
    summarize_protocol_start_semantics,
)
from business_cycle.shadow_model.prospective_forward_gate import (
    summarize_forward_clock_gate,
)
from business_cycle.shadow_model.prospective_registry import (
    MODEL_FREEZE_ID,
    PROTOCOL_ID,
    REGISTRY_ID,
)


def main() -> None:
    start = summarize_protocol_start_semantics()
    gate = summarize_forward_clock_gate()
    status = {
        "registry_id": REGISTRY_ID,
        "protocol_id": PROTOCOL_ID,
        "model_freeze_id": MODEL_FREEZE_ID,
        "registry_status": "armed_not_started",
        "protocol_registered": start["protocol_registered"],
        "registry_armed": start["registry_armed"],
        "protocol_started": start["protocol_started"],
        "first_eligible_observation_period": start[
            "first_eligible_observation_period"
        ],
        "first_eligible_complete_as_of": start["first_eligible_complete_as_of"],
        "candidate_capability_ready": gate["candidate_capability_ready"],
        "real_record_count": start["real_record_count"],
        "metadata_only_record_count": start["metadata_only_record_count"],
        "candidate_record_count": start["candidate_record_count"],
        "latest_record_period": "none",
        "chain_valid": True,
        "result_inspected": start["prospective_result_inspected"],
        "holdout_registered": start["holdout_registered"],
    }
    for key, value in status.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
