from __future__ import annotations

from business_cycle.audits.qa11_production_isolation import (
    summarize_qa11_production_isolation,
)


def test_qa11_production_isolation_counts_are_zero() -> None:
    summary = summarize_qa11_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_observation_runtime_count"] == 0
    assert summary["production_pipeline_observation_step_count"] == 0
    assert summary["dashboard_observation_dependency_count"] == 0
    assert summary["portfolio_observation_dependency_count"] == 0
    assert summary["production_behavior_change_count"] == 0

