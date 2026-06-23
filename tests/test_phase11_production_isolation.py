from __future__ import annotations

from business_cycle.audits.phase11_production_isolation import (
    summarize_phase11_production_isolation,
)


def test_phase11_production_and_prospective_isolation() -> None:
    summary = summarize_phase11_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_phase11_evaluator_count"] == 0
    assert summary["production_catalog_changed_count"] == 0
    assert summary["production_pipeline_phase11_step_count"] == 0
    assert summary["resolver_phase11_dependency_count"] == 0
    assert summary["state_machine_phase11_dependency_count"] == 0
    assert summary["dashboard_phase11_dependency_count"] == 0
    assert summary["workflow_phase11_command_count"] == 0
    assert summary["public_phase11_output_count"] == 0
    assert summary["portfolio_phase11_dependency_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["prospective_date_change_count"] == 0
    assert summary["qa12_freeze_change_count"] == 0
    assert summary["real_registry_write_attempt_count"] == 0
    assert summary["real_registry_record_count"] == 0
    assert summary["prospective_result_inspected_count"] == 0
