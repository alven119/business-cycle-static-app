from __future__ import annotations

from business_cycle.audits.prospective_manual_start_freeze import (
    summarize_prospective_manual_start_freeze,
)


def main() -> None:
    summary = summarize_prospective_manual_start_freeze()
    for key in (
        "phase",
        "manual_start_freeze_ready",
        "freeze_id",
        "parent_model_freeze_id",
        "parent_monitoring_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "freeze_hash_valid",
        "parent_model_freeze_present",
        "parent_monitoring_freeze_present",
        "prior_freezes_preserved",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "holdout_registered",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

