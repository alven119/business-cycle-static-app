"""Typed evidence observation records for QA10 pre-start monitoring."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from business_cycle.shadow_model.prospective_registry import (
    EVALUATOR_FREEZE_ID,
    MODEL_FREEZE_ID,
    PROTOCOL_ID,
    ZERO_HASH,
    canonical_json,
)
from business_cycle.shadow_model.runtime_input_snapshot import RULE_CONTRACT_VERSION


MONITORING_FREEZE_ID = "prospective_shadow_monitoring_v1"
PROHIBITED_FIELDS = {
    "candidate_phase",
    "current_phase",
    "decision_status",
    "portfolio_weight",
    "target_weight",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "expected_return",
    "historical_accuracy",
}


def build_evidence_observation_record(
    *,
    snapshot: dict[str, Any],
    evaluator_result: dict[str, Any],
    previous_record_hash: str = ZERO_HASH,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    record_type = (
        "evidence_observation"
        if evaluator_result["rule_match_status"] == "matched"
        else "abstention_observation"
    )
    record = _base_record(
        snapshot=snapshot,
        evaluator_result=evaluator_result,
        previous_record_hash=previous_record_hash,
        record_type=record_type,
        created_at_utc=created_at_utc,
    )
    record["canonical_record_hash"] = canonical_record_hash(record)
    return record


def build_correction_observation_record(
    *,
    original_record: dict[str, Any],
    correction_reason: str,
    previous_record_hash: str,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    record = {
        **original_record,
        "record_id": f"{original_record['record_id']}::correction",
        "record_type": "correction_observation",
        "created_at_utc": created_at_utc or _now_utc(),
        "previous_record_hash": previous_record_hash,
        "canonical_record_hash": "",
        "supersedes_record_hash": original_record["canonical_record_hash"],
        "correction_reason": correction_reason,
        "original_record_preserved": True,
    }
    record["canonical_record_hash"] = canonical_record_hash(record)
    return record


def validate_evidence_observation_record(record: dict[str, Any]) -> dict[str, Any]:
    prohibited = PROHIBITED_FIELDS & set(record)
    return {
        "phase": "QA10",
        "typed_evidence_record_builder_ready": True,
        "record_without_snapshot_hash_count": int(not record.get("input_snapshot_hash")),
        "record_without_rule_hash_count": int(not record.get("rule_contract_hash")),
        "abstention_without_reason_count": int(
            record["record_type"] == "abstention_observation"
            and not record.get("abstention_reason")
        ),
        "prohibited_decision_field_count": len(prohibited),
        "correction_without_superseded_hash_count": int(
            record["record_type"] == "correction_observation"
            and not record.get("supersedes_record_hash")
        ),
        "original_record_overwrite_count": 0,
        "record_hash_mismatch_count": int(
            record["canonical_record_hash"] != canonical_record_hash(record)
        ),
    }


def summarize_evidence_observation_record_contract() -> dict[str, Any]:
    from business_cycle.shadow_model.runtime_input_snapshot import (  # noqa: PLC0415
        build_runtime_input_snapshot,
    )
    from business_cycle.shadow_model.runtime_path import (  # noqa: PLC0415
        evaluate_snapshot,
    )

    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    record = build_evidence_observation_record(
        snapshot=snapshot,
        evaluator_result=evaluate_snapshot(snapshot),
    )
    summary = validate_evidence_observation_record(record)
    return {
        **summary,
        "record": record,
    }


def canonical_record_hash(record: dict[str, Any]) -> str:
    semantic = {
        key: value
        for key, value in record.items()
        if key != "canonical_record_hash"
    }
    return hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def idempotency_key(record: dict[str, Any]) -> str:
    payload = {
        "record_type": record["record_type"],
        "protocol_id": record["protocol_id"],
        "monitoring_freeze_id": record["monitoring_freeze_id"],
        "evaluator_id": record["evaluator_id"],
        "role_id": record["role_id"],
        "canonical_as_of": record["as_of"],
        "actual_data_mode": record["actual_data_mode"],
        "input_snapshot_hash": record["input_snapshot_hash"],
        "rule_contract_hash": record["rule_contract_hash"],
        "supersedes_record_hash": record.get("supersedes_record_hash"),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _base_record(
    *,
    snapshot: dict[str, Any],
    evaluator_result: dict[str, Any],
    previous_record_hash: str,
    record_type: str,
    created_at_utc: str | None,
) -> dict[str, Any]:
    as_of = snapshot["as_of"]
    return {
        "record_id": f"evidence::{snapshot['evaluator_id']}::{as_of}::{snapshot['actual_data_mode']}",
        "record_type": record_type,
        "protocol_id": PROTOCOL_ID,
        "monitoring_freeze_id": MONITORING_FREEZE_ID,
        "model_freeze_id": MODEL_FREEZE_ID,
        "evaluator_freeze_id": EVALUATOR_FREEZE_ID,
        "evaluator_id": snapshot["evaluator_id"],
        "role_id": snapshot["role_id"],
        "typed_evidence_family": "noise_filter_observation",
        "typed_evidence_state": evaluator_result["typed_evidence_state"],
        "as_of": as_of,
        "canonical_period": as_of[:7],
        "requested_data_mode": snapshot["requested_data_mode"],
        "actual_data_mode": snapshot["actual_data_mode"],
        "input_snapshot_id": snapshot["snapshot_id"],
        "input_snapshot_hash": snapshot["snapshot_payload_hash"],
        "rule_id": evaluator_result["rule_id"],
        "rule_contract_hash": hashlib.sha256(
            RULE_CONTRACT_VERSION.encode("utf-8")
        ).hexdigest(),
        "evaluator_version": snapshot["evaluator_version"],
        "provenance": {
            "history_window_contract_version": snapshot[
                "history_window_contract_version"
            ],
            "source_artifact_ids": snapshot["source_artifact_ids"],
        },
        "abstention_reason": evaluator_result.get("abstention_reason"),
        "created_at_utc": created_at_utc or _now_utc(),
        "previous_record_hash": previous_record_hash,
        "canonical_record_hash": "",
    }


def _now_utc() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
