from __future__ import annotations

from business_cycle.audits.shadow_gap_resolution_freeze import (
    summarize_shadow_gap_resolution_freeze,
)


def main() -> None:
    summary = summarize_shadow_gap_resolution_freeze()
    for key in (
        "phase",
        "gap_resolution_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "alpha8_freeze_hash_valid",
        "alpha7_parent_preserved",
        "parent_freeze_present",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "candidate_selection_enabled",
        "current_phase_enabled",
        "prospective_protocol_started",
        "prospective_registry_record_count",
        "prospective_registry_write_attempt_count",
        "holdout_registered",
        "economic_validation_status",
        "book_alignment_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "gap_resolution_registry_ready",
        "newly_operationalized_evaluator_count",
        "false_resolution_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
