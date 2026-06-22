from __future__ import annotations

from business_cycle.audits.shadow_evaluator_production_isolation import (
    summarize_shadow_evaluator_production_isolation,
)


def test_shadow_evaluator_production_isolation_counts_are_zero() -> None:
    summary = summarize_shadow_evaluator_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_shadow_evaluator_count"] == 0
    assert summary["production_imports_prospective_gate_count"] == 0
    assert summary["production_pipeline_shadow_evaluator_step_count"] == 0
    assert summary["resolver_prospective_dependency_count"] == 0
    assert summary["state_machine_prospective_dependency_count"] == 0
    assert summary["dashboard_shadow_evidence_dependency_count"] == 0
    assert summary["workflow_shadow_evaluator_command_count"] == 0
    assert summary["public_shadow_evidence_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
