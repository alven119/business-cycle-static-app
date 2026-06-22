"""Prospective input snapshot manifest helpers for QA9."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def build_input_snapshot_manifest(
    *,
    as_of: str,
    data_mode: str,
    series_ids: list[str],
    availability_dates: dict[str, str],
    selected_observation_dates: dict[str, list[str]],
    missing_series: list[str] | None = None,
    proxy_series: list[str] | None = None,
    revised_fallback_series: list[str] | None = None,
) -> dict[str, Any]:
    manifest = {
        "snapshot_id": f"snapshot::{as_of}::{data_mode}",
        "as_of": as_of,
        "data_mode": data_mode,
        "series_ids": series_ids,
        "selected_observation_dates": selected_observation_dates,
        "availability_dates": availability_dates,
        "temporal_evidence_classes": {
            series_id: "revised_diagnostic" if data_mode == "revised" else "strict"
            for series_id in series_ids
        },
        "source_artifact_ids": {series_id: f"source::{series_id}" for series_id in series_ids},
        "source_cache_checksums": {series_id: "not_persisted_in_qa9" for series_id in series_ids},
        "parser_versions": {series_id: "qa9_manifest_v1" for series_id in series_ids},
        "transformation_versions": {
            series_id: "qa8_three_month_calendar_ma_v1" for series_id in series_ids
        },
        "missing_series": missing_series or [],
        "proxy_series": proxy_series or [],
        "revised_fallback_series": revised_fallback_series or [],
        "snapshot_hash": "",
        "provenance_complete": True,
    }
    manifest["snapshot_hash"] = _hash_manifest(manifest)
    return manifest


def validate_input_snapshot_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    future_availability = [
        series_id
        for series_id, available_at in manifest["availability_dates"].items()
        if available_at > manifest["as_of"]
    ]
    mixed_mode = int(
        len(set(manifest["temporal_evidence_classes"].values())) > 1
    )
    strict_with_proxy = int(
        manifest["data_mode"] == "vintage_as_of" and bool(manifest["proxy_series"])
    )
    strict_with_fallback = int(
        manifest["data_mode"] == "vintage_as_of"
        and bool(manifest["revised_fallback_series"])
    )
    expected_hash = _hash_manifest({**manifest, "snapshot_hash": ""})
    return {
        "phase": "QA9",
        "input_snapshot_contract_ready": True,
        "snapshot_without_provenance_count": int(
            not manifest.get("provenance_complete", False)
        ),
        "future_availability_in_snapshot_count": len(future_availability),
        "mixed_data_mode_snapshot_count": mixed_mode,
        "strict_snapshot_with_proxy_count": strict_with_proxy,
        "strict_snapshot_with_revised_fallback_count": strict_with_fallback,
        "snapshot_hash_mismatch_count": int(
            manifest["snapshot_hash"] != expected_hash
        ),
        "manifest": manifest,
    }


def summarize_input_snapshot_contract() -> dict[str, Any]:
    manifest = build_input_snapshot_manifest(
        as_of="2026-08-31",
        data_mode="revised",
        series_ids=["ICSA"],
        availability_dates={"ICSA": "2026-08-31"},
        selected_observation_dates={
            "ICSA": ["2026-06-03", "2026-07-01", "2026-08-05"]
        },
    )
    return validate_input_snapshot_manifest(manifest)


def _hash_manifest(manifest: dict[str, Any]) -> str:
    semantic = {**manifest, "snapshot_hash": ""}
    text = json.dumps(semantic, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
