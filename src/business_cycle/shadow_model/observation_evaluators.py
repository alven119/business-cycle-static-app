"""QA11 observation-only evaluators for forward-ready book-core roles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)


DEFAULT_OBSERVATION_CONTRACT_PATH = Path(
    "specs/audits/book_core_observation_evaluator_contract.yaml"
)
OBSERVATION_EVALUATOR_VERSION = "qa11_observation_only_v1"


def load_observation_evaluator_contract(
    path: str | Path = DEFAULT_OBSERVATION_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_observation_evaluator_contract"
    ]


def build_observation_evaluator_contracts(
    path: str | Path = DEFAULT_OBSERVATION_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    spec = load_observation_evaluator_contract(path)
    rows: list[dict[str, Any]] = []
    for role in build_book_core_forward_data_gap_rows():
        if not role["observation_evaluator_supported"]:
            continue
        evaluator_type = (
            "smoothed_level_observation"
            if role["role_id"] == "recovery_weekly_claim_noise_filter"
            else "raw_direction_observation"
        )
        rows.append(
            {
                "role_id": role["role_id"],
                "major_group_id": role["major_group_id"],
                "evaluator_id": f"observation::{role['role_id']}",
                "evaluator_version": OBSERVATION_EVALUATOR_VERSION,
                "source_series_ids": role["current_series_ids"],
                "transformation_id": f"transform::{role['role_id']}",
                "evaluator_type": evaluator_type,
                "minimum_observations": 3
                if evaluator_type == "smoothed_level_observation"
                else 2,
                "lookback_type": "calendar_months",
                "lookback_duration": 3,
                "allowed_observation_states": spec["allowed_observation_states"],
                "numeric_threshold": None,
                "candidate_selection_eligible": False,
                "phase_support_allowed": False,
                "historical_label_input_allowed": False,
                "scenario_specific_branch_allowed": False,
                "external_context_allowed": False,
            }
        )
    return rows


def evaluate_observation_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a role snapshot as observation-only metadata."""

    contracts = {
        row["role_id"]: row for row in build_observation_evaluator_contracts()
    }
    contract = contracts.get(snapshot["role_id"])
    if contract is None:
        return _abstention(
            snapshot=snapshot,
            reason="observation_evaluator_not_supported",
        )
    if not snapshot["ready_for_evaluator"]:
        return _abstention(snapshot=snapshot, reason=snapshot["abstention_reason"])
    observations = snapshot["history_windows"][0]["observations"]
    if len(observations) < contract["minimum_observations"]:
        return _abstention(snapshot=snapshot, reason="insufficient_lookback")
    values = [float(row["value"]) for row in observations]
    state = _observation_state(contract, values)
    return {
        "role_id": snapshot["role_id"],
        "major_group_id": contract["major_group_id"],
        "evaluator_id": contract["evaluator_id"],
        "evaluator_version": contract["evaluator_version"],
        "observation_state": state,
        "observation_status": "matched",
        "raw_value": values[-1],
        "transformed_value": _transformed_value(contract, values),
        "transformation_id": contract["transformation_id"],
        "runtime_window_id": snapshot["history_windows"][0]["window_id"],
        "input_snapshot_hash": snapshot["snapshot_payload_hash"],
        "actual_data_mode": snapshot["actual_data_mode"],
        "as_of": snapshot["as_of"],
        "source_provenance": snapshot["source_artifact_ids"],
        "candidate_selection_eligible": False,
        "phase_support_emitted": False,
        "numeric_threshold_used": False,
        "historical_label_used": False,
        "abstention_reason": None,
    }


def summarize_book_core_observation_evaluators() -> dict[str, Any]:
    contracts = build_observation_evaluator_contracts()
    eligible_count = len(contracts)
    threshold_count = sum(row["numeric_threshold"] is not None for row in contracts)
    candidate_count = sum(row["candidate_selection_eligible"] for row in contracts)
    phase_support_count = sum(row["phase_support_allowed"] for row in contracts)
    historical_label_count = sum(
        row["historical_label_input_allowed"] for row in contracts
    )
    states = Counter(row["evaluator_type"] for row in contracts)
    return {
        "phase": "QA11",
        "observation_evaluator_layer_ready": eligible_count > 1
        and threshold_count == 0
        and candidate_count == 0
        and phase_support_count == 0
        and historical_label_count == 0,
        "observation_evaluator_contract_count": len(contracts),
        "runtime_observable_eligible_role_count": eligible_count,
        "implemented_observation_evaluator_count": len(contracts),
        "new_runtime_observable_role_count": max(0, len(contracts) - 1),
        "observation_evaluator_with_numeric_threshold_count": threshold_count,
        "observation_evaluator_candidate_eligible_count": candidate_count,
        "observation_evaluator_emitted_phase_support_count": phase_support_count,
        "observation_evaluator_read_historical_label_count": historical_label_count,
        "observation_evaluator_type_counts": dict(sorted(states.items())),
        "contracts": contracts,
    }


def _observation_state(contract: dict[str, Any], values: list[float]) -> str:
    if contract["evaluator_type"] == "smoothed_level_observation":
        return "smoothed_level_observation"
    if values[-1] > values[-2]:
        return "raw_direction_up"
    if values[-1] < values[-2]:
        return "raw_direction_down"
    return "raw_direction_unchanged_exact"


def _transformed_value(contract: dict[str, Any], values: list[float]) -> float:
    if contract["evaluator_type"] == "smoothed_level_observation":
        return sum(values[-3:]) / 3
    return values[-1] - values[-2]


def _abstention(snapshot: dict[str, Any], reason: str | None) -> dict[str, Any]:
    return {
        "role_id": snapshot["role_id"],
        "major_group_id": None,
        "evaluator_id": snapshot["evaluator_id"],
        "evaluator_version": OBSERVATION_EVALUATOR_VERSION,
        "observation_state": "temporal_abstention"
        if reason == "temporal_evidence_missing"
        else "insufficient_lookback",
        "observation_status": "abstained",
        "raw_value": None,
        "transformed_value": None,
        "transformation_id": f"transform::{snapshot['role_id']}",
        "runtime_window_id": snapshot["history_windows"][0]["window_id"],
        "input_snapshot_hash": snapshot["snapshot_payload_hash"],
        "actual_data_mode": snapshot["actual_data_mode"],
        "as_of": snapshot["as_of"],
        "source_provenance": snapshot["source_artifact_ids"],
        "candidate_selection_eligible": False,
        "phase_support_emitted": False,
        "numeric_threshold_used": False,
        "historical_label_used": False,
        "abstention_reason": reason or "observation_not_available",
    }
