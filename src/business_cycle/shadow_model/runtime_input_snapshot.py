"""Runtime input snapshots for QA10 shadow evaluator execution."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.shadow_model.history_window import (
    build_history_window_request,
    materialize_history_window,
)
from business_cycle.shadow_model.prospective_registry import canonical_json


DEFAULT_RUNTIME_INPUT_SNAPSHOT_CONTRACT_PATH = Path(
    "specs/audits/shadow_runtime_input_snapshot_contract.yaml"
)
EVALUATOR_VERSION = "qa8_three_month_calendar_ma_v1"
RULE_CONTRACT_VERSION = "book_explicit_evaluator_registry_v1"
HISTORY_WINDOW_CONTRACT_VERSION = "shadow_runtime_history_window_contract_v1"


def load_runtime_input_snapshot_contract(
    path: str | Path = DEFAULT_RUNTIME_INPUT_SNAPSHOT_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_runtime_input_snapshot_contract"
    ]


def build_runtime_input_snapshot(
    *,
    as_of: str,
    data_mode: str,
    observations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request = build_history_window_request(
        evaluator_id="evaluator::recovery_weekly_claim_noise_filter",
        role_id="recovery_weekly_claim_noise_filter",
        series_id="ICSA",
        as_of=as_of,
        data_mode=data_mode,
    )
    window = materialize_history_window(request, observations)
    snapshot = {
        "snapshot_id": f"runtime_snapshot::{request.evaluator_id}::{as_of}::{data_mode}",
        "evaluator_id": request.evaluator_id,
        "role_id": request.role_id,
        "as_of": as_of,
        "requested_data_mode": data_mode,
        "actual_data_mode": window["actual_data_mode"],
        "series_ids": [request.series_id],
        "history_windows": [window],
        "source_artifact_ids": [
            row["source_artifact_id"] for row in window["observations"]
        ],
        "temporal_evidence_classes": {
            request.series_id: "strict" if data_mode == "vintage_as_of" else "revised_diagnostic"
        },
        "availability_dates": {
            row["source_artifact_id"]: row["availability_date"]
            for row in window["observations"]
        },
        "latest_observation_dates": {
            request.series_id: window["observations"][-1]["date"]
            if window["observations"]
            else None
        },
        "snapshot_payload_hash": "",
        "contract_hash": _contract_hash(),
        "provenance_complete": window["provenance_complete"],
        "ready_for_evaluator": window["window_status"] == "ready",
        "abstention_reason": window["abstention_reason"],
        "evaluator_version": EVALUATOR_VERSION,
        "rule_contract_version": RULE_CONTRACT_VERSION,
        "history_window_contract_version": HISTORY_WINDOW_CONTRACT_VERSION,
    }
    snapshot["snapshot_payload_hash"] = _payload_hash(snapshot)
    return snapshot


def validate_runtime_input_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    windows = snapshot["history_windows"]
    future = sum(window["future_observation_count"] for window in windows)
    mixed = sum(window["mixed_data_mode_count"] for window in windows)
    proxy = sum(window["proxy_input_count"] for window in windows)
    fallback = sum(window["revised_fallback_count"] for window in windows)
    return {
        "phase": "QA10",
        "runtime_input_snapshot_contract_ready": True,
        "snapshot_without_payload_hash_count": int(
            not snapshot.get("snapshot_payload_hash")
        ),
        "snapshot_without_contract_hash_count": int(not snapshot.get("contract_hash")),
        "snapshot_without_provenance_count": int(
            not snapshot.get("provenance_complete")
            and snapshot.get("abstention_reason") != "temporal_evidence_missing"
        ),
        "snapshot_with_future_data_count": future,
        "snapshot_with_mixed_data_mode_count": mixed,
        "snapshot_with_proxy_count": proxy,
        "strict_snapshot_with_revised_fallback_count": int(
            snapshot["requested_data_mode"] == "vintage_as_of" and fallback > 0
        ),
        "snapshot_hash_mismatch_count": int(
            snapshot["snapshot_payload_hash"]
            != _payload_hash({**snapshot, "snapshot_payload_hash": ""})
        ),
    }


def summarize_runtime_input_snapshot_contract() -> dict[str, Any]:
    snapshot = build_runtime_input_snapshot(as_of="2026-08-31", data_mode="revised")
    return validate_runtime_input_snapshot(snapshot)


def _payload_hash(snapshot: dict[str, Any]) -> str:
    semantic = {
        **snapshot,
        "snapshot_payload_hash": "",
    }
    return hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def _contract_hash() -> str:
    return hashlib.sha256(
        Path(DEFAULT_RUNTIME_INPUT_SNAPSHOT_CONTRACT_PATH).read_bytes()
    ).hexdigest()
