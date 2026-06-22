"""QA4 current v1 versus proposed v2 scope diff."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_faithful_scope import (
    summarize_book_faithful_formal_model_scope,
)
from business_cycle.audits.formal_indicator_scope_matrix import (
    build_formal_indicator_scope_matrix,
)


def summarize_formal_model_scope_diff() -> dict[str, Any]:
    """Return QA4 scope diff without changing production behavior."""

    matrix = build_formal_indicator_scope_matrix()
    scope = summarize_book_faithful_formal_model_scope()
    rows = [_diff_row(row) for row in matrix]
    return {
        "phase": "QA4",
        "formal_scope_diff_ready": True,
        "current_formal_v1_indicator_count": sum(
            row["current_formal_v1"] for row in matrix if row["row_type"] == "existing_indicator"
        ),
        "proposed_v2_core_role_count": scope["book_core_scope_item_count"],
        "retained_v1_indicator_count": sum(
            row["scope_classification"] == "retain_in_proposed_v2" for row in matrix
        ),
        "v1_to_supporting_count": sum(
            row["scope_classification"] == "demote_to_supporting" for row in matrix
        ),
        "v1_modern_extension_count": sum(
            row["scope_classification"] == "retain_as_modern_extension"
            and row["current_formal_v1"]
            for row in matrix
        ),
        "proposed_v2_experimental_candidate_count": sum(
            row["scope_classification"] == "experimental_candidate_for_v2"
            for row in matrix
        ),
        "proposed_v2_missing_role_count": sum(
            row["scope_classification"] == "missing_book_core_role" for row in matrix
        ),
        "proposed_v2_temporal_blocked_count": sum(
            row["vintage_status"] in {"missing", "not_mapped"} for row in matrix
        ),
        "proposed_v2_data_contract_blocked_count": sum(
            "adp" in row["indicator_or_role_id"] for row in matrix
        ),
        "proposed_v2_independent_validation_blocked_count": sum(
            row["scope_classification"]
            in {"experimental_candidate_for_v2", "missing_book_core_role"}
            for row in matrix
        ),
        "production_behavior_change_count": 0,
        "rows": rows,
    }


def _diff_row(row: dict[str, Any]) -> dict[str, Any]:
    classification = row["scope_classification"]
    if classification == "retain_in_proposed_v2":
        change_type = "retain"
        implementation_required = False
    elif classification == "demote_to_supporting":
        change_type = "v1_to_supporting_scope"
        implementation_required = True
    elif classification == "retain_as_modern_extension":
        change_type = "retain_as_modern_extension"
        implementation_required = False
    elif classification == "experimental_candidate_for_v2":
        change_type = "candidate_not_promoted"
        implementation_required = True
    elif classification == "missing_book_core_role":
        change_type = "missing_book_core_role"
        implementation_required = True
    else:
        change_type = "scope_review_required"
        implementation_required = True
    return {
        "scope_item_id": row["indicator_or_role_id"],
        "current_v1_status": "formal_v1"
        if row["current_formal_v1"]
        else "experimental"
        if row["current_experimental"]
        else "missing",
        "proposed_v2_status": classification,
        "change_type": change_type,
        "reason": row["reason"],
        "book_requirement_id": row["indicator_or_role_id"].removeprefix(
            "missing_role::"
        ),
        "implementation_required": implementation_required,
        "decision_behavior_changed_now": False,
    }

