from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.product_capability_95_roadmap import (
    TARGET_CAPABILITY_IDS,
    summarize_product_capability_95_roadmap,
)


def test_product_capability_95_roadmap_passes() -> None:
    summary = summarize_product_capability_95_roadmap()

    assert summary["result"] == "passed"
    assert summary["roadmap_ready"] is True
    assert summary["target_capability_count"] == 3
    assert set(summary["target_capability_ids"]) == TARGET_CAPABILITY_IDS
    assert summary["planned_phase_count"] <= summary["max_phase_count"]
    assert summary["planned_phase_count"] == 9
    assert summary["target_phase_id"] == 64
    assert summary["post_target_enabler_count"] == 4
    assert summary["post_target_enabler_phase_ids"] == [65, 66, 67, 68]
    assert summary["phase65_test_suite_reduction_enabler_present"] is True
    assert summary["phase66_archive_shard_enabler_present"] is True
    assert summary["phase67_transition_timing_enabler_present"] is True
    assert summary["phase68_test_index_and_numeric_overlay_enabler_present"] is True
    assert summary["all_target_capabilities_reach_95"] is True
    assert summary["monotonic_progress_targets"] is True
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_product_capability_95_roadmap_targets_are_monotonic() -> None:
    summary = summarize_product_capability_95_roadmap()

    for row in summary["target_capabilities"]:
        previous = int(row["baseline_percent"])
        for _, value in sorted(
            row["phase_targets"].items(), key=lambda item: int(item[0])
        ):
            current = int(value)
            assert current >= previous
            previous = current
        assert previous == 95


def test_product_capability_95_roadmap_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_product_capability_95_roadmap.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "roadmap_ready=True" in result.stdout
    assert "planned_phase_count=9" in result.stdout
    assert "phase65_test_suite_reduction_enabler_present=True" in result.stdout
    assert "phase66_archive_shard_enabler_present=True" in result.stdout
    assert "phase67_transition_timing_enabler_present=True" in result.stdout
    assert (
        "phase68_test_index_and_numeric_overlay_enabler_present=True"
        in result.stdout
    )
    assert "all_target_capabilities_reach_95=True" in result.stdout
