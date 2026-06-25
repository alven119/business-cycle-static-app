from __future__ import annotations

from business_cycle.audits.shadow_recession_recovery_evidence_completion_freeze import (
    summarize_shadow_recession_recovery_evidence_completion_freeze,
)


def main() -> None:
    summary = summarize_shadow_recession_recovery_evidence_completion_freeze()
    for key in (
        "phase",
        "recession_recovery_evidence_completion_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_manifest_hash",
        "alpha33_freeze_hash_valid",
        "alpha32_parent_preserved",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "economic_validation_status",
        "phase36r_progress_status",
        "development_next_phase",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
