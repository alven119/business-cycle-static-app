from __future__ import annotations

from business_cycle.audits.qa10_production_isolation import (
    summarize_qa10_production_isolation,
)


def test_qa10_production_isolation() -> None:
    summary = summarize_qa10_production_isolation()

    assert summary["production_isolation_verified"] is True
    assert summary["production_imports_registry_count"] == 0
    assert summary["production_registry_write_count"] == 0
    assert summary["production_registry_read_count"] == 0
    assert summary["resolver_registry_dependency_count"] == 0
    assert summary["state_machine_registry_dependency_count"] == 0
    assert summary["dashboard_registry_dependency_count"] == 0
    assert summary["portfolio_registry_dependency_count"] == 0
    assert summary["workflow_registry_command_count"] == 0
    assert summary["public_registry_output_count"] == 0
    assert summary["production_behavior_change_count"] == 0
