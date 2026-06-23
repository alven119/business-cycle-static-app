from __future__ import annotations

from business_cycle.data_sources.book_core_adapter import (
    build_phase10_adapters,
    summarize_book_core_adapter_contract,
)


def test_book_core_adapter_interface_is_complete_for_new_official_sources() -> None:
    summary = summarize_book_core_adapter_contract()
    adapters = build_phase10_adapters()

    assert summary["adapter_interface_ready"] is True
    assert summary["implemented_adapter_count"] == 11
    assert summary["adapter_with_complete_interface_count"] == 11
    assert summary["adapter_without_cache_contract_count"] == 0
    assert summary["adapter_without_no_write_preflight_count"] == 0
    assert summary["adapter_without_offline_fixture_count"] == 0
    assert {adapter.network_required for adapter in adapters} == {False}
    assert all(adapter.no_write_preflight()["registry_write_attempted"] is False for adapter in adapters)
