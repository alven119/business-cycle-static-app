from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.recession_recovery_comparability_unblock import (
    build_recession_recovery_comparability_unblock,
    write_recession_recovery_comparability_unblock,
)


def test_recession_recovery_unblock_records_genuine_remaining_gaps() -> None:
    run = build_recession_recovery_comparability_unblock()

    assert run["recession_recovery_comparability_unblock_ready"] is True
    assert run["attempted_fix_iteration_count"] == 2
    assert run["scenario_count"] == 5
    assert run["pre_comparable_scenario_count"] == 2
    assert run["post_comparable_scenario_count"] == 2
    assert run["safe_fixable_recession_recovery_gap_count"] == 0
    assert run["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
    assert (
        run["all_remaining_recession_recovery_non_comparable_reasons_are_genuine"]
        is True
    )
    assert run["false_comparability_count"] == 0
    assert run["scenario_promoted_without_required_evidence_count"] == 0
    assert run["scenario_promoted_by_taxonomy_only_count"] == 0
    assert run["scenario_promoted_by_modern_proxy_count"] == 0
    assert run["evidence_rule_modified_count"] == 0
    assert run["predicted_mapping_rule_modified_count"] == 0
    assert run["threshold_modified_count"] == 0
    assert run["historical_accuracy_metric_count"] == 5
    assert run["new_accuracy_metric_computed_count"] == 0
    assert run["economic_performance_metric_count"] == 0
    assert run["label_used_by_runtime_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False
    assert run["phase36_validation_progress_status"] == (
        "historical_validation_results_generated_remaining_recession_recovery_"
        "genuine_non_comparable"
    )


def test_recession_recovery_unblock_does_not_special_case_scenario_ids() -> None:
    run = build_recession_recovery_comparability_unblock()
    profiles = run["recession_recovery_unblock_artifact"][
        "recession_recovery_scenario_profiles"
    ]

    assert len(profiles) == 3
    for profile in profiles:
        assert profile["scenario_family"] == "recession_recovery_cycle"
        assert profile["post_comparable"] is False
        assert profile["post_predicted_label"] == "abstained"
        assert profile["post_abstention_state"] == (
            "insufficient_recession_recovery_phase_evidence_abstain"
        )
        assert "missing_recession_confirmation_evidence" in profile[
            "gap_classes_reviewed"
        ]
        assert "missing_recovery_confirmation_evidence" in profile[
            "gap_classes_reviewed"
        ]
        assert profile["remaining_genuine_non_comparable_evidence"]


def test_recession_recovery_unblock_writes_tmp_only(tmp_path: Path) -> None:
    output = tmp_path / "phase36_recession_recovery_unblock.json"
    result = write_recession_recovery_comparability_unblock(
        build_recession_recovery_comparability_unblock(),
        output=output,
    )

    assert result["recession_recovery_comparability_unblock_written"] is True
    assert result["written_file_count"] == 1
    assert output.is_file()


def test_recession_recovery_unblock_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_recession_recovery_comparability_unblock(
            build_recession_recovery_comparability_unblock(),
            output="data/backtests/phase36_rr_unblock.json",
        )


def test_run_recession_recovery_unblock_script(tmp_path: Path) -> None:
    output = tmp_path / "phase36_recession_recovery_unblock.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_recession_recovery_comparability_unblock.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "recession_recovery_comparability_unblock_ready=true" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
    assert output.is_file()
