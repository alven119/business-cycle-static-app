"""Phase 27 offline predicted-label artifact generation.

The generator is intentionally label-blind: it consumes Phase 25 research
decision outputs and the Phase 26 mapping contract, then materializes offline
validation-only predicted-label artifacts. It does not read validation labels,
run comparisons, compute metrics, or expose candidate/current phase outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_research_decision_outputs import (
    build_historical_research_decision_outputs,
)
from business_cycle.validation.offline_predicted_label_mapping_contract import (
    DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH,
    load_offline_predicted_label_mapping_contract,
)


DEFAULT_OFFLINE_PREDICTED_LABEL_ARTIFACT_CONTRACT_PATH = Path(
    "specs/common/offline_predicted_label_artifact_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase27_offline_predicted_label_artifacts_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"
PHASE_LIKE_LABELS = frozenset({"recession", "recovery", "growth", "boom"})
ABSTENTION_STATES = frozenset(
    {
        "abstained",
        "temporal_abstention",
        "runtime_abstention",
        "unavailable",
        "insufficient",
        "missing",
    }
)


def load_offline_predicted_label_artifact_contract(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("offline predicted label artifact contract must map")
    contract = payload.get("offline_predicted_label_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError("offline_predicted_label_artifact_contract must be a mapping")
    return contract


def build_offline_predicted_label_artifacts(
    *,
    research_decision_output_run: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = load_offline_predicted_label_artifact_contract()
    mapping_contract = load_offline_predicted_label_mapping_contract()
    mapping_contract_hash = _mapping_contract_hash()
    research_run = research_decision_output_run or build_historical_research_decision_outputs()
    research_outputs = research_run["research_decision_outputs"]
    artifacts = [
        _build_predicted_label_artifact(
            research_output=artifact,
            contract=contract,
            mapping_contract=mapping_contract,
            mapping_contract_hash=mapping_contract_hash,
        )
        for artifact in research_outputs
    ]
    validations = [
        validate_offline_predicted_label_artifact(
            artifact,
            contract=contract,
            mapping_contract_hash=mapping_contract_hash,
        )
        for artifact in artifacts
    ]
    prohibited_artifact_field_count = sum(
        validation["prohibited_artifact_field_count"] for validation in validations
    )
    predicted_label_output_count = sum(
        validation["predicted_label_output_count"] for validation in validations
    )
    predicted_label_provenance_complete_count = sum(
        validation["predicted_label_provenance_complete"] for validation in validations
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
        "phase": "27",
        "run_id": RUN_ID,
        "offline_predicted_label_artifact_contract_ready": (
            validate_offline_predicted_label_artifact_contract(contract)[
                "contract_schema_valid"
            ]
        ),
        "offline_predicted_label_artifact_generator_ready": all(
            validation["artifact_schema_valid"] for validation in validations
        ),
        "scenario_count": research_run["scenario_count"],
        "research_decision_output_count": len(research_outputs),
        "predicted_label_artifact_count": len(artifacts),
        "predicted_label_output_count": predicted_label_output_count,
        "predicted_label_provenance_complete_count": (
            predicted_label_provenance_complete_count
        ),
        "mapping_contract_hash_verified": mapping_contract_hash_verified,
        "label_used_by_runtime_count": 0,
        "label_comparison_executed": False,
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
        "offline_predicted_label_artifacts": artifacts,
        "artifact_validations": validations,
        "research_decision_output_run": research_run,
        "contract": contract,
        "mapping_contract": mapping_contract,
        "mapping_contract_hash": mapping_contract_hash,
    }


def summarize_offline_predicted_label_artifacts() -> dict[str, Any]:
    contract = load_offline_predicted_label_artifact_contract()
    run = build_offline_predicted_label_artifacts()
    gates = contract["readiness_gates"]
    ready = (
        run["offline_predicted_label_artifact_contract_ready"] is True
        and run["offline_predicted_label_artifact_generator_ready"] is True
        and run["scenario_count"] == gates["scenario_count_required"]
        and run["research_decision_output_count"] == run["scenario_count"]
        and run["predicted_label_artifact_count"]
        == gates["predicted_label_artifact_count_required"]
        and run["predicted_label_output_count"]
        == gates["predicted_label_output_count_required"]
        and run["predicted_label_provenance_complete_count"] == run["scenario_count"]
        and run["mapping_contract_hash_verified"]
        is gates["mapping_contract_hash_verified_required"]
        and run["label_used_by_runtime_count"] == 0
        and run["label_comparison_executed"] is False
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
        "phase": "27",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "offline_predicted_label_artifact_contract_ready": ready,
        "offline_predicted_label_artifact_generator_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "research_decision_output_count",
                "predicted_label_artifact_count",
                "predicted_label_output_count",
                "predicted_label_provenance_complete_count",
                "mapping_contract_hash_verified",
                "label_used_by_runtime_count",
                "label_comparison_executed",
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


def validate_offline_predicted_label_artifact_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_mapping_contract_id",
        "parent_mapping_contract_freeze_id",
        "artifact_version",
        "predicted_label_taxonomy_version",
        "allowed_inputs",
        "prohibited_inputs",
        "allowed_artifact_fields",
        "forbidden_artifact_fields",
        "predicted_label_taxonomy",
        "mapping_execution_policy",
        "output_policy",
        "output_restrictions",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    taxonomy = contract.get("predicted_label_taxonomy", {})
    execution = contract.get("mapping_execution_policy", {})
    output = contract.get("output_policy", {})
    restrictions = contract.get("output_restrictions", {})
    disabled = contract.get("disabled_runtime_guards", {})
    required_taxonomy = {
        "recession",
        "recovery",
        "growth",
        "boom",
        "abstained",
        "blocked",
        "not_comparable",
    }
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "predicted_label_artifacts_allowed_no_comparison_or_metrics"
        and required_taxonomy.issubset(taxonomy)
        and execution.get("historical_labels_may_be_read") is False
        and execution.get("nber_dates_may_be_read") is False
        and execution.get("label_manifest_may_be_read") is False
        and execution.get("label_comparison_may_execute") is False
        and execution.get("metrics_may_execute") is False
        and execution.get("blocked_state_preserved_as_nonjudgment") is True
        and execution.get("abstained_state_preserved_as_nonjudgment") is True
        and output.get("explicit_output_path_required") is True
        and output.get("tmp_output_allowed") is True
        and output.get("committed_artifact_allowed") is False
        and output.get("data_backtests_write_allowed") is False
        and output.get("data_prospective_write_allowed") is False
        and output.get("public_output_allowed") is False
        and restrictions.get("label_comparison_executed") is False
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
        "predicted_label_taxonomy_ready": required_taxonomy.issubset(taxonomy),
    }


def validate_offline_predicted_label_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
    mapping_contract_hash: str | None = None,
) -> dict[str, Any]:
    contract = contract or load_offline_predicted_label_artifact_contract()
    mapping_contract_hash = mapping_contract_hash or _mapping_contract_hash()
    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    output_keys = set(artifact)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    predicted_label_paths = _find_forbidden_output_paths(artifact, {"predicted_label"})
    provenance = artifact.get("provenance", {})
    evidence = artifact.get("evidence_completeness_summary", {})
    mapping_contract_hash_verified = (
        artifact.get("source_mapping_contract_hash") == mapping_contract_hash
        and provenance.get("source_mapping_contract_hash") == mapping_contract_hash
    )
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and artifact.get("predicted_label") in contract["predicted_label_taxonomy"]
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("source_mapping_contract_id")
        == contract["parent_mapping_contract_id"]
        and artifact.get("predicted_label_taxonomy_version")
        == contract["predicted_label_taxonomy_version"]
        and mapping_contract_hash_verified
        and provenance.get("historical_labels_read") is False
        and provenance.get("nber_dates_read") is False
        and provenance.get("label_comparison_executed") is False
        and provenance.get("label_used_by_runtime") is False
        and provenance.get("metric_computation_enabled") is False
        and provenance.get("candidate_phase_emitted") is False
        and provenance.get("current_phase_emitted") is False
        and provenance.get("production_phase_emitted") is False
        and provenance.get("provenance_complete") is True
        and evidence.get("label_used_by_runtime") is False
        and evidence.get("label_comparison_executed") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "predicted_label_output_count": len(predicted_label_paths),
        "predicted_label_provenance_complete": int(
            provenance.get("provenance_complete") is True
            and mapping_contract_hash_verified
        ),
        "mapping_contract_hash_verified": mapping_contract_hash_verified,
        "candidate_phase_emitted": provenance.get("candidate_phase_emitted") is True,
        "current_phase_emitted": provenance.get("current_phase_emitted") is True,
        "forbidden_artifact_paths": forbidden_paths,
    }


def write_offline_predicted_label_artifacts(
    artifact_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": artifact_run["run_id"],
        "phase": artifact_run["phase"],
        "offline_predicted_label_artifacts": artifact_run[
            "offline_predicted_label_artifacts"
        ],
        "scenario_count": artifact_run["scenario_count"],
        "predicted_label_artifact_count": artifact_run[
            "predicted_label_artifact_count"
        ],
        "predicted_label_output_count": artifact_run["predicted_label_output_count"],
        "label_comparison_executed": False,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "allowed_uses": [
            "offline_validation_label_join_preparation",
            "research_historical_validation_artifact_review",
            "label_blind_mapping_provenance_review",
        ],
        "prohibited_uses": [
            "runtime_decision_logic",
            "candidate_phase_output",
            "current_phase_output",
            "production_phase_output",
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "parameter_tuning",
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "offline_predicted_label_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_predicted_label_artifact(
    *,
    research_output: dict[str, Any],
    contract: dict[str, Any],
    mapping_contract: dict[str, Any],
    mapping_contract_hash: str,
) -> dict[str, Any]:
    predicted_label, mapping_rule_id, mapping_basis = _map_research_output(
        research_output
    )
    blocked_reason_codes = list(research_output["blocked_reason_codes"])
    return {
        "artifact_version": contract["artifact_version"],
        "scenario_id": research_output["scenario_id"],
        "as_of": research_output["as_of"],
        "data_mode": research_output["data_mode"],
        "source_research_decision_output_id": research_output["research_output_id"],
        "source_mapping_contract_id": mapping_contract["contract_id"],
        "source_mapping_contract_hash": mapping_contract_hash,
        "predicted_label": predicted_label,
        "predicted_label_taxonomy_version": contract[
            "predicted_label_taxonomy_version"
        ],
        "mapping_rule_id": mapping_rule_id,
        "mapping_basis": mapping_basis,
        "abstention_state": research_output["abstention_state"],
        "blocked_reason_codes": blocked_reason_codes,
        "evidence_completeness_summary": {
            "source_decision_state": research_output["decision_state"],
            "source_abstention_state": research_output["abstention_state"],
            "blocked_reason_count": len(blocked_reason_codes),
            "source_output_mode": research_output["output_mode"],
            "label_used_by_runtime": False,
            "label_comparison_executed": False,
            "historical_accuracy_metric_count": 0,
            "economic_performance_metric_count": 0,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "runtime_decision_logic",
            "candidate_phase_output",
            "current_phase_output",
            "production_phase_output",
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "portfolio_or_trade_decision",
            "parameter_tuning",
        ],
        "provenance": {
            "source_research_decision_output_id": research_output["research_output_id"],
            "source_mapping_contract_id": mapping_contract["contract_id"],
            "source_mapping_contract_hash": mapping_contract_hash,
            "source_mapping_contract_freeze_id": contract[
                "parent_mapping_contract_freeze_id"
            ],
            "mapping_rule_id": mapping_rule_id,
            "historical_labels_read": False,
            "nber_dates_read": False,
            "label_manifest_read": False,
            "scenario_answer_read": False,
            "label_comparison_executed": False,
            "label_used_by_runtime": False,
            "metric_computation_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
            "production_phase_emitted": False,
            "provenance_complete": True,
        },
    }


def _map_research_output(
    research_output: dict[str, Any],
) -> tuple[str, str, dict[str, Any]]:
    blocked_reason_codes = list(research_output.get("blocked_reason_codes", []))
    abstention_state = str(research_output.get("abstention_state", "")).lower()
    decision_state = str(research_output.get("decision_state", "")).lower()
    if blocked_reason_codes:
        return (
            "blocked",
            "map_blocked_reasons_to_blocked",
            {
                "source_fields": ["blocked_reason_codes"],
                "blocked_reason_count": len(blocked_reason_codes),
                "nonjudgment_state_preserved": True,
            },
        )
    if abstention_state in ABSTENTION_STATES or "abstain" in abstention_state:
        return (
            "abstained",
            "map_runtime_abstention_to_abstained",
            {
                "source_fields": ["abstention_state"],
                "source_abstention_state": research_output.get("abstention_state"),
                "nonjudgment_state_preserved": True,
            },
        )
    if decision_state in PHASE_LIKE_LABELS:
        return (
            decision_state,
            "map_research_ready_phase_like_state",
            {
                "source_fields": ["decision_state"],
                "source_decision_state": research_output.get("decision_state"),
                "offline_validation_only": True,
            },
        )
    return (
        "not_comparable",
        "map_missing_research_output_to_not_comparable",
        {
            "source_fields": ["decision_state"],
            "source_decision_state": research_output.get("decision_state"),
            "nonjudgment_state_preserved": True,
        },
    )


def _mapping_contract_hash() -> str:
    return hashlib.sha256(
        DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_CONTRACT_PATH.read_bytes()
    ).hexdigest()


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 27 predicted label output must be under /tmp: {output}")
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
