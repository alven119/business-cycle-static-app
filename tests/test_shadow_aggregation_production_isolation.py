from __future__ import annotations

from business_cycle.audits.shadow_aggregation_production_isolation import (
    summarize_shadow_aggregation_production_isolation,
)


def test_shadow_aggregation_is_isolated_from_production() -> None:
    summary = summarize_shadow_aggregation_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_shadow_aggregation_count"] == 0
    assert summary["production_pipeline_shadow_aggregation_step_count"] == 0
    assert summary["resolver_shadow_aggregation_dependency_count"] == 0
    assert summary["dashboard_shadow_aggregation_dependency_count"] == 0
    assert summary["public_shadow_aggregation_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
