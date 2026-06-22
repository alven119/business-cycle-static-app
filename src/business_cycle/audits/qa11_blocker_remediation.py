"""QA11 remediation registry for forward-data blockers."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)


def build_qa11_blocker_remediation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for role in build_book_core_forward_data_gap_rows():
        status = role["forward_prospective_capture_status"]
        if status in {"ready", "ready_with_manual_capture"}:
            continue
        blocker_class = _blocker_class(status)
        rows.append(
            {
                "blocker_id": f"qa11_blocker::{role['role_id']}",
                "role_id": role["role_id"],
                "blocker_class": blocker_class,
                "evidence": ";".join(role["unresolved_reasons"]),
                "required_artifact_or_adapter": _required_artifact(blocker_class),
                "resolution_changes_model_semantics": blocker_class
                in {"source_identity", "transformation"},
                "resolution_requires_new_rule_version": blocker_class
                in {"release_semantics", "transformation"},
                "resolution_requires_new_freeze": True,
                "recommended_next_action": role["remediation_work_package"],
                "substitution_requires_equivalence_review": True,
            }
        )
    return rows


def summarize_qa11_blocker_remediation() -> dict[str, Any]:
    rows = build_qa11_blocker_remediation_rows()
    without_remediation = [row for row in rows if not row["recommended_next_action"]]
    ignored = [row for row in rows if not row["evidence"]]
    substitution_without_review = [
        row
        for row in rows
        if not row["substitution_requires_equivalence_review"]
    ]
    return {
        "phase": "QA11",
        "blocker_remediation_registry_ready": not without_remediation
        and not ignored
        and not substitution_without_review,
        "unresolved_blocker_count": len(rows),
        "blocker_without_remediation_count": len(without_remediation),
        "blocker_silently_ignored_count": len(ignored),
        "substitution_proposed_without_equivalence_review_count": len(
            substitution_without_review
        ),
        "blockers": rows,
    }


def _blocker_class(status: str) -> str:
    return {
        "blocked_source_identity": "source_identity",
        "blocked_access": "access",
        "blocked_adapter": "adapter",
        "blocked_release_semantics": "release_semantics",
    }.get(status, "transformation")


def _required_artifact(blocker_class: str) -> str:
    return {
        "source_identity": "official_source_identity_review",
        "access": "authorized_data_access_decision",
        "adapter": "official_adapter_with_fake_http_fixtures",
        "release_semantics": "release_revision_correction_contract",
        "transformation": "transformation_or_rule_preregistration",
    }[blocker_class]
