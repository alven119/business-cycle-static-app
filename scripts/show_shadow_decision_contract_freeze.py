from __future__ import annotations

from business_cycle.audits.shadow_decision_contract_freeze import (
    summarize_shadow_decision_contract_freeze,
)


def main() -> None:
    summary = summarize_shadow_decision_contract_freeze()
    for key in (
        "phase",
        "decision_contract_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "alpha9_freeze_hash_valid",
        "alpha8_parent_preserved",
        "parent_freeze_present",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prospective_protocol_started",
        "prospective_registry_record_count",
        "prospective_registry_write_attempt_count",
        "holdout_registered",
        "economic_validation_status",
        "formal_decision_model_ready",
        "candidate_capability_ready",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "formal_decision_contract_ready",
        "candidate_precondition_profile_ready",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
