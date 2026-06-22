"""Phase-level shadow evidence profiles."""

from __future__ import annotations

from collections import Counter
from typing import Any


PHASE_REQUIRED_GROUPS = {
    "recovery": 4,
    "growth": 4,
    "boom": 7,
    "recession_trough": 9,
}


def build_phase_profiles(role_evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate role evidence into non-decision phase profiles."""

    profiles = []
    for phase, required_group_count in PHASE_REQUIRED_GROUPS.items():
        rows = [row for row in role_evidence if row["phase"] == phase]
        group_profiles = _group_profiles(rows)
        ready_group_count = sum(
            group["ready_role_count"] > 0 for group in group_profiles.values()
        )
        counts = Counter(row["evidence_status"] for row in rows)
        completeness = (
            round(ready_group_count / required_group_count, 4)
            if required_group_count
            else 0.0
        )
        if ready_group_count == required_group_count:
            profile_status = "complete_evidence_profile"
        elif ready_group_count == 0:
            profile_status = "structurally_unavailable"
        else:
            profile_status = "partial_evidence_profile"
        profiles.append(
            {
                "phase_id": phase,
                "required_major_group_count": required_group_count,
                "ready_major_group_count": ready_group_count,
                "incomplete_major_group_count": required_group_count - ready_group_count,
                "supportive_role_count": counts["supportive"],
                "contradictory_role_count": counts["contradictory"],
                "neutral_role_count": counts["neutral"],
                "unavailable_role_count": counts["unavailable"],
                "raw_transform_only_count": counts["raw_transform_only"],
                "major_group_profiles": group_profiles,
                "evidence_completeness_ratio": completeness,
                "shadow_profile_status": profile_status,
                "formal_candidate_phase_computed": False,
            }
        )
    return profiles


def _group_profiles(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    groups = sorted({row["major_group_id"] for row in rows})
    profiles: dict[str, dict[str, int]] = {}
    for group in groups:
        group_rows = [row for row in rows if row["major_group_id"] == group]
        profiles[group] = {
            "role_count": len(group_rows),
            "ready_role_count": sum(
                row["evidence_status"]
                in {"supportive", "contradictory", "neutral", "raw_transform_only"}
                for row in group_rows
            ),
            "unavailable_role_count": sum(
                row["evidence_status"] == "unavailable" for row in group_rows
            ),
        }
    return profiles

