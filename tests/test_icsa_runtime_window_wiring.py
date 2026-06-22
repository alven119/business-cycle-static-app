from __future__ import annotations

from business_cycle.shadow_model.runtime_path import (
    run_shadow_evaluator_runtime_diagnostic,
    summarize_implemented_evaluator_runtime_path,
)


def test_2019_revised_runtime_materializes_window_and_outputs() -> None:
    summary = run_shadow_evaluator_runtime_diagnostic(
        as_of="2019-12-31",
        data_mode="revised",
    )

    assert summary["evaluator_invoked_count"] == 1
    assert summary["input_window_ready_count"] == 1
    assert summary["evaluator_output_count"] == 1
    assert summary["evaluator_abstention_count"] == 0
    assert summary["runtime_input_assembly_failure_count"] == 0
    assert summary["candidate_phase_emitted"] is False


def test_strict_early_dates_abstain_legitimately_without_fallback() -> None:
    summary = run_shadow_evaluator_runtime_diagnostic(
        as_of="2008-09-30",
        data_mode="vintage_as_of",
    )

    assert summary["evaluator_output_count"] == 0
    assert summary["legitimate_temporal_abstention_count"] == 1
    assert summary["unexplained_runtime_abstention_count"] == 0


def test_runtime_path_summary_hard_gates() -> None:
    summary = summarize_implemented_evaluator_runtime_path()

    assert summary["implemented_evaluator_runtime_path_ready"] is True
    assert summary["runtime_output_on_2019_revised_count"] == 1
    assert summary["runtime_input_assembly_failure_count"] == 0
    assert summary["ready_window_but_no_runtime_output_count"] == 0
    assert summary["unexplained_runtime_abstention_count"] == 0
