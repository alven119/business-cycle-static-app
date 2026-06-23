from __future__ import annotations

from business_cycle.audits.prospective_source_adapter_inventory import (
    summarize_prospective_source_adapter_inventory,
)


def test_source_adapter_inventory_is_complete_and_official() -> None:
    summary = summarize_prospective_source_adapter_inventory()

    assert summary["source_adapter_inventory_ready"] is True
    assert summary["adapter_count"] == 28
    assert summary["implemented_adapter_count"] == 28
    assert summary["adapter_without_official_domain_count"] == 0
    assert summary["adapter_without_revision_policy_count"] == 0
    assert summary["adapter_without_no_write_preflight_count"] == 0
    assert summary["adapter_without_offline_fixture_count"] == 0
    assert summary["role_with_multiple_unresolved_adapters_count"] == 0
