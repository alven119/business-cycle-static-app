from __future__ import annotations

from business_cycle.audits.shadow_candidate_production_isolation import (
    summarize_shadow_candidate_production_isolation,
)


def test_shadow_candidate_production_isolation() -> None:
    summary = summarize_shadow_candidate_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_shadow_evaluator_count"] == 0
    assert summary["production_imports_shadow_candidate_selection_count"] == 0
    assert summary["production_pipeline_candidate_step_count"] == 0
    assert summary["resolver_shadow_candidate_dependency_count"] == 0
    assert summary["state_machine_shadow_candidate_dependency_count"] == 0
    assert summary["dashboard_shadow_candidate_dependency_count"] == 0
    assert summary["workflow_shadow_candidate_command_count"] == 0
    assert summary["public_shadow_candidate_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
