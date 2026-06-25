from __future__ import annotations

from business_cycle.audits.shadow_historical_comparability_realization_freeze import (
    summarize_shadow_historical_comparability_realization_freeze,
)


def main() -> None:
    summary = summarize_shadow_historical_comparability_realization_freeze()
    for key in (
        "phase",
        "historical_comparability_realization_freeze_ready",
        "freeze_id",
        "parent_freeze_id",
        "freeze_manifest_hash",
        "alpha31_freeze_hash_valid",
        "alpha30_parent_preserved",
        "qa12_freeze_unchanged",
        "missing_file_count",
        "hash_mismatch_count",
        "secret_count",
        "production_file_count",
        "post_comparable_scenario_count",
        "false_comparability_count",
        "historical_accuracy_metric_count",
        "economic_performance_metric_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "prospective_registry_write_attempt_count",
        "economic_validation_status",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
