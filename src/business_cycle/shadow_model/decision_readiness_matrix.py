"""Phase 14 decision readiness matrix for non-emitting diagnostics."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.formal_decision_runtime import (
    run_formal_decision_runtime_diagnostics,
    summarize_formal_decision_runtime,
)


def build_decision_readiness_matrix(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> list[dict[str, Any]]:
    diagnostics = run_formal_decision_runtime_diagnostics(
        as_of=as_of,
        data_mode=data_mode,
    )
    rows: list[dict[str, Any]] = []
    for result in diagnostics["precondition_check_results"]:
        blockers = result["readiness_blockers"]
        rows.append(
            {
                "profile_id": result["profile_id"],
                "diagnostic_phase_id": result["diagnostic_phase_id"],
                "phase_presence_layer": result["phase_presence_layer"],
                "readiness_status": (
                    "complete_but_candidate_output_disabled"
                    if result["precondition_evidence_complete"]
                    else "blocked_or_abstained"
                ),
                "required_major_group_count": result["required_major_group_count"],
                "missing_major_group_count": result["missing_major_group_count"],
                "incomplete_required_major_group_count": result[
                    "incomplete_required_major_group_count"
                ],
                "mixed_or_contradictory_group_count": result[
                    "mixed_or_contradictory_group_count"
                ],
                "candidate_input_eligible": False,
                "candidate_selection_enabled": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
                "blocked_reason_codes": blockers,
            }
        )
    return rows


def summarize_decision_readiness_matrix() -> dict[str, Any]:
    matrix = build_decision_readiness_matrix()
    runtime = summarize_formal_decision_runtime()
    return {
        "phase": "14",
        "decision_readiness_matrix_ready": (
            runtime["non_emitting_decision_runtime_ready"]
            and len(matrix) > 0
            and all(row["candidate_input_eligible"] is False for row in matrix)
            and all(row["candidate_selection_enabled"] is False for row in matrix)
            and all(row["candidate_phase_emitted"] is False for row in matrix)
            and all(row["current_phase_emitted"] is False for row in matrix)
        ),
        "decision_readiness_matrix_row_count": len(matrix),
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_decision_output_field_count": runtime[
            "prohibited_decision_output_field_count"
        ],
        "selected_phase_output_count": runtime["selected_phase_output_count"],
        "phase_rank_output_count": runtime["phase_rank_output_count"],
        "phase_score_output_count": runtime["phase_score_output_count"],
        "rows": matrix,
    }
