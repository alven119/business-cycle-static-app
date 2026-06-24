"""Phase 32 genuine validation blocker resolution protocol."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


DEFAULT_PROTOCOL_PATH = Path(
    "specs/common/genuine_validation_blocker_resolution_protocol.yaml"
)


@lru_cache(maxsize=1)
def load_genuine_blocker_resolution_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("genuine blocker resolution protocol must map")
    protocol = payload.get("genuine_validation_blocker_resolution_protocol")
    if not isinstance(protocol, dict):
        raise ValueError(
            "genuine_validation_blocker_resolution_protocol must be a mapping"
        )
    return protocol


@lru_cache(maxsize=1)
def summarize_genuine_blocker_resolution_protocol() -> dict[str, Any]:
    protocol = load_genuine_blocker_resolution_protocol()
    validation = validate_genuine_blocker_resolution_protocol(protocol)
    return {
        "phase": "32",
        "protocol_id": protocol["protocol_id"],
        "protocol_version": protocol["protocol_version"],
        "genuine_blocker_resolution_protocol_ready": validation[
            "protocol_schema_valid"
        ],
        "blocker_type_count": len(protocol["blocker_types"]),
        "allowed_resolution_action_count": len(
            protocol["allowed_resolution_actions"]
        ),
        "prohibited_resolution_action_count": len(
            protocol["prohibited_resolution_actions"]
        ),
        "required_work_package_field_count": len(
            protocol["required_work_package_fields"]
        ),
        "blocker_resolution_executed": False,
        "scenario_promoted_to_comparable_count": 0,
        "evidence_rule_modified_count": 0,
        "predicted_mapping_rule_modified_count": 0,
        "formal_decision_contract_modified_count": 0,
        "threshold_modified_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "validation": validation,
        "protocol": protocol,
    }


def validate_genuine_blocker_resolution_protocol(
    protocol: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "protocol_id",
        "protocol_version",
        "protocol_status",
        "parent_freeze_id",
        "source_phase31_remediation_contract_id",
        "allowed_inputs",
        "prohibited_inputs",
        "blocker_types",
        "allowed_resolution_actions",
        "prohibited_resolution_actions",
        "resolution_policy",
        "required_work_package_fields",
        "output_restrictions",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in protocol]
    policy = protocol.get("resolution_policy", {})
    restrictions = protocol.get("output_restrictions", {})
    guards = protocol.get("disabled_runtime_guards", {})
    schema_valid = (
        not missing
        and protocol.get("protocol_status")
        == "preregistered_planning_only_no_resolution_execution"
        and policy.get("planning_only") is True
        and policy.get("blocker_resolution_execution_allowed") is False
        and policy.get("scenario_promotion_allowed") is False
        and policy.get("evidence_rule_modification_allowed") is False
        and policy.get("predicted_mapping_modification_allowed") is False
        and policy.get("formal_decision_contract_modification_allowed") is False
        and policy.get("historical_tuning_allowed") is False
        and restrictions.get("false_resolution_count") == 0
        and restrictions.get("blocker_resolution_executed") is False
        and restrictions.get("scenario_promoted_to_comparable_count") == 0
        and restrictions.get("new_accuracy_metric_computed_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("backtest_execution_enabled") is False
        and all(value is False for value in guards.values())
        and _has_required_resolution_actions(protocol)
        and _has_required_prohibited_actions(protocol)
    )
    return {
        "protocol_schema_valid": schema_valid,
        "missing_protocol_key_count": len(missing),
        "missing_protocol_keys": missing,
    }


def _has_required_resolution_actions(protocol: dict[str, Any]) -> bool:
    required = {
        "add_source_availability_contract",
        "add_transformation_contract",
        "add_validation_fixture",
        "add_observation_only_artifact",
        "add_book_rule_preregistration",
        "add_point_in_time_input_manifest",
        "preserve_blocker_with_documented_reason",
    }
    return required.issubset(set(protocol.get("allowed_resolution_actions", [])))


def _has_required_prohibited_actions(protocol: dict[str, Any]) -> bool:
    required = {
        "tune_rule_from_historical_result",
        "add_arbitrary_threshold",
        "add_numeric_weight",
        "add_role_count_voting",
        "use_label_in_runtime",
        "use_scenario_id_special_case",
        "promote_abstention_to_phase_label",
        "promote_blocked_to_comparable",
        "use_modern_proxy_as_book_core",
        "modify_production_behavior",
    }
    return required.issubset(set(protocol.get("prohibited_resolution_actions", [])))
