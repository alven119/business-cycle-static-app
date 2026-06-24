"""Phase 26 offline predicted-label mapping contract preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH = Path(
    "specs/common/offline_predicted_label_mapping_contract.yaml"
)
REQUIRED_CONTRACT_KEYS = (
    "contract_id",
    "contract_version",
    "required_prior_freezes",
    "allowed_inputs",
    "prohibited_inputs",
    "research_decision_state_taxonomy",
    "offline_predicted_label_taxonomy",
    "mapping_rules",
    "abstention_mapping_policy",
    "blocked_mapping_policy",
    "missing_output_mapping_policy",
    "label_usage_policy",
    "candidate_phase_prohibition",
    "current_phase_prohibition",
    "production_phase_prohibition",
    "no_metric_computation_policy",
    "no_tuning_after_mapping_policy",
    "output_restrictions",
    "readiness_gates",
    "disabled_runtime_guards",
)


def load_offline_predicted_label_mapping_contract(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("offline predicted label mapping contract must map")
    contract = payload.get("offline_predicted_label_mapping_contract")
    if not isinstance(contract, dict):
        raise ValueError("offline_predicted_label_mapping_contract must be a mapping")
    return contract


def summarize_offline_predicted_label_mapping_contract() -> dict[str, Any]:
    contract = load_offline_predicted_label_mapping_contract()
    validation = validate_offline_predicted_label_mapping_contract(contract)
    restrictions = contract["output_restrictions"]
    disabled = contract["disabled_runtime_guards"]
    ready = (
        validation["contract_schema_valid"] is True
        and validation["research_decision_state_taxonomy_ready"] is True
        and validation["offline_predicted_label_taxonomy_ready"] is True
        and validation["mapping_rule_count"] > 0
        and restrictions["predicted_label_output_count"] == 0
        and restrictions["predicted_label_artifact_count"] == 0
        and restrictions["label_comparison_executed"] is False
        and restrictions["label_used_by_runtime_count"] == 0
        and restrictions["historical_accuracy_metric_count"] == 0
        and restrictions["economic_performance_metric_count"] == 0
        and restrictions["metric_computation_enabled"] is False
        and restrictions["backtest_execution_enabled"] is False
        and restrictions["candidate_phase_emitted"] is False
        and restrictions["current_phase_emitted"] is False
        and all(value is False for value in disabled.values())
    )
    return {
        "phase": "26",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "predicted_label_mapping_contract_ready": ready,
        "research_decision_state_taxonomy_ready": validation[
            "research_decision_state_taxonomy_ready"
        ],
        "offline_predicted_label_taxonomy_ready": validation[
            "offline_predicted_label_taxonomy_ready"
        ],
        "mapping_rule_count": validation["mapping_rule_count"],
        "predicted_label_output_count": restrictions[
            "predicted_label_output_count"
        ],
        "predicted_label_artifact_count": restrictions[
            "predicted_label_artifact_count"
        ],
        "label_comparison_executed": restrictions["label_comparison_executed"],
        "label_used_by_runtime_count": restrictions["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": restrictions[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": restrictions[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": restrictions["metric_computation_enabled"],
        "backtest_execution_enabled": restrictions["backtest_execution_enabled"],
        "candidate_phase_emitted": restrictions["candidate_phase_emitted"],
        "current_phase_emitted": restrictions["current_phase_emitted"],
        "production_behavior_change_count": restrictions[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": restrictions[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": restrictions[
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(disabled["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(disabled["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(disabled["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(disabled["historical_tuning_used"]),
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "economic_validation_status": (
            "predicted_label_mapping_preregistered_no_emission"
        ),
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "contract_validation": validation,
        "contract": contract,
    }


def validate_offline_predicted_label_mapping_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    missing_contract_keys = [
        key for key in REQUIRED_CONTRACT_KEYS if key not in contract
    ]
    research_taxonomy = contract.get("research_decision_state_taxonomy", {})
    offline_taxonomy = contract.get("offline_predicted_label_taxonomy", {})
    mapping_rules = contract.get("mapping_rules", [])
    restrictions = contract.get("output_restrictions", {})
    disabled = contract.get("disabled_runtime_guards", {})
    label_policy = contract.get("label_usage_policy", {})
    metric_policy = contract.get("no_metric_computation_policy", {})
    tuning_policy = contract.get("no_tuning_after_mapping_policy", {})
    candidate_prohibition = contract.get("candidate_phase_prohibition", {})
    current_prohibition = contract.get("current_phase_prohibition", {})
    production_prohibition = contract.get("production_phase_prohibition", {})
    research_ready = (
        isinstance(research_taxonomy, dict)
        and {"mapping_ready", "abstained", "blocked", "not_comparable"}.issubset(
            research_taxonomy
        )
    )
    offline_ready = (
        isinstance(offline_taxonomy, dict)
        and {"recession", "recovery", "growth", "boom", "abstained", "blocked"}.issubset(
            offline_taxonomy
        )
        and "not_comparable" in offline_taxonomy
    )
    mapping_rule_count = len(mapping_rules) if isinstance(mapping_rules, list) else 0
    mapping_rules_non_emitting = (
        mapping_rule_count > 0
        and all(rule.get("emission_allowed_this_phase") is False for rule in mapping_rules)
    )
    schema_valid = (
        not missing_contract_keys
        and contract.get("contract_status")
        == "preregistered_no_predicted_label_emission"
        and research_ready
        and offline_ready
        and mapping_rules_non_emitting
        and restrictions.get("predicted_label_output_count") == 0
        and restrictions.get("predicted_label_artifact_count") == 0
        and restrictions.get("label_comparison_executed") is False
        and restrictions.get("historical_accuracy_metric_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("metric_computation_enabled") is False
        and label_policy.get("labels_may_be_used_by_runtime") is False
        and label_policy.get("labels_may_be_used_for_rule_tuning") is False
        and label_policy.get("labels_may_be_materialized_this_phase") is False
        and metric_policy.get("historical_accuracy_metric_enabled") is False
        and metric_policy.get("economic_performance_metric_enabled") is False
        and metric_policy.get("portfolio_metric_enabled") is False
        and tuning_policy.get("threshold_tuning_allowed") is False
        and tuning_policy.get("weight_tuning_allowed") is False
        and tuning_policy.get("role_count_voting_allowed") is False
        and candidate_prohibition.get("candidate_phase_output_allowed") is False
        and current_prohibition.get("current_phase_output_allowed") is False
        and production_prohibition.get("production_phase_output_allowed") is False
        and all(value is False for value in disabled.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing_contract_keys),
        "missing_contract_keys": missing_contract_keys,
        "research_decision_state_taxonomy_ready": research_ready,
        "offline_predicted_label_taxonomy_ready": offline_ready,
        "mapping_rule_count": mapping_rule_count,
        "mapping_rules_non_emitting": mapping_rules_non_emitting,
    }
