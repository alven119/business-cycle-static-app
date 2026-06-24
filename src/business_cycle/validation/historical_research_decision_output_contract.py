"""Phase 24 research-only historical decision output contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_HISTORICAL_RESEARCH_DECISION_OUTPUT_CONTRACT_PATH = Path(
    "specs/common/historical_research_decision_output_contract.yaml"
)
REQUIRED_CONTRACT_KEYS = (
    "contract_id",
    "contract_version",
    "allowed_inputs",
    "prohibited_inputs",
    "required_prior_freezes",
    "required_runtime_artifacts",
    "output_taxonomy",
    "abstention_output_policy",
    "blocked_output_policy",
    "label_usage_policy",
    "candidate_phase_prohibition",
    "current_phase_prohibition",
    "production_phase_prohibition",
    "metric_computation_policy",
    "no_tuning_after_output_policy",
    "output_restrictions",
    "readiness_gates",
    "disabled_runtime_guards",
)


def load_historical_research_decision_output_contract(
    path: str | Path = DEFAULT_HISTORICAL_RESEARCH_DECISION_OUTPUT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical research decision output contract must map")
    contract = payload.get("historical_research_decision_output_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_research_decision_output_contract must be a mapping"
        )
    return contract


def summarize_historical_research_decision_output_contract() -> dict[str, Any]:
    contract = load_historical_research_decision_output_contract()
    validation = validate_historical_research_decision_output_contract(contract)
    restrictions = contract["output_restrictions"]
    disabled = contract["disabled_runtime_guards"]
    ready = (
        validation["contract_schema_valid"] is True
        and validation["output_taxonomy_ready"] is True
        and restrictions["predicted_label_output_count"] == 0
        and restrictions["research_decision_output_emitted"] is False
        and restrictions["label_used_by_runtime_count"] == 0
        and restrictions["historical_accuracy_metric_count"] == 0
        and restrictions["economic_performance_metric_count"] == 0
        and restrictions["accuracy_metric_enabled"] is False
        and restrictions["economic_performance_metric_enabled"] is False
        and restrictions["backtest_execution_enabled"] is False
        and restrictions["candidate_phase_emitted"] is False
        and restrictions["current_phase_emitted"] is False
        and all(value is False for value in disabled.values())
    )
    return {
        "phase": "24",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "research_decision_output_contract_ready": ready,
        "output_taxonomy_ready": validation["output_taxonomy_ready"],
        "future_allowed_field_count": len(contract["future_allowed_fields"]),
        "forbidden_output_field_count": validation["forbidden_output_field_count"],
        "predicted_label_output_count": restrictions[
            "predicted_label_output_count"
        ],
        "research_decision_output_emitted": restrictions[
            "research_decision_output_emitted"
        ],
        "label_used_by_runtime_count": restrictions["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": restrictions[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": restrictions[
            "economic_performance_metric_count"
        ],
        "accuracy_metric_enabled": restrictions["accuracy_metric_enabled"],
        "economic_performance_metric_enabled": restrictions[
            "economic_performance_metric_enabled"
        ],
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
            "research_decision_output_contract_preregistered_no_emission"
        ),
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "contract_validation": validation,
        "contract": contract,
    }


def validate_historical_research_decision_output_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    missing_contract_keys = [
        key for key in REQUIRED_CONTRACT_KEYS if key not in contract
    ]
    forbidden_output_fields = set(contract.get("forbidden_output_fields", ()))
    future_allowed_fields = set(contract.get("future_allowed_fields", ()))
    taxonomy = contract.get("output_taxonomy", {})
    taxonomy_ready = (
        isinstance(taxonomy, dict)
        and taxonomy.get("research_only_historical_validation_output", {}).get(
            "status"
        )
        == "preregistered_not_emitted"
        and taxonomy.get("offline_validation_label", {}).get("status")
        == "label_source_only_not_runtime_input"
        and taxonomy.get("candidate_phase", {}).get("status") == "prohibited"
        and taxonomy.get("current_phase", {}).get("status") == "prohibited"
        and taxonomy.get("production_phase", {}).get("status") == "prohibited"
    )
    future_forbidden_fields = sorted(
        future_allowed_fields.intersection(forbidden_output_fields)
    )
    required_values = contract.get("required_future_field_values", {})
    restrictions = contract.get("output_restrictions", {})
    disabled = contract.get("disabled_runtime_guards", {})
    label_policy = contract.get("label_usage_policy", {})
    metric_policy = contract.get("metric_computation_policy", {})
    no_tuning = contract.get("no_tuning_after_output_policy", {})
    schema_valid = (
        not missing_contract_keys
        and taxonomy_ready
        and not future_forbidden_fields
        and required_values.get("output_mode")
        == "research_historical_validation_only"
        and required_values.get("label_used_by_runtime") is False
        and restrictions.get("research_decision_output_emitted") is False
        and restrictions.get("predicted_label_output_count") == 0
        and restrictions.get("historical_accuracy_metric_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("accuracy_metric_enabled") is False
        and restrictions.get("economic_performance_metric_enabled") is False
        and label_policy.get("labels_may_be_used_by_runtime") is False
        and label_policy.get("labels_may_be_used_for_rule_tuning") is False
        and metric_policy.get("historical_accuracy_metric_enabled") is False
        and metric_policy.get("economic_performance_metric_enabled") is False
        and no_tuning.get("threshold_tuning_allowed") is False
        and no_tuning.get("weight_tuning_allowed") is False
        and all(value is False for value in disabled.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing_contract_keys),
        "missing_contract_keys": missing_contract_keys,
        "output_taxonomy_ready": taxonomy_ready,
        "future_forbidden_field_count": len(future_forbidden_fields),
        "future_forbidden_fields": future_forbidden_fields,
        "forbidden_output_field_count": 0 if not future_forbidden_fields else len(
            future_forbidden_fields
        ),
    }
