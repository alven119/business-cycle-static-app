from __future__ import annotations

from business_cycle.audits.shadow_candidate_freeze import (
    summarize_book_faithful_shadow_candidate_freeze,
)


def main() -> None:
    summary = summarize_book_faithful_shadow_candidate_freeze()
    for key in (
        "phase",
        "shadow_candidate_freeze_ready",
        "candidate_model_id",
        "freeze_type",
        "shadow_freeze_hash_valid",
        "shadow_freeze_missing_file_count",
        "shadow_freeze_hash_mismatch_count",
        "production_file_in_shadow_freeze_count",
        "secret_in_shadow_freeze_count",
        "decision_parameter_frozen_count",
        "holdout_registered",
        "production_migration_allowed",
    ):
        if key in summary:
            value = summary[key]
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

