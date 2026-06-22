from __future__ import annotations

from business_cycle.audits.shadow_aggregation_freeze import (
    summarize_shadow_aggregation_freeze,
)


def main() -> None:
    summary = summarize_shadow_aggregation_freeze()
    for key in (
        "phase",
        "shadow_aggregation_freeze_ready",
        "freeze_id",
        "parent_candidate_id",
        "freeze_type",
        "aggregation_freeze_hash_valid",
        "aggregation_freeze_missing_file_count",
        "aggregation_freeze_hash_mismatch_count",
        "secret_in_aggregation_freeze_count",
        "numeric_weight_frozen_count",
        "threshold_frozen_count",
        "holdout_registered",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
