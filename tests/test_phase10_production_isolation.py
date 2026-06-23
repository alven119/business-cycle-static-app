from __future__ import annotations

from business_cycle.audits.phase10_production_isolation import (
    summarize_phase10_production_isolation,
)


def test_phase10_source_adapters_are_not_imported_by_production() -> None:
    summary = summarize_phase10_production_isolation()

    assert summary["production_isolation_verified"] is True
    for key, value in summary.items():
        if key.endswith("_count"):
            assert value == 0
