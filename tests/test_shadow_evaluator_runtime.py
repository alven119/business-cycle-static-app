from __future__ import annotations

from business_cycle.audits.shadow_evaluator_runtime import (
    summarize_shadow_evaluator_runtime,
)


def test_shadow_evaluator_runtime_wired_but_not_candidate_eligible() -> None:
    summary = summarize_shadow_evaluator_runtime()

    assert summary["evaluator_runtime_audit_ready"] is True
    assert summary["implemented_evaluator_count"] == 1
    assert summary["contract_evaluable_evaluator_count"] == 1
    assert summary["runtime_registered_evaluator_count"] == 1
    assert summary["runtime_executable_evaluator_count"] == 1
    assert summary["evaluator_marked_evaluable_but_runner_unwired_count"] == 0
    assert summary["unexplained_runtime_abstention_count"] == 0
    assert summary["smoothing_output_mislabeled_directional_count"] == 0
    assert summary["smoothing_output_mislabeled_confirmation_count"] == 0
    assert summary["candidate_selection_eligible_evaluator_count"] == 0


def test_shadow_evaluator_runtime_real_diagnostic_explains_abstention() -> None:
    row = summarize_shadow_evaluator_runtime()["rows"][0]
    diagnostic = row["real_diagnostic"]

    assert diagnostic["as_of"] == "2019-12-31"
    assert diagnostic["runtime_output_available"] is False
    assert diagnostic["evaluator_abstained"] is True
    assert "same-data-mode ICSA history" in diagnostic["missing_window"]
    assert diagnostic["directional_evidence"] is False
    assert diagnostic["candidate_phase_emitted"] is False
