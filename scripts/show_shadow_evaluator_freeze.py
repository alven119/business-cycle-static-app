from __future__ import annotations

from business_cycle.audits.shadow_evaluator_freeze import (
    summarize_shadow_evaluator_freeze,
)


def main() -> None:
    summary = summarize_shadow_evaluator_freeze()
    for key in (
        "phase",
        "evaluator_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_type",
        "freeze_hash_valid",
        "parent_freeze_present",
        "prior_freeze_preserved",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "non_book_threshold_added_count",
        "holdout_registered",
        "prospective_protocol_registered",
        "prospective_protocol_started",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
