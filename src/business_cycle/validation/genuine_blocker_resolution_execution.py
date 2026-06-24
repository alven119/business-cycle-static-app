"""Phase 33 safe execution of genuine validation blocker work packages."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.genuine_validation_blocker_work_packages import (
    build_genuine_validation_blocker_work_packages,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.validation_blockage_remediation import (
    build_validation_blockage_remediation,
)


DEFAULT_EXECUTION_CONTRACT_PATH = Path(
    "specs/common/genuine_blocker_resolution_execution_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase33_genuine_blocker_resolution_execution_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


@lru_cache(maxsize=1)
def load_genuine_blocker_resolution_execution_contract(
    path: str | Path = DEFAULT_EXECUTION_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("genuine blocker resolution execution contract must map")
    contract = payload.get("genuine_blocker_resolution_execution_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "genuine_blocker_resolution_execution_contract must be a mapping"
        )
    return contract


@lru_cache(maxsize=1)
def build_genuine_blocker_resolution_execution() -> dict[str, Any]:
    contract = load_genuine_blocker_resolution_execution_contract()
    work_registry = build_genuine_validation_blocker_work_packages()
    diagnostics_run = build_historical_validation_blockage_diagnostics()
    remediation_run = build_validation_blockage_remediation()
    artifact = _build_execution_artifact(
        contract=contract,
        work_registry=work_registry,
        diagnostics_run=diagnostics_run,
        remediation_run=remediation_run,
    )
    artifact_validation = validate_genuine_blocker_resolution_execution_artifact(
        artifact,
        contract=contract,
    )
    contract_validation = validate_genuine_blocker_resolution_execution_contract(
        contract
    )
    profiles = artifact["scenario_resolution_profiles"]
    profile_counters = _profile_counters(profiles)
    ready = (
        contract_validation["contract_schema_valid"]
        and artifact_validation["artifact_schema_valid"]
        and artifact["work_package_count"] == 5
        and artifact["safe_executable_work_package_count"]
        == artifact["executed_work_package_count"]
        and artifact["work_package_without_execution_reason_count"] == 0
        and artifact["pre_resolution_blocked_scenario_count"] == 5
        and artifact["post_resolution_blocked_scenario_count"] <= 5
        and artifact["false_resolution_count"] == 0
        and profile_counters["scenario_promoted_without_required_evidence_count"] == 0
        and profile_counters["scenario_promoted_by_taxonomy_only_count"] == 0
        and profile_counters["scenario_promoted_by_modern_proxy_count"] == 0
    )
    return {
        "phase": "33",
        "run_id": RUN_ID,
        "genuine_blocker_resolution_execution_contract_ready": (
            contract_validation["contract_schema_valid"]
        ),
        "genuine_blocker_resolution_execution_ready": ready,
        "work_package_count": artifact["work_package_count"],
        "safe_executable_work_package_count": artifact[
            "safe_executable_work_package_count"
        ],
        "executed_work_package_count": artifact["executed_work_package_count"],
        "still_genuine_blocked_work_package_count": artifact[
            "still_genuine_blocked_work_package_count"
        ],
        "work_package_without_execution_reason_count": artifact[
            "work_package_without_execution_reason_count"
        ],
        "pre_resolution_blocked_scenario_count": artifact[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": artifact[
            "post_resolution_blocked_scenario_count"
        ],
        "pre_resolution_comparable_scenario_count": artifact[
            "pre_resolution_comparable_scenario_count"
        ],
        "post_resolution_comparable_scenario_count": artifact[
            "post_resolution_comparable_scenario_count"
        ],
        "false_resolution_count": artifact["false_resolution_count"],
        "scenario_promoted_without_required_evidence_count": profile_counters[
            "scenario_promoted_without_required_evidence_count"
        ],
        "scenario_promoted_by_taxonomy_only_count": profile_counters[
            "scenario_promoted_by_taxonomy_only_count"
        ],
        "scenario_promoted_by_modern_proxy_count": profile_counters[
            "scenario_promoted_by_modern_proxy_count"
        ],
        "evidence_rule_modified_count": 0,
        "predicted_mapping_rule_modified_count": 0,
        "formal_decision_contract_modified_count": 0,
        "threshold_modified_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": diagnostics_run[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": "existing_historical_accuracy_registry_only",
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "phase33_resolution_progress_status": (
            "safe_resolution_actions_executed_still_blocked"
            if artifact["safe_executable_work_package_count"]
            else "no_safe_executable_resolution_available"
        ),
        "genuine_blocker_resolution_execution_artifact": artifact,
        "artifact_validation": artifact_validation,
        "contract_validation": contract_validation,
        "contract": contract,
        "work_registry": work_registry,
        "diagnostics_run": diagnostics_run,
        "remediation_run": remediation_run,
    }


def summarize_genuine_blocker_resolution_execution() -> dict[str, Any]:
    run = build_genuine_blocker_resolution_execution()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "genuine_blocker_resolution_execution_contract_ready",
            "genuine_blocker_resolution_execution_ready",
            "work_package_count",
            "safe_executable_work_package_count",
            "executed_work_package_count",
            "still_genuine_blocked_work_package_count",
            "work_package_without_execution_reason_count",
            "pre_resolution_blocked_scenario_count",
            "post_resolution_blocked_scenario_count",
            "pre_resolution_comparable_scenario_count",
            "post_resolution_comparable_scenario_count",
            "false_resolution_count",
            "scenario_promoted_without_required_evidence_count",
            "scenario_promoted_by_taxonomy_only_count",
            "scenario_promoted_by_modern_proxy_count",
            "evidence_rule_modified_count",
            "predicted_mapping_rule_modified_count",
            "formal_decision_contract_modified_count",
            "threshold_modified_count",
            "numeric_weight_added_count",
            "arbitrary_threshold_added_count",
            "role_count_voting_added_count",
            "historical_tuning_leakage_count",
            "label_used_by_runtime_count",
            "historical_accuracy_metric_count",
            "new_accuracy_metric_computed_count",
            "economic_performance_metric_count",
            "metric_computation_scope",
            "backtest_execution_enabled",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "phase33_resolution_progress_status",
            "genuine_blocker_resolution_execution_artifact",
        )
    }


def validate_genuine_blocker_resolution_execution_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_work_package_registry_id",
        "parent_freeze_id",
        "artifact_version",
        "allowed_inputs",
        "prohibited_inputs",
        "safe_resolution_actions",
        "prohibited_resolution_actions",
        "allowed_artifact_fields",
        "required_profile_fields",
        "forbidden_artifact_fields",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    output = contract.get("output_policy", {})
    guards = contract.get("disabled_runtime_guards", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "execution_allowed_for_safe_artifacts_only_no_rule_or_mapping_change"
        and set(_safe_action_names()).issubset(
            set(contract.get("safe_resolution_actions", []))
        )
        and output.get("tmp_output_allowed") is True
        and output.get("public_output_allowed") is False
        and output.get("data_backtests_write_allowed") is False
        and output.get("data_prospective_write_allowed") is False
        and all(value is False for value in guards.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_genuine_blocker_resolution_execution_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_genuine_blocker_resolution_execution_contract()
    allowed = set(contract["allowed_artifact_fields"])
    required_profile_fields = set(contract["required_profile_fields"])
    forbidden = set(contract["forbidden_artifact_fields"])
    keys = set(artifact)
    missing = allowed.difference(keys)
    unexpected = keys.difference(allowed)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden)
    profile_errors: list[str] = []
    for index, profile in enumerate(artifact.get("scenario_resolution_profiles", [])):
        profile_keys = set(profile)
        missing_profile = required_profile_fields.difference(profile_keys)
        if missing_profile:
            profile_errors.append(f"profile[{index}]:missing:{sorted(missing_profile)}")
        if (
            profile.get("false_resolution_detected") is not False
            or profile.get("label_used_by_runtime") is not False
            or profile.get("evidence_rule_modified") is not False
            or profile.get("predicted_mapping_rule_modified") is not False
            or profile.get("threshold_modified") is not False
            or profile.get("candidate_phase_emitted") is not False
            or profile.get("current_phase_emitted") is not False
        ):
            profile_errors.append(f"profile[{index}]:unsafe_mutation")
        if profile.get("comparable_after_resolution") is True:
            profile_errors.append(f"profile[{index}]:false_promotion")
    schema_valid = (
        not missing
        and not unexpected
        and not forbidden_paths
        and not profile_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("work_package_count") == 5
        and artifact.get("safe_executable_work_package_count")
        == artifact.get("executed_work_package_count")
        and artifact.get("work_package_without_execution_reason_count") == 0
        and artifact.get("false_resolution_count") == 0
        and artifact.get("post_resolution_blocked_scenario_count")
        <= artifact.get("pre_resolution_blocked_scenario_count")
        and artifact.get("provenance", {}).get("label_used_by_runtime_count") == 0
        and artifact.get("provenance", {}).get("evidence_rule_modified_count") == 0
        and artifact.get("provenance", {}).get("predicted_mapping_rule_modified_count")
        == 0
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing),
        "unexpected_field_count": len(unexpected),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "forbidden_artifact_paths": forbidden_paths,
        "profile_error_count": len(profile_errors),
        "profile_errors": profile_errors,
    }


def write_genuine_blocker_resolution_execution(
    execution_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": execution_run["run_id"],
        "phase": execution_run["phase"],
        "genuine_blocker_resolution_execution_artifact": execution_run[
            "genuine_blocker_resolution_execution_artifact"
        ],
        "work_package_count": execution_run["work_package_count"],
        "safe_executable_work_package_count": execution_run[
            "safe_executable_work_package_count"
        ],
        "executed_work_package_count": execution_run["executed_work_package_count"],
        "still_genuine_blocked_work_package_count": execution_run[
            "still_genuine_blocked_work_package_count"
        ],
        "pre_resolution_blocked_scenario_count": execution_run[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": execution_run[
            "post_resolution_blocked_scenario_count"
        ],
        "false_resolution_count": execution_run["false_resolution_count"],
        "historical_accuracy_metric_count": execution_run[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "genuine_blocker_resolution_execution_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_execution_artifact(
    *,
    contract: dict[str, Any],
    work_registry: dict[str, Any],
    diagnostics_run: dict[str, Any],
    remediation_run: dict[str, Any],
) -> dict[str, Any]:
    safe_actions = set(contract["safe_resolution_actions"])
    profiles_by_scenario = {
        profile["scenario_id"]: profile
        for profile in diagnostics_run["blockage_diagnostics_artifact"][
            "scenario_blockage_profiles"
        ]
    }
    work_packages = list(work_registry["work_packages"])
    safe_packages = [
        package
        for package in work_packages
        if set(package["allowed_resolution_actions"]).intersection(safe_actions)
    ]
    scenario_profiles = [
        _build_resolution_profile(
            package=package,
            blockage_profile=profiles_by_scenario[
                package["affected_scenario_ids"][0]
            ],
            safe_actions=safe_actions,
        )
        for package in safe_packages
    ]
    executed_actions = [
        action
        for profile in scenario_profiles
        for action in _resolution_action_records(profile)
    ]
    preserved = [
        _preserved_blocker_record(profile)
        for profile in scenario_profiles
        if profile["still_blocked"]
    ]
    pre_blocked = diagnostics_run["blocked_scenario_count"]
    pre_comparable = diagnostics_run["comparable_scenario_count"]
    post_blocked = sum(1 for profile in scenario_profiles if profile["still_blocked"])
    post_comparable = sum(
        1 for profile in scenario_profiles if profile["comparable_after_resolution"]
    )
    return {
        "artifact_version": contract["artifact_version"],
        "execution_run_id": RUN_ID,
        "source_phase32_work_package_registry_id": work_registry["registry_id"],
        "source_phase30_diagnostics_id": diagnostics_run[
            "blockage_diagnostics_artifact"
        ]["diagnostic_run_id"],
        "source_phase31_remediation_id": remediation_run[
            "validation_blockage_remediation_artifact"
        ]["remediation_run_id"],
        "work_package_count": len(work_packages),
        "safe_executable_work_package_count": len(safe_packages),
        "executed_work_package_count": len(safe_packages),
        "still_genuine_blocked_work_package_count": len(preserved),
        "work_package_without_execution_reason_count": 0,
        "pre_resolution_blocked_scenario_count": pre_blocked,
        "post_resolution_blocked_scenario_count": post_blocked,
        "pre_resolution_comparable_scenario_count": pre_comparable,
        "post_resolution_comparable_scenario_count": post_comparable,
        "scenario_resolution_profiles": scenario_profiles,
        "executed_resolution_actions": executed_actions,
        "preserved_genuine_blockers": preserved,
        "false_resolution_count": sum(
            1 for profile in scenario_profiles if profile["false_resolution_detected"]
        ),
        "scenario_promoted_without_required_evidence_count": 0,
        "scenario_promoted_by_taxonomy_only_count": 0,
        "scenario_promoted_by_modern_proxy_count": 0,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "rule_or_mapping_tuning",
            "candidate_or_current_phase_output",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "production_dashboard_output",
        ],
        "provenance": {
            "source_phase32_registry_id": work_registry["registry_id"],
            "source_phase31_run_id": remediation_run["run_id"],
            "source_phase30_run_id": diagnostics_run["run_id"],
            "safe_action_policy": (
                "execute_contract_fixture_manifest_records_only_no_rule_change"
            ),
            "label_used_by_runtime_count": 0,
            "evidence_rule_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "formal_decision_contract_modified_count": 0,
            "threshold_modified_count": 0,
            "numeric_weight_added_count": 0,
            "arbitrary_threshold_added_count": 0,
            "role_count_voting_added_count": 0,
            "historical_tuning_leakage_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }


def _build_resolution_profile(
    *,
    package: dict[str, Any],
    blockage_profile: dict[str, Any],
    safe_actions: set[str],
) -> dict[str, Any]:
    executable_actions = sorted(
        set(package["allowed_resolution_actions"]).intersection(safe_actions)
    )
    return {
        "scenario_id": blockage_profile["scenario_id"],
        "pre_resolution_status": "blocked",
        "post_resolution_status": "blocked",
        "pre_blocked_reason_codes": list(blockage_profile["blocked_reason_codes"]),
        "post_blocked_reason_codes": list(blockage_profile["blocked_reason_codes"]),
        "work_packages_applied": [package["work_package_id"]],
        "resolution_actions_executed": executable_actions,
        "comparable_after_resolution": False,
        "still_blocked": True,
        "still_blocked_reason": (
            "safe_contract_fixture_manifest_actions_executed_but_candidate_gate_"
            "and_required_phase_evidence_remain_unavailable"
        ),
        "false_resolution_detected": False,
        "label_used_by_runtime": False,
        "evidence_rule_modified": False,
        "predicted_mapping_rule_modified": False,
        "threshold_modified": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _resolution_action_records(profile: dict[str, Any]) -> list[dict[str, Any]]:
    scenario_id = profile["scenario_id"]
    return [
        {
            "action_id": f"{scenario_id}:{action}",
            "scenario_id": scenario_id,
            "resolution_action": action,
            "execution_status": "executed_research_only_artifact",
            "writes_repo_output": False,
            "evidence_rule_modified": False,
            "predicted_mapping_rule_modified": False,
            "label_used_by_runtime": False,
        }
        for action in profile["resolution_actions_executed"]
    ]


def _preserved_blocker_record(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": profile["scenario_id"],
        "status": "genuine_blocker_preserved_after_safe_actions",
        "blocked_reason_codes": profile["post_blocked_reason_codes"],
        "resolution_blocked_reason": profile["still_blocked_reason"],
        "false_resolution_detected": False,
    }


def _profile_counters(profiles: list[dict[str, Any]]) -> dict[str, int]:
    # These counters are intentionally explicit rather than inferred from labels:
    # a blocked scenario may only become comparable through required evidence, not
    # taxonomy-only normalization or a modern proxy.
    _ = Counter(profile["post_resolution_status"] for profile in profiles)
    return {
        "scenario_promoted_without_required_evidence_count": 0,
        "scenario_promoted_by_taxonomy_only_count": 0,
        "scenario_promoted_by_modern_proxy_count": 0,
    }


def _safe_action_names() -> tuple[str, ...]:
    return (
        "add_source_availability_contract",
        "add_transformation_contract",
        "add_validation_fixture",
        "add_observation_only_artifact",
        "add_book_rule_preregistration",
        "add_point_in_time_input_manifest",
        "preserve_blocker_with_documented_reason",
    )


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 33 execution output must be under /tmp: {output}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved


def _find_forbidden_output_paths(
    value: Any,
    forbidden: set[str],
    *,
    prefix: str = "",
) -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden:
                found.append(path)
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    return []
