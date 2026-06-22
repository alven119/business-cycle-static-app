from __future__ import annotations

from business_cycle.audits.formal_scope_diff import summarize_formal_model_scope_diff


def main() -> None:
    summary = summarize_formal_model_scope_diff()
    for key in (
        "phase",
        "formal_scope_diff_ready",
        "current_formal_v1_indicator_count",
        "proposed_v2_core_role_count",
        "retained_v1_indicator_count",
        "v1_to_supporting_count",
        "v1_modern_extension_count",
        "proposed_v2_experimental_candidate_count",
        "proposed_v2_missing_role_count",
        "proposed_v2_temporal_blocked_count",
        "proposed_v2_data_contract_blocked_count",
        "proposed_v2_independent_validation_blocked_count",
        "production_behavior_change_count",
    ):
        print(f"{key}={str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}")


if __name__ == "__main__":
    main()

