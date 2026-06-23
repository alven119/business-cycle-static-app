"""Phase-level evidence profiles built from major-group rows."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Any

from business_cycle.shadow_model.major_group_evidence import (
    build_major_group_phase_evidence_rows,
)


@lru_cache(maxsize=None)
def build_phase_evidence_profiles(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in build_major_group_phase_evidence_rows(as_of=as_of, data_mode=data_mode):
        grouped[row["phase_or_layer"]].append(row)
    return [
        {
            "phase_or_layer": phase,
            "major_group_count": len(rows),
            "partial_major_group_count": sum(
                row["group_evidence_status"] == "incomplete" for row in rows
            ),
            "complete_major_group_count": sum(
                row["group_evidence_status"]
                in {"supportive", "contradictory", "mixed", "neutral"}
                for row in rows
            ),
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
            "candidate_input_eligible": False,
            "major_groups": rows,
        }
        for phase, rows in sorted(grouped.items())
    ]
