from __future__ import annotations

from business_cycle.audits.formal_scope_freeze import (
    summarize_book_faithful_formal_scope_freeze,
)


def main() -> None:
    summary = summarize_book_faithful_formal_scope_freeze()
    for key in (
        "phase",
        "formal_scope_freeze_ready",
        "scope_freeze_hash_valid",
        "scope_freeze_missing_file_count",
        "scope_freeze_hash_mismatch_count",
        "scope_freeze_secret_count",
        "decision_parameter_frozen_by_scope_phase_count",
        "implementation_status",
        "economic_validation_status",
        "production_migration_status",
        "holdout_status",
    ):
        if key in summary:
            value = summary[key]
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

