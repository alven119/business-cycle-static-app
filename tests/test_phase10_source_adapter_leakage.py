from __future__ import annotations

from business_cycle.audits.phase10_source_adapter_leakage import (
    summarize_phase10_source_adapter_leakage,
)


def test_phase10_source_adapter_leakage_counts_are_zero() -> None:
    summary = summarize_phase10_source_adapter_leakage()

    assert summary["leakage_guard_ready"] is True
    for key, value in summary.items():
        if key.endswith("_count"):
            assert value == 0
