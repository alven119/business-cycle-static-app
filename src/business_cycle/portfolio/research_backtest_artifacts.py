"""Research-only backtest artifact generation for Phase80."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)
from business_cycle.portfolio.metric_registry import (
    load_backtest_metric_formula_registry,
)
from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)
from business_cycle.validation.historical_replay_runner import (
    summarize_historical_replay_runner_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/portfolio/research_backtest_artifact_contract.yaml"
)
DEFAULT_METRIC_REGISTRY_PATH = ROOT / "specs/portfolio/backtest_metric_formula_registry.yaml"

PROHIBITED_BACKTEST_ARTIFACT_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "phase_probability",
    "expected_label",
    "actual_label",
    "correct",
    "incorrect",
    "historical_accuracy",
    "confusion_matrix",
    "precision",
    "recall",
    "hit_rate",
    "portfolio_return",
    "CAGR",
    "drawdown",
    "Sharpe",
    "current_allocation",
    "current_allocation_recommendation",
    "target_weight",
    "target_weights",
    "buy_signal",
    "sell_signal",
    "trade_action",
}

DISABLED_GUARD_KEYS = (
    "formal_decision_runtime_execution_enabled",
    "historical_validation_execution_enabled",
    "label_comparison_enabled",
    "metric_computation_enabled",
    "backtest_execution_enabled",
    "portfolio_policy_replay_execution_enabled",
    "current_allocation_recommendation_enabled",
    "live_allocation_enabled",
    "trade_signal_enabled",
    "candidate_phase_emission_enabled",
    "current_phase_emission_enabled",
    "production_integration_enabled",
    "public_output_enabled",
)


class ResearchBacktestArtifactContractError(ValueError):
    """Raised when the Phase80 artifact contract or output path is invalid."""


def load_research_backtest_artifact_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load and validate the Phase80 research-only backtest artifact contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ResearchBacktestArtifactContractError("contract YAML must be a mapping")
    contract = payload.get("research_backtest_artifact_contract")
    if not isinstance(contract, dict):
        raise ResearchBacktestArtifactContractError(
            "YAML must contain research_backtest_artifact_contract",
        )
    validate_research_backtest_artifact_contract(contract)
    return contract


def validate_research_backtest_artifact_contract(contract: dict[str, Any]) -> None:
    """Validate output, metric, disabled-runtime, and field boundaries."""

    if int(contract.get("phase_id")) != 80:
        raise ResearchBacktestArtifactContractError("phase_id must be 80")
    if (
        contract.get("status")
        != "active_research_only_backtest_artifact_generation_no_metrics"
    ):
        raise ResearchBacktestArtifactContractError("unexpected Phase80 status")
    _validate_artifact_contract(contract["artifact_contract"])
    _validate_output_policy(contract["output_policy"])
    _validate_metric_policy(contract["metric_policy"])
    _validate_disabled_guards(contract["disabled_runtime_guards"])


def build_research_backtest_artifact_bundle(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build research-only backtest artifacts from replay rows without execution."""

    contract = load_research_backtest_artifact_contract(path)
    replay = summarize_historical_replay_runner_preview()
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    metric_registry = load_backtest_metric_formula_registry(DEFAULT_METRIC_REGISTRY_PATH)
    metric_refs = _metric_formula_refs(metric_registry.metric_definitions)
    source_contract_hashes = _source_contract_hashes(contract)
    artifacts = [
        _build_artifact(
            replay_row=row,
            contract=contract,
            schedule=schedule,
            kernel=kernel,
            metric_refs=metric_refs,
            source_contract_hashes=source_contract_hashes,
        )
        for row in replay["replay_rows"]
    ]
    return {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "80",
        "phase_id": 80,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "scenario_count": replay["scenario_count"],
        "source_replay_row_count": replay["replay_row_count"],
        "research_backtest_artifacts": artifacts,
        "source_contract_hashes": source_contract_hashes,
        "metric_formula_reference_family_count": len(metric_refs),
        "metric_value_count": 0,
        "risk_metric_value_count": 0,
        "allowed_uses": contract["output_policy"]["allowed_uses"],
        "prohibited_uses": contract["output_policy"]["prohibited_uses"],
        "trust_metadata": {
            "source_contract": contract["contract_id"],
            "historical_replay_runner_ready": replay["historical_replay_runner_ready"],
            "policy_replay_schedule_contract_ready": schedule[
                "portfolio_policy_replay_schedule_contract_ready"
            ],
            "cash_flow_kernel_contract_ready": kernel[
                "cash_flow_aware_backtest_kernel_contract_ready"
            ],
            "metric_formula_values_computed": False,
            "historical_accuracy_metrics_computed": False,
            "economic_performance_metrics_computed": False,
            "backtest_execution_enabled": False,
            "generated_output_under_tmp_only": contract["output_policy"][
                "generated_output_under_tmp_only"
            ],
        },
    }


def summarize_research_backtest_artifacts(
    path: str | Path = DEFAULT_CONTRACT_PATH,
    *,
    bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return compact Phase80 hard-gate fields for tests, CLI, and closure."""

    contract = load_research_backtest_artifact_contract(path)
    replay = summarize_historical_replay_runner_preview()
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    bundle = bundle or build_research_backtest_artifact_bundle(path)
    artifacts = bundle["research_backtest_artifacts"]
    summary: dict[str, Any] = {
        "phase": "80",
        "phase_id": 80,
        "research_backtest_artifact_contract_ready": True,
        "research_backtest_artifact_generator_ready": True,
        "contract_id": contract["contract_id"],
        "historical_replay_runner_ready": replay["historical_replay_runner_ready"],
        "policy_replay_schedule_contract_ready": schedule[
            "portfolio_policy_replay_schedule_contract_ready"
        ],
        "cash_flow_kernel_contract_ready": kernel[
            "cash_flow_aware_backtest_kernel_contract_ready"
        ],
        "scenario_count": bundle["scenario_count"],
        "source_replay_row_count": bundle["source_replay_row_count"],
        "research_backtest_artifact_count": len(artifacts),
        "artifact_with_policy_schedule_ref_count": sum(
            bool(row.get("source_policy_schedule_contract_id")) for row in artifacts
        ),
        "artifact_with_cash_flow_kernel_ref_count": sum(
            bool(row.get("source_cash_flow_kernel_contract_id")) for row in artifacts
        ),
        "artifact_with_metric_formula_refs_count": sum(
            bool(row.get("metric_formula_refs")) for row in artifacts
        ),
        "artifact_with_input_hash_count": sum(
            bool(row.get("input_hash")) for row in artifacts
        ),
        "artifact_with_provenance_count": sum(
            bool(row.get("provenance")) for row in artifacts
        ),
        "metric_formula_reference_family_count": bundle[
            "metric_formula_reference_family_count"
        ],
        "metric_value_count": bundle["metric_value_count"],
        "risk_metric_value_count": bundle["risk_metric_value_count"],
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": False,
        "backtest_execution_count": 0,
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "live_allocation_output_count": 0,
        "prohibited_output_field_count": _recursive_key_count(
            artifacts,
            PROHIBITED_BACKTEST_ARTIFACT_FIELDS,
        ),
        "repository_output_count": 0,
        "public_output_count": 0,
        "generated_output_under_tmp_only": contract["output_policy"][
            "generated_output_under_tmp_only"
        ],
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_research_backtest_artifacts_ready"
        ),
        "portfolio_policy_research_alignment": (
            "research_backtest_artifacts_generated_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "research_backtest_artifacts_generated_no_metric_values"
        ),
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 81,
        "phase80_closure_status": (
            "closed_research_backtest_artifacts_generated_no_public_output_or_metrics"
        ),
    }
    summary["result"] = "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    summary["research_backtest_artifact_generator_ready"] = summary["result"] == "passed"
    return summary


def write_research_backtest_artifacts(
    output: str | Path,
    *,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write a Phase80 research-only artifact bundle to an explicit /tmp path."""

    output_path = Path(output)
    if not output_path.is_absolute() or not output_path.as_posix().startswith("/tmp/"):
        raise ResearchBacktestArtifactContractError(
            "output must be an absolute /tmp path",
        )
    bundle = build_research_backtest_artifact_bundle(path)
    summary = summarize_research_backtest_artifacts(path, bundle=bundle)
    payload = {**summary, "research_backtest_artifacts": bundle["research_backtest_artifacts"]}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return payload


def _build_artifact(
    *,
    replay_row: dict[str, Any],
    contract: dict[str, Any],
    schedule: dict[str, Any],
    kernel: dict[str, Any],
    metric_refs: list[dict[str, Any]],
    source_contract_hashes: dict[str, str],
) -> dict[str, Any]:
    payload_for_hash = {
        "replay_row": replay_row,
        "policy_schedule_contract": schedule["contract_id"],
        "cash_flow_kernel_contract": kernel["contract_id"],
        "metric_formula_ids": [row["metric_id"] for row in metric_refs],
        "source_contract_hashes": source_contract_hashes,
    }
    return {
        "artifact_id": f"phase80::{replay_row['replay_row_id']}",
        "artifact_version": contract["artifact_contract"]["artifact_version"],
        "scenario_id": replay_row["scenario_id"],
        "data_mode": replay_row["data_mode"],
        "validation_window_start": replay_row["validation_window_start"],
        "validation_window_end": replay_row["validation_window_end"],
        "output_mode": contract["output_policy"]["output_mode"],
        "source_replay_row_id": replay_row["replay_row_id"],
        "source_replay_runner_contract_id": replay_row["trust_metadata"][
            "source_contract"
        ],
        "source_policy_schedule_contract_id": schedule["contract_id"],
        "source_cash_flow_kernel_contract_id": kernel["contract_id"],
        "source_metric_formula_registry_id": "backtest_metric_formula_registry_v1",
        "policy_replay_reference_status": "referenced_no_execution",
        "cash_flow_kernel_reference_status": "referenced_no_execution",
        "metric_formula_refs": metric_refs,
        "metric_value_count": 0,
        "risk_metric_value_count": 0,
        "input_hash": _hash_payload(payload_for_hash),
        "caveats_zh": [
            "此 artifact 僅供 historical replay/backtest research surface 使用。",
            "本階段未計算任何績效、風險、準確率或 portfolio result 值。",
            "不得作為目前配置、交易行動或 production phase decision。",
        ],
        "allowed_uses": contract["output_policy"]["allowed_uses"],
        "prohibited_uses": contract["output_policy"]["prohibited_uses"],
        "trust_metadata": {
            "replay_status": replay_row["replay_status"],
            "input_readiness_status": replay_row["input_readiness_status"],
            "abstention_expected": replay_row["abstention_expected"],
            "labels_read_by_runtime": False,
            "metric_values_computed": False,
            "backtest_execution_enabled": False,
            "current_allocation_recommendation_enabled": False,
        },
        "provenance": {
            "source_contract_hashes": source_contract_hashes,
            "source_replay_row_blocked_reason_codes": replay_row[
                "blocked_reason_codes"
            ],
            "metric_policy": "formula_references_only_no_values",
        },
        "research_only": True,
    }


def _metric_formula_refs(
    definitions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "metric_id": metric_id,
            "category": str(definition["category"]),
            "value_computed": False,
        }
        for metric_id, definition in sorted(definitions.items())
    ]


def _source_contract_hashes(contract: dict[str, Any]) -> dict[str, str]:
    return {
        key: _sha256_file(ROOT / value)
        for key, value in sorted(contract["dependencies"].items())
        if key
        in {
            "historical_replay_runner_contract",
            "portfolio_policy_replay_schedule_contract",
            "cash_flow_kernel_contract",
            "metric_formula_registry",
        }
    }


def _validate_artifact_contract(artifact_contract: dict[str, Any]) -> None:
    required_fields = artifact_contract.get("required_fields")
    if not isinstance(required_fields, list) or not required_fields:
        raise ResearchBacktestArtifactContractError(
            "artifact_contract.required_fields must exist",
        )
    prohibited = set(artifact_contract.get("prohibited_fields") or [])
    missing = PROHIBITED_BACKTEST_ARTIFACT_FIELDS - prohibited
    if missing:
        raise ResearchBacktestArtifactContractError(
            f"artifact_contract.prohibited_fields missing: {', '.join(sorted(missing))}",
        )


def _validate_output_policy(output_policy: dict[str, Any]) -> None:
    if output_policy.get("output_mode") != "research_only_backtest_artifact":
        raise ResearchBacktestArtifactContractError("unexpected output mode")
    if output_policy.get("generated_output_under_tmp_only") is not True:
        raise ResearchBacktestArtifactContractError(
            "generated_output_under_tmp_only must be true",
        )
    for key in (
        "repository_output_allowed",
        "public_output_allowed",
        "backtest_execution_allowed",
        "metric_computation_allowed",
        "economic_performance_metric_allowed",
        "historical_accuracy_metric_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
        "production_integration_allowed",
    ):
        if bool(output_policy.get(key)):
            raise ResearchBacktestArtifactContractError(f"output_policy.{key} must be false")


def _validate_metric_policy(metric_policy: dict[str, Any]) -> None:
    if metric_policy.get("metric_formula_references_allowed") is not True:
        raise ResearchBacktestArtifactContractError(
            "metric_formula_references_allowed must be true",
        )
    for key in (
        "metric_value_computation_allowed",
        "risk_metric_value_computation_allowed",
        "economic_performance_metric_computation_allowed",
        "historical_accuracy_metric_computation_allowed",
    ):
        if bool(metric_policy.get(key)):
            raise ResearchBacktestArtifactContractError(f"metric_policy.{key} must be false")


def _validate_disabled_guards(guards: dict[str, Any]) -> None:
    for key in DISABLED_GUARD_KEYS:
        if bool(guards.get(key)):
            raise ResearchBacktestArtifactContractError(f"{key} must be false")


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(int(key in prohibited) + _recursive_key_count(item, prohibited) for key, item in value.items())
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0


def _hash_payload(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8"),
    ).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())
