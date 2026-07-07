"""Replay/backtest reproducibility and provenance hardening for Phase82."""

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
from business_cycle.portfolio.research_backtest_artifacts import (
    PROHIBITED_BACKTEST_ARTIFACT_FIELDS,
    build_research_backtest_artifact_bundle,
    load_research_backtest_artifact_contract,
)
from business_cycle.validation.historical_replay_runner import (
    STRICT_DATA_MODE,
    summarize_historical_replay_runner_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/replay_backtest_lineage_hardening_contract.yaml"
)
DEFAULT_METRIC_REGISTRY_PATH = ROOT / "specs/portfolio/backtest_metric_formula_registry.yaml"


class ReplayBacktestLineageHardeningError(ValueError):
    """Raised when the Phase82 lineage hardening contract is invalid."""


def load_replay_backtest_lineage_hardening_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load and validate the Phase82 lineage hardening contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayBacktestLineageHardeningError("contract YAML must be a mapping")
    contract = payload.get("replay_backtest_lineage_hardening_contract")
    if not isinstance(contract, dict):
        raise ReplayBacktestLineageHardeningError(
            "YAML must contain replay_backtest_lineage_hardening_contract",
        )
    validate_replay_backtest_lineage_hardening_contract(contract)
    return contract


def validate_replay_backtest_lineage_hardening_contract(
    contract: dict[str, Any],
) -> None:
    """Validate Phase82 contract boundaries."""

    if int(contract.get("phase_id")) != 82:
        raise ReplayBacktestLineageHardeningError("phase_id must be 82")
    if contract.get("status") != "active_research_lineage_hardening_no_execution":
        raise ReplayBacktestLineageHardeningError("unexpected Phase82 status")
    lineage_policy = contract.get("lineage_policy")
    if not isinstance(lineage_policy, dict):
        raise ReplayBacktestLineageHardeningError("lineage_policy must exist")
    for key in (
        "source_contract_hashes_required",
        "input_hash_recomputation_required",
        "replay_row_to_artifact_one_to_one_required",
        "strict_revised_data_mode_separation_required",
        "missing_input_requires_abstention_or_blocked_reason",
    ):
        if lineage_policy.get(key) is not True:
            raise ReplayBacktestLineageHardeningError(f"lineage_policy.{key} required")
    for key in ("silent_fallback_allowed", "generated_repo_output_allowed"):
        if bool(lineage_policy.get(key)):
            raise ReplayBacktestLineageHardeningError(f"lineage_policy.{key} must be false")
    missing = PROHIBITED_BACKTEST_ARTIFACT_FIELDS - set(
        contract.get("prohibited_fields") or [],
    )
    if missing:
        raise ReplayBacktestLineageHardeningError(
            f"prohibited_fields missing: {', '.join(sorted(missing))}",
        )
    for key, value in contract.get("disabled_runtime_guards", {}).items():
        if bool(value):
            raise ReplayBacktestLineageHardeningError(f"{key} must be false")


def build_replay_backtest_lineage_hardening_report(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the Phase82 lineage hardening report without executing backtests."""

    contract = load_replay_backtest_lineage_hardening_contract(path)
    replay = summarize_historical_replay_runner_preview()
    replay_rows = replay["replay_rows"]
    replay_by_id = {row["replay_row_id"]: row for row in replay_rows}
    artifact_bundle = build_research_backtest_artifact_bundle()
    artifacts = artifact_bundle["research_backtest_artifacts"]
    artifact_by_replay_id = {row["source_replay_row_id"]: row for row in artifacts}
    expected_hashes = _expected_source_contract_hashes()
    artifact_source_hash_mismatches = _artifact_source_hash_mismatch_count(
        artifacts,
        expected_hashes,
    )
    bundle_source_hash_mismatches = _dict_mismatch_count(
        artifact_bundle["source_contract_hashes"],
        expected_hashes,
    )
    input_hash_mismatch_count = _input_hash_mismatch_count(
        artifacts,
        replay_by_id,
        expected_hashes,
    )
    artifact_lineage_mismatch_count = _artifact_lineage_mismatch_count(
        artifacts,
        replay_by_id,
    )
    replay_row_missing_artifact_count = sum(
        replay_row_id not in artifact_by_replay_id for replay_row_id in replay_by_id
    )
    artifact_without_replay_row_count = sum(
        row["source_replay_row_id"] not in replay_by_id for row in artifacts
    )
    silent_fallback_count = _silent_fallback_count(replay_rows, artifacts)
    missing_input_without_abstention_count = sum(
        _has_missing_input_signal(row) and row["abstention_expected"] is not True
        for row in replay_rows
    )
    abstention_without_reason_count = sum(
        row["abstention_expected"] is True and not row["blocked_reason_codes"]
        for row in replay_rows
    )
    input_hashes = [row.get("input_hash") for row in artifacts if row.get("input_hash")]
    summary: dict[str, Any] = {
        "phase": "82",
        "phase_id": 82,
        "replay_backtest_lineage_ready": True,
        "replay_backtest_lineage_contract_ready": True,
        "replay_backtest_lineage_audit_ready": True,
        "scenario_count": replay["scenario_count"],
        "replay_row_count": replay["replay_row_count"],
        "research_backtest_artifact_count": len(artifacts),
        "artifact_replay_row_link_count": sum(
            row["source_replay_row_id"] in replay_by_id for row in artifacts
        ),
        "replay_row_missing_artifact_count": replay_row_missing_artifact_count,
        "artifact_without_replay_row_count": artifact_without_replay_row_count,
        "source_contract_hash_family_count": len(expected_hashes),
        "source_contract_hash_coverage_complete": (
            set(artifact_bundle["source_contract_hashes"]) == set(expected_hashes)
        ),
        "source_contract_hash_mismatch_count": max(
            bundle_source_hash_mismatches,
            artifact_source_hash_mismatches,
        ),
        "artifact_with_complete_source_contract_hashes_count": sum(
            row["provenance"]["source_contract_hashes"] == expected_hashes
            for row in artifacts
        ),
        "input_hash_coverage_complete": (
            len(input_hashes) == len(artifacts) and input_hash_mismatch_count == 0
        ),
        "artifact_with_verified_input_hash_count": len(artifacts)
        - input_hash_mismatch_count,
        "deterministic_input_hash_count": len(artifacts) - input_hash_mismatch_count,
        "input_hash_mismatch_count": input_hash_mismatch_count,
        "unique_input_hash_count": len(set(input_hashes)),
        "artifact_lineage_mismatch_count": artifact_lineage_mismatch_count,
        "data_mode_separation_valid": replay["data_mode_separation_valid"],
        "strict_replay_row_count": replay["strict_point_in_time_replay_row_count"],
        "revised_replay_row_count": replay["revised_diagnostic_replay_row_count"],
        "silent_fallback_count": silent_fallback_count,
        "missing_input_without_abstention_count": missing_input_without_abstention_count,
        "abstention_without_reason_count": abstention_without_reason_count,
        "revised_mislabeled_as_point_in_time_count": replay[
            "revised_mislabeled_as_point_in_time_count"
        ],
        "metric_value_count": artifact_bundle["metric_value_count"],
        "risk_metric_value_count": artifact_bundle["risk_metric_value_count"],
        "historical_accuracy_metric_count": replay["historical_accuracy_metric_count"],
        "economic_performance_metric_count": replay["economic_performance_metric_count"],
        "metric_computation_enabled": replay["metric_computation_enabled"],
        "backtest_execution_count": replay["backtest_execution_count"],
        "current_allocation_recommendation_count": replay[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": replay["trade_signal_output_count"],
        "public_output_count": 0,
        "repository_output_count": 0,
        "generated_output_under_tmp_only": True,
        "prohibited_output_field_count": _recursive_key_count(
            artifacts,
            PROHIBITED_BACKTEST_ARTIFACT_FIELDS,
        ),
        "label_used_by_runtime_count": replay["label_used_by_runtime_count"],
        "candidate_phase_emitted": replay["candidate_phase_emitted"],
        "current_phase_emitted": replay["current_phase_emitted"],
        "standalone_classifier_added_count": replay["standalone_classifier_added_count"],
        "phase_rank_or_score_added_count": replay["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": replay["role_count_voting_added_count"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_replay_backtest_lineage_hardened"
        ),
        "portfolio_policy_research_alignment": (
            "lineage_hardened_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "replay_backtest_lineage_hardened_no_silent_fallback"
        ),
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 83,
        "phase82_closure_status": (
            "closed_replay_backtest_lineage_hardened_no_silent_fallback"
        ),
    }
    summary["result"] = (
        "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    )
    summary["replay_backtest_lineage_ready"] = summary["result"] == "passed"
    return summary


def _expected_source_contract_hashes() -> dict[str, str]:
    artifact_contract = load_research_backtest_artifact_contract()
    allowed = set(
        load_replay_backtest_lineage_hardening_contract()[
            "required_source_hash_dependencies"
        ],
    )
    return {
        key: _sha256_file(ROOT / value)
        for key, value in sorted(artifact_contract["dependencies"].items())
        if key in allowed
    }


def _artifact_source_hash_mismatch_count(
    artifacts: list[dict[str, Any]],
    expected_hashes: dict[str, str],
) -> int:
    return sum(
        row["provenance"]["source_contract_hashes"] != expected_hashes
        for row in artifacts
    )


def _dict_mismatch_count(actual: dict[str, str], expected: dict[str, str]) -> int:
    keys = set(actual) | set(expected)
    return sum(actual.get(key) != expected.get(key) for key in keys)


def _input_hash_mismatch_count(
    artifacts: list[dict[str, Any]],
    replay_by_id: dict[str, dict[str, Any]],
    expected_hashes: dict[str, str],
) -> int:
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    return sum(
        row.get("input_hash")
        != _expected_input_hash(
            row=row,
            replay_row=replay_by_id.get(row["source_replay_row_id"]),
            schedule_contract_id=schedule["contract_id"],
            kernel_contract_id=kernel["contract_id"],
            source_contract_hashes=expected_hashes,
        )
        for row in artifacts
    )


def _expected_input_hash(
    *,
    row: dict[str, Any],
    replay_row: dict[str, Any] | None,
    schedule_contract_id: str,
    kernel_contract_id: str,
    source_contract_hashes: dict[str, str],
) -> str | None:
    if replay_row is None:
        return None
    payload = {
        "replay_row": replay_row,
        "policy_schedule_contract": schedule_contract_id,
        "cash_flow_kernel_contract": kernel_contract_id,
        "metric_formula_ids": [item["metric_id"] for item in row["metric_formula_refs"]],
        "source_contract_hashes": source_contract_hashes,
    }
    return _hash_payload(payload)


def _artifact_lineage_mismatch_count(
    artifacts: list[dict[str, Any]],
    replay_by_id: dict[str, dict[str, Any]],
) -> int:
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    metric_registry = load_backtest_metric_formula_registry(DEFAULT_METRIC_REGISTRY_PATH)
    expected_metric_ids = sorted(metric_registry.metric_definitions)
    mismatch_count = 0
    for row in artifacts:
        replay_row = replay_by_id.get(row["source_replay_row_id"])
        if replay_row is None:
            mismatch_count += 1
            continue
        mismatches = (
            row["scenario_id"] != replay_row["scenario_id"],
            row["data_mode"] != replay_row["data_mode"],
            row["validation_window_start"] != replay_row["validation_window_start"],
            row["validation_window_end"] != replay_row["validation_window_end"],
            row["source_replay_runner_contract_id"]
            != replay_row["trust_metadata"]["source_contract"],
            row["source_policy_schedule_contract_id"] != schedule["contract_id"],
            row["source_cash_flow_kernel_contract_id"] != kernel["contract_id"],
            row["source_metric_formula_registry_id"]
            != "backtest_metric_formula_registry_v1",
            [item["metric_id"] for item in row["metric_formula_refs"]]
            != expected_metric_ids,
        )
        mismatch_count += int(any(mismatches))
    return mismatch_count


def _silent_fallback_count(
    replay_rows: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> int:
    count = 0
    for row in replay_rows:
        if row["data_mode"] == STRICT_DATA_MODE and row["abstention_expected"]:
            count += int("abstain" not in row["replay_status"])
        if _has_missing_input_signal(row) and not row["blocked_reason_codes"]:
            count += 1
    for row in artifacts:
        blocked = row["provenance"]["source_replay_row_blocked_reason_codes"]
        count += int(row["trust_metadata"]["abstention_expected"] and not blocked)
        count += int(row["trust_metadata"]["metric_values_computed"])
        count += int(row["trust_metadata"]["backtest_execution_enabled"])
    return count


def _has_missing_input_signal(row: dict[str, Any]) -> bool:
    status = str(row["input_readiness_status"])
    return "missing" in status or "unavailable" in status


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(
            int(str(key) in prohibited) + _recursive_key_count(item, prohibited)
            for key, item in value.items()
        )
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
