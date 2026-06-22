"""Show QA11 shadow observation freeze."""

from __future__ import annotations

from business_cycle.audits.shadow_observation_freeze import (
    summarize_shadow_observation_freeze,
)


def main() -> None:
    summary = summarize_shadow_observation_freeze()
    for key in (
        "phase",
        "observation_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_manifest_hash",
        "component_file_count",
        "source_file_count",
        "freeze_hash_valid",
        "parent_freeze_present",
        "prior_freeze_preserved",
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
