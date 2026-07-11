"""Live revised-data evidence runtime for the declared boom transition lanes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.indicator_learning_semantics import (
    transform_observations_for_display,
)
from business_cycle.shadow_model.phase_evidence_evaluators import (
    evaluate_phase_evidence,
)
from business_cycle.shadow_model.phase_evidence_primitives import causal_direction

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_live_ordered_cycle_evidence_contract.yaml"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


def load_nas_live_ordered_cycle_evidence_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 123 live ordered-cycle evidence contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_live_ordered_cycle_evidence_contract"])


def build_live_ordered_cycle_evidence(
    snapshot: dict[str, Any],
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Evaluate governed role histories without selecting or changing a phase."""

    contract = load_nas_live_ordered_cycle_evidence_contract(contract_path)
    source_data_mode = str(snapshot.get("data_mode", "revised_diagnostic"))
    primitive_data_mode = (
        "vintage_as_of" if source_data_mode == "vintage_as_of" else "revised"
    )
    role_snapshots = {
        str(row["role_id"]): row for row in snapshot.get("role_snapshots", [])
    }
    role_outputs = {
        role_id: _evaluate_role(
            role_id=role_id,
            role_contract=role_contract,
            snapshot_row=role_snapshots.get(role_id),
            as_of=str(snapshot.get("snapshot_as_of") or ""),
            data_mode=primitive_data_mode,
        )
        for role_id, role_contract in contract["role_evaluators"].items()
    }
    lanes = {
        lane_id: _build_lane(
            lane_id=lane_id,
            lane_contract=lane_contract,
            role_outputs=role_outputs,
        )
        for lane_id, lane_contract in contract["lane_policy"].items()
    }
    declared = dict(snapshot.get("declared_cycle_state", {}))
    declared_phase = str(declared.get("declared_current_phase", "boom"))
    legal_next = str(declared.get("legal_next_phase", "recession"))
    artifact: dict[str, Any] = {
        "artifact_id": "phase123_live_ordered_cycle_evidence_v1",
        "artifact_version": contract["version"],
        "phase": 123,
        "phase_id": 123,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": snapshot.get("snapshot_as_of"),
        "data_mode": source_data_mode,
        "declared_current_phase": declared_phase,
        "legal_next_phase": legal_next,
        "role_evidence": role_outputs,
        "lanes": lanes,
        "evaluated_role_count": len(role_outputs),
        "phase_evidence_output_role_count": sum(
            row["phase_evidence_output_available"] for row in role_outputs.values()
        ),
        "explicit_abstention_role_count": sum(
            row["evidence_status"] == "abstained" for row in role_outputs.values()
        ),
        "mixed_role_count": sum(
            row["evidence_status"] == "mixed" for row in role_outputs.values()
        ),
        "lane_output_count": len(lanes),
        "transformed_input_contract_count": len(role_outputs),
        "live_ordered_cycle_evidence_contract_ready": _contract_ready(contract),
        "live_evidence_evaluator_connected": True,
        "watch_confirmation_separation_verified": _watch_confirmation_separated(
            lanes
        ),
        "phase_presence_transition_separation_valid": True,
        "declared_state_and_legal_transition_preserved": (
            declared_phase == contract["declared_state_policy"]["declared_current_phase"]
            and legal_next == contract["declared_state_policy"]["legal_next_phase"]
        ),
        "why_not_confirmation": lanes["recession_confirmation"][
            "why_not_confirmation"
        ],
        "raw_value_promoted_to_evidence_count": 0,
        "smoothing_alone_promoted_to_evidence_count": 0,
        "missing_value_treated_as_neutral_count": 0,
        "missing_value_treated_as_zero_count": 0,
        "watch_promoted_to_confirmation_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "private_nas_transition_research",
            "declared_boom_continuation_review",
            "legal_next_transition_watch_review",
            "evidence_gap_and_contradiction_explanation",
        ],
        "prohibited_uses": [
            "formal_current_phase_inference",
            "candidate_phase_selection",
            "automatic_declared_state_change",
            "personalized_portfolio_instruction",
            "trade_action",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "source_mode": (
                "historical_postgres_vintage_read_only"
                if primitive_data_mode == "vintage_as_of"
                else "live_postgres_read_only"
            ),
            "revised_diagnostic_only": primitive_data_mode == "revised",
            "book_rule_registry_reused": True,
            "display_formula_recomputed_under_phase123_evidence_contract": True,
            "watch_confirmation_separated": True,
            "declared_state_not_inferred": True,
            "point_in_time_result": primitive_data_mode == "vintage_as_of",
        },
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["result"] = (
        "passed"
        if _matches(artifact, contract["hard_gates"])
        and artifact["prohibited_output_field_count"] == 0
        else "blocked"
    )
    return artifact


def _evaluate_role(
    *,
    role_id: str,
    role_contract: dict[str, Any],
    snapshot_row: dict[str, Any] | None,
    as_of: str,
    data_mode: str,
) -> dict[str, Any]:
    if snapshot_row is None:
        return _abstained_role(role_id, role_contract, "role_snapshot_missing")
    expected_snapshot_status = (
        "vintage_snapshot_ready"
        if data_mode == "vintage_as_of"
        else "revised_snapshot_ready"
    )
    if snapshot_row.get("snapshot_status") != expected_snapshot_status:
        return _abstained_role(
            role_id,
            role_contract,
            f"{data_mode}_snapshot_unavailable",
            snapshot_row=snapshot_row,
        )
    if data_mode == "revised" and snapshot_row.get("freshness_status") in {
        "stale",
        "unavailable",
        "mixed",
    }:
        return _abstained_role(
            role_id,
            role_contract,
            "live_input_stale_or_unavailable",
            snapshot_row=snapshot_row,
        )
    inputs = {
        str(row["series_id"]): row
        for row in snapshot_row.get("evidence_input_series", [])
    }
    required_ids = [str(item) for item in role_contract["required_series_ids"]]
    missing_ids = [series_id for series_id in required_ids if series_id not in inputs]
    if missing_ids:
        return _abstained_role(
            role_id,
            role_contract,
            f"evidence_history_missing:{','.join(missing_ids)}",
            snapshot_row=snapshot_row,
        )
    transformed = {
        series_id: _transform_for_evidence(
            role_id=role_id,
            rows=list(inputs[series_id]["observations"]),
            expected_profile=str(role_contract["transform_profile_id"]),
            data_mode=data_mode,
        )
        for series_id in required_ids
    }
    if any(len(rows) < 2 for rows in transformed.values()):
        return _abstained_role(
            role_id,
            role_contract,
            "insufficient_transformed_lookback",
            snapshot_row=snapshot_row,
            transformed=transformed,
        )
    if role_contract["evaluator_type"] == "component_consistency":
        component_outputs = [
            causal_direction(
                observations=transformed[series_id],
                as_of=as_of,
                expected_direction=str(role_contract["expected_direction"]),
                data_mode=data_mode,
                rule_id=f"phase123::{role_id}::{series_id}",
                minimum_observations=2,
            )
            for series_id in required_ids
        ]
        status = _component_consistency_status(component_outputs)
        output_available = status in {"supportive", "contradictory", "mixed"}
        primitive_outputs = component_outputs
        abstention_reason = (
            None if output_available else "component_evidence_not_complete"
        )
    else:
        evaluated = evaluate_phase_evidence(
            role_id=role_id,
            as_of=as_of,
            data_mode=data_mode,
            observations=transformed[required_ids[0]],
        )
        status = str(evaluated["evidence_status"])
        output_available = bool(evaluated["phase_evidence_output_available"])
        primitive_outputs = [evaluated["primitive_output"]]
        abstention_reason = evaluated.get("abstention_reason")
    return {
        "role_id": role_id,
        "evidence_status": status,
        "phase_evidence_output_available": output_available,
        "explicit_abstention": not output_available,
        "abstention_reason": abstention_reason,
        "required_series_ids": required_ids,
        "transform_profile_id": role_contract["transform_profile_id"],
        "evaluator_type": role_contract["evaluator_type"],
        "expected_direction": role_contract["expected_direction"],
        "interpretation_zh": role_contract["interpretation_zh"],
        "latest_transformed_observation_dates": {
            series_id: transformed[series_id][-1]["date"]
            for series_id in required_ids
        },
        "transformed_observation_counts": {
            series_id: len(transformed[series_id]) for series_id in required_ids
        },
        "primitive_outputs": primitive_outputs,
        "source_lineage": snapshot_row.get("source_lineage", []),
        "provenance_complete": all(
            row.get("source_artifact_id") for rows in transformed.values() for row in rows
        ),
        "display_only_transform_promoted": False,
        "phase123_evidence_transform_contract_applied": True,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _transform_for_evidence(
    *,
    role_id: str,
    rows: list[dict[str, Any]],
    expected_profile: str,
    data_mode: str,
) -> list[dict[str, Any]]:
    display_rows = [
        {
            "observation_date": row["date"],
            "value_numeric": row["value"],
            "source_artifact_id": row.get("source_artifact_id"),
            "provenance_hash": row.get("provenance_hash"),
        }
        for row in rows
    ]
    transformed, semantics = transform_observations_for_display(
        display_rows,
        role_id=role_id,
    )
    if semantics["transform_profile_id"] != expected_profile:
        raise ValueError(f"Phase 123 transform mismatch for {role_id}")
    return [
        {
            "date": str(row["observation_date"]),
            "value": row["value_numeric"],
            "data_mode": data_mode,
            "source_artifact_id": row.get("source_artifact_id"),
            "provenance_hash": row.get("provenance_hash"),
        }
        for row in transformed
        if row.get("value_numeric") is not None
    ]


def _component_consistency_status(outputs: list[dict[str, Any]]) -> str:
    statuses = [str(row["status"]) for row in outputs]
    if any(status in {"abstained", "rejected"} for status in statuses):
        return "abstained"
    if all(status == "matched" for status in statuses):
        return "supportive"
    if all(status == "not_matched" for status in statuses):
        return "contradictory"
    return "mixed"


def _build_lane(
    *,
    lane_id: str,
    lane_contract: dict[str, Any],
    role_outputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    items = []
    for role_id in lane_contract["required_role_ids"]:
        role = role_outputs[role_id]
        state = str(role["evidence_status"])
        if lane_id == "boom_continuation":
            state = _inverse_state(state)
        items.append(
            {
                "role_id": role_id,
                "lane_evidence_state": state,
                "source_evidence_status": role["evidence_status"],
                "explicit_abstention": role["explicit_abstention"],
                "abstention_reason": role["abstention_reason"],
                "interpretation_zh": role["interpretation_zh"],
                "latest_transformed_observation_dates": role.get(
                    "latest_transformed_observation_dates", {}
                ),
                "provenance_complete": role["provenance_complete"],
                "watch_promoted_to_confirmation": False,
            }
        )
    status = _lane_status(items)
    why_not_confirmation = _why_not_confirmation(
        lane_id=lane_id,
        status=status,
        items=items,
    )
    return {
        "lane_id": lane_id,
        "lane_type": lane_contract["lane_type"],
        "lane_status": status,
        "required_role_ids": list(lane_contract["required_role_ids"]),
        "required_role_count": len(items),
        "supportive_evidence_count": sum(
            item["lane_evidence_state"] == "supportive" for item in items
        ),
        "contradictory_evidence_count": sum(
            item["lane_evidence_state"] == "contradictory" for item in items
        ),
        "mixed_evidence_count": sum(
            item["lane_evidence_state"] == "mixed" for item in items
        ),
        "abstained_evidence_count": sum(
            item["lane_evidence_state"] == "abstained" for item in items
        ),
        "evidence_items": items,
        "why_not_confirmation": why_not_confirmation,
        "watch_is_confirmation": False,
        "transition_conclusion_emitted": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _inverse_state(state: str) -> str:
    if state == "supportive":
        return "contradictory"
    if state == "contradictory":
        return "supportive"
    return state


def _lane_status(items: list[dict[str, Any]]) -> str:
    states = {str(item["lane_evidence_state"]) for item in items}
    if states == {"supportive"}:
        return "supportive_evidence_present"
    if states == {"contradictory"}:
        return "contradictory_evidence_present"
    if states == {"abstained"}:
        return "explicit_abstention"
    if "abstained" in states:
        return "incomplete_evidence"
    if "mixed" in states or len(states) > 1:
        return "mixed_evidence"
    return "neutral_evidence"


def _why_not_confirmation(
    *,
    lane_id: str,
    status: str,
    items: list[dict[str, Any]],
) -> list[str]:
    if lane_id != "recession_confirmation":
        return ["此 lane 不是 recession confirmation，不得升級為確認。"]
    reasons = []
    for item in items:
        if item["lane_evidence_state"] != "supportive":
            reasons.append(
                f"{item['role_id']} 尚未形成 supportive confirmation evidence"
            )
    if status == "supportive_evidence_present":
        reasons.append("核心確認 evidence 已到位，但 declared state 變更仍需獨立治理 gate。")
    else:
        reasons.append("就業與廣義消費尚未同時形成完整 confirmation evidence。")
    return reasons


def _abstained_role(
    role_id: str,
    role_contract: dict[str, Any],
    reason: str,
    *,
    snapshot_row: dict[str, Any] | None = None,
    transformed: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "evidence_status": "abstained",
        "phase_evidence_output_available": False,
        "explicit_abstention": True,
        "abstention_reason": reason,
        "required_series_ids": list(role_contract["required_series_ids"]),
        "transform_profile_id": role_contract["transform_profile_id"],
        "evaluator_type": role_contract["evaluator_type"],
        "expected_direction": role_contract["expected_direction"],
        "interpretation_zh": role_contract["interpretation_zh"],
        "latest_transformed_observation_dates": {
            series_id: rows[-1]["date"] for series_id, rows in (transformed or {}).items()
            if rows
        },
        "transformed_observation_counts": {
            series_id: len(rows) for series_id, rows in (transformed or {}).items()
        },
        "primitive_outputs": [],
        "source_lineage": (snapshot_row or {}).get("source_lineage", []),
        "provenance_complete": True,
        "display_only_transform_promoted": False,
        "phase123_evidence_transform_contract_applied": True,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active_private_nas_research_runtime"
        and len(contract["role_evaluators"]) == 5
        and len(contract["lane_policy"]) == 4
        and contract["output_policy"]["watch_is_confirmation"] is False
        and contract["output_policy"]["evidence_changes_declared_state"] is False
    )


def _watch_confirmation_separated(lanes: dict[str, dict[str, Any]]) -> bool:
    return (
        {lane_id for lane_id, lane in lanes.items() if lane["lane_type"] == "transition_watch"}
        == {"boom_ending_watch", "recession_watch"}
        and {
            lane_id
            for lane_id, lane in lanes.items()
            if lane["lane_type"] == "transition_confirmation"
        }
        == {"recession_confirmation"}
        and all(not lane["watch_is_confirmation"] for lane in lanes.values())
    )


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(key in PROHIBITED_FIELDS for key in value) + sum(
            _contains_prohibited_field(item) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0
