"""View model for Phase47 phase-start research context."""

from __future__ import annotations

from typing import Any

from business_cycle.cycle_state.phase_start_research_assistant import (
    PROHIBITED_FIELDS,
    build_phase_start_research_assistant,
)


def build_phase_start_research_view_model(
    *,
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a research-only dashboard/artifact view model."""

    artifact = artifact or build_phase_start_research_assistant()
    view_model = {
        "view_model_version": "phase_start_research_view_v1",
        "readiness_label": "phase_start_research_ready_registry_unchanged",
        "research_only": True,
        "declared_state_label": "declared_state_not_inferred_current_phase",
        "declared_current_phase": artifact["declared_current_phase"],
        "declared_phase_start_date_current_value": artifact[
            "declared_phase_start_date_current_value"
        ],
        "phase_age_status_current_value": artifact["phase_age_status_current_value"],
        "legal_next_phase": artifact["legal_next_phase"],
        "hypothesis_summaries": [
            {
                "hypothesis_id": hypothesis["hypothesis_id"],
                "hypothesis_source": hypothesis["hypothesis_source"],
                "candidate_start_date_or_window": hypothesis[
                    "candidate_start_date_or_window"
                ],
                "hypothesis_status": hypothesis["hypothesis_status"],
                "supporting_evidence_count": len(hypothesis["supporting_evidence"]),
                "contradictory_evidence_count": len(
                    hypothesis["contradictory_evidence"]
                ),
                "missing_evidence_count": len(hypothesis["missing_evidence"]),
            }
            for hypothesis in artifact["hypotheses"]
        ],
        "missing_evidence_summary": artifact["missing_evidence_summary"],
        "source_provenance_summary": artifact["source_provenance_summary"],
        "book_traceability_summary": artifact["book_traceability_summary"],
        "top_phase48_evidence_wiring_priorities": artifact[
            "top_phase48_evidence_wiring_priorities"
        ],
        "user_confirmation_required": artifact["user_confirmation_required"],
        "registry_write_allowed": artifact["registry_write_allowed"],
        "declared_registry_modified": artifact["declared_registry_modified"],
        "phase_age_used_as_transition_gate": artifact[
            "phase_age_used_as_transition_gate"
        ],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "uses_current_data_to_infer_declared_phase": False,
            "declared_registry_write": False,
            "production_behavior_change": False,
        },
    }
    if PROHIBITED_FIELDS.intersection(view_model):
        raise ValueError("Phase start research view model contains prohibited fields")
    return view_model
