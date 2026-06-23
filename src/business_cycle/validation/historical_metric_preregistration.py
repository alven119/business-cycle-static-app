"""Phase 21 historical metric preregistration, with computation disabled."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_label_comparison_contract import (
    summarize_historical_label_comparison_contract,
)


DEFAULT_METRIC_PREREGISTRATION_CONTRACT_PATH = Path(
    "specs/common/historical_metric_preregistration_contract.yaml"
)
DEFAULT_HISTORICAL_METRIC_REGISTRY_PATH = Path(
    "specs/audits/historical_metric_registry.yaml"
)


def load_historical_metric_preregistration_contract(
    path: str | Path = DEFAULT_METRIC_PREREGISTRATION_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical metric preregistration contract must map")
    contract = payload.get("historical_metric_preregistration_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_metric_preregistration_contract must be a mapping"
        )
    return contract


def load_historical_metric_registry(
    path: str | Path = DEFAULT_HISTORICAL_METRIC_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical metric registry must map")
    registry = payload.get("historical_metric_registry")
    if not isinstance(registry, dict):
        raise ValueError("historical_metric_registry must be a mapping")
    return registry


def summarize_historical_metric_registry(
    path: str | Path = DEFAULT_HISTORICAL_METRIC_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_historical_metric_registry(path)
    metrics = registry["metrics"]
    counters = registry["counters"]
    computation_enabled_metric_count = sum(
        metric["computation_enabled"] is True for metric in metrics
    )
    metric_without_denominator_count = sum(
        not metric.get("denominator_definition") for metric in metrics
    )
    metric_without_abstention_policy_count = sum(
        not metric.get("abstention_treatment") for metric in metrics
    )
    metric_without_blocked_policy_count = sum(
        not metric.get("blocked_treatment") for metric in metrics
    )
    metric_without_missing_policy_count = sum(
        not metric.get("missing_treatment") for metric in metrics
    )
    ready = (
        registry["registry_status"] == "preregistered_no_metric_computation"
        and len(metrics) == counters["preregistered_metric_count"]
        and counters["preregistered_metric_count"] > 0
        and computation_enabled_metric_count
        == counters["computation_enabled_metric_count"]
        == 0
        and metric_without_denominator_count
        == counters["metric_without_denominator_count"]
        == 0
        and metric_without_abstention_policy_count
        == counters["metric_without_abstention_policy_count"]
        == 0
        and metric_without_blocked_policy_count
        == counters["metric_without_blocked_policy_count"]
        == 0
        and metric_without_missing_policy_count
        == counters["metric_without_missing_policy_count"]
        == 0
        and counters["label_comparison_executed"] is False
        and counters["historical_accuracy_metric_count"] == 0
        and counters["economic_performance_metric_count"] == 0
    )
    return {
        "phase": "21",
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "historical_metric_registry_ready": ready,
        "preregistered_metric_count": len(metrics),
        "computation_enabled_metric_count": computation_enabled_metric_count,
        "metric_without_denominator_count": metric_without_denominator_count,
        "metric_without_abstention_policy_count": (
            metric_without_abstention_policy_count
        ),
        "metric_without_blocked_policy_count": metric_without_blocked_policy_count,
        "metric_without_missing_policy_count": metric_without_missing_policy_count,
        "label_comparison_executed": counters["label_comparison_executed"],
        "historical_accuracy_metric_count": counters[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": counters[
            "economic_performance_metric_count"
        ],
        "registry": registry,
    }


def summarize_historical_metric_preregistration(
    path: str | Path = DEFAULT_METRIC_PREREGISTRATION_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_historical_metric_preregistration_contract(path)
    label_contract = summarize_historical_label_comparison_contract()
    registry = summarize_historical_metric_registry()
    policy = contract["metric_preregistration_policy"]
    gates = contract["readiness_gates"]
    guards = contract["disabled_runtime_guards"]
    ready = (
        contract["contract_status"] == "metrics_preregistered_no_computation"
        and label_contract["historical_label_comparison_contract_ready"] is True
        and registry["historical_metric_registry_ready"] is True
        and registry["preregistered_metric_count"]
        >= gates["preregistered_metric_count_minimum"]
        and policy["computation_enabled"] is False
        and policy["metric_values_materialized_this_phase"] is False
        and policy["confusion_matrix_generation_enabled"] is False
        and policy["historical_accuracy_computation_enabled"] is False
        and policy["economic_performance_computation_enabled"] is False
        and policy["backtest_execution_enabled"] is False
        and all(
            value is True
            for key, value in gates.items()
            if key != "preregistered_metric_count_minimum"
        )
        and all(value is False for value in guards.values())
    )
    return {
        "phase": "21",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_metric_preregistration_ready": ready,
        "historical_metric_registry_ready": registry[
            "historical_metric_registry_ready"
        ],
        "preregistered_metric_count": registry["preregistered_metric_count"],
        "label_runtime_usage_prohibited": label_contract[
            "label_runtime_usage_prohibited"
        ],
        "label_comparison_executed": registry["label_comparison_executed"],
        "historical_accuracy_metric_count": registry[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": registry[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": policy["computation_enabled"],
        "backtest_execution_enabled": policy["backtest_execution_enabled"],
        "holdout_registered": guards["holdout_registered"],
        "candidate_selection_enabled": guards["candidate_selection_enabled"],
        "candidate_phase_emitted": guards["candidate_phase_emitted"],
        "current_phase_emitted": guards["current_phase_emitted"],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(
            guards["arbitrary_threshold_added"]
        ),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "contract": contract,
        "label_comparison_contract": label_contract,
        "metric_registry": registry,
    }
