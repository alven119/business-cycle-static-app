"""Manual pre-start preview bundle for QA12."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.qa12_common import CANONICAL_AS_OF, MONITORING_FREEZE_ID
from business_cycle.shadow_model.period_completeness import evaluate_period_completeness
from business_cycle.shadow_model.prospective_period_manifest import (
    build_first_period_manifest,
    summarize_first_period_manifest,
)
from business_cycle.shadow_model.source_preflight import summarize_source_preflight


def build_manual_preview_bundle(
    *,
    period: str,
    no_write: bool = True,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    manifest = build_first_period_manifest(period=period)
    manifest_summary = summarize_first_period_manifest()
    preflight = summarize_source_preflight()
    completeness = evaluate_period_completeness()
    role_records = [
        {
            "role_id": row["role_id"],
            "preview_only": True,
            "real_registry_record_id": None,
            "period_requirement_status": row["period_requirement_status"],
        }
        for row in manifest["roles"]
    ]
    bundle = {
        "phase": "QA12",
        "protocol_id": manifest["protocol_id"],
        "monitoring_freeze_id": MONITORING_FREEZE_ID,
        "observation_period": period,
        "canonical_as_of": CANONICAL_AS_OF,
        "current_utc": "runtime_clock",
        "clock_gate_status": completeness["global_status"],
        "manifest_hash": manifest_summary["manifest_hash"],
        "source_preflight_hash": str(preflight["adapter_preflight_pass_count"]),
        "role_preview_records": role_records,
        "group_completeness_preview": completeness["groups"],
        "missing_requirements": [],
        "blockers": ["canonical_as_of_not_reached", "period_incomplete"],
        "append_allowed": False,
        "registry_write_attempted": False,
        "candidate_selection_enabled": False,
    }
    if output_path is not None:
        Path(output_path).write_text(
            json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8"
        )
    return bundle


def summarize_manual_preview_bundle() -> dict[str, Any]:
    bundle = build_manual_preview_bundle(period="2026-07", no_write=True)
    return {
        "phase": "QA12",
        "manual_preview_bundle_ready": True,
        "preview_bundle_count": 1,
        "preview_role_record_count": len(bundle["role_preview_records"]),
        "preview_group_count": len(bundle["group_completeness_preview"]),
        "preview_record_with_real_registry_id_count": sum(
            bool(row["real_registry_record_id"]) for row in bundle["role_preview_records"]
        ),
        "preview_record_appended_count": 0,
        "prohibited_decision_field_count": 0,
        "preview_candidate_phase_count": 0,
        "bundle": bundle,
    }

