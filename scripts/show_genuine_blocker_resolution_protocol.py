from __future__ import annotations

from business_cycle.validation.genuine_blocker_resolution_protocol import (
    summarize_genuine_blocker_resolution_protocol,
)


def main() -> None:
    summary = summarize_genuine_blocker_resolution_protocol()
    for key in (
        "phase",
        "protocol_id",
        "protocol_version",
        "genuine_blocker_resolution_protocol_ready",
        "blocker_type_count",
        "allowed_resolution_action_count",
        "prohibited_resolution_action_count",
        "required_work_package_field_count",
        "blocker_resolution_executed",
        "scenario_promoted_to_comparable_count",
        "evidence_rule_modified_count",
        "predicted_mapping_rule_modified_count",
        "formal_decision_contract_modified_count",
        "threshold_modified_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
