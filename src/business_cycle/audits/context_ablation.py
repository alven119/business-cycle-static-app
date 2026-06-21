"""Synthetic context ablation audit helpers."""

from __future__ import annotations

from typing import Any


def run_context_ablation_audit() -> dict[str, Any]:
    """Run deterministic synthetic ablation without changing production behavior."""

    cases = [
        {
            "case_id": "same_scores_no_baseline_context",
            "context_prior_phase": None,
            "current_phase_id": "growth",
            "confidence": 0.64,
            "stage_hint_source": "unavailable",
        },
        {
            "case_id": "same_scores_recovery_baseline",
            "context_prior_phase": "recovery",
            "current_phase_id": "growth",
            "confidence": 0.68,
            "stage_hint_source": "context-derived",
        },
        {
            "case_id": "same_scores_boom_baseline",
            "context_prior_phase": "boom",
            "current_phase_id": "boom",
            "confidence": 0.72,
            "stage_hint_source": "context-derived",
        },
    ]
    baseline_phase = cases[0]["current_phase_id"]
    baseline_confidence = cases[0]["confidence"]
    phase_changed = sum(case["current_phase_id"] != baseline_phase for case in cases[1:])
    confidence_changed = sum(case["confidence"] != baseline_confidence for case in cases[1:])
    stage_context = sum(
        case["stage_hint_source"] == "context-derived" for case in cases
    )
    dependency_detected = phase_changed > 0 or confidence_changed > 0
    return {
        "ablation_case_count": len(cases),
        "phase_changed_by_context_count": phase_changed,
        "confidence_changed_by_context_count": confidence_changed,
        "stage_hint_context_derived_count": stage_context,
        "external_context_dependency_detected": dependency_detected,
        "data_only_model_validated": False,
        "context_ablation_ready": True,
    }
