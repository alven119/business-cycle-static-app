#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.validation.validation_blockage_remediation import (
    build_validation_blockage_remediation,
    write_validation_blockage_remediation,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    remediation_run = build_validation_blockage_remediation()
    write_result = write_validation_blockage_remediation(
        remediation_run,
        output=args.output,
    )
    for key in (
        "phase",
        "validation_blockage_remediation_contract_ready",
        "validation_blockage_remediation_runtime_ready",
        "scenario_count",
        "pre_remediation_blocked_scenario_count",
        "post_remediation_blocked_scenario_count",
        "reviewed_blocker_count",
        "safe_remediation_candidate_count",
        "safe_remediation_executed_count",
        "genuine_blocker_count",
        "unresolved_blocker_count",
        "false_resolution_count",
        "remediation_action_executed",
        "rule_modified_count",
        "evidence_rule_modified_count",
        "mapping_rule_modified_count",
        "threshold_modified_count",
        "numeric_weight_added_count",
        "arbitrary_threshold_added_count",
        "role_count_voting_added_count",
        "historical_tuning_leakage_count",
        "historical_accuracy_metric_count",
        "new_accuracy_metric_computed_count",
        "economic_performance_metric_count",
        "metric_computation_scope",
        "backtest_execution_enabled",
        "label_used_by_runtime_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "prohibited_artifact_field_count",
        "production_behavior_change_count",
        "prospective_registry_record_count",
        "real_registry_write_attempt_count",
        "forbidden_repo_output_count",
    ):
        value = remediation_run[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={write_result['output']}")
    print(
        "validation_blockage_remediation_artifact_written="
        f"{str(write_result['validation_blockage_remediation_artifact_written']).lower()}"
    )


if __name__ == "__main__":
    main()
