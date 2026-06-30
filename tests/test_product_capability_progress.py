from __future__ import annotations

from business_cycle.audits.product_capability_progress import (
    CORE_CAPABILITY_IDS,
    summarize_product_capability_progress,
)


def test_product_capability_progress_passes() -> None:
    summary = summarize_product_capability_progress()

    assert summary["result"] == "passed"
    assert summary["product_capability_progress_ready"] is True
    assert summary["capability_count"] == 8
    assert summary["capability_with_percent_count"] == 8
    assert set(row["capability_id"] for row in summary["capability_progress"]) == (
        CORE_CAPABILITY_IDS
    )
    assert summary["impacted_capability_count"] == 5
    assert summary["progress_percent_out_of_range_count"] == 0
    assert summary["unsupported_readiness_claim_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_progress_is_orientation_not_readiness_claim() -> None:
    summary = summarize_product_capability_progress()

    assert "production readiness" in summary["phase_label"] or (
        summary["phase_label"] == "official_macro_source_adapter_wiring"
    )
    assert all(
        0 <= row["current_progress_percent"] <= 100
        for row in summary["capability_progress"]
    )
    assert all(
        "investment" not in row["phase52_impact_zh"].lower()
        for row in summary["capability_progress"]
    )
