"""Phase 29 research-only historical accuracy metric computation.

The runtime consumes Phase 28 predicted-label comparison artifacts and the
Phase 21 preregistered metric registry only. It does not re-run the decision
runtime, read labels back into model logic, compute economic performance, or
produce candidate/current phase outputs.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_metric_preregistration import (
    DEFAULT_HISTORICAL_METRIC_REGISTRY_PATH,
    load_historical_metric_registry,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
    load_predicted_label_comparison_artifact_contract,
    validate_predicted_label_comparison_artifact,
)


DEFAULT_HISTORICAL_ACCURACY_METRIC_ARTIFACT_CONTRACT_PATH = Path(
    "specs/common/historical_accuracy_metric_artifact_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase29_historical_accuracy_metrics_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


def load_historical_accuracy_metric_artifact_contract(
    path: str | Path = DEFAULT_HISTORICAL_ACCURACY_METRIC_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical accuracy metric artifact contract must map")
    contract = payload.get("historical_accuracy_metric_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_accuracy_metric_artifact_contract must be a mapping"
        )
    return contract


def compute_historical_accuracy_metrics(
    *,
    comparison_artifact_run: dict[str, Any] | None = None,
    metric_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = load_historical_accuracy_metric_artifact_contract()
    comparison_run = comparison_artifact_run or build_predicted_label_comparison_artifacts()
    registry = metric_registry or load_historical_metric_registry()
    registry_hash = _metric_registry_hash()
    comparison_artifacts = list(
        comparison_run.get("predicted_label_comparison_artifacts", [])
    )
    scenario_count = int(comparison_run.get("scenario_count", 0))
    artifact_analysis = _analyze_comparison_artifacts(
        comparison_artifacts=comparison_artifacts,
        scenario_count=scenario_count,
        comparison_run=comparison_run,
    )
    metric_results = _build_metric_results(
        registry=registry,
        scenario_count=scenario_count,
        artifact_count=len(comparison_artifacts),
        status_counts=artifact_analysis["status_counts"],
        missing_comparison_artifact_count=artifact_analysis[
            "missing_comparison_artifact_count"
        ],
    )
    artifact = _build_metric_artifact(
        contract=contract,
        comparison_run=comparison_run,
        registry=registry,
        registry_hash=registry_hash,
        metric_results=metric_results,
        analysis=artifact_analysis,
    )
    artifact_validation = validate_historical_accuracy_metric_artifact(
        artifact,
        contract=contract,
        registry_hash=registry_hash,
    )
    contract_validation = validate_historical_accuracy_metric_artifact_contract(
        contract
    )
    historical_accuracy_metric_count = len(metric_results)
    return {
        "phase": "29",
        "run_id": RUN_ID,
        "historical_accuracy_metric_artifact_contract_ready": (
            contract_validation["contract_schema_valid"]
        ),
        "historical_accuracy_metric_runtime_ready": artifact_validation[
            "artifact_schema_valid"
        ],
        "preregistered_metric_registry_used": _registry_matches_contract(
            registry,
            contract,
        ),
        "scenario_count": scenario_count,
        "label_comparison_artifact_count": len(comparison_artifacts),
        "comparable_scenario_count": artifact_analysis[
            "comparable_scenario_count"
        ],
        "non_comparable_scenario_count": artifact_analysis[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": artifact_analysis["abstained_scenario_count"],
        "blocked_scenario_count": artifact_analysis["blocked_scenario_count"],
        "taxonomy_mismatch_count": artifact_analysis["taxonomy_mismatch_count"],
        "historical_accuracy_metric_count": historical_accuracy_metric_count,
        "computed_metric_count": sum(
            result["result_status"] == "computed" for result in metric_results
        ),
        "skipped_metric_count": sum(
            result["result_status"] != "computed" for result in metric_results
        ),
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": True,
        "metric_computation_scope": contract["metric_scope"],
        "backtest_execution_enabled": False,
        "label_used_by_runtime_count": 0,
        "mapping_rule_modified_after_comparison_count": int(
            contract["disabled_runtime_guards"][
                "mapping_rule_modified_after_comparison"
            ]
        ),
        "threshold_modified_after_metric_count": int(
            contract["disabled_runtime_guards"]["threshold_modified_after_metric"]
        ),
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
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_metric_field_count": artifact_validation[
            "prohibited_metric_field_count"
        ],
        "production_behavior_change_count": contract["output_restrictions"][
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": contract["output_restrictions"][
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": contract["output_restrictions"][
            "real_registry_write_attempt_count"
        ],
        "forbidden_repo_output_count": 0,
        "missing_comparison_artifact_count": artifact_analysis[
            "missing_comparison_artifact_count"
        ],
        "malformed_comparison_artifact_count": artifact_analysis[
            "malformed_comparison_artifact_count"
        ],
        "forbidden_comparison_artifact_field_count": artifact_analysis[
            "forbidden_comparison_artifact_field_count"
        ],
        "duplicate_scenario_artifact_count": artifact_analysis[
            "duplicate_scenario_artifact_count"
        ],
        "registry_hash_mismatch_count": int(
            artifact["source_metric_registry_hash"] != registry_hash
        ),
        "accuracy_metric_artifact": artifact,
        "metric_results": metric_results,
        "artifact_validation": artifact_validation,
        "contract_validation": contract_validation,
        "comparison_artifact_run": comparison_run,
        "metric_registry": registry,
        "contract": contract,
    }


def summarize_historical_accuracy_metrics() -> dict[str, Any]:
    contract = load_historical_accuracy_metric_artifact_contract()
    run = compute_historical_accuracy_metrics()
    gates = contract["readiness_gates"]
    ready = (
        run["historical_accuracy_metric_artifact_contract_ready"] is True
        and run["historical_accuracy_metric_runtime_ready"] is True
        and run["preregistered_metric_registry_used"] is True
        and run["scenario_count"] == gates["scenario_count_required"]
        and run["label_comparison_artifact_count"]
        == gates["label_comparison_artifact_count_required"]
        and run["historical_accuracy_metric_count"]
        >= gates["historical_accuracy_metric_count_minimum"]
        and run["economic_performance_metric_count"]
        == gates["economic_performance_metric_count_required"]
        and run["metric_computation_enabled"] is True
        and run["metric_computation_scope"] == "historical_accuracy_only"
        and run["backtest_execution_enabled"] is False
        and run["label_used_by_runtime_count"] == 0
        and run["mapping_rule_modified_after_comparison_count"] == 0
        and run["threshold_modified_after_metric_count"] == 0
        and run["candidate_phase_emitted"] is False
        and run["current_phase_emitted"] is False
        and run["prohibited_metric_field_count"]
        == gates["prohibited_metric_field_count_required"]
        and run["registry_hash_mismatch_count"] == 0
        and all(
            value is False
            for key, value in contract["disabled_runtime_guards"].items()
            if key != "metric_computation_enabled"
        )
    )
    return {
        "phase": "29",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_accuracy_metric_artifact_contract_ready": ready,
        "historical_accuracy_metric_runtime_ready": ready,
        **{
            key: run[key]
            for key in (
                "preregistered_metric_registry_used",
                "scenario_count",
                "label_comparison_artifact_count",
                "comparable_scenario_count",
                "non_comparable_scenario_count",
                "abstained_scenario_count",
                "blocked_scenario_count",
                "taxonomy_mismatch_count",
                "historical_accuracy_metric_count",
                "computed_metric_count",
                "skipped_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "metric_computation_scope",
                "backtest_execution_enabled",
                "label_used_by_runtime_count",
                "mapping_rule_modified_after_comparison_count",
                "threshold_modified_after_metric_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "prohibited_metric_field_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "missing_comparison_artifact_count",
                "malformed_comparison_artifact_count",
                "forbidden_comparison_artifact_field_count",
                "duplicate_scenario_artifact_count",
                "registry_hash_mismatch_count",
            )
        },
        "metric_artifact": run["accuracy_metric_artifact"],
        "metric_results": run["metric_results"],
        "metric_run": run,
    }


def validate_historical_accuracy_metric_artifact_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_predicted_label_comparison_freeze_id",
        "source_comparison_artifact_contract_id",
        "source_metric_registry_id",
        "artifact_version",
        "metric_scope",
        "metric_computation_mode",
        "allowed_inputs",
        "prohibited_inputs",
        "allowed_artifact_fields",
        "forbidden_artifact_fields",
        "metric_execution_policy",
        "output_policy",
        "output_restrictions",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    execution = contract.get("metric_execution_policy", {})
    output = contract.get("output_policy", {})
    restrictions = contract.get("output_restrictions", {})
    disabled = contract.get("disabled_runtime_guards", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "historical_accuracy_metrics_allowed_research_only_no_performance"
        and contract.get("metric_scope") == "historical_accuracy_only"
        and execution.get("preregistered_metric_registry_required") is True
        and execution.get("comparison_artifacts_are_only_runtime_input") is True
        and execution.get("historical_labels_may_enter_runtime") is False
        and execution.get("raw_runtime_reexecution_allowed") is False
        and execution.get("mapping_rule_mutation_allowed") is False
        and execution.get("threshold_or_weight_mutation_allowed") is False
        and execution.get("economic_performance_metric_allowed") is False
        and execution.get("portfolio_backtest_allowed") is False
        and output.get("explicit_output_path_required") is True
        and output.get("tmp_output_allowed") is True
        and output.get("committed_artifact_allowed") is False
        and output.get("data_backtests_write_allowed") is False
        and output.get("data_prospective_write_allowed") is False
        and output.get("public_output_allowed") is False
        and restrictions.get("metric_computation_enabled") is True
        and restrictions.get("metric_computation_scope") == "historical_accuracy_only"
        and restrictions.get("economic_performance_metric_count") == 0
        and restrictions.get("backtest_execution_enabled") is False
        and restrictions.get("label_used_by_runtime_count") == 0
        and restrictions.get("candidate_phase_emitted") is False
        and restrictions.get("current_phase_emitted") is False
        and all(value is False for value in disabled.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_historical_accuracy_metric_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
    registry_hash: str | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_accuracy_metric_artifact_contract()
    registry_hash = registry_hash or _metric_registry_hash()
    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    output_keys = set(artifact)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    provenance = artifact.get("provenance", {})
    registry_hash_verified = artifact.get("source_metric_registry_hash") == registry_hash
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and registry_hash_verified
        and artifact.get("metric_scope") == "historical_accuracy_only"
        and artifact.get("metric_computation_mode")
        == "preregistered_registry_only"
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and provenance.get("label_used_by_runtime") is False
        and provenance.get("mapping_rule_modified_after_comparison") is False
        and provenance.get("threshold_modified_after_metric") is False
        and provenance.get("economic_performance_metric_count") == 0
        and provenance.get("backtest_execution_enabled") is False
        and provenance.get("candidate_phase_emitted") is False
        and provenance.get("current_phase_emitted") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_metric_field_count": len(forbidden_paths),
        "registry_hash_verified": registry_hash_verified,
        "forbidden_metric_paths": forbidden_paths,
    }


def write_historical_accuracy_metrics(
    metric_run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": metric_run["run_id"],
        "phase": metric_run["phase"],
        "accuracy_metric_artifact": metric_run["accuracy_metric_artifact"],
        "scenario_count": metric_run["scenario_count"],
        "label_comparison_artifact_count": metric_run[
            "label_comparison_artifact_count"
        ],
        "historical_accuracy_metric_count": metric_run[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": True,
        "metric_computation_scope": metric_run["metric_computation_scope"],
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "allowed_uses": [
            "research_only_historical_metric_review",
            "metric_prerequisite_gap_review",
            "validation_artifact_lineage_review",
        ],
        "prohibited_uses": [
            "economic_validation_claim",
            "portfolio_performance_claim",
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
        "historical_accuracy_metric_artifact_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _build_metric_artifact(
    *,
    contract: dict[str, Any],
    comparison_run: dict[str, Any],
    registry: dict[str, Any],
    registry_hash: str,
    metric_results: list[dict[str, Any]],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_version": contract["artifact_version"],
        "metric_run_id": RUN_ID,
        "source_comparison_artifact_set_id": comparison_run["run_id"],
        "source_metric_registry_id": registry["registry_id"],
        "source_metric_registry_hash": registry_hash,
        "scenario_count": comparison_run["scenario_count"],
        "label_comparison_artifact_count": len(
            comparison_run["predicted_label_comparison_artifacts"]
        ),
        "comparable_scenario_count": analysis["comparable_scenario_count"],
        "non_comparable_scenario_count": analysis[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": analysis["abstained_scenario_count"],
        "blocked_scenario_count": analysis["blocked_scenario_count"],
        "taxonomy_mismatch_count": analysis["taxonomy_mismatch_count"],
        "preregistered_metric_results": metric_results,
        "metric_scope": contract["metric_scope"],
        "metric_computation_mode": contract["metric_computation_mode"],
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "economic_validation_claim",
            "portfolio_performance_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "provenance": {
            "source_comparison_artifact_contract_id": contract[
                "source_comparison_artifact_contract_id"
            ],
            "source_metric_registry_id": registry["registry_id"],
            "source_metric_registry_hash": registry_hash,
            "comparison_artifacts_are_only_runtime_input": True,
            "preregistered_metric_registry_used": True,
            "label_used_by_runtime": False,
            "mapping_rule_modified_after_comparison": False,
            "threshold_modified_after_metric": False,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
            "production_behavior_change_count": 0,
        },
    }


def _build_metric_results(
    *,
    registry: dict[str, Any],
    scenario_count: int,
    artifact_count: int,
    status_counts: Counter[str],
    missing_comparison_artifact_count: int,
) -> list[dict[str, Any]]:
    results = []
    for metric in registry["metrics"]:
        metric_id = metric["metric_id"]
        if metric_id == "label_join_coverage_rate":
            result = _computed_metric_result(
                metric=metric,
                numerator=artifact_count,
                denominator=scenario_count,
                value=_rate(artifact_count, scenario_count),
                notes=["comparison_artifact_materialized_for_each_scenario"],
            )
        elif metric_id == "label_match_rate":
            result = {
                "metric_id": metric_id,
                "result_status": "skipped_prerequisite_unavailable",
                "value": None,
                "numerator": None,
                "denominator": status_counts["comparable"],
                "denominator_definition": metric["denominator_definition"],
                "abstention_treatment": metric["abstention_treatment"],
                "blocked_treatment": metric["blocked_treatment"],
                "missing_treatment": metric["missing_treatment"],
                "skip_reason": (
                    "phase28_reference_label_values_are_provenance_only"
                ),
                "prohibited_uses": metric["prohibited_uses"],
            }
        elif metric_id == "abstention_share":
            result = _computed_metric_result(
                metric=metric,
                numerator=status_counts["abstained"],
                denominator=artifact_count,
                value=_rate(status_counts["abstained"], artifact_count),
                notes=["abstained_comparison_status_counted_in_numerator"],
            )
        elif metric_id == "blocked_result_share":
            result = _computed_metric_result(
                metric=metric,
                numerator=status_counts["blocked"],
                denominator=artifact_count,
                value=_rate(status_counts["blocked"], artifact_count),
                notes=["blocked_comparison_status_counted_in_numerator"],
            )
        elif metric_id == "missing_result_share":
            result = _computed_metric_result(
                metric=metric,
                numerator=missing_comparison_artifact_count,
                denominator=scenario_count,
                value=_rate(missing_comparison_artifact_count, scenario_count),
                notes=["missing_comparison_artifacts_counted_in_numerator"],
            )
        else:
            result = {
                "metric_id": metric_id,
                "result_status": "skipped_unknown_metric_id",
                "value": None,
                "numerator": None,
                "denominator": None,
                "denominator_definition": metric.get("denominator_definition"),
                "abstention_treatment": metric.get("abstention_treatment"),
                "blocked_treatment": metric.get("blocked_treatment"),
                "missing_treatment": metric.get("missing_treatment"),
                "skip_reason": "metric_id_not_supported_by_phase29_runtime",
                "prohibited_uses": metric.get("prohibited_uses", []),
            }
        results.append(result)
    return results


def _computed_metric_result(
    *,
    metric: dict[str, Any],
    numerator: int,
    denominator: int,
    value: float,
    notes: list[str],
) -> dict[str, Any]:
    return {
        "metric_id": metric["metric_id"],
        "result_status": "computed",
        "value": value,
        "numerator": numerator,
        "denominator": denominator,
        "denominator_definition": metric["denominator_definition"],
        "numerator_definition": metric["numerator_definition"],
        "abstention_treatment": metric["abstention_treatment"],
        "blocked_treatment": metric["blocked_treatment"],
        "missing_treatment": metric["missing_treatment"],
        "notes": notes,
        "prohibited_uses": metric["prohibited_uses"],
    }


def _analyze_comparison_artifacts(
    *,
    comparison_artifacts: list[dict[str, Any]],
    scenario_count: int,
    comparison_run: dict[str, Any],
) -> dict[str, Any]:
    comparison_contract = load_predicted_label_comparison_artifact_contract()
    mapping_hash = comparison_run.get("mapping_contract_hash")
    validations = [
        validate_predicted_label_comparison_artifact(
            artifact,
            contract=comparison_contract,
            mapping_contract_hash=mapping_hash,
        )
        for artifact in comparison_artifacts
    ]
    scenario_ids = [
        artifact.get("scenario_id")
        for artifact in comparison_artifacts
        if artifact.get("scenario_id") is not None
    ]
    duplicate_scenario_artifact_count = len(scenario_ids) - len(set(scenario_ids))
    missing_comparison_artifact_count = max(0, scenario_count - len(set(scenario_ids)))
    status_counts: Counter[str] = Counter(
        artifact.get("comparison_status", "malformed")
        for artifact in comparison_artifacts
    )
    non_comparable_count = status_counts["not_comparable"]
    return {
        "status_counts": status_counts,
        "comparable_scenario_count": status_counts["comparable"],
        "non_comparable_scenario_count": non_comparable_count,
        "abstained_scenario_count": status_counts["abstained"],
        "blocked_scenario_count": status_counts["blocked"],
        "taxonomy_mismatch_count": status_counts["taxonomy_mismatch"],
        "missing_comparison_artifact_count": missing_comparison_artifact_count,
        "malformed_comparison_artifact_count": sum(
            validation["artifact_schema_valid"] is False
            for validation in validations
        ),
        "forbidden_comparison_artifact_field_count": sum(
            validation["prohibited_artifact_field_count"]
            for validation in validations
        ),
        "duplicate_scenario_artifact_count": duplicate_scenario_artifact_count,
    }


def _registry_matches_contract(
    registry: dict[str, Any],
    contract: dict[str, Any],
) -> bool:
    metric_ids = {metric["metric_id"] for metric in registry.get("metrics", [])}
    return (
        registry.get("registry_id") == contract["source_metric_registry_id"]
        and len(metric_ids) == len(registry.get("metrics", []))
        and bool(metric_ids)
    )


def _metric_registry_hash() -> str:
    return hashlib.sha256(DEFAULT_HISTORICAL_METRIC_REGISTRY_PATH.read_bytes()).hexdigest()


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 29 historical accuracy metrics output must be under /tmp: {output}"
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
