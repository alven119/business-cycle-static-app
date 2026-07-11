"""Governed command-center view model for the private NAS dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_cycle_command_center_contract.yaml"
DEFAULT_ROLE_LABELS_PATH = ROOT / "specs/common/book_core_role_display_labels_zh.yaml"

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


def load_nas_cycle_command_center_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 120 command-center contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_cycle_command_center_contract"])


def build_nas_cycle_command_center(
    snapshot: dict[str, Any],
    *,
    live_transition_evidence: dict[str, Any] | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    role_labels_path: str | Path = DEFAULT_ROLE_LABELS_PATH,
) -> dict[str, Any]:
    """Build a no-selection homepage model from the live/rehearsal snapshot."""

    contract = load_nas_cycle_command_center_contract(contract_path)
    labels = _load_role_labels(role_labels_path)
    roles = {str(row["role_id"]): row for row in snapshot["role_snapshots"]}
    declared = dict(snapshot.get("declared_cycle_state", {}))
    phase = str(declared.get("declared_current_phase", "boom"))
    legal_next = str(declared.get("legal_next_phase", "recession"))
    live_lanes = (live_transition_evidence or {}).get("lanes", {})
    live_roles = (live_transition_evidence or {}).get("role_evidence", {})
    lanes = [
        _lane_view(
            row,
            roles=roles,
            role_labels=labels,
            live_lane=live_lanes.get(row["lane_id"]),
        )
        for row in contract["transition_lanes"]
    ]
    key_indicators = [
        _indicator_view(
            roles[role_id],
            labels[role_id],
            live_evidence=live_roles.get(role_id),
        )
        for role_id in contract["key_indicator_role_ids"]
    ]
    navigation = [dict(row) for row in contract["navigation"]]
    command_center: dict[str, Any] = {
        "view_model_id": "nas_cycle_command_center_v1",
        "view_model_version": contract["version"],
        "phase": 120,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": snapshot.get("snapshot_as_of"),
        "data_mode": snapshot.get("data_mode", "revised_diagnostic"),
        "declared_state": {
            "declared_current_phase": phase,
            "declared_current_phase_label_zh": declared.get(
                "declared_current_phase_label_zh",
                contract["phase_labels_zh"].get(phase, phase),
            ),
            "legal_next_phase": legal_next,
            "legal_next_phase_label_zh": declared.get(
                "legal_next_phase_label_zh",
                contract["phase_labels_zh"].get(legal_next, legal_next),
            ),
            "declared_phase_start_display_zh": declared.get(
                "declared_phase_start_display_zh",
                "尚待使用者確認",
            ),
            "declared_phase_age_days": declared.get("declared_phase_age_days"),
            "declared_phase_age_range_days": declared.get(
                "declared_phase_age_range_days"
            ),
            "declaration_source": declared.get(
                "active_registry_source",
                "canonical_default",
            ),
            "state_is_declared_not_inferred": True,
        },
        "cycle_order": [
            {
                "phase_id": phase_id,
                "label_zh": contract["phase_labels_zh"][phase_id],
                "is_declared": phase_id == phase,
                "is_legal_next": phase_id == legal_next,
            }
            for phase_id in contract["cycle_order"]
        ],
        "navigation": navigation,
        "transition_lanes": lanes,
        "key_indicators": key_indicators,
        "data_health": _data_health(snapshot),
        "live_transition_evaluator_connected": bool(
            live_transition_evidence
            and live_transition_evidence.get("result") == "passed"
        ),
        "live_transition_evidence": live_transition_evidence,
        "transition_conclusion_output_count": 0,
        "watch_promoted_to_confirmation_count": 0,
        "raw_value_promoted_to_evidence_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "trust_metadata": {
            "output_label": "research_only_declared_cycle_context",
            "declared_state_not_inferred": True,
            "transition_lane_status_is_input_readiness_not_conclusion": (
                live_transition_evidence is None
            ),
            "live_transition_evaluator_connected": bool(
                live_transition_evidence
                and live_transition_evidence.get("result") == "passed"
            ),
            "revised_diagnostic_only": snapshot.get("data_mode")
            == "revised_diagnostic",
            "watch_confirmation_separated": True,
            "frontend_database_access_allowed": False,
        },
        "allowed_uses": [
            "private_nas_cycle_orientation",
            "transition_input_readiness_review",
            "indicator_navigation",
            "data_health_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_inference",
            "transition_confirmation_from_raw_values",
            "candidate_phase_selection",
            "personalized_portfolio_instruction",
            "trade_action",
        ],
        "development_next_phase": (
            124
            if live_transition_evidence is not None
            else int(contract["hard_gates"]["development_next_phase"])
        ),
    }
    command_center["nas_cycle_command_center_contract_ready"] = _contract_ready(
        contract
    )
    command_center["prohibited_output_field_count"] = _contains_prohibited_field(
        command_center
    )
    command_center["cycle_command_center_view_model_ready"] = (
        command_center["nas_cycle_command_center_contract_ready"]
        and command_center["prohibited_output_field_count"] == 0
        and len(lanes) == 4
        and len(key_indicators) == 5
        and phase == "boom"
        and legal_next == "recession"
    )
    command_center["result"] = (
        "passed" if command_center["cycle_command_center_view_model_ready"] else "blocked"
    )
    return command_center


def summarize_nas_cycle_command_center(
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Return the Phase 120 hard-gate summary."""

    view = build_nas_cycle_command_center(snapshot)
    return {
        "phase": 120,
        "nas_cycle_command_center_contract_ready": view[
            "nas_cycle_command_center_contract_ready"
        ],
        "cycle_command_center_view_model_ready": view[
            "cycle_command_center_view_model_ready"
        ],
        "declared_current_phase": view["declared_state"][
            "declared_current_phase"
        ],
        "legal_next_phase": view["declared_state"]["legal_next_phase"],
        "legal_cycle_order_valid": [
            row["phase_id"] for row in view["cycle_order"]
        ]
        == ["recession", "recovery", "growth", "boom"],
        "navigation_item_count": len(view["navigation"]),
        "enabled_navigation_item_count": sum(
            row["enabled"] is True for row in view["navigation"]
        ),
        "transition_lane_count": len(view["transition_lanes"]),
        "key_indicator_count": len(view["key_indicators"]),
        "live_transition_evaluator_connected": view[
            "live_transition_evaluator_connected"
        ],
        "transition_conclusion_output_count": view[
            "transition_conclusion_output_count"
        ],
        "watch_promoted_to_confirmation_count": view[
            "watch_promoted_to_confirmation_count"
        ],
        "raw_value_promoted_to_evidence_count": view[
            "raw_value_promoted_to_evidence_count"
        ],
        "candidate_phase_emitted": view["candidate_phase_emitted"],
        "current_phase_emitted": view["current_phase_emitted"],
        "standalone_classifier_added_count": view[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": view[
            "phase_rank_or_score_added_count"
        ],
        "production_behavior_change_count": view[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": view["semantic_drift_count"],
        "development_next_phase": view["development_next_phase"],
        "result": view["result"],
        "command_center": view,
    }


def _lane_view(
    lane: dict[str, Any],
    *,
    roles: dict[str, dict[str, Any]],
    role_labels: dict[str, str],
    live_lane: dict[str, Any] | None = None,
) -> dict[str, Any]:
    role_rows = [roles[role_id] for role_id in lane["required_role_ids"]]
    available = sum(
        row["snapshot_status"] == "revised_snapshot_ready" for row in role_rows
    )
    stale = sum(row.get("freshness_status") == "stale" for row in role_rows)
    missing = len(role_rows) - available
    if missing:
        input_status = "missing_required_input"
        status_zh = "核心資料不完整，暫不判讀"
    elif stale:
        input_status = "stale_input_evaluation_pending"
        status_zh = "資料可能過期，等待規則評估"
    else:
        input_status = "input_ready_evaluation_pending"
        status_zh = "資料已到位，等待即時 evidence evaluator"
    row = {
        "lane_id": lane["lane_id"],
        "title_zh": lane["title_zh"],
        "lane_type": lane["lane_type"],
        "purpose_zh": lane["purpose_zh"],
        "required_role_ids": list(lane["required_role_ids"]),
        "required_role_count": len(role_rows),
        "available_input_count": available,
        "missing_input_count": missing,
        "stale_input_count": stale,
        "input_readiness_status": input_status,
        "display_status_zh": status_zh,
        "evidence_evaluation_status": "not_evaluated_in_live_runtime",
        "transition_conclusion_emitted": False,
        "watch_is_confirmation": False,
    }
    if live_lane is None:
        return row
    lane_status = str(live_lane["lane_status"])
    row |= {
        "evidence_evaluation_status": lane_status,
        "display_status_zh": _live_lane_status_zh(lane_status),
        "supportive_evidence_count": live_lane["supportive_evidence_count"],
        "contradictory_evidence_count": live_lane[
            "contradictory_evidence_count"
        ],
        "mixed_evidence_count": live_lane["mixed_evidence_count"],
        "abstained_evidence_count": live_lane["abstained_evidence_count"],
        "evidence_items": [
            {
                **item,
                "display_name_zh": role_labels[str(item["role_id"])],
            }
            for item in live_lane["evidence_items"]
        ],
        "why_not_confirmation": list(live_lane["why_not_confirmation"]),
        "transition_conclusion_emitted": False,
    }
    return row


def _indicator_view(
    row: dict[str, Any],
    label: str,
    *,
    live_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    latest = row.get("latest_revised_observations", [])
    observation = latest[0] if latest else {}
    interpreted = row.get("latest_interpretation_observations", [])
    interpretation = interpreted[0] if interpreted else {}
    value = interpretation.get("value_numeric")
    if value is None and not row.get("learning_semantics"):
        value = observation.get("value_numeric")
    if value is None and not row.get("learning_semantics"):
        value = observation.get("value_text")
    return {
        "role_id": row["role_id"],
        "display_name_zh": label,
        "latest_observation_date": interpretation.get("observation_date")
        or observation.get("observation_date"),
        "latest_value": value,
        "latest_unit": interpretation.get("unit"),
        "display_transform": row.get("learning_semantics", {}).get(
            "transform_profile_id"
        ),
        "snapshot_status": row["snapshot_status"],
        "freshness_status": row.get("freshness_status", "unavailable"),
        "chart_available": row.get("chart_payload_detail", {}).get(
            "chart_available",
            False,
        ),
        "detail_path": f"/indicators#role-{row['role_id']}",
        "raw_value_is_phase_evidence": False,
        "live_evidence_status": (
            live_evidence.get("evidence_status") if live_evidence else None
        ),
        "live_evidence_abstention_reason": (
            live_evidence.get("abstention_reason") if live_evidence else None
        ),
    }


def _live_lane_status_zh(status: str) -> str:
    return {
        "supportive_evidence_present": "已有支持證據（研究用，不改變 declared state）",
        "contradictory_evidence_present": "目前證據反對此 lane",
        "mixed_evidence": "證據互相矛盾，維持 mixed",
        "incomplete_evidence": "證據不完整，明確 abstain",
        "explicit_abstention": "缺少可判讀證據，明確 abstain",
        "neutral_evidence": "目前證據中性，未形成方向",
    }.get(status, status)


def _data_health(snapshot: dict[str, Any]) -> dict[str, Any]:
    rows = list(snapshot["role_snapshots"])
    freshness = [str(row.get("freshness_status", "unavailable")) for row in rows]
    refresh = dict(snapshot.get("refresh_status", {}))
    return {
        "snapshot_as_of": snapshot.get("snapshot_as_of"),
        "database_latest_observation_date": snapshot.get(
            "database_latest_observation_date"
        ),
        "data_mode": snapshot.get("data_mode", "revised_diagnostic"),
        "role_count": len(rows),
        "available_role_count": int(snapshot["role_with_revised_snapshot_count"]),
        "blocked_role_count": int(snapshot["role_without_revised_snapshot_count"]),
        "fresh_role_count": freshness.count("fresh"),
        "stale_role_count": freshness.count("stale"),
        "mixed_role_count": freshness.count("mixed"),
        "unavailable_freshness_role_count": freshness.count("unavailable"),
        "chart_available_role_count": int(snapshot.get("chart_available_role_count", 0)),
        "refresh_state": refresh.get("refresh_state", "not_started"),
        "last_completed_at_utc": refresh.get("last_completed_at_utc"),
        "next_scheduled_at_utc": refresh.get("next_scheduled_at_utc"),
        "source_refresh_health_status": snapshot.get(
            "source_refresh_health_status",
            "unavailable",
        ),
    }


def _load_role_labels(path: str | Path) -> dict[str, str]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {
        str(key): str(value)
        for key, value in payload["book_core_role_display_labels_zh"]["roles"].items()
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active_research_contract"
        and contract["output_policy"]["language"] == "zh-Hant-TW"
        and contract["output_policy"]["declared_state_not_inferred"] is True
        and contract["output_policy"]["live_transition_evaluator_connected"] is False
        and len(contract["navigation"]) == 7
        and len(contract["transition_lanes"]) == 4
        and len(contract["key_indicator_role_ids"]) == 5
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(key in PROHIBITED_FIELDS for key in value) + sum(
            _contains_prohibited_field(item) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0
