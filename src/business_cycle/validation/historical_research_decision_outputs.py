"""Phase 25 research-only historical decision output artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_comparison_coverage_metrics import (
    run_historical_comparison_coverage_metrics,
)
from business_cycle.validation.historical_label_joiner import (
    build_historical_label_comparison_artifacts,
)


DEFAULT_RESEARCH_DECISION_OUTPUT_ARTIFACT_CONTRACT_PATH = Path(
    "specs/common/historical_research_decision_output_artifact_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase25_research_decision_outputs_v1"


def load_historical_research_decision_output_artifact_contract(
    path: str | Path = DEFAULT_RESEARCH_DECISION_OUTPUT_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical research decision output artifact contract must map")
    contract = payload.get("historical_research_decision_output_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_research_decision_output_artifact_contract must be a mapping"
        )
    return contract


def build_historical_research_decision_outputs() -> dict[str, Any]:
    contract = load_historical_research_decision_output_artifact_contract()
    comparison_run = build_historical_label_comparison_artifacts()
    coverage_run = run_historical_comparison_coverage_metrics()
    artifacts = [
        _build_research_output_artifact(
            comparison_artifact=artifact,
            contract=contract,
            coverage_metric_artifact_id=coverage_run["run_id"],
        )
        for artifact in comparison_run["label_comparison_artifacts"]
    ]
    validations = [
        validate_historical_research_decision_output_artifact(
            artifact,
            contract=contract,
        )
        for artifact in artifacts
    ]
    prohibited_artifact_field_count = sum(
        validation["prohibited_artifact_field_count"] for validation in validations
    )
    predicted_label_output_count = sum(
        validation["predicted_label_output_count"] for validation in validations
    )
    output_mode_research_only_count = sum(
        artifact["output_mode"] == contract["output_mode_required"]
        for artifact in artifacts
    )
    label_used_by_runtime_count = sum(
        artifact["label_used_by_runtime"] is True for artifact in artifacts
    )
    candidate_phase_emitted = any(
        artifact["trust_metadata"]["candidate_phase_emitted"] for artifact in artifacts
    )
    current_phase_emitted = any(
        artifact["trust_metadata"]["current_phase_emitted"] for artifact in artifacts
    )
    return {
        "phase": "25",
        "run_id": RUN_ID,
        "research_decision_output_artifact_contract_ready": (
            contract["contract_status"]
            == "research_outputs_allowed_no_predicted_labels_or_metrics"
        ),
        "research_decision_output_runtime_ready": all(
            validation["artifact_schema_valid"] is True for validation in validations
        ),
        "scenario_count": comparison_run["scenario_count"],
        "research_decision_output_count": len(artifacts),
        "output_mode_research_only_count": output_mode_research_only_count,
        "predicted_label_output_count": predicted_label_output_count,
        "label_used_by_runtime_count": label_used_by_runtime_count,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_scope": contract["metric_policy"][
            "metric_computation_scope"
        ],
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
        "research_decision_outputs": artifacts,
        "artifact_validations": validations,
        "comparison_run": comparison_run,
        "coverage_run": coverage_run,
        "contract": contract,
    }


def summarize_historical_research_decision_outputs() -> dict[str, Any]:
    contract = load_historical_research_decision_output_artifact_contract()
    run = build_historical_research_decision_outputs()
    gates = contract["readiness_gates"]
    ready = (
        run["research_decision_output_artifact_contract_ready"] is True
        and run["research_decision_output_runtime_ready"] is True
        and run["scenario_count"] == contract["scenario_count_required"]
        and run["research_decision_output_count"] == run["scenario_count"]
        and run["output_mode_research_only_count"] == run["scenario_count"]
        and run["predicted_label_output_count"] == 0
        and run["label_used_by_runtime_count"] == 0
        and run["historical_accuracy_metric_count"] == 0
        and run["economic_performance_metric_count"] == 0
        and run["metric_computation_scope"] == "none"
        and run["backtest_execution_enabled"] is False
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and run["prohibited_artifact_field_count"] == 0
        and all(
            value is True
            for key, value in gates.items()
            if key != "prohibited_artifact_field_count_required"
        )
        and gates["prohibited_artifact_field_count_required"] == 0
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "25",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "research_decision_output_artifact_contract_ready": ready,
        "research_decision_output_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
                "scenario_count",
                "research_decision_output_count",
                "output_mode_research_only_count",
                "predicted_label_output_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_scope",
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


def validate_historical_research_decision_output_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_research_decision_output_artifact_contract()
    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    output_keys = set(artifact)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    predicted_label_paths = _find_forbidden_output_paths(
        artifact,
        {"predicted_label"},
    )
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and artifact.get("output_mode") == contract["output_mode_required"]
        and artifact.get("label_used_by_runtime") is False
        and artifact.get("trust_metadata", {}).get("label_used_by_runtime") is False
        and artifact.get("trust_metadata", {}).get("metric_computation_scope")
        == "none"
        and artifact.get("trust_metadata", {}).get("provenance_complete") is True
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "predicted_label_output_count": len(predicted_label_paths),
        "forbidden_artifact_paths": forbidden_paths,
    }


def write_historical_research_decision_outputs(
    artifact_run: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_dir(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": artifact_run["run_id"],
        "phase": artifact_run["phase"],
        "research_decision_outputs": artifact_run["research_decision_outputs"],
        "research_decision_output_count": artifact_run[
            "research_decision_output_count"
        ],
        "metric_computation_scope": artifact_run["metric_computation_scope"],
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "predicted_label_output_count": artifact_run[
            "predicted_label_output_count"
        ],
        "candidate_phase_emitted": artifact_run["candidate_phase_emitted"],
        "current_phase_emitted": artifact_run["current_phase_emitted"],
        "allowed_uses": [
            "research_historical_validation_artifact_review",
            "abstention_and_blocker_diagnostics",
            "offline_label_join_preparation_without_label_values",
        ],
        "prohibited_uses": [
            "predicted_label_output",
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
    }
    output_file = output_path / "research_decision_outputs.json"
    output_file.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output_dir": str(output_path),
        "research_decision_output_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_file)],
    }


def _build_research_output_artifact(
    *,
    comparison_artifact: dict[str, Any],
    contract: dict[str, Any],
    coverage_metric_artifact_id: str,
) -> dict[str, Any]:
    runtime_summary = comparison_artifact["runtime_result_summary"]
    scenario_id = comparison_artifact["scenario_id"]
    as_of = comparison_artifact["as_of"]
    return {
        "research_output_id": f"phase25_research_output:{scenario_id}:{as_of}",
        "scenario_id": scenario_id,
        "as_of": as_of,
        "data_mode": comparison_artifact["data_mode"],
        "output_mode": contract["output_mode_required"],
        "source_runtime_artifact_id": comparison_artifact["dry_run_result_id"],
        "source_comparison_artifact_id": comparison_artifact["artifact_id"],
        "source_coverage_metric_artifact_id": coverage_metric_artifact_id,
        "decision_state": runtime_summary["readiness_label"],
        "abstention_state": comparison_artifact["abstention_status"],
        "blocked_reason_codes": comparison_artifact["blocked_reason_codes"],
        "label_used_by_runtime": False,
        "allowed_uses": [
            "research_historical_validation_output_review",
            "abstention_and_blocker_diagnostics",
            "lineage_and_provenance_review",
        ],
        "prohibited_uses": [
            "predicted_label_output",
            "historical_accuracy_claim",
            "confusion_matrix_generation",
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "trust_metadata": {
            "artifact_schema_version": contract["artifact_schema_version"],
            "parent_freeze_id": contract[
                "parent_research_decision_output_contract_freeze_id"
            ],
            "source_runtime_artifact_id": comparison_artifact["dry_run_result_id"],
            "source_comparison_artifact_id": comparison_artifact["artifact_id"],
            "source_coverage_metric_artifact_id": coverage_metric_artifact_id,
            "label_provenance_verified": comparison_artifact[
                "label_provenance_verified"
            ],
            "label_used_by_runtime": False,
            "metric_computation_scope": "none",
            "candidate_phase_emitted": runtime_summary["candidate_phase_emitted"],
            "current_phase_emitted": runtime_summary["current_phase_emitted"],
            "provenance_complete": True,
        },
    }


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 25 research decision output must be under /tmp: {output_dir}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
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
