from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase67_transition_timing_replay_preview_closure import (
    summarize_phase67_transition_timing_replay_preview_closure,
)


def test_phase67_transition_timing_replay_preview_closure_passes() -> None:
    summary = summarize_phase67_transition_timing_replay_preview_closure()

    assert summary["result"] == "passed"
    assert summary["phase67_transition_timing_replay_preview_ready"] is True
    assert summary["transition_timing_replay_preview_ready"] is True
    assert summary["dashboard_transition_timing_replay_preview_view_ready"] is True
    assert summary["rendered_transition_timing_replay_preview_ready"] is True
    assert summary["github_actions_test_efficiency_ready"] is True
    assert summary["transition_replay_checkpoint_count"] == 3
    assert summary["transition_lane_timing_preview_count"] == 13
    assert summary["evidence_accumulation_event_count"] == 39
    assert summary["default_product_core_test_file_count"] == 29
    assert summary["nightly_archive_shard_count"] == 8
    assert summary["nightly_monolithic_archive_pytest_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert (
        summary["phase67_closure_status"]
        == "closed_transition_timing_replay_preview_ready_ci_efficiency_verified"
    )


def test_show_phase67_transition_timing_replay_preview_closure_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_phase67_transition_timing_replay_preview_closure.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase67_transition_timing_replay_preview_ready=true" in completed.stdout
    assert "github_actions_test_efficiency_ready=true" in completed.stdout
    assert "nightly_monolithic_archive_pytest_count=0" in completed.stdout
    assert "result=passed" in completed.stdout
