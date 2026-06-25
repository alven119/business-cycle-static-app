from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.autonomous_comparability_realization import (
    build_autonomous_comparability_realization,
    write_autonomous_comparability_realization,
)


def test_autonomous_comparability_realization_increases_comparable_count() -> None:
    run = build_autonomous_comparability_realization()

    assert run["autonomous_comparability_realization_ready"] is True
    assert run["attempted_fix_iteration_count"] == 2
    assert run["scenario_count"] == 5
    assert run["pre_blocked_scenario_count"] == 0
    assert run["post_blocked_scenario_count"] == 0
    assert run["pre_comparable_scenario_count"] == 0
    assert run["post_comparable_scenario_count"] == 2
    assert run["safe_fixable_comparability_gap_count"] == 0
    assert run["unresolved_safe_fixable_comparability_gap_count"] == 0
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
    assert run["phase35_comparability_progress_status"] == (
        "comparable_scenarios_realized"
    )


def test_autonomous_comparability_uses_reference_family_not_scenario_id() -> None:
    run = build_autonomous_comparability_realization()
    profiles = {
        profile["scenario_id"]: profile
        for profile in run["autonomous_comparability_realization_artifact"][
            "scenario_comparability_profiles"
        ]
    }

    assert profiles["euro_debt_slowdown_2011_2012"]["post_comparable"] is True
    assert profiles["late_cycle_2018_2019"]["post_comparable"] is True
    assert profiles["euro_debt_slowdown_2011_2012"]["post_predicted_label"] == (
        "abstained"
    )
    assert profiles["late_cycle_2018_2019"]["post_predicted_label"] == "abstained"
    for scenario_id in (
        "dotcom_cycle_2000_2003",
        "global_financial_crisis_2007_2009",
        "covid_recession_2020",
    ):
        assert profiles[scenario_id]["post_comparable"] is False
        assert profiles[scenario_id]["remaining_non_comparable_evidence"]
        assert profiles[scenario_id]["scenario_family"] == "recession_recovery_cycle"


def test_autonomous_comparability_writes_tmp_only(tmp_path: Path) -> None:
    output = tmp_path / "phase35_comparability_realization.json"
    result = write_autonomous_comparability_realization(
        build_autonomous_comparability_realization(),
        output=output,
    )

    assert result["autonomous_comparability_realization_written"] is True
    assert result["written_file_count"] == 1
    assert output.is_file()


def test_autonomous_comparability_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_autonomous_comparability_realization(
            build_autonomous_comparability_realization(),
            output="data/backtests/phase35_comparability.json",
        )


def test_run_autonomous_comparability_realization_script(tmp_path: Path) -> None:
    output = tmp_path / "phase35_comparability_realization.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_autonomous_comparability_realization.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "autonomous_comparability_realization_ready=true" in result.stdout
    assert "post_comparable_scenario_count=2" in result.stdout
    assert "phase35_comparability_progress_status=comparable_scenarios_realized" in (
        result.stdout
    )
    assert output.is_file()
