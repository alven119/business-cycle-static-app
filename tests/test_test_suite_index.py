from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.test_suite_index import summarize_test_suite_index


def test_test_suite_index_passes_and_preserves_default_suite_size() -> None:
    summary = summarize_test_suite_index()

    assert summary["result"] == "passed"
    assert summary["test_suite_index_ready"] is True
    assert summary["indexed_test_file_count_equals_discovered"] is True
    assert summary["default_product_core_test_file_count"] == 30
    assert summary["default_product_core_indexed_count"] == 30
    assert summary["duplicate_test_guard_key_count"] == 0
    assert summary["similar_test_reference_count"] > 0
    assert summary["new_test_preflight_policy_ready"] is True
    assert summary["similar_test_extension_policy_ready"] is True
    assert summary["product_capability_mapping_complete"] is True


def test_test_suite_index_explains_where_to_extend_existing_tests() -> None:
    summary = summarize_test_suite_index()
    row = next(
        item
        for item in summary["index_rows"]
        if item["test_path"] == "tests/test_transition_timing_replay_preview.py"
    )

    assert row["suite_tier"] == "default_product_core"
    assert row["component_area"] == "ordered_transition_monitoring"
    assert row["extension_policy"] == (
        "extend_existing_product_core_test_before_adding_new_file"
    )
    assert row["similar_test_paths"]


def test_show_test_suite_index_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_test_suite_index.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "test_suite_index_ready=true" in completed.stdout
    assert "default_product_core_test_file_count=30" in completed.stdout
    assert "duplicate_test_guard_key_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
