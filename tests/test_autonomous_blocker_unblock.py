from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.autonomous_blocker_unblock import (
    build_autonomous_blocker_unblock,
    write_autonomous_blocker_unblock,
)


def test_autonomous_blocker_unblock_runtime_reduces_blocked_without_promotion() -> None:
    run = build_autonomous_blocker_unblock()

    assert run["autonomous_blocker_unblock_runtime_ready"] is True
    assert run["attempted_fix_iteration_count"] == 2
    assert run["pre_resolution_blocked_scenario_count"] == 5
    assert run["post_resolution_blocked_scenario_count"] == 0
    assert run["pre_resolution_comparable_scenario_count"] == 0
    assert run["post_resolution_comparable_scenario_count"] == 0
    assert run["safe_fixable_blocker_count"] == 0
    assert run["unresolved_safe_fixable_blocker_count"] == 0
    assert run["all_remaining_blockers_are_genuine"] is True
    assert run["false_resolution_count"] == 0
    assert run["scenario_promoted_without_required_evidence_count"] == 0
    assert run["scenario_promoted_by_taxonomy_only_count"] == 0
    assert run["scenario_promoted_by_modern_proxy_count"] == 0
    assert run["evidence_rule_modified_count"] == 0
    assert run["predicted_mapping_rule_modified_count"] == 0
    assert run["threshold_modified_count"] == 0
    assert run["historical_accuracy_metric_count"] == 5
    assert run["economic_performance_metric_count"] == 0
    assert run["label_used_by_runtime_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False


def test_autonomous_unblock_preserves_abstention_not_comparable() -> None:
    run = build_autonomous_blocker_unblock()
    post_statuses = {
        artifact["comparison_status"]
        for artifact in run["post_comparison_run"]["predicted_label_comparison_artifacts"]
    }
    post_labels = {
        artifact["predicted_label"]
        for artifact in run["post_predicted_run"]["offline_predicted_label_artifacts"]
    }

    assert post_statuses == {"abstained"}
    assert post_labels == {"abstained"}
    for profile in run["autonomous_blocker_unblock_artifact"][
        "scenario_unblock_profiles"
    ]:
        assert profile["post_comparison_status"] == "abstained"
        assert profile["post_predicted_label"] == "abstained"
        assert profile["remaining_genuine_blocker_evidence"]


def test_autonomous_blocker_unblock_writes_tmp_only(tmp_path: Path) -> None:
    output = tmp_path / "phase34_autonomous_unblock.json"
    result = write_autonomous_blocker_unblock(
        build_autonomous_blocker_unblock(),
        output=output,
    )

    assert result["autonomous_blocker_unblock_written"] is True
    assert result["written_file_count"] == 1
    assert output.is_file()


def test_autonomous_blocker_unblock_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_autonomous_blocker_unblock(
            build_autonomous_blocker_unblock(),
            output="data/backtests/phase34_autonomous_unblock.json",
        )


def test_run_autonomous_blocker_unblock_script(tmp_path: Path) -> None:
    output = tmp_path / "phase34_autonomous_unblock.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_autonomous_blocker_unblock.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "autonomous_blocker_unblock_runtime_ready=true" in result.stdout
    assert "post_resolution_blocked_scenario_count=0" in result.stdout
    assert "phase34_resolution_progress_status=blocked_scenario_count_reduced" in (
        result.stdout
    )
    assert output.is_file()
