from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.test_suite_doctrine_quarantine import (
    summarize_test_suite_doctrine_quarantine,
)


def test_test_suite_doctrine_quarantine_passes() -> None:
    summary = summarize_test_suite_doctrine_quarantine()

    assert summary["result"] == "passed"
    assert summary["test_suite_doctrine_quarantine_ready"] is True
    assert summary["pytest_marker_taxonomy_ready"] is True
    assert summary["default_product_core_test_file_count"] == 29
    assert (
        summary["default_product_core_test_file_count"]
        <= summary["default_product_core_max_file_count"]
    )
    assert summary["archive_regression_test_count"] > 0
    assert summary["closure_archive_test_count"] > 0
    assert summary["legacy_v1_default_test_count"] == 0
    assert summary["v1_default_removed"] is True
    assert summary["product_core_capability_mapping_ready"] is True
    assert summary["high_risk_test_file_count"] > 0
    assert summary["unmarked_high_risk_test_count"] == 0
    assert summary["legacy_v1_missing_compatibility_label_count"] == 0
    assert summary["mature_product_test_asserts_phase_winner_count"] == 0
    assert summary["mature_product_test_asserts_phase_rank_count"] == 0
    assert summary["mature_product_test_asserts_arbitrary_phase_score_count"] == 0
    assert summary["mature_product_test_asserts_isolated_candidate_count"] == 0
    assert summary["historical_backtest_static_label_only_unmarked_count"] == 0
    assert summary["portfolio_test_recommendation_wording_count"] == 0
    assert summary["production_behavior_change_count"] == 0


def test_test_suite_doctrine_quarantine_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/audit_test_suite_doctrine_quarantine.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "test_suite_doctrine_quarantine_ready=true" in completed.stdout
    assert "default_product_core_test_file_count=29" in completed.stdout
    assert "legacy_v1_default_test_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
