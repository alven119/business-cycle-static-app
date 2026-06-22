"""Canonical prospective shadow observation records for QA9."""

from __future__ import annotations

import hashlib
import json
from typing import Any


REGISTRY_ID = "prospective_shadow_observation_registry_v1"
PROTOCOL_ID = "prospective_shadow_candidate_diagnostic_protocol_v1"
MODEL_FREEZE_ID = "book_faithful_shadow_v2_alpha4"
EVALUATOR_FREEZE_ID = "book_faithful_shadow_v2_alpha4"
CANDIDATE_SELECTION_FREEZE_ID = "book_faithful_shadow_v2_alpha3"
AGGREGATION_FREEZE_ID = "book_faithful_shadow_v2_alpha2"
ZERO_HASH = "0" * 64


def canonical_json(payload: dict[str, Any]) -> str:
    """Serialize payload deterministically for hashing."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def semantic_record_hash(record: dict[str, Any]) -> str:
    """Hash all semantic record fields except record_hash itself."""

    semantic = {key: value for key, value in record.items() if key != "record_hash"}
    return hashlib.sha256(canonical_json(semantic).encode("utf-8")).hexdigest()


def build_prospective_record(
    *,
    sequence_number: int,
    previous_record_hash: str,
    observation_period: str,
    as_of: str,
    input_snapshot_manifest_hash: str,
    recorded_at_utc: str = "2026-09-01T00:00:00Z",
    requested_data_mode: str = "revised",
    actual_data_mode: str = "revised",
    candidate_selection_status: str = "disabled",
    candidate_phase: str | None = None,
    inspection_status: str = "metadata_only",
    provenance_complete: bool = True,
    model_freeze_id: str = MODEL_FREEZE_ID,
    protocol_id: str = PROTOCOL_ID,
    protocol_version: int = 1,
) -> dict[str, Any]:
    """Build a canonical prospective shadow observation record."""

    record = {
        "registry_schema_version": 1,
        "registry_id": REGISTRY_ID,
        "record_id": f"{REGISTRY_ID}::{sequence_number:06d}",
        "sequence_number": sequence_number,
        "previous_record_hash": previous_record_hash,
        "record_hash": "",
        "protocol_id": protocol_id,
        "protocol_version": protocol_version,
        "model_freeze_id": model_freeze_id,
        "evaluator_freeze_id": EVALUATOR_FREEZE_ID,
        "candidate_selection_freeze_id": CANDIDATE_SELECTION_FREEZE_ID,
        "aggregation_freeze_id": AGGREGATION_FREEZE_ID,
        "observation_period": observation_period,
        "as_of": as_of,
        "recorded_at_utc": recorded_at_utc,
        "eligible_period_start": "2026-07",
        "first_eligible_complete_as_of": "2026-08-31",
        "requested_data_mode": requested_data_mode,
        "actual_data_mode": actual_data_mode,
        "input_snapshot_manifest_hash": input_snapshot_manifest_hash,
        "source_cache_manifest_hashes": {},
        "source_series_count": 1,
        "source_release_cutoff": as_of,
        "role_evidence_count": 40,
        "evaluator_invoked_count": 1,
        "evaluator_output_available_count": 0,
        "evaluator_abstention_count": 1,
        "raw_transform_only_count": 23,
        "unavailable_role_count": 14,
        "candidate_selection_enabled": False,
        "candidate_selection_status": candidate_selection_status,
        "candidate_phase": candidate_phase,
        "inspection_status": inspection_status,
        "context_prior_used": False,
        "display_hint_used": False,
        "performance_metric_computed": False,
        "portfolio_output_generated": False,
        "public_output_written": False,
        "created_by_code_version": "qa9",
        "provenance_complete": provenance_complete,
    }
    record["record_hash"] = semantic_record_hash(record)
    return record


def summarize_registry_contract() -> dict[str, Any]:
    return {
        "phase": "QA9",
        "registry_contract_ready": True,
        "registry_id": REGISTRY_ID,
        "registry_status": "armed_not_started",
        "canonical_json_hashing": True,
        "append_only": True,
        "overwrite_allowed": False,
        "delete_api_allowed": False,
        "rewrite_api_allowed": False,
        "compact_api_allowed": False,
    }
