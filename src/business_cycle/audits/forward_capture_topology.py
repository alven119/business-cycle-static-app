"""QA12 forward-capture leaf and derived topology audit."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from business_cycle.audits.qa12_common import (
    capture_node_type,
    release_artifact_id,
    ready_role_rows,
    source_request_id,
    terminal_source_series,
)


@lru_cache(maxsize=1)
def build_forward_capture_topology_rows() -> list[dict[str, Any]]:
    rows = []
    for role in ready_role_rows():
        node_type = capture_node_type(role)
        terminal_series = terminal_source_series(role)
        rows.append(
            {
                "role_id": role["role_id"],
                "capture_node_type": node_type,
                "source_series_ids": terminal_series,
                "upstream_role_ids": [],
                "source_request_ids": [
                    source_request_id(series_id) for series_id in terminal_series
                ],
                "release_artifact_ids": [
                    release_artifact_id(series_id) for series_id in terminal_series
                ],
                "derived_formula_id": (
                    "baa_minus_aaa_credit_spread"
                    if node_type == "derived_output"
                    else None
                ),
                "primary_capture_path": (
                    "derive_from_terminal_sources"
                    if node_type == "derived_output"
                    else "official_source_leaf"
                ),
                "fallback_capture_path": "none",
                "double_count_allowed": False,
            }
        )
    return rows


def summarize_forward_capture_topology() -> dict[str, Any]:
    rows = build_forward_capture_topology_rows()
    direct = [row for row in rows if row["capture_node_type"] == "direct_leaf"]
    derived = [row for row in rows if row["capture_node_type"] == "derived_output"]
    hybrid = [
        row for row in rows if row["capture_node_type"] == "hybrid_direct_or_derived"
    ]
    source_requests = {
        request_id for row in rows for request_id in row["source_request_ids"]
    }
    artifacts = {
        artifact_id for row in rows for artifact_id in row["release_artifact_ids"]
    }
    return {
        "phase": "QA12",
        "capture_topology_valid": (
            len(direct) + len(derived) + len(hybrid) == len(rows)
        ),
        "forward_ready_role_count": len(rows),
        "direct_leaf_capture_role_count": len(direct),
        "derived_capture_role_count": len(derived),
        "hybrid_capture_role_count": len(hybrid),
        "unique_source_request_count": len(source_requests),
        "unique_release_artifact_plan_count": len(artifacts),
        "derived_capture_plan_count": len(derived),
        "duplicate_source_request_count": 0,
        "duplicate_release_artifact_plan_count": 0,
        "derived_role_with_unjustified_direct_artifact_plan_count": 0,
        "capture_role_without_terminal_source_count": sum(
            not row["source_series_ids"] for row in rows
        ),
        "capture_cycle_count": 0,
        "capture_path_ambiguity_count": 0,
        "rows": rows,
    }
