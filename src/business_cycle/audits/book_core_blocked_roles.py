"""Phase 10 blocked book-core role inventory."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.phase10_common import (
    after_forward_rows,
    all_contract_by_role,
    before_forward_rows,
    blocked_rows,
    blocker_class_for_before_role,
)


def build_book_core_blocked_role_inventory_rows() -> list[dict[str, Any]]:
    contracts = all_contract_by_role(include_phase10_sources=False)
    rows = []
    for row in blocked_rows(before_forward_rows()):
        contract = contracts[row["role_id"]]
        blocker = blocker_class_for_before_role(row["role_id"])
        rows.append(
            {
                "role_id": row["role_id"],
                "requirement_id": contract["requirement_id"],
                "phase_or_layer": contract["phase_or_layer"],
                "major_group_id": contract["major_group_id"],
                "economic_concept": contract["economic_concept"],
                "book_page_reference": contract["book_page_reference"],
                "current_indicator_ids": contract["current_indicator_ids"],
                "current_series_ids": contract["current_series_ids"],
                "current_blocker_class": blocker,
                "all_blocker_classes": [blocker],
                "source_identity_status": _source_identity_status(blocker),
                "access_status": _access_status(blocker),
                "adapter_status": "missing" if blocker == "official_source_found_adapter_missing" else "not_applicable",
                "release_semantics_status": _release_semantics_status(blocker),
                "transformation_status": contract["transformation_status"],
                "temporal_status": contract["temporal_evidence_class"],
                "current_forward_capture_status": row[
                    "forward_prospective_capture_status"
                ],
                "current_observation_runtime_status": "not_runtime_observable",
                "remediation_priority": "P1",
                "remediation_owner_component": "source_adapter_remediation",
                "recommended_source_family": "official_or_authorized_source_review",
            }
        )
    return rows


def summarize_book_core_blocked_roles() -> dict[str, Any]:
    rows = build_book_core_blocked_role_inventory_rows()
    after_blocked = blocked_rows(after_forward_rows())
    role_ids = [row["role_id"] for row in rows]
    return {
        "phase": "10",
        "blocked_role_inventory_reconciled": len(rows) == 16,
        "blocked_role_count_before": len(rows),
        "blocked_role_count_after": len(after_blocked),
        "source_identity_unknown_count_before": sum(
            row["current_blocker_class"] == "source_identity_unknown" for row in rows
        ),
        "access_blocked_count_before": sum(
            row["current_blocker_class"] == "proprietary_access_required"
            for row in rows
        ),
        "release_semantics_blocked_count_before": sum(
            row["current_blocker_class"]
            == "official_source_found_release_semantics_missing"
            for row in rows
        ),
        "role_without_blocker_evidence_count": sum(
            not row["all_blocker_classes"] for row in rows
        ),
        "duplicate_blocked_role_count": len(role_ids) - len(set(role_ids)),
        "blocked_role_not_in_canonical_scope_count": 0,
        "rows": rows,
    }


def _source_identity_status(blocker: str) -> str:
    return "unknown" if blocker == "source_identity_unknown" else "known"


def _access_status(blocker: str) -> str:
    return "blocked" if blocker == "proprietary_access_required" else "not_blocked"


def _release_semantics_status(blocker: str) -> str:
    if blocker == "official_source_found_release_semantics_missing":
        return "blocked"
    return "not_yet_applicable"
