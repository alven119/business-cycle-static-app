"""Phase 32 genuine validation blocker work package registry."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.genuine_blocker_resolution_protocol import (
    load_genuine_blocker_resolution_protocol,
    summarize_genuine_blocker_resolution_protocol,
)
from business_cycle.validation.validation_blockage_remediation import (
    summarize_validation_blockage_remediation,
)


DEFAULT_WORK_PACKAGE_REGISTRY_PATH = Path(
    "specs/audits/genuine_validation_blocker_work_packages.yaml"
)


@lru_cache(maxsize=1)
def load_genuine_validation_blocker_work_package_spec(
    path: str | Path = DEFAULT_WORK_PACKAGE_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("genuine validation blocker work package spec must map")
    spec = payload.get("genuine_validation_blocker_work_packages")
    if not isinstance(spec, dict):
        raise ValueError(
            "genuine_validation_blocker_work_packages must be a mapping"
        )
    return spec


@lru_cache(maxsize=1)
def build_genuine_validation_blocker_work_packages() -> dict[str, Any]:
    spec = load_genuine_validation_blocker_work_package_spec()
    protocol = load_genuine_blocker_resolution_protocol()
    phase31 = summarize_validation_blockage_remediation()
    profiles = phase31["validation_blockage_remediation_artifact"][
        "scenario_remediation_profiles"
    ]
    genuine_profiles = [
        profile
        for profile in profiles
        if profile["blocker_type"] == "genuine_model_gate_or_evidence_limitation"
    ]
    work_packages = [
        _build_work_package(profile, protocol=protocol, sequence=index + 1)
        for index, profile in enumerate(genuine_profiles)
    ]
    source_blocker_ids = {
        _source_blocker_id(profile["scenario_id"]) for profile in genuine_profiles
    }
    package_source_ids = {
        package["source_blocker_id"] for package in work_packages
    }
    validation = validate_genuine_validation_blocker_work_packages(
        work_packages,
        source_blocker_ids=source_blocker_ids,
        protocol=protocol,
    )
    blocker_type_counts = Counter(package["blocker_type"] for package in work_packages)
    root_cause_counts = Counter(
        package["root_cause_category"] for package in work_packages
    )
    return {
        "phase": "32",
        "registry_id": spec["registry_id"],
        "registry_version": spec["registry_version"],
        "genuine_blocker_resolution_protocol_ready": (
            summarize_genuine_blocker_resolution_protocol()[
                "genuine_blocker_resolution_protocol_ready"
            ]
        ),
        "genuine_blocker_work_package_registry_ready": validation[
            "work_package_registry_valid"
        ],
        "reviewed_genuine_blocker_count": len(genuine_profiles),
        "work_package_count": len(work_packages),
        "blocker_without_work_package_count": len(
            source_blocker_ids.difference(package_source_ids)
        ),
        "work_package_without_source_blocker_count": validation[
            "work_package_without_source_blocker_count"
        ],
        "work_package_without_allowed_action_count": validation[
            "work_package_without_allowed_action_count"
        ],
        "work_package_without_prohibited_action_count": validation[
            "work_package_without_prohibited_action_count"
        ],
        "work_package_without_completion_gate_count": validation[
            "work_package_without_completion_gate_count"
        ],
        "false_resolution_count": 0,
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
        "historical_accuracy_metric_count": phase31[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": "existing_historical_accuracy_registry_only",
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "blocker_type_counts": dict(sorted(blocker_type_counts.items())),
        "root_cause_category_counts": dict(sorted(root_cause_counts.items())),
        "source_blocker_ids": sorted(source_blocker_ids),
        "work_packages": work_packages,
        "validation": validation,
        "source_phase31_remediation": phase31,
        "spec": spec,
        "protocol": protocol,
    }


@lru_cache(maxsize=1)
def summarize_genuine_validation_blocker_work_packages() -> dict[str, Any]:
    registry = build_genuine_validation_blocker_work_packages()
    return {
        key: registry[key]
        for key in (
            "phase",
            "registry_id",
            "registry_version",
            "genuine_blocker_resolution_protocol_ready",
            "genuine_blocker_work_package_registry_ready",
            "reviewed_genuine_blocker_count",
            "work_package_count",
            "blocker_without_work_package_count",
            "work_package_without_source_blocker_count",
            "work_package_without_allowed_action_count",
            "work_package_without_prohibited_action_count",
            "work_package_without_completion_gate_count",
            "false_resolution_count",
            "blocker_resolution_executed",
            "scenario_promoted_to_comparable_count",
            "evidence_rule_modified_count",
            "predicted_mapping_rule_modified_count",
            "formal_decision_contract_modified_count",
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
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "blocker_type_counts",
            "root_cause_category_counts",
            "work_packages",
        )
    }


def validate_genuine_validation_blocker_work_packages(
    work_packages: list[dict[str, Any]],
    *,
    source_blocker_ids: set[str],
    protocol: dict[str, Any] | None = None,
) -> dict[str, Any]:
    protocol = protocol or load_genuine_blocker_resolution_protocol()
    required_fields = set(protocol["required_work_package_fields"])
    allowed_actions = set(protocol["allowed_resolution_actions"])
    prohibited_actions = set(protocol["prohibited_resolution_actions"])
    supported_types = set(protocol["blocker_types"])
    without_source = [
        package["work_package_id"]
        for package in work_packages
        if package.get("source_blocker_id") not in source_blocker_ids
    ]
    missing_fields = [
        package.get("work_package_id", "<unknown>")
        for package in work_packages
        if required_fields.difference(package)
    ]
    without_allowed = [
        package["work_package_id"]
        for package in work_packages
        if not set(package.get("allowed_resolution_actions", [])).intersection(
            allowed_actions
        )
    ]
    without_prohibited = [
        package["work_package_id"]
        for package in work_packages
        if not prohibited_actions.issubset(
            set(package.get("prohibited_resolution_actions", []))
        )
    ]
    without_gate = [
        package["work_package_id"]
        for package in work_packages
        if not package.get("completion_gate")
    ]
    unsupported_type = [
        package["work_package_id"]
        for package in work_packages
        if package.get("blocker_type") not in supported_types
    ]
    unsafe = [
        package["work_package_id"]
        for package in work_packages
        if package.get("requires_preregistration") is not True
        or package.get("can_be_resolved_without_threshold") is not True
        or package.get("current_status") != "preregistered_unresolved"
    ]
    valid = (
        not missing_fields
        and not without_source
        and not without_allowed
        and not without_prohibited
        and not without_gate
        and not unsupported_type
        and not unsafe
        and len(work_packages) >= 5
    )
    return {
        "work_package_registry_valid": valid,
        "work_package_missing_required_field_count": len(missing_fields),
        "work_package_without_source_blocker_count": len(without_source),
        "work_package_without_allowed_action_count": len(without_allowed),
        "work_package_without_prohibited_action_count": len(without_prohibited),
        "work_package_without_completion_gate_count": len(without_gate),
        "unsupported_blocker_type_count": len(unsupported_type),
        "unsafe_work_package_count": len(unsafe),
    }


def _build_work_package(
    profile: dict[str, Any],
    *,
    protocol: dict[str, Any],
    sequence: int,
) -> dict[str, Any]:
    reasons = list(profile["original_blocked_reason_codes"])
    scenario_id = profile["scenario_id"]
    return {
        "work_package_id": f"phase32_wp_{sequence:02d}_{scenario_id}",
        "source_blocker_id": _source_blocker_id(scenario_id),
        "affected_scenario_ids": [scenario_id],
        "affected_artifact_layers": _affected_artifact_layers(reasons),
        "blocker_type": _primary_blocker_type(reasons),
        "root_cause_category": _root_cause_category(reasons),
        "required_new_contracts": _required_new_contracts(reasons),
        "required_new_inputs": _required_new_inputs(reasons),
        "required_new_tests": _required_new_tests(reasons),
        "allowed_resolution_actions": _allowed_resolution_actions(
            reasons,
            protocol=protocol,
        ),
        "prohibited_resolution_actions": list(
            protocol["prohibited_resolution_actions"]
        ),
        "historical_tuning_leakage_risk": "high",
        "requires_preregistration": True,
        "can_be_resolved_without_rule_change": _can_resolve_without_rule_change(
            reasons
        ),
        "can_be_resolved_without_new_data": _can_resolve_without_new_data(reasons),
        "can_be_resolved_without_threshold": True,
        "expected_next_phase": 33,
        "completion_gate": (
            "preregister_new_contracts_and_tests_then_preserve_label_blind_"
            "runtime_no_threshold_or_performance"
        ),
        "current_status": "preregistered_unresolved",
    }


def _source_blocker_id(scenario_id: str) -> str:
    return f"phase31_genuine_blocker:{scenario_id}"


def _affected_artifact_layers(reasons: list[str]) -> list[str]:
    layers = {"phase31_validation_blockage_remediation"}
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        layers.add("major_group_phase_evidence_profile")
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        layers.add("book_phase_evidence_rule_registry")
    if any("candidate_output_disabled" in reason for reason in reasons):
        layers.add("candidate_precondition_profile")
    if "label_blind_runtime" in reasons:
        layers.add("historical_validation_label_boundary")
    if "backtest_execution_disabled" in reasons:
        layers.add("backtest_execution_gate")
    if "metric_computation_disabled" in reasons:
        layers.add("historical_metric_scope_gate")
    return sorted(layers)


def _primary_blocker_type(reasons: list[str]) -> str:
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        return "insufficient_phase_evidence"
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        return "unresolved_book_rule_semantics"
    if "label_blind_runtime" in reasons:
        return "taxonomy_or_label_scope_mismatch"
    if "candidate_output_disabled" in reasons:
        return "abstention_required_by_contract"
    return "unsupported_comparison_scope"


def _root_cause_category(reasons: list[str]) -> str:
    has_incomplete = any(
        reason.startswith("incomplete_required_major_group") for reason in reasons
    )
    has_raw = any(reason.startswith("raw_observation_only") for reason in reasons)
    has_candidate = any("candidate_output_disabled" in reason for reason in reasons)
    if has_incomplete and has_raw and has_candidate:
        return "candidate_gate_incomplete_major_groups_and_raw_observation_only"
    if has_incomplete:
        return "incomplete_major_group_phase_evidence"
    if has_raw:
        return "raw_observation_without_operational_rule"
    return "validation_scope_guard"


def _required_new_contracts(reasons: list[str]) -> list[str]:
    contracts = {"genuine_blocker_resolution_contract"}
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        contracts.add("major_group_phase_evidence_completion_contract")
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        contracts.add("book_rule_semantics_preregistration_contract")
    if any("candidate_output_disabled" in reason for reason in reasons):
        contracts.add("candidate_capability_gate_contract")
    if "label_blind_runtime" in reasons:
        contracts.add("offline_validation_label_boundary_contract")
    return sorted(contracts)


def _required_new_inputs(reasons: list[str]) -> list[str]:
    inputs = {"documented_blocker_resolution_evidence"}
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        inputs.add("major_group_core_role_evidence_inputs")
        inputs.add("point_in_time_input_manifest")
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        inputs.add("book_rule_semantics_review")
        inputs.add("phase_evidence_fixture_inputs")
    return sorted(inputs)


def _required_new_tests(reasons: list[str]) -> list[str]:
    tests = {
        "blocker_resolution_contract_test",
        "no_historical_tuning_regression_test",
    }
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        tests.add("major_group_completion_regression_test")
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        tests.add("book_rule_semantics_metamorphic_test")
    if "label_blind_runtime" in reasons:
        tests.add("label_runtime_boundary_test")
    return sorted(tests)


def _allowed_resolution_actions(
    reasons: list[str],
    *,
    protocol: dict[str, Any],
) -> list[str]:
    actions = {"preserve_blocker_with_documented_reason"}
    if any(reason.startswith("incomplete_required_major_group") for reason in reasons):
        actions.add("add_point_in_time_input_manifest")
        actions.add("add_validation_fixture")
    if any(reason.startswith("raw_observation_only") for reason in reasons):
        actions.add("add_book_rule_preregistration")
        actions.add("add_transformation_contract")
    allowed = set(protocol["allowed_resolution_actions"])
    return sorted(actions.intersection(allowed))


def _can_resolve_without_rule_change(reasons: list[str]) -> bool:
    return not any(
        reason.startswith(("raw_observation_only", "incomplete_required_major_group"))
        for reason in reasons
    )


def _can_resolve_without_new_data(reasons: list[str]) -> bool:
    return not any(
        reason.startswith("incomplete_required_major_group") for reason in reasons
    )
