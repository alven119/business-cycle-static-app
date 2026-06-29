"""Dashboard-ready view model for the boom transition monitor."""

from __future__ import annotations

from typing import Any

from business_cycle.transition_monitor.boom_transition_monitor import (
    PROHIBITED_FIELDS,
    build_boom_transition_monitor,
)


def build_boom_transition_view_model(
    *,
    monitor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a research-only view model for the boom-to-recession monitor."""

    monitor = monitor or build_boom_transition_monitor()
    view_model = {
        "view_model_version": "boom_transition_monitor_view_v1",
        "readiness_label": "declared_boom_transition_monitor_ready_no_phase_selection",
        "declared_state_label": "declared_state_not_inferred_current_phase",
        "legal_transition_label": "boom_to_recession",
        "watch_confirmation_label": "watch_not_confirmation",
        "research_only": True,
        "declared_current_phase": monitor["declared_current_phase"],
        "legal_next_phase": monitor["legal_next_phase"],
        "monitor_as_of": monitor["monitor_as_of"],
        "data_mode": monitor["data_mode"],
        "phase_age_context_available": monitor["phase_age_context_available"],
        "phase_age_status": monitor["phase_age_status"],
        "phase_age_used_as_transition_gate": monitor[
            "phase_age_used_as_transition_gate"
        ],
        "lane_summaries": {
            "boom_continuation": _lane_summary(monitor["boom_continuation_evidence"]),
            "boom_ending_watch": _lane_summary(monitor["boom_ending_watch_evidence"]),
            "recession_watch": _lane_summary(monitor["recession_watch_evidence"]),
            "recession_confirmation": _lane_summary(
                monitor["recession_confirmation_evidence"]
            ),
        },
        "missing_or_stale_evidence_count": len(monitor["missing_or_stale_evidence"]),
        "blocker_summary": monitor["blocker_summary"],
        "why_not_formal_transition": monitor["why_not_formal_transition"],
        "allowed_uses": monitor["allowed_uses"],
        "prohibited_uses": monitor["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "uses_current_data_to_infer_declared_phase": False,
            "production_behavior_change": False,
            "watch_confirmation_separated": monitor[
                "watch_confirmation_separation_valid"
            ],
        },
    }
    if PROHIBITED_FIELDS.intersection(view_model):
        raise ValueError("Boom transition view model contains prohibited fields")
    return view_model


def _lane_summary(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane_id": lane["lane_id"],
        "lane_type": lane["lane_type"],
        "lane_status": lane["lane_status"],
        "lane_ready": lane["lane_ready"],
        "watch_lane": lane["watch_lane"],
        "confirmation_lane": lane["confirmation_lane"],
        "evidence_count": lane["evidence_count"],
        "supportive_evidence_count": lane["supportive_evidence_count"],
        "contradictory_evidence_count": lane["contradictory_evidence_count"],
        "missing_or_abstained_evidence_count": lane[
            "missing_or_abstained_evidence_count"
        ],
        "book_logic_summary": lane["book_logic_summary"],
    }
