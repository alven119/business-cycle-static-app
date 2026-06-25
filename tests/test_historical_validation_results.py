from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from business_cycle.validation.historical_validation_results import (
    build_historical_validation_results,
    validate_historical_validation_result_artifact,
    write_historical_validation_results,
)


def test_historical_validation_results_materialize_comparable_subset() -> None:
    run = build_historical_validation_results()
    artifact = run["historical_validation_result_artifact"]

    assert run["historical_validation_result_runtime_ready"] is True
    assert run["scenario_count"] == 5
    assert run["comparable_scenario_count"] == 2
    assert run["non_comparable_scenario_count"] == 3
    assert run["historical_validation_result_artifact_count"] == 1
    assert run["historical_accuracy_metric_count"] == 5
    assert run["metric_computation_scope"] == "historical_accuracy_only"
    assert run["economic_performance_metric_count"] == 0
    assert run["candidate_phase_emitted"] is False
    assert run["current_phase_emitted"] is False
    assert run["label_used_by_runtime_count"] == 0
    assert artifact["research_only"] is True
    assert artifact["validation_only"] is True
    assert {item["scenario_id"] for item in artifact["comparable_scenario_results"]} == {
        "euro_debt_slowdown_2011_2012",
        "late_cycle_2018_2019",
    }
    assert len(artifact["non_comparable_scenario_evidence"]) == 3


def test_historical_validation_result_validation_rejects_forbidden_fields() -> None:
    run = build_historical_validation_results()
    artifact = dict(run["historical_validation_result_artifact"])
    artifact["buy_signal"] = "never"

    validation = validate_historical_validation_result_artifact(artifact)

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_result_field_count"] == 1


def test_historical_validation_results_writes_tmp_only(tmp_path: Path) -> None:
    output = tmp_path / "phase36_historical_validation_results.json"
    result = write_historical_validation_results(
        build_historical_validation_results(),
        output=output,
    )

    assert result["historical_validation_result_written"] is True
    assert result["written_file_count"] == 1
    assert output.is_file()


def test_historical_validation_results_rejects_repo_output() -> None:
    with pytest.raises(ValueError):
        write_historical_validation_results(
            build_historical_validation_results(),
            output="data/backtests/phase36_results.json",
        )


def test_generate_historical_validation_results_script(tmp_path: Path) -> None:
    output = tmp_path / "phase36_historical_validation_results.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_historical_validation_results.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "historical_validation_result_runtime_ready=true" in result.stdout
    assert "comparable_scenario_count=2" in result.stdout
    assert "historical_validation_result_written=true" in result.stdout
    assert output.is_file()
