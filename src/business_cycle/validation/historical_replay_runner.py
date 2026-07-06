"""Phase79 historical replay runner preview with strict/revised separation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)
from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)
from business_cycle.render.transition_timing_replay_preview import (
    summarize_transition_timing_replay_preview,
)
from business_cycle.validation.historical_validation_input_readiness import (
    build_scenario_input_readiness_outputs,
)
from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/historical_replay_runner_contract.yaml"

STRICT_DATA_MODE = "vintage_as_of"
REVISED_DATA_MODE = "revised_declared_comparison_only"

PROHIBITED_REPLAY_OUTPUT_FIELDS = {
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
    "candidate_selection_enabled",
    "candidate_phase_emission_enabled",
    "current_phase_emission_enabled",
    "production_integration_enabled",
    "public_output_enabled",
    "portfolio_policy_replay_execution_enabled",
)


class HistoricalReplayRunnerContractError(ValueError):
    """Raised when the Phase79 replay runner contract is invalid."""


def load_historical_replay_runner_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load and validate the Phase79 historical replay runner contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise HistoricalReplayRunnerContractError("contract YAML must be a mapping")
    contract = payload.get("historical_replay_runner_contract")
    if not isinstance(contract, dict):
        raise HistoricalReplayRunnerContractError(
            "YAML must contain historical_replay_runner_contract",
        )
    validate_historical_replay_runner_contract(contract)
    return contract


def validate_historical_replay_runner_contract(contract: dict[str, Any]) -> None:
    """Validate data-mode, output, and disabled-runtime boundaries."""

    if int(contract.get("phase_id")) != 79:
        raise HistoricalReplayRunnerContractError("phase_id must be 79")
    if contract.get("status") != "active_research_replay_runner_preview_no_execution":
        raise HistoricalReplayRunnerContractError(
            "status must be active_research_replay_runner_preview_no_execution",
        )
    data_modes = contract.get("replay_data_modes")
    if not isinstance(data_modes, list) or len(data_modes) != 2:
        raise HistoricalReplayRunnerContractError("replay_data_modes must contain two rows")
    by_mode = {str(row["data_mode"]): row for row in data_modes}
    if set(by_mode) != {STRICT_DATA_MODE, REVISED_DATA_MODE}:
        raise HistoricalReplayRunnerContractError("unexpected replay data modes")
    if by_mode[STRICT_DATA_MODE].get("revised_diagnostic_allowed") is not False:
        raise HistoricalReplayRunnerContractError("strict row cannot allow revised diagnostic")
    if by_mode[REVISED_DATA_MODE].get("point_in_time_result_allowed") is not False:
        raise HistoricalReplayRunnerContractError(
            "revised row cannot allow point-in-time result",
        )
    _validate_output_policy(contract["output_policy"])
    _validate_disabled_guards(contract["disabled_runtime_guards"])


def build_historical_replay_runner_preview(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build scenario × data-mode replay preview rows without executing models."""

    contract = load_historical_replay_runner_contract(path)
    manifest = summarize_historical_validation_manifest()
    input_rows = {
        row["scenario_id"]: row for row in build_scenario_input_readiness_outputs()
    }
    transition_preview = summarize_transition_timing_replay_preview()
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    replay_rows = [
        _build_replay_row(
            scenario=row,
            data_mode=data_mode,
            input_row=input_rows[row["scenario_id"]],
            contract=contract,
            transition_preview=transition_preview,
            schedule=schedule,
            kernel=kernel,
        )
        for row in manifest["scenario_manifest"]["scenario_rows"]
        for data_mode in contract["replay_data_modes"]
    ]
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "79",
        "phase_id": 79,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "scenario_count": manifest["scenario_count"],
        "replay_data_mode_count": len(contract["replay_data_modes"]),
        "replay_rows": replay_rows,
        "allowed_uses": contract["output_policy"]["allowed_uses"],
        "prohibited_uses": contract["output_policy"]["prohibited_uses"],
        "trust_metadata": {
            "source_contract": contract["contract_id"],
            "scenario_manifest_dependency": contract["dependencies"][
                "scenario_manifest"
            ],
            "input_readiness_dependency": contract["dependencies"][
                "input_readiness"
            ],
            "transition_timing_replay_preview_ready": transition_preview[
                "transition_timing_replay_preview_ready"
            ],
            "policy_replay_schedule_contract_ready": schedule[
                "portfolio_policy_replay_schedule_contract_ready"
            ],
            "cash_flow_kernel_contract_ready": kernel[
                "cash_flow_aware_backtest_kernel_contract_ready"
            ],
            "formal_decision_runtime_executed": False,
            "historical_validation_executed": False,
            "metric_computation_enabled": False,
            "backtest_execution_enabled": False,
            "generated_output_under_tmp_only": contract["output_policy"][
                "generated_output_under_tmp_only"
            ],
        },
        "transition_timing_replay_preview_ready": transition_preview[
            "transition_timing_replay_preview_ready"
        ],
        "policy_replay_schedule_contract_ready": schedule[
            "portfolio_policy_replay_schedule_contract_ready"
        ],
        "cash_flow_kernel_contract_ready": kernel[
            "cash_flow_aware_backtest_kernel_contract_ready"
        ],
        "historical_validation_executed": False,
        "label_comparison_executed": False,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "metric_computation_enabled": False,
        "backtest_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_historical_replay_runner_ready"
        ),
        "portfolio_policy_research_alignment": (
            "policy_replay_inputs_ready_no_execution"
        ),
        "historical_replay_backtest_alignment": (
            "historical_replay_runner_ready_no_backtest_execution"
        ),
        "legal_transition_semantics_preserved": True,
    }
    artifact["prohibited_replay_output_field_count"] = _recursive_key_count(
        artifact["replay_rows"],
        PROHIBITED_REPLAY_OUTPUT_FIELDS,
    )
    artifact["historical_replay_runner_ready"] = _passes(
        summarize_historical_replay_runner_preview(artifact=artifact),
        contract["hard_gates"],
    )
    artifact["result"] = "passed" if artifact["historical_replay_runner_ready"] else "blocked"
    return artifact


def summarize_historical_replay_runner_preview(
    path: str | Path = DEFAULT_CONTRACT_PATH,
    *,
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return compact Phase79 replay runner hard-gate fields."""

    contract = load_historical_replay_runner_contract(path)
    artifact = artifact or build_historical_replay_runner_preview(path)
    rows = artifact["replay_rows"]
    scenario_ids = {row["scenario_id"] for row in rows}
    strict_rows = [row for row in rows if row["data_mode"] == STRICT_DATA_MODE]
    revised_rows = [row for row in rows if row["data_mode"] == REVISED_DATA_MODE]
    revised_mislabeled = sum(
        row["data_mode"] == REVISED_DATA_MODE and row["point_in_time_result_emitted"]
        for row in rows
    )
    summary: dict[str, Any] = {
        "phase": "79",
        "phase_id": 79,
        "historical_replay_runner_ready": True,
        "contract_id": contract["contract_id"],
        "scenario_count": artifact["scenario_count"],
        "replay_data_mode_count": artifact["replay_data_mode_count"],
        "replay_row_count": len(rows),
        "strict_point_in_time_replay_row_count": len(strict_rows),
        "revised_diagnostic_replay_row_count": len(revised_rows),
        "scenario_with_replay_rows_count": len(scenario_ids),
        "transition_timing_replay_preview_ready": artifact[
            "transition_timing_replay_preview_ready"
        ],
        "policy_replay_schedule_contract_ready": artifact[
            "policy_replay_schedule_contract_ready"
        ],
        "cash_flow_kernel_contract_ready": artifact[
            "cash_flow_kernel_contract_ready"
        ],
        "data_mode_separation_valid": _data_mode_separation_valid(rows),
        "revised_mislabeled_as_point_in_time_count": revised_mislabeled,
        "point_in_time_result_emitted_count": sum(
            row["point_in_time_result_emitted"] for row in rows
        ),
        "label_used_by_runtime_count": sum(row["label_used_by_runtime"] for row in rows),
        "model_execution_count": sum(row["model_executed"] for row in rows),
        "historical_validation_executed": artifact["historical_validation_executed"],
        "label_comparison_executed": artifact["label_comparison_executed"],
        "historical_accuracy_metric_count": artifact["historical_accuracy_metric_count"],
        "economic_performance_metric_count": artifact[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": artifact["metric_computation_enabled"],
        "backtest_execution_count": artifact["backtest_execution_count"],
        "generated_output_under_tmp_only": contract["output_policy"][
            "generated_output_under_tmp_only"
        ],
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "live_allocation_output_count": 0,
        "prohibited_replay_output_field_count": artifact[
            "prohibited_replay_output_field_count"
        ],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "portfolio_policy_research_alignment": artifact[
            "portfolio_policy_research_alignment"
        ],
        "historical_replay_backtest_alignment": artifact[
            "historical_replay_backtest_alignment"
        ],
        "legal_transition_semantics_preserved": artifact[
            "legal_transition_semantics_preserved"
        ],
        "replay_rows": rows,
        "result": "passed",
    }
    summary["result"] = "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    summary["historical_replay_runner_ready"] = summary["result"] == "passed"
    return summary


def write_historical_replay_runner_preview(
    output: str | Path,
    *,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write replay preview JSON to an explicit /tmp path only."""

    output_path = Path(output)
    if not output_path.is_absolute() or not output_path.as_posix().startswith("/tmp/"):
        raise HistoricalReplayRunnerContractError("output must be an absolute /tmp path")
    artifact = build_historical_replay_runner_preview(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact


def _build_replay_row(
    *,
    scenario: dict[str, Any],
    data_mode: dict[str, Any],
    input_row: dict[str, Any],
    contract: dict[str, Any],
    transition_preview: dict[str, Any],
    schedule: dict[str, Any],
    kernel: dict[str, Any],
) -> dict[str, Any]:
    mode = str(data_mode["data_mode"])
    strict = mode == STRICT_DATA_MODE
    missing_input = int(input_row["missing_input_count"]) > 0
    missing_vintage = int(input_row["missing_vintage_count"]) > 0
    abstention_expected = missing_input or missing_vintage
    if strict and abstention_expected:
        replay_status = "strict_replay_abstain_missing_inputs_no_execution"
    elif strict:
        replay_status = "strict_replay_metadata_ready_no_execution"
    else:
        replay_status = "revised_diagnostic_preview_only_no_execution"
    return {
        "replay_row_id": f"{scenario['scenario_id']}::{mode}",
        "scenario_id": scenario["scenario_id"],
        "validation_window_start": scenario["validation_window_start"],
        "validation_window_end": scenario["validation_window_end"],
        "data_mode": mode,
        "data_mode_family": data_mode["mode_family"],
        "replay_status": replay_status,
        "point_in_time_result_emitted": False,
        "revised_diagnostic_label": "revised_diagnostic_only" if not strict else None,
        "transition_timing_preview_ready": transition_preview[
            "transition_timing_replay_preview_ready"
        ],
        "policy_schedule_ready": schedule[
            "portfolio_policy_replay_schedule_contract_ready"
        ],
        "cash_flow_kernel_ready": kernel[
            "cash_flow_aware_backtest_kernel_contract_ready"
        ],
        "input_readiness_status": input_row["point_in_time_readiness_status"],
        "abstention_expected": abstention_expected,
        "blocked_reason_codes": sorted(
            set(input_row["blocked_reason_codes"])
            | {
                "replay_execution_disabled",
                "metric_computation_disabled",
                "backtest_execution_disabled",
                "label_runtime_usage_disabled",
            }
        ),
        "label_used_by_runtime": False,
        "model_executed": False,
        "allowed_uses": contract["output_policy"]["allowed_uses"],
        "prohibited_uses": contract["output_policy"]["prohibited_uses"],
        "trust_metadata": {
            "source_contract": contract["contract_id"],
            "scenario_manifest_id": "book_faithful_shadow_historical_validation_manifest_v1",
            "transition_timing_preview_contract": "transition_timing_replay_preview_v1",
            "policy_replay_schedule_contract": schedule["contract_id"],
            "cash_flow_kernel_contract": kernel["contract_id"],
            "point_in_time_required": bool(scenario["point_in_time_required"]),
            "point_in_time_result_emitted": False,
            "revised_data_allowed_only_for_declared_comparison": not strict,
            "labels_read_by_runtime": False,
            "formal_decision_runtime_executed": False,
            "portfolio_returns_read": False,
        },
    }


def _validate_output_policy(output_policy: dict[str, Any]) -> None:
    if output_policy.get("output_mode") != "historical_replay_runner_preview_only":
        raise HistoricalReplayRunnerContractError(
            "output_policy.output_mode must be historical_replay_runner_preview_only",
        )
    for key in (
        "replay_execution_allowed_now",
        "formal_decision_runtime_execution_allowed",
        "validation_execution_allowed",
        "label_comparison_allowed",
        "metric_computation_allowed",
        "backtest_execution_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
        "public_output_allowed",
    ):
        if bool(output_policy.get(key)):
            raise HistoricalReplayRunnerContractError(f"output_policy.{key} must be false")
    if output_policy.get("generated_output_under_tmp_only") is not True:
        raise HistoricalReplayRunnerContractError(
            "output_policy.generated_output_under_tmp_only must be true",
        )
    missing = PROHIBITED_REPLAY_OUTPUT_FIELDS - set(output_policy["prohibited_fields"])
    if missing:
        raise HistoricalReplayRunnerContractError(
            f"output_policy.prohibited_fields missing: {', '.join(sorted(missing))}",
        )


def _validate_disabled_guards(guards: dict[str, Any]) -> None:
    for key in DISABLED_GUARD_KEYS:
        if bool(guards.get(key)):
            raise HistoricalReplayRunnerContractError(f"{key} must be false")


def _data_mode_separation_valid(rows: list[dict[str, Any]]) -> bool:
    strict_rows = [row for row in rows if row["data_mode"] == STRICT_DATA_MODE]
    revised_rows = [row for row in rows if row["data_mode"] == REVISED_DATA_MODE]
    return (
        bool(strict_rows)
        and bool(revised_rows)
        and all(row["revised_diagnostic_label"] is None for row in strict_rows)
        and all(
            row["revised_diagnostic_label"] == "revised_diagnostic_only"
            for row in revised_rows
        )
        and all(row["point_in_time_result_emitted"] is False for row in revised_rows)
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(1 for key in value if str(key) in prohibited) + sum(
            _recursive_key_count(item, prohibited) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0
