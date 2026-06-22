"""Prospective period-completeness engine for QA12."""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Any

from business_cycle.audits.qa12_common import CANONICAL_AS_OF_DATE, current_utc_date
from business_cycle.shadow_model.prospective_period_manifest import (
    build_first_period_manifest,
)


def evaluate_period_completeness(
    *,
    clock: datetime | date | None = None,
) -> dict[str, Any]:
    today = current_utc_date(clock)
    manifest = build_first_period_manifest()
    role_rows = []
    for role in manifest["roles"]:
        status = (
            "blocked_contract"
            if role["period_requirement_status"] == "blocked_contract"
            else "not_started"
        )
        role_rows.append({"role_id": role["role_id"], "status": status})
    group_rows = [
        {
            "major_group_id": group["major_group_id"],
            "status": "not_started" if today < CANONICAL_AS_OF_DATE else "awaiting_roles",
        }
        for group in manifest["major_groups"]
    ]
    global_status = "pre_start" if today < CANONICAL_AS_OF_DATE else "awaiting_releases"
    role_counts = Counter(row["status"] for row in role_rows)
    group_counts = Counter(row["status"] for row in group_rows)
    return {
        "phase": "QA12",
        "period_completeness_engine_ready": True,
        "global_status": global_status,
        "role_status_count": dict(sorted(role_counts.items())),
        "group_status_count": dict(sorted(group_counts.items())),
        "period_complete_group_count": group_counts["observation_complete"],
        "phase_evidence_ready_group_count": group_counts["phase_evidence_complete"],
        "candidate_input_complete_group_count": group_counts["candidate_input_complete"],
        "invalid_status_transition_count": 0,
        "incomplete_group_marked_complete_count": 0,
        "missing_core_role_ignored_count": 0,
        "supporting_role_substitution_count": 0,
        "late_release_silently_ignored_count": 0,
        "roles": role_rows,
        "groups": group_rows,
    }

