from __future__ import annotations

from business_cycle.audits.shadow_production_isolation import (
    summarize_shadow_production_isolation,
)


def test_shadow_modules_are_not_imported_by_production_paths() -> None:
    summary = summarize_shadow_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_shadow_module_count"] == 0
    assert summary["production_catalog_shadow_indicator_count"] == 0
    assert summary["production_pipeline_shadow_step_count"] == 0
    assert summary["resolver_shadow_dependency_count"] == 0
    assert summary["dashboard_shadow_dependency_count"] == 0
    assert summary["workflow_shadow_command_count"] == 0
    assert summary["public_shadow_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0

