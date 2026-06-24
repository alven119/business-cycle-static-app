"""Phase 28 predicted-label comparison artifact generation.

This phase joins Phase 27 offline predicted-label artifacts to the Phase 17
historical validation manifest. It executes comparison-status generation only:
no correctness labels, accuracy metrics, confusion matrices, performance
metrics, backtests, or runtime label feedback are produced.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
)
from business_cycle.validation.offline_predicted_label_artifacts import (
    build_offline_predicted_label_artifacts,
)
from business_cycle.validation.offline_predicted_label_mapping_contract import (
    DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


DEFAULT_PREDICTED_LABEL_COMPARISON_ARTIFACT_CONTRACT_PATH = Path(
    "specs/common/predicted_label_comparison_artifact_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase28_predicted_label_comparison_artifacts_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


def load_predicted_label_comparison_artifact_contract(
    path: str | Path = DEFAULT_PREDICTED_LABEL_COMPARISON_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("predicted label comparison artifact contract must map")
    contract = payload.get("predicted_label_comparison_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "predicted_label_comparison_artifact_contract must be a mapping"
        )
    return contract


def build_predicted_label_comparison_artifacts(
    *,
    predicted_label_artifact_run: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = load_predicted_label_comparison_artifact_contract()
    predicted_run = (
        predicted_label_artifact_run or build_offline_predicted_label_artifacts()
    )
    manifest = load_historical_validation_scenario_manifest()
    label_policy = summarize_validation_label_policy()
    mapping_contract_hash = _mapping_contract_hash()
    manifest_rows = {
        row["scenario_id"]: row for row in manifest["scenario_rows"]
    }
    artifacts = [
        _build_comparison_artifact(
            predicted_artifact=artifact,
            manifest_row=manifest_rows[artifact["scenario_id"]],
            contract=contract,
            manifest_id=manifest["manifest_id"],
            label_policy=label_policy,
            mapping_contract_hash=mapping_contract_hash,
        )
        for artifact in predicted_run["offline_predicted_label_artifacts"]
    ]
    validations = [
        validate_predicted_label_comparison_artifact(
            artifact,
            contract=contract,
            mapping_contract_hash=mapping_contract_hash,
        )
        for artifact in artifacts
    ]
    prohibited_artifact_field_count = sum(
        validation["prohibited_artifact_field_count"] for validation in validations
    )
    predicted_label_provenance_verified_count = sum(
        validation["predicted_label_provenance_verified"] for validation in validations
    )
    historical_label_provenance_verified_count = sum(
        validation["historical_label_provenance_verified"] for validation in validations
    )
    mapping_contract_hash_verified = all(
        validation["mapping_contract_hash_verified"] for validation in validations
    )
    candidate_phase_emitted = any(
        validation["candidate_phase_emitted"] for validation in validations
    )
    current_phase_emitted = any(
        validation["current_phase_emitted"] for validation in validations
    )
    return {
        "phase": "28",
        "run_id": RUN_ID,
        "predicted_label_comparison_artifact_contract_ready": (
            validate_predicted_label_comparison_artifact_contract(contract)[
                "contract_schema_valid"
            ]
        ),
        "predicted_label_comparison_generator_ready": all(
            validation["artifact_schema_valid"] for validation in validations
        ),
        "scenario_count": predicted_run["scenario_count"],
        "predicted_label_artifact_count": predicted_run[
            "predicted_label_artifact_count"
        ],
        "label_comparison_artifact_count": len(artifacts),
        "label_comparison_executed": True,
        "predicted_label_provenance_verified_count": (
            predicted_label_provenance_verified_count
        ),
        "historical_label_provenance_verified_count": (
            historical_label_provenance_verified_count
        ),
        "mapping_contract_hash_verified": mapping_contract_hash_verified,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": False,
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": candidate_phase_emitted,
        "current_phase_emitted": current_phase_emitted,
        "prohibited_artifact_field_count": prohibited_artifact_field_count,
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(
            contract["disabled_runtime_guards"]["numeric_weight_added"]
        ),
        "arbitrary_threshold_added_count": int(
            contract["disabled_runtime_guards"]["arbitrary_threshold_added"]
        ),
        "role_count_voting_added_count": int(
            contract["disabled_runtime_guards"]["role_count_voting_added"]
        ),
        "historical_tuning_leakage_count": int(
            contract["disabled_runtime_guards"]["historical_tuning_used"]
        ),
        "predicted_label_comparison_artifacts": artifacts,
        "artifact_validations": validations,
        "predicted_label_artifact_run": predicted_run,
        "scenario_manifest": manifest,
        "label_policy": label_policy,
        "contract": contract,
        "mapping_contract_hash": mapping_contract_hash,
    }


def summarize_predicted_label_comparison_artifacts() -> dict[str, Any]:
    contract = load_predicted_label_comparison_artifact_contract()
    run = build_predicted_label_comparison_artifacts()
    gates = contract["readiness_gates"]
    ready = (
        run["predicted_label_comparison_artifact_contract_ready"] is True
        and run["predicted_label_comparison_generator_ready"] is True
        and run["scenario_count"] == gates["scenario_count_required"]
        and run["predicted_label_artifact_count"]
        == gates["predicted_label_artifact_count_required"]
        and run["label_comparison_artifact_count"]
        == gates["label_comparison_artifact_count_required"]
        and run["label_comparison_executed"] is True
        and run["predicted_label_provenance_verified_count"]
        == gates["predicted_label_provenance_verified_count_required"]
        and run["historical_label_provenance_verified_count"]
        == gates["historical_label_provenance_verified_count_required"]
        and run["mapping_contract_hash_verified"]
        is gates["mapping_contract_hash_verified_required"]
        and run["label_used_by_runtime_count"] == 0
        and run["historical_accuracy_metric_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["metric_computation_enabled"] is False
        and run["backtest_execution_enabled"] is False
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and run["prohibited_artifact_field_count"]
        == gates["prohibited_artifact_field_count_required"]
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "28",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "predicted_label_comparison_artifact_contract_ready": ready,
        "predicted_label_comparison_generator_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "predicted_label_artifact_count",
                "label_comparison_artifact_count",
                "label_comparison_executed",
                "predicted_label_provenance_verified_count",
                "historical_label_provenance_verified_count",
                "mapping_contract_hash_verified",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "prohibited_artifact_field_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
            )
        },
        "artifact_run": run,
    }


def validate_predicted_label_comparison_artifact_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_predicted_label_artifact_freeze_id",
        "source_predicted_label_artifact_contract_id",
        "source_historical_label_manifest_id",
        "source_historical_label_policy_id",
        "source_mapping_contract_id",
        "artifact_version",
        "predicted_label_taxonomy_version",
        "reference_label_taxonomy_version",
        "allowed_inputs",
        "prohibited_inputs",
        "allowed_artifact_fields",
        "forbidden_artifact_fields",
        "comparison_status_taxonomy",
        "reference_label_policy",
        "comparison_policy",
        "output_policy",
        "output_restrictions",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    status_taxonomy = contract.get("comparison_status_taxonomy", {})
    reference_policy = contract.get("reference_label_policy", {})
    comparison_policy = contract.get("comparison_policy", {})
    output_policy = contract.get("output_policy", {})
    restrictions = contract.get("output_restrictions", {})
    disabled = contract.get("disabled_runtime_guards", {})
    required_statuses = {
        "comparable",
        "not_comparable",
        "abstained",
        "blocked",
        "taxonomy_mismatch",
    }
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "comparison_artifacts_allowed_no_accuracy_or_performance_metrics"
        and required_statuses.issubset(status_taxonomy)
        and reference_policy.get("label_values_materialized") is False
        and reference_policy.get("labels_may_enter_runtime") is False
        and reference_policy.get("labels_may_tune_rules") is False
        and reference_policy.get("labels_may_tune_mapping") is False
        and comparison_policy.get("label_comparison_executed") is True
        and comparison_policy.get("correctness_metric_allowed") is False
        and comparison_policy.get("confusion_matrix_allowed") is False
        and comparison_policy.get("accuracy_metric_allowed") is False
        and comparison_policy.get("economic_performance_metric_allowed") is False
        and comparison_policy.get("backtest_execution_allowed") is False
        and comparison_policy.get("mapping_rule_mutation_allowed") is False
        and output_policy.get("explicit_output_path_required") is True
        and output_policy.get("tmp_output_allowed") is True
        and output_policy.get("committed_artifact_allowed") is False
        and output_policy.get("data_backtests_write_allowed") is False
        and output_policy.get("data_prospective_write_allowed") is False
        and output_policy.get("public_output_allowed") is False
        and restrictions.get("label_comparison_executed") is True
        and restrictions.get("historical_accuracy_metric_count") == 0
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("metric_computation_enabled") is False
        and restrictions.get("backtest_execution_enabled") is False
        and restrictions.get("candidate_phase_emitted") is False
        and restrictions.get("current_phase_emitted") is False
        and all(value is False for value in disabled.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
        "comparison_status_taxonomy_ready": required_statuses.issubset(
            status_taxonomy
        ),
    }


def validate_predicted_label_comparison_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
    mapping_contract_hash: str | None = None,
) -> dict[str, Any]:
    contract = contract or load_predicted_label_comparison_artifact_contract()
    mapping_contract_hash = mapping_contract_hash or _mapping_contract_hash()
    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    output_keys = set(artifact)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    predicted_provenance = artifact.get("predicted_label_provenance", {})
    historical_provenance = artifact.get("historical_label_provenance", {})
    mapping_contract_hash_verified = (
        artifact.get("mapping_contract_hash") == mapping_contract_hash
        and predicted_provenance.get("source_mapping_contract_hash")
        == mapping_contract_hash
    )
    predicted_label_provenance_verified = (
        predicted_provenance.get("provenance_complete") is True
        and predicted_provenance.get("label_used_by_runtime") is False
        and predicted_provenance.get("metric_computation_enabled") is False
        and mapping_contract_hash_verified
    )
    historical_label_provenance_verified = (
        historical_provenance.get("provenance_complete") is True
        and historical_provenance.get("label_used_by_runtime") is False
        and historical_provenance.get("label_values_materialized") is False
    )
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and artifact.get("comparison_status")
        in contract["comparison_status_taxonomy"]
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("predicted_label_taxonomy_version")
        == contract["predicted_label_taxonomy_version"]
        and artifact.get("reference_label_taxonomy_version")
        == contract["reference_label_taxonomy_version"]
        and mapping_contract_hash_verified
        and predicted_label_provenance_verified
        and historical_label_provenance_verified
        and predicted_provenance.get("candidate_phase_emitted") is False
        and predicted_provenance.get("current_phase_emitted") is False
        and historical_provenance.get("label_used_for_rule_tuning") is False
        and historical_provenance.get("label_used_for_mapping_tuning") is False
        and historical_provenance.get("historical_accuracy_metric_count") == 0
        and historical_provenance.get("economic_performance_metric_count") == 0
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "predicted_label_provenance_verified": int(
            predicted_label_provenance_verified
        ),
        "historical_label_provenance_verified": int(
            historical_label_provenance_verified
        ),
        "mapping_contract_hash_verified": mapping_contract_hash_verified,
        "candidate_phase_emitted": predicted_provenance.get(
            "candidate_phase_emitted"
        )
        is True,
        "current_phase_emitted": predicted_provenance.get("current_phase_emitted")
        is True,
        "forbidden_artifact_paths": forbidden_paths,
    }


def write_predicted_label_comparison_artifacts(
    artifact_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": artifact_run["run_id"],
        "phase": artifact_run["phase"],
        "predicted_label_comparison_artifacts": artifact_run[
            "predicted_label_comparison_artifacts"
        ],
        "scenario_count": artifact_run["scenario_count"],
        "predicted_label_artifact_count": artifact_run[
            "predicted_label_artifact_count"
        ],
        "label_comparison_artifact_count": artifact_run[
            "label_comparison_artifact_count"
        ],
        "label_comparison_executed": True,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "allowed_uses": [
            "offline_predicted_label_comparison_review",
            "label_and_prediction_provenance_review",
            "future_metric_prerequisite_artifact_review",
        ],
        "prohibited_uses": [
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "predicted_label_comparison_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_comparison_artifact(
    *,
    predicted_artifact: dict[str, Any],
    manifest_row: dict[str, Any],
    contract: dict[str, Any],
    manifest_id: str,
    label_policy: dict[str, Any],
    mapping_contract_hash: str,
) -> dict[str, Any]:
    comparison_status, comparison_status_reason, comparable = _comparison_status(
        predicted_artifact=predicted_artifact,
        manifest_row=manifest_row,
        contract=contract,
        mapping_contract_hash=mapping_contract_hash,
    )
    scenario_id = predicted_artifact["scenario_id"]
    as_of = predicted_artifact["as_of"]
    predicted_label_artifact_id = f"phase27_predicted_label:{scenario_id}:{as_of}"
    label_provenance_complete = bool(
        label_policy["validation_label_policy_ready"]
        and manifest_row["label_provenance_complete"] is True
    )
    return {
        "artifact_version": contract["artifact_version"],
        "scenario_id": scenario_id,
        "as_of": as_of,
        "data_mode": predicted_artifact["data_mode"],
        "predicted_label_artifact_id": predicted_label_artifact_id,
        "historical_label_manifest_id": manifest_id,
        "predicted_label": predicted_artifact["predicted_label"],
        "predicted_label_taxonomy_version": predicted_artifact[
            "predicted_label_taxonomy_version"
        ],
        "reference_label_set": {
            "label_source_id": manifest_row["label_source_id"],
            "label_source_role": manifest_row["label_source_role"],
            "scenario_family": manifest_row["scenario_family"],
            "validation_window_start": manifest_row["validation_window_start"],
            "validation_window_end": manifest_row["validation_window_end"],
            "label_values_materialized": False,
            "reference_only": True,
        },
        "reference_label_taxonomy_version": contract[
            "reference_label_taxonomy_version"
        ],
        "comparison_status": comparison_status,
        "comparison_status_reason": comparison_status_reason,
        "comparable": comparable,
        "abstention_state": predicted_artifact["abstention_state"],
        "blocked_reason_codes": list(predicted_artifact["blocked_reason_codes"]),
        "predicted_label_provenance": {
            **predicted_artifact["provenance"],
            "predicted_label_artifact_id": predicted_label_artifact_id,
            "predicted_label_taxonomy_version": predicted_artifact[
                "predicted_label_taxonomy_version"
            ],
        },
        "historical_label_provenance": {
            "historical_label_manifest_id": manifest_id,
            "label_policy_id": label_policy["policy_id"],
            "label_policy_version": label_policy["policy_version"],
            "label_source_id": manifest_row["label_source_id"],
            "label_source_role": manifest_row["label_source_role"],
            "label_provenance_complete": manifest_row[
                "label_provenance_complete"
            ],
            "provenance_complete": label_provenance_complete,
            "label_values_materialized": False,
            "label_used_by_runtime": False,
            "label_used_for_rule_tuning": False,
            "label_used_for_mapping_tuning": False,
            "historical_accuracy_metric_count": 0,
            "economic_performance_metric_count": 0,
        },
        "mapping_contract_hash": mapping_contract_hash,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
    }


def _comparison_status(
    *,
    predicted_artifact: dict[str, Any],
    manifest_row: dict[str, Any],
    contract: dict[str, Any],
    mapping_contract_hash: str,
) -> tuple[str, str, bool]:
    predicted_label = predicted_artifact.get("predicted_label")
    source_hash = predicted_artifact.get("source_mapping_contract_hash")
    taxonomy = {
        "recession",
        "recovery",
        "growth",
        "boom",
        "abstained",
        "blocked",
        "not_comparable",
    }
    if (
        predicted_label not in taxonomy
        or predicted_artifact.get("predicted_label_taxonomy_version")
        != contract["predicted_label_taxonomy_version"]
        or source_hash != mapping_contract_hash
        or manifest_row.get("label_provenance_complete") is not True
    ):
        return "taxonomy_mismatch", "taxonomy_or_provenance_mismatch", False
    if predicted_label == "blocked" or predicted_artifact.get("blocked_reason_codes"):
        return "blocked", "blocked_reason_codes_preserved", False
    if predicted_label == "abstained":
        return "abstained", "runtime_abstention_preserved", False
    if predicted_label == "not_comparable":
        return "not_comparable", "predicted_label_not_comparable", False
    return "comparable", "predicted_and_reference_taxonomies_aligned", True


def _mapping_contract_hash() -> str:
    return hashlib.sha256(
        DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH.read_bytes()
    ).hexdigest()


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 28 predicted label comparison output must be under /tmp: {output}"
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
