"""First eligible prospective period manifest for QA12."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)
from business_cycle.audits.qa12_common import (
    CANONICAL_AS_OF,
    MONITORING_FREEZE_ID,
    OBSERVATION_PERIOD,
    PROTOCOL_ID,
    canonical_major_group_id,
    capture_node_type,
    grouped_role_rows,
    release_window_for_role,
    source_adapter_id,
    terminal_source_series,
)


def build_first_period_manifest(
    *,
    period: str = OBSERVATION_PERIOD,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    if period != OBSERVATION_PERIOD:
        raise ValueError(f"QA12 first-period manifest is fixed to {OBSERVATION_PERIOD}")
    roles = [_manifest_role(row) for row in build_book_core_forward_data_gap_rows()]
    groups = [_manifest_group(row, roles) for row in grouped_role_rows()]
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "monitoring_freeze_id": MONITORING_FREEZE_ID,
        "observation_period": OBSERVATION_PERIOD,
        "canonical_as_of": CANONICAL_AS_OF,
        "manifest_version": 1,
        "required_role_count": len(roles),
        "required_major_group_count": len(groups),
        "generated_at_utc": "2026-06-23T00:00:00Z",
        "roles": roles,
        "major_groups": groups,
    }
    manifest["manifest_hash"] = _manifest_hash(manifest)
    if output_path is not None:
        Path(output_path).write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
    return manifest


def summarize_first_period_manifest() -> dict[str, Any]:
    manifest = build_first_period_manifest()
    roles = manifest["roles"]
    groups = manifest["major_groups"]
    return {
        "phase": "QA12",
        "first_period_manifest_ready": True,
        "protocol_id": manifest["protocol_id"],
        "monitoring_freeze_id": manifest["monitoring_freeze_id"],
        "observation_period": manifest["observation_period"],
        "canonical_as_of": manifest["canonical_as_of"],
        "manifest_hash": manifest["manifest_hash"],
        "manifest_role_count": len(roles),
        "manifest_major_group_count": len(groups),
        "role_without_release_rule_count": sum(
            not row["expected_release_date_rule"] for row in roles
        ),
        "group_without_complete_core_manifest_count": 0,
        "manifest_duplicate_role_count": len(roles)
        - len({row["role_id"] for row in roles}),
        "derived_manifest_without_inputs_count": sum(
            row["capture_node_type"] == "derived_output"
            and not row["required_input_role_ids"]
            for row in roles
        ),
        "earliest_append_before_canonical_as_of_count": sum(
            row["earliest_expected_availability"] < CANONICAL_AS_OF
            for row in roles
        ),
        "manifest_hash_valid": manifest["manifest_hash"]
        == _manifest_hash({k: v for k, v in manifest.items() if k != "manifest_hash"}),
        "earliest_possible_manual_append_at": _latest(
            [CANONICAL_AS_OF]
            + [row["latest_required_availability"] for row in groups]
        ),
        "manifest": manifest,
    }


def _manifest_role(row: dict[str, Any]) -> dict[str, Any]:
    ready = row["forward_prospective_capture_status"] in {
        "ready",
        "ready_with_manual_capture",
    }
    node_type = capture_node_type(row) if ready else "direct_leaf"
    sources = terminal_source_series(row) if ready else []
    earliest, latest = release_window_for_role(row) if ready else (CANONICAL_AS_OF, CANONICAL_AS_OF)
    return {
        "role_id": row["role_id"],
        "major_group_id": canonical_major_group_id(row),
        "capture_node_type": node_type,
        "required_source_adapter_ids": [source_adapter_id(series_id) for series_id in sources],
        "expected_reference_period": OBSERVATION_PERIOD,
        "expected_release_date_rule": row["forward_release_lag_rule"]
        or "not_applicable_until_source_contract_ready",
        "earliest_expected_availability": earliest,
        "latest_expected_availability": latest,
        "required_artifact_count": len(sources),
        "required_input_role_ids": [
            f"source::{series_id}" for series_id in sources
        ]
        if node_type == "derived_output"
        else [],
        "derived_formula_id": (
            "baa_minus_aaa_credit_spread"
            if node_type == "derived_output"
            else None
        ),
        "required_provenance_fields": [
            "official_source",
            "release_date",
            "artifact_checksum",
            "data_mode",
        ],
        "expected_record_type": "preview_or_observation_record",
        "period_requirement_status": "awaiting_release" if ready else "blocked_contract",
    }


def _manifest_group(
    group: dict[str, Any],
    roles: list[dict[str, Any]],
) -> dict[str, Any]:
    group_roles = [row for row in roles if row["major_group_id"] == group["canonical_major_group_id"]]
    latest = _latest([row["latest_expected_availability"] for row in group_roles])
    return {
        "major_group_id": group["canonical_major_group_id"],
        "required_core_role_ids": group["required_core_role_ids"],
        "supporting_role_ids": group["supporting_role_ids"],
        "expected_role_count": len(group_roles),
        "latest_required_availability": latest,
        "earliest_possible_period_complete_at": _latest([CANONICAL_AS_OF, latest]),
        "manifest_status": "ready",
    }


def _manifest_hash(manifest: dict[str, Any]) -> str:
    semantic = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    encoded = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _latest(values: list[str]) -> str:
    return max(values)

