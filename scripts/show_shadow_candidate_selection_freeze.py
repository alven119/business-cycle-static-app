from __future__ import annotations

from business_cycle.audits.shadow_candidate_selection_freeze import (
    summarize_shadow_candidate_selection_freeze,
)


def main() -> None:
    summary = summarize_shadow_candidate_selection_freeze()
    for key in (
        "phase",
        "candidate_selection_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_hash_valid",
        "freeze_missing_file_count",
        "freeze_hash_mismatch_count",
        "parent_freeze_missing_count",
        "secret_in_freeze_count",
        "production_file_in_freeze_count",
        "numeric_weight_frozen_count",
        "production_threshold_change_count",
        "holdout_registered",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
