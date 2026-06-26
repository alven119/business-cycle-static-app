from __future__ import annotations

import json
import subprocess
import sys

from business_cycle.validation.recession_recovery_pit_remediation import (
    build_recession_recovery_pit_remediation,
    summarize_recession_recovery_pit_remediation,
    write_recession_recovery_pit_remediation,
)


def test_recession_recovery_pit_remediation_runtime_preserves_safety() -> None:
    summary = summarize_recession_recovery_pit_remediation()

    assert summary["recession_recovery_pit_remediation_runtime_ready"] is True
    assert summary["attempted_fix_iteration_count"] == 2
    assert summary["pre_insufficient_point_in_time_role_gap_count"] == 13
    assert summary["post_insufficient_point_in_time_role_gap_count"] == 6
    assert summary["pre_comparable_scenario_count"] == 2
    assert summary["post_comparable_scenario_count"] == 2
    assert summary["false_comparability_count"] == 0
    assert summary["scenario_promoted_without_required_evidence_count"] == 0
    assert summary["label_used_by_runtime_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["phase37_progress_status"] == (
        "pit_gaps_reduced_but_comparability_still_limited"
    )
    assert summary["development_next_phase"] == 38


def test_recession_recovery_pit_remediation_writes_only_tmp(tmp_path) -> None:
    output = tmp_path / "phase37_pit_remediation.json"
    write = write_recession_recovery_pit_remediation(
        build_recession_recovery_pit_remediation(),
        output=output,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write["recession_recovery_pit_remediation_written"] is True
    assert payload["post_insufficient_point_in_time_role_gap_count"] == 6


def test_run_recession_recovery_pit_remediation_script(tmp_path) -> None:
    output = tmp_path / "phase37_pit_remediation.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_recession_recovery_pit_remediation.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.is_file()
    assert "phase37_progress_status=pit_gaps_reduced_but_comparability_still_limited" in (
        result.stdout
    )
    assert "result=passed" in result.stdout
