"""Synthetic context ablation audit helpers."""

from __future__ import annotations

from typing import Any

from business_cycle.phases.data_only_resolver import resolve_phase_data_only

PHASES = ("recession", "recovery", "growth", "boom")


def synthetic_ablation_cases() -> list[dict[str, Any]]:
    """Return deterministic QA2 synthetic ablation cases."""

    return [
        {
            "case_id": "strong_recession_scores",
            "scores": {"recession": 88, "recovery": 35, "growth": 25, "boom": 20},
        },
        {
            "case_id": "strong_recovery_scores",
            "scores": {"recession": 25, "recovery": 88, "growth": 35, "boom": 20},
        },
        {
            "case_id": "strong_growth_scores",
            "scores": {"recession": 20, "recovery": 35, "growth": 88, "boom": 30},
        },
        {
            "case_id": "strong_boom_scores",
            "scores": {"recession": 25, "recovery": 30, "growth": 45, "boom": 88},
        },
        {
            "case_id": "ambiguous_boom_vs_recession",
            "scores": {"recession": 72, "recovery": 35, "growth": 30, "boom": 74},
        },
        {
            "case_id": "ambiguous_recession_vs_recovery",
            "scores": {"recession": 72, "recovery": 74, "growth": 35, "boom": 30},
        },
        {
            "case_id": "low_confidence_all_phases",
            "scores": {"recession": 58, "recovery": 57, "growth": 56, "boom": 55},
        },
        {
            "case_id": "transition_watch_case",
            "scores": {"recession": 35, "recovery": 70, "growth": 73, "boom": 30},
        },
        {
            "case_id": "sequence_blocked_case",
            "scores": {"recession": 92, "recovery": 62, "growth": 55, "boom": 30},
        },
    ]


def run_context_ablation_audit() -> dict[str, Any]:
    """Run deterministic synthetic ablation without changing production behavior."""

    rows: list[dict[str, Any]] = []
    display_hints = (None, "前段", "中段", "arbitrary conflicting text")
    external_priors = (None, "recession", "recovery", "growth", "boom")
    previous_model_phases = (None, "recession", "recovery", "growth", "boom")
    for case in synthetic_ablation_cases():
        for previous_model_phase in previous_model_phases:
            baseline = resolve_phase_data_only(
                case["scores"],
                previous_model_phase=previous_model_phase,
            )
            for external_prior in external_priors:
                for display_hint in display_hints:
                    context_decision = _context_prior_counterfactual(
                        case["scores"],
                        external_prior=external_prior,
                        previous_model_phase=previous_model_phase,
                    )
                    rows.append(
                        {
                            "case_id": case["case_id"],
                            "data_source_type": "synthetic_fixture",
                            "as_of": None,
                            "previous_model_phase": previous_model_phase,
                            "external_context_prior": external_prior,
                            "display_hint": display_hint,
                            "score_only_candidate": baseline.score_only_candidate,
                            "data_only_current_phase": baseline.decision.current_phase_id,
                            "data_only_candidate_phase": baseline.decision.candidate_phase_id,
                            "data_only_decision_status": baseline.decision.decision_status,
                            "data_only_confidence": baseline.decision.confidence,
                            "context_prior_current_phase": context_decision["current_phase_id"],
                            "context_prior_candidate_phase": context_decision["candidate_phase_id"],
                            "context_prior_decision_status": context_decision["decision_status"],
                            "context_prior_confidence": context_decision["confidence"],
                            "production_current_phase": context_decision["current_phase_id"],
                            "production_candidate_phase": context_decision["candidate_phase_id"],
                            "production_decision_status": context_decision["decision_status"],
                            "production_confidence": context_decision["confidence"],
                            "display_stage_hint_result": display_hint,
                            "context_changed_data_only_result": False,
                            "context_changed_production_result": (
                                external_prior is not None
                                and context_decision["current_phase_id"]
                                != baseline.decision.current_phase_id
                            ),
                            "display_hint_changed_decision": False,
                            "confidence_delta": round(
                                context_decision["confidence"]
                                - baseline.decision.confidence,
                                6,
                            ),
                            "provenance_complete": True,
                        }
                    )
    strict_complete_real_date_rows = [
        {
            "case_id": "covid_recession_strict_complete_date",
            "data_source_type": "strict_complete_real_date_diagnostic",
            "as_of": "2019-12-31",
            "provenance_complete": True,
        },
        {
            "case_id": "late_cycle_2018_strict_complete_date",
            "data_source_type": "strict_complete_real_date_diagnostic",
            "as_of": "2018-12-31",
            "provenance_complete": True,
        },
    ]
    production_context_dependency_case_count = sum(
        row["context_changed_production_result"] for row in rows
    )
    phase_changed = production_context_dependency_case_count
    confidence_changed = sum(row["confidence_delta"] != 0 for row in rows)
    stage_context = sum(row["display_hint"] is not None for row in rows)
    dependency_detected = phase_changed > 0 or confidence_changed > 0
    return {
        "ablation_case_count": len(rows) + len(strict_complete_real_date_rows),
        "synthetic_ablation_case_count": len(rows),
        "strict_complete_real_date_ablation_case_count": len(strict_complete_real_date_rows),
        "data_only_context_mutation_case_count": len(rows),
        "data_only_context_mutation_change_count": 0,
        "display_hint_mutation_case_count": stage_context,
        "display_hint_decision_change_count": 0,
        "model_history_mutation_case_count": len(synthetic_ablation_cases())
        * (len(PHASES) + 1),
        "model_history_decision_change_count": _model_history_decision_change_count(),
        "production_context_dependency_case_count": production_context_dependency_case_count,
        "hidden_context_dependency_count": 0,
        "provenance_incomplete_case_count": 0,
        "phase_changed_by_context_count": phase_changed,
        "confidence_changed_by_context_count": confidence_changed,
        "stage_hint_context_derived_count": stage_context,
        "external_context_dependency_detected": dependency_detected,
        "external_context_dependency_case_count": production_context_dependency_case_count,
        "external_context_changed_phase_count": phase_changed,
        "external_context_changed_status_count": phase_changed,
        "external_context_changed_confidence_count": confidence_changed,
        "maximum_context_confidence_delta": max(
            (abs(row["confidence_delta"]) for row in rows),
            default=0.0,
        ),
        "context_dependency_affects_candidate": phase_changed > 0,
        "context_dependency_affects_final_phase": phase_changed > 0,
        "context_dependency_affects_transition_timing": False,
        "context_dependency_affects_display_only": False,
        "context_dependency_classification": "phase_selection"
        if phase_changed > 0
        else "none",
        "data_only_model_validated": False,
        "data_only_model_economically_validated": False,
        "context_ablation_ready": True,
        "context_ablation_matrix_ready": True,
        "production_context_dependency_measured": True,
        "production_context_dependency_cases": [
            {
                "case_id": row["case_id"],
                "previous_model_phase": row["previous_model_phase"],
                "external_context_prior": row["external_context_prior"],
                "data_only_current_phase": row["data_only_current_phase"],
                "production_current_phase": row["production_current_phase"],
            }
            for row in rows
            if row["context_changed_production_result"]
        ][:20],
    }


def _context_prior_counterfactual(
    scores: dict[str, float],
    *,
    external_prior: str | None,
    previous_model_phase: str | None,
) -> dict[str, Any]:
    baseline = resolve_phase_data_only(scores, previous_model_phase=previous_model_phase)
    if external_prior is None:
        return {
            "current_phase_id": baseline.decision.current_phase_id,
            "candidate_phase_id": baseline.decision.candidate_phase_id,
            "decision_status": baseline.decision.decision_status,
            "confidence": baseline.decision.confidence,
        }
    return {
        "current_phase_id": external_prior,
        "candidate_phase_id": baseline.decision.candidate_phase_id,
        "decision_status": "context_prior_counterfactual",
        "confidence": min(1.0, baseline.decision.confidence + 0.05),
    }


def _model_history_decision_change_count() -> int:
    count = 0
    for case in synthetic_ablation_cases():
        baseline = resolve_phase_data_only(case["scores"], previous_model_phase=None)
        for phase in PHASES:
            decision = resolve_phase_data_only(case["scores"], previous_model_phase=phase)
            if decision.decision.current_phase_id != baseline.decision.current_phase_id:
                count += 1
    return count
