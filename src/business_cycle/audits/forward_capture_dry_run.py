"""QA11 dry-run planning for forward capture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
    summarize_book_core_forward_data_gaps,
)
from business_cycle.shadow_model.forward_capture_contract import (
    summarize_forward_capture_contracts,
)


def preview_book_core_forward_capture(
    *,
    role_id: str | None = None,
    major_group: str | None = None,
    all_forward_ready: bool = False,
    as_of: str | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    rows = build_book_core_forward_data_gap_rows()
    if role_id:
        rows = [row for row in rows if row["role_id"] == role_id]
    if major_group:
        rows = [row for row in rows if row["major_group_id"] == major_group]
    if all_forward_ready:
        rows = [
            row
            for row in rows
            if row["forward_prospective_capture_status"]
            in {"ready", "ready_with_manual_capture"}
        ]
    contracts = summarize_forward_capture_contracts()
    requested = len(rows)
    forward_ready = sum(
        row["forward_prospective_capture_status"] in {"ready", "ready_with_manual_capture"}
        for row in rows
    )
    summary = {
        "phase": "QA11",
        "as_of": as_of,
        "forward_capture_dry_run_ready": True,
        "requested_role_count": requested,
        "forward_ready_role_count": forward_ready,
        "forward_blocked_role_count": requested - forward_ready,
        "source_request_plan_count": forward_ready,
        "release_artifact_plan_count": forward_ready,
        "derived_capture_plan_count": sum(
            any("credit_spread" in series_id for series_id in row["current_series_ids"])
            for row in rows
        ),
        "unresolved_contract_count": contracts[
            "ready_role_without_capture_contract_count"
        ],
        "registry_write_attempted": False,
        "prospective_result_inspected": False,
        "candidate_selection_enabled": False,
    }
    if output:
        Path(output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def summarize_forward_capture_dry_run() -> dict[str, Any]:
    gaps = summarize_book_core_forward_data_gaps()
    preview = preview_book_core_forward_capture(all_forward_ready=True)
    return {
        **preview,
        "requested_role_count": gaps["forward_capture_ready_role_count"]
        + gaps["forward_manual_capture_role_count"],
    }
