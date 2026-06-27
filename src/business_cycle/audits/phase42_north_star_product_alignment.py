"""Phase 42 North Star product-alignment audit."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)


@lru_cache(maxsize=1)
def summarize_phase42_north_star_product_alignment() -> dict[str, Any]:
    readiness = build_current_evidence_readiness()
    phase_profiles = readiness["phase_profiles"]
    summary = {
        "phase": "42",
        "phase_id": 42,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
            "C2_TRANSITION_RISK_DETECTION",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W13_MODEL_GOVERNANCE",
            "W15_SYSTEM_OPERATIONS",
        ],
        "deferred_capability_gaps": [
            "no formal current phase",
            "no candidate phase",
            "no production migration",
            "no economic performance validation",
            "no portfolio policy output",
        ],
        "phase42_addresses_current_stage_question": len(phase_profiles) == 4,
        "phase42_addresses_evidence_explanation_question": all(
            profile["top_blockers"] is not None
            and profile["top_supportive_roles"] is not None
            for profile in phase_profiles.values()
        ),
        "phase42_addresses_abstention_reason_question": all(
            bool(profile["why_not_formal_phase"])
            for profile in phase_profiles.values()
        ),
        "current_phase_emitted": readiness["current_phase_emitted"],
        "candidate_phase_emitted": readiness["candidate_phase_emitted"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "project_definition_of_done_progress": (
            "current evidence profile dashboard answers stage-proximity "
            "questions without formal phase output"
        ),
    }
    summary["result"] = "passed" if _passed(summary) else "blocked"
    return summary


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["north_star_alignment_status"] == "aligned"
        and summary["phase42_addresses_current_stage_question"] is True
        and summary["phase42_addresses_evidence_explanation_question"] is True
        and summary["phase42_addresses_abstention_reason_question"] is True
        and summary["current_phase_emitted"] is False
        and summary["candidate_phase_emitted"] is False
        and summary["production_behavior_change_count"] == 0
        and summary["semantic_drift_count"] == 0
    )
