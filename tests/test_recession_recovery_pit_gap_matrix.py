from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    summarize_recession_recovery_pit_gap_matrix,
)


def test_recession_recovery_pit_gap_matrix_reduces_strict_pit_role_gaps() -> None:
    summary = summarize_recession_recovery_pit_gap_matrix()

    assert summary["recession_recovery_pit_gap_matrix_ready"] is True
    assert summary["pre_insufficient_point_in_time_role_gap_count"] == 13
    assert summary["post_insufficient_point_in_time_role_gap_count"] == 6
    assert summary["cache_remediated_pit_role_gap_count"] == 7
    assert summary["pre_insufficient_point_in_time_scenario_role_gap_count"] == 39
    assert summary["post_insufficient_point_in_time_scenario_role_gap_count"] == 16
    assert summary["phase37_clean_environment_deterministic"] is True
    assert summary["scenario_role_gap_row_count_fields_separated"] is True
    assert summary["safe_fixable_pit_gap_count"] == 0
    assert summary["official_history_insufficient_gap_count"] == 1
    assert summary["genuine_source_unavailable_gap_count"] == 5
    assert summary["rule_unresolved_gap_count"] == 1
    assert summary["revised_fallback_used_count"] == 0
    assert summary["proxy_fallback_used_count"] == 0


def test_show_recession_recovery_pit_gap_matrix_script() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/show_recession_recovery_pit_gap_matrix.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "recession_recovery_pit_gap_matrix_ready=true" in result.stdout
    assert "post_insufficient_point_in_time_role_gap_count=6" in result.stdout
    assert "post_insufficient_point_in_time_scenario_role_gap_count=16" in result.stdout
    assert "scenario_role_gap_row_count_fields_separated=true" in result.stdout
    assert "result=passed" in result.stdout
