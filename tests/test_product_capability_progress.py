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
    assert summary["capability_with_completed_summary_count"] == 8
    assert summary["capability_with_incomplete_summary_count"] == 8
    assert summary["capability_with_next_gap_count"] == 8
    assert set(row["capability_id"] for row in summary["capability_progress"]) == (
        CORE_CAPABILITY_IDS
    )
    assert summary["impacted_capability_count"] == 8
    assert summary["progress_decrease_count"] == 0
    assert summary["progress_decrease_without_reason_count"] == 0
    assert summary["progress_percent_out_of_range_count"] == 0
    assert summary["unsupported_readiness_claim_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_progress_is_orientation_not_readiness_claim() -> None:
    summary = summarize_product_capability_progress()

    assert "formal production use" in summary["progress_semantics"]
    assert "monotonic by default" in summary["progress_semantics"]
    assert (
        summary["phase_label"]
        == "replay_backtest_lineage_hardened_no_silent_fallback"
    )
    assert all(
        0 <= row["current_progress_percent"] <= 100
        for row in summary["capability_progress"]
    )
    assert all(
        "investment" not in str(row.get("phase_impact_zh", "")).lower()
        for row in summary["capability_progress"]
    )


def test_product_capability_progress_table_contract() -> None:
    summary = summarize_product_capability_progress()

    assert len(summary["capability_table_rows"]) == 8
    required_fields = {
        "capability",
        "previous",
        "current",
        "delta",
        "phase_impact",
        "next_gap",
        "completed_summary",
        "incomplete_summary",
        "decrease_reason",
    }
    for row in summary["capability_table_rows"]:
        assert required_fields <= set(row)
        assert row["completed_summary"]
        assert row["incomplete_summary"]
        assert row["next_gap"]


def test_product_capability_progress_does_not_decrease_without_reason() -> None:
    summary = summarize_product_capability_progress()

    for row in summary["capability_progress"]:
        current = int(row["current_progress_percent"])
        previous = int(row["previous_progress_percent"])
        if current < previous:
            assert row["decrease_reason_zh"]
