from __future__ import annotations

from business_cycle.audits.prospective_monitoring_freeze import (
    summarize_prospective_monitoring_freeze,
)


def main() -> None:
    summary = summarize_prospective_monitoring_freeze()
    for key in (
        "phase",
        "monitoring_infrastructure_freeze_ready",
        "freeze_id",
        "parent_model_freeze_id",
        "parent_protocol_id",
        "monitoring_freeze_hash_valid",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "automatic_scheduler_allowed",
        "protocol_started",
        "holdout_registered",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
