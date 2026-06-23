from __future__ import annotations

from business_cycle.audits.shadow_phase_evidence_freeze import (
    summarize_shadow_phase_evidence_freeze,
)


def main() -> None:
    summary = summarize_shadow_phase_evidence_freeze()
    for key in (
        "phase",
        "phase_evidence_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_manifest_hash",
        "freeze_hash_valid",
        "parent_freeze_present",
        "prior_freeze_preserved",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "candidate_selection_enabled",
        "current_phase_enabled",
        "holdout_registered",
        "economic_validation_status",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
