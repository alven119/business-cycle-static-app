from __future__ import annotations

from business_cycle.audits.qa12_prestart_leakage import (
    summarize_qa12_prestart_leakage,
)


def test_qa12_prestart_leakage_counts_are_zero() -> None:
    summary = summarize_qa12_prestart_leakage()

    assert summary["leakage_guard_ready"] is True
    for key, value in summary.items():
        if key.endswith("_count"):
            assert value == 0

