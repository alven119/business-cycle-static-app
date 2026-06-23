"""Phase 21 historical label-comparison contract preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_validation_dry_run_results import (
    summarize_historical_validation_dry_run_results,
)


DEFAULT_LABEL_COMPARISON_CONTRACT_PATH = Path(
    "specs/common/historical_label_comparison_contract.yaml"
)


def load_historical_label_comparison_contract(
    path: str | Path = DEFAULT_LABEL_COMPARISON_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical label comparison contract must map")
    contract = payload.get("historical_label_comparison_contract")
    if not isinstance(contract, dict):
        raise ValueError("historical_label_comparison_contract must be a mapping")
    return contract


def summarize_historical_label_comparison_contract(
    path: str | Path = DEFAULT_LABEL_COMPARISON_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_historical_label_comparison_contract(path)
    dry_run_registry = summarize_historical_validation_dry_run_results()
    output = contract["output_restrictions"]
    gates = contract["readiness_gates"]
    guards = contract["disabled_runtime_guards"]
    required = contract["required_dry_run_result_artifacts"]
    label_policy = contract["label_source_policy"]
    join_policy = contract["label_join_policy"]
    ready = (
        contract["contract_status"]
        == "preregistered_no_label_comparison_execution"
        and dry_run_registry["historical_validation_dry_run_result_registry_ready"]
        is True
        and dry_run_registry["scenario_dry_run_result_count"]
        == required["required_scenario_result_count"]
        and dry_run_registry["prohibited_result_field_count"]
        == required["prohibited_result_field_count_required"]
        and dry_run_registry["label_used_by_runtime_count"] == 0
        and required["label_blind_execution_required"] is True
        and label_policy["label_runtime_usage_prohibited"] is True
        and join_policy["require_one_to_one_join"] is True
        and all(value is True for value in gates.values())
        and all(_disabled_value(value) for value in output.values())
        and all(value is False for value in guards.values())
    )
    return {
        "phase": "21",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_label_comparison_contract_ready": ready,
        "label_runtime_usage_prohibited": label_policy[
            "label_runtime_usage_prohibited"
        ],
        "required_dry_run_result_count": required[
            "required_scenario_result_count"
        ],
        "dry_run_result_registry_ready": dry_run_registry[
            "historical_validation_dry_run_result_registry_ready"
        ],
        "dry_run_result_count": dry_run_registry["scenario_dry_run_result_count"],
        "label_join_policy_ready": gates["label_join_policy_ready"],
        "denominator_policy_ready": gates["denominator_policy_ready"],
        "abstention_handling_policy_ready": gates[
            "abstention_handling_policy_ready"
        ],
        "blocked_result_handling_policy_ready": gates[
            "blocked_result_handling_policy_ready"
        ],
        "missing_result_handling_policy_ready": gates[
            "missing_result_handling_policy_ready"
        ],
        "label_comparison_executed": output["label_comparison_executed"],
        "historical_accuracy_metric_count": output[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": output[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": output["metric_computation_enabled"],
        "backtest_execution_enabled": output["backtest_execution_enabled"],
        "candidate_phase_emitted": output["candidate_phase_emitted"],
        "current_phase_emitted": output["current_phase_emitted"],
        "production_behavior_change_count": output[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": output[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": output[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(
            guards["arbitrary_threshold_added"]
        ),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "contract": contract,
        "dry_run_result_registry": dry_run_registry,
    }


def _disabled_value(value: object) -> bool:
    if type(value) is bool:
        return value is False
    if type(value) is int:
        return value == 0
    return False
