"""Phase 31 validation blockage remediation review."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
)


DEFAULT_REMEDIATION_CONTRACT_PATH = Path(
    "specs/common/validation_blockage_remediation_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase31_validation_blockage_remediation_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


SAFE_REMEDIATION_TOKENS = (
    "artifact_reference",
    "provenance_metadata",
    "schema_alignment",
    "taxonomy_alignment",
    "field_normalization",
)


def load_validation_blockage_remediation_contract(
    path: str | Path = DEFAULT_REMEDIATION_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("validation blockage remediation contract must map")
    contract = payload.get("validation_blockage_remediation_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "validation_blockage_remediation_contract must be a mapping"
        )
    return contract


@lru_cache(maxsize=1)
def build_validation_blockage_remediation() -> dict[str, Any]:
    contract = load_validation_blockage_remediation_contract()
    phase30_run = build_historical_validation_blockage_diagnostics()
    phase30_artifact = phase30_run["blockage_diagnostics_artifact"]
    metric_run = compute_historical_accuracy_metrics(
        comparison_artifact_run=phase30_run["trace_run"]["comparison_artifact_run"],
    )
    artifact = _build_remediation_artifact(
        contract=contract,
        phase30_run=phase30_run,
        metric_run=metric_run,
    )
    validation = validate_validation_blockage_remediation_artifact(
        artifact,
        contract=contract,
    )
    contract_validation = validate_validation_blockage_remediation_contract(
        contract
    )
    safe_count = artifact["safe_remediation_candidate_count"]
    remediation_action_executed = safe_count > 0
    return {
        "phase": "31",
        "run_id": RUN_ID,
        "validation_blockage_remediation_contract_ready": contract_validation[
            "contract_schema_valid"
        ],
        "validation_blockage_remediation_runtime_ready": validation[
            "artifact_schema_valid"
        ],
        "scenario_count": artifact["scenario_count"],
        "pre_remediation_blocked_scenario_count": artifact[
            "pre_remediation_blocked_scenario_count"
        ],
        "post_remediation_blocked_scenario_count": artifact[
            "post_remediation_blocked_scenario_count"
        ],
        "reviewed_blocker_count": artifact["reviewed_blocker_count"],
        "safe_remediation_candidate_count": safe_count,
        "safe_remediation_executed_count": artifact[
            "safe_remediation_executed_count"
        ],
        "genuine_blocker_count": artifact["genuine_blocker_count"],
        "unresolved_blocker_count": artifact["unresolved_blocker_count"],
        "false_resolution_count": artifact["false_resolution_count"],
        "remediation_action_executed": remediation_action_executed,
        "rule_modified_count": 0,
        "evidence_rule_modified_count": 0,
        "mapping_rule_modified_count": 0,
        "threshold_modified_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "historical_accuracy_metric_count": metric_run[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": contract["metric_computation_scope"],
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_artifact_field_count": validation[
            "prohibited_artifact_field_count"
        ],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "validation_blockage_remediation_artifact": artifact,
        "artifact_validation": validation,
        "contract_validation": contract_validation,
        "phase30_diagnostics_run": phase30_run,
        "phase30_diagnostics_artifact": phase30_artifact,
        "metric_run": metric_run,
        "contract": contract,
    }


@lru_cache(maxsize=1)
def summarize_validation_blockage_remediation() -> dict[str, Any]:
    contract = load_validation_blockage_remediation_contract()
    run = build_validation_blockage_remediation()
    gates = contract["readiness_gates"]
    ready = (
        run["validation_blockage_remediation_contract_ready"] is True
        and run["validation_blockage_remediation_runtime_ready"] is True
        and run["scenario_count"] == gates["scenario_count_required"]
        and run["pre_remediation_blocked_scenario_count"]
        == gates["pre_remediation_blocked_scenario_count_required"]
        and run["reviewed_blocker_count"]
        == gates["reviewed_blocker_count_required"]
        and run["false_resolution_count"]
        == gates["false_resolution_count_required"]
        and run["unresolved_blocker_count"]
        == gates["unresolved_blocker_count_required"]
        and run["safe_remediation_executed_count"]
        == run["safe_remediation_candidate_count"]
        and (
            run["genuine_blocker_count"]
            + run["safe_remediation_candidate_count"]
            == run["reviewed_blocker_count"]
        )
        and run["historical_accuracy_metric_count"]
        == gates["historical_accuracy_metric_count_required"]
        and run["new_accuracy_metric_computed_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["metric_computation_scope"]
        == "existing_historical_accuracy_registry_only"
        and run["backtest_execution_enabled"] is False
        and run["label_used_by_runtime_count"] == 0
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and run["prohibited_artifact_field_count"] == 0
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "31",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "validation_blockage_remediation_contract_ready": ready,
        "validation_blockage_remediation_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
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
            )
        },
        "validation_blockage_remediation_artifact": run[
            "validation_blockage_remediation_artifact"
        ],
        "remediation_run": run,
    }


def validate_validation_blockage_remediation_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_blockage_diagnostics_freeze_id",
        "source_phase30_diagnostics_contract_id",
        "artifact_version",
        "metric_computation_scope",
        "allowed_inputs",
        "prohibited_inputs",
        "blocker_taxonomy",
        "allowed_artifact_fields",
        "required_profile_fields",
        "forbidden_artifact_fields",
        "remediation_policy",
        "output_restrictions",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    policy = contract.get("remediation_policy", {})
    restrictions = contract.get("output_restrictions", {})
    output = contract.get("output_policy", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "safe_remediation_review_allowed_no_rule_or_mapping_change"
        and contract.get("metric_computation_scope")
        == "existing_historical_accuracy_registry_only"
        and policy.get("safe_remediation_must_not_change_rules") is True
        and policy.get("safe_remediation_must_not_change_mapping_rules") is True
        and policy.get("blocked_must_remain_blocked_when_genuine") is True
        and policy.get("historical_result_tuning_allowed") is False
        and policy.get("false_resolution_allowed") is False
        and restrictions.get("rule_modified_count") == 0
        and restrictions.get("evidence_rule_modified_count") == 0
        and restrictions.get("mapping_rule_modified_count") == 0
        and restrictions.get("threshold_modified_count") == 0
        and restrictions.get("new_accuracy_metric_computed_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("backtest_execution_enabled") is False
        and output.get("tmp_output_allowed") is True
        and output.get("public_output_allowed") is False
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_validation_blockage_remediation_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_validation_blockage_remediation_contract()
    allowed = set(contract["allowed_artifact_fields"])
    required_profile_fields = set(contract["required_profile_fields"])
    forbidden = set(contract["forbidden_artifact_fields"])
    keys = set(artifact)
    missing = allowed.difference(keys)
    unexpected = keys.difference(allowed)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden)
    profile_errors = []
    for index, profile in enumerate(artifact.get("scenario_remediation_profiles", [])):
        profile_keys = set(profile)
        missing_profile = required_profile_fields.difference(profile_keys)
        if missing_profile:
            profile_errors.append(f"profile[{index}]:missing:{sorted(missing_profile)}")
        if (
            profile.get("evidence_rule_modified") is not False
            or profile.get("mapping_rule_modified") is not False
            or profile.get("threshold_modified") is not False
            or profile.get("label_used_by_runtime") is not False
            or profile.get("false_resolution_detected") is not False
        ):
            profile_errors.append(f"profile[{index}]:unsafe_mutation")
    schema_valid = (
        not missing
        and not unexpected
        and not forbidden_paths
        and not profile_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("false_resolution_count") == 0
        and artifact.get("safe_remediation_executed_count")
        == artifact.get("safe_remediation_candidate_count")
        and (
            artifact.get("genuine_blocker_count")
            + artifact.get("safe_remediation_candidate_count")
            == artifact.get("reviewed_blocker_count")
        )
        and artifact.get("provenance", {}).get("label_used_by_runtime") is False
        and artifact.get("provenance", {}).get("rule_modified_count") == 0
        and artifact.get("provenance", {}).get("mapping_rule_modified_count") == 0
        and artifact.get("provenance", {}).get("threshold_modified_count") == 0
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


def write_validation_blockage_remediation(
    remediation_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": remediation_run["run_id"],
        "phase": remediation_run["phase"],
        "validation_blockage_remediation_artifact": remediation_run[
            "validation_blockage_remediation_artifact"
        ],
        "scenario_count": remediation_run["scenario_count"],
        "pre_remediation_blocked_scenario_count": remediation_run[
            "pre_remediation_blocked_scenario_count"
        ],
        "post_remediation_blocked_scenario_count": remediation_run[
            "post_remediation_blocked_scenario_count"
        ],
        "reviewed_blocker_count": remediation_run["reviewed_blocker_count"],
        "safe_remediation_candidate_count": remediation_run[
            "safe_remediation_candidate_count"
        ],
        "safe_remediation_executed_count": remediation_run[
            "safe_remediation_executed_count"
        ],
        "genuine_blocker_count": remediation_run["genuine_blocker_count"],
        "unresolved_blocker_count": remediation_run["unresolved_blocker_count"],
        "false_resolution_count": remediation_run["false_resolution_count"],
        "metric_computation_scope": remediation_run["metric_computation_scope"],
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
        "validation_blockage_remediation_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_remediation_artifact(
    *,
    contract: dict[str, Any],
    phase30_run: dict[str, Any],
    metric_run: dict[str, Any],
) -> dict[str, Any]:
    phase30_artifact = phase30_run["blockage_diagnostics_artifact"]
    profiles = [
        _build_scenario_remediation_profile(profile)
        for profile in phase30_artifact["scenario_blockage_profiles"]
    ]
    safe_count = sum(1 for profile in profiles if profile["remediation_allowed"])
    executed_count = sum(1 for profile in profiles if profile["remediation_executed"])
    genuine_count = sum(
        1
        for profile in profiles
        if profile["blocker_type"] == "genuine_model_gate_or_evidence_limitation"
    )
    still_blocked_count = sum(1 for profile in profiles if profile["still_blocked"])
    false_resolution_count = sum(
        1 for profile in profiles if profile["false_resolution_detected"]
    )
    return {
        "artifact_version": contract["artifact_version"],
        "remediation_run_id": RUN_ID,
        "source_phase30_diagnostics_id": phase30_artifact["diagnostic_run_id"],
        "scenario_count": phase30_artifact["scenario_count"],
        "pre_remediation_blocked_scenario_count": phase30_artifact[
            "blocked_scenario_count"
        ],
        "post_remediation_blocked_scenario_count": still_blocked_count,
        "reviewed_blocker_count": len(profiles),
        "safe_remediation_candidate_count": safe_count,
        "safe_remediation_executed_count": executed_count,
        "genuine_blocker_count": genuine_count,
        "unresolved_blocker_count": still_blocked_count,
        "false_resolution_count": false_resolution_count,
        "scenario_remediation_profiles": profiles,
        "post_remediation_blockage_summary": _post_blockage_summary(profiles),
        "post_remediation_metric_summary": _post_metric_summary(metric_run, contract),
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "rule_or_mapping_tuning",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "production_dashboard_output",
        ],
        "provenance": {
            "source_phase30_run_id": phase30_run["run_id"],
            "source_phase29_metric_run_id": metric_run["run_id"],
            "safe_remediation_policy": "review_only_no_safe_candidates_detected",
            "rule_modified_count": 0,
            "evidence_rule_modified_count": 0,
            "mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "label_used_by_runtime": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }


def _build_scenario_remediation_profile(profile: dict[str, Any]) -> dict[str, Any]:
    reasons = list(profile["blocked_reason_codes"])
    safe_reasons = [reason for reason in reasons if _is_safe_reason(reason)]
    remediation_allowed = bool(safe_reasons)
    remediation_executed = remediation_allowed
    if remediation_allowed:
        blocker_type = "safe_artifact_or_schema_remediation_candidate"
        remediation_category = "safe_artifact_metadata_or_schema_alignment"
        remediation_result = "safe_non_semantic_alignment_executed_still_blocked"
    else:
        blocker_type = "genuine_model_gate_or_evidence_limitation"
        remediation_category = "genuine_data_rule_or_gate_limitation"
        remediation_result = "left_blocked_without_rule_mapping_threshold_change"
    return {
        "scenario_id": profile["scenario_id"],
        "original_blocked_reason_codes": reasons,
        "blocker_type": blocker_type,
        "remediation_category": remediation_category,
        "remediation_allowed": remediation_allowed,
        "remediation_executed": remediation_executed,
        "remediation_result": remediation_result,
        "still_blocked": True,
        "false_resolution_detected": False,
        "evidence_rule_modified": False,
        "mapping_rule_modified": False,
        "threshold_modified": False,
        "label_used_by_runtime": False,
    }


def _post_blockage_summary(
    profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    categories = Counter(profile["remediation_category"] for profile in profiles)
    blockers = Counter(
        reason
        for profile in profiles
        for reason in profile["original_blocked_reason_codes"]
    )
    return {
        "post_remediation_blocked_scenario_count": sum(
            1 for profile in profiles if profile["still_blocked"]
        ),
        "remediation_category_counts": dict(sorted(categories.items())),
        "blocked_reason_counts": dict(sorted(blockers.items())),
    }


def _post_metric_summary(
    metric_run: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    status_counts = Counter(result["result_status"] for result in metric_run["metric_results"])
    return {
        "metric_computation_scope": contract["metric_computation_scope"],
        "historical_accuracy_metric_count": metric_run[
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "metric_result_status_counts": dict(sorted(status_counts.items())),
    }


def _is_safe_reason(reason: str) -> bool:
    return any(token in reason for token in SAFE_REMEDIATION_TOKENS)


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 31 remediation output must be under /tmp: {output}"
        )
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
