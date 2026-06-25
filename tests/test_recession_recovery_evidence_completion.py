from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.recession_recovery_evidence_completion import (
    build_recession_recovery_evidence_completion,
    summarize_recession_recovery_evidence_completion,
)


def test_recession_recovery_evidence_completion_attempts_all_target_scenarios() -> None:
    summary = summarize_recession_recovery_evidence_completion()

    assert summary["recession_recovery_evidence_completion_runtime_ready"] is True
    assert summary["attempted_fix_iteration_count"] == 2
    assert summary["scenario_count"] == 5
    assert summary["target_recession_recovery_scenario_count"] == 3
    assert summary["pre_comparable_scenario_count"] == 2
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["phase_evidence_completion_attempted_scenario_count"] == 3
    assert summary["safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
    assert summary["false_comparability_count"] == 0
    assert summary["evidence_completion_false_positive_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["phase36r_progress_status"] == (
        "all_safe_recession_recovery_evidence_completion_attempted_remaining_genuine"
    )


def test_recession_recovery_evidence_completion_records_role_level_gaps() -> None:
    run = build_recession_recovery_evidence_completion()
    gaps = run["role_level_remaining_evidence_gaps"]

    assert set(gaps) == {
        "covid_recession_2020",
        "dotcom_cycle_2000_2003",
        "global_financial_crisis_2007_2009",
    }
    assert all(gaps[scenario_id] for scenario_id in gaps)
    assert {
        row["gap_class"]
        for scenario_gaps in gaps.values()
        for row in scenario_gaps
    } >= {"insufficient_point_in_time_input", "rule_unresolved"}
    assert all(
        row["safe_fixable"] is False
        for scenario_gaps in gaps.values()
        for row in scenario_gaps
    )


def test_run_recession_recovery_evidence_completion_script(tmp_path) -> None:
    output = tmp_path / "completion.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_recession_recovery_evidence_completion.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert "recession_recovery_evidence_completion_runtime_ready=true" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
