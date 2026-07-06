from __future__ import annotations

import json
import subprocess
import sys

import pytest

from business_cycle.portfolio.research_backtest_artifacts import (
    ResearchBacktestArtifactContractError,
    build_research_backtest_artifact_bundle,
    load_research_backtest_artifact_contract,
    summarize_research_backtest_artifacts,
    write_research_backtest_artifacts,
)


def test_phase80_research_backtest_artifacts_pass() -> None:
    summary = summarize_research_backtest_artifacts()

    assert summary["result"] == "passed"
    assert summary["research_backtest_artifact_contract_ready"] is True
    assert summary["research_backtest_artifact_generator_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["source_replay_row_count"] == 10
    assert summary["research_backtest_artifact_count"] == 10
    assert summary["artifact_with_policy_schedule_ref_count"] == 10
    assert summary["artifact_with_cash_flow_kernel_ref_count"] == 10
    assert summary["artifact_with_metric_formula_refs_count"] == 10
    assert summary["artifact_with_input_hash_count"] == 10
    assert summary["artifact_with_provenance_count"] == 10
    assert summary["metric_formula_reference_family_count"] == 11
    assert summary["metric_value_count"] == 0
    assert summary["risk_metric_value_count"] == 0
    assert summary["historical_accuracy_metric_count"] == 0
    assert summary["economic_performance_metric_count"] == 0
    assert summary["metric_computation_enabled"] is False
    assert summary["backtest_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["public_output_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_phase80_artifacts_preserve_formula_refs_without_values() -> None:
    bundle = build_research_backtest_artifact_bundle()
    artifacts = bundle["research_backtest_artifacts"]

    assert len(artifacts) == 10
    assert {row["output_mode"] for row in artifacts} == {
        "research_only_backtest_artifact"
    }
    assert all(row["research_only"] is True for row in artifacts)
    assert all(row["metric_value_count"] == 0 for row in artifacts)
    assert all(row["risk_metric_value_count"] == 0 for row in artifacts)
    assert all(row["input_hash"] for row in artifacts)
    assert all(row["provenance"]["metric_policy"] for row in artifacts)
    assert all(
        metric["value_computed"] is False
        for row in artifacts
        for metric in row["metric_formula_refs"]
    )


def test_phase80_contract_disables_execution_paths() -> None:
    contract = load_research_backtest_artifact_contract()

    assert contract["output_policy"]["output_mode"] == "research_only_backtest_artifact"
    assert contract["output_policy"]["generated_output_under_tmp_only"] is True
    assert contract["output_policy"]["backtest_execution_allowed"] is False
    assert contract["output_policy"]["metric_computation_allowed"] is False
    assert contract["output_policy"]["public_output_allowed"] is False
    assert contract["metric_policy"]["metric_formula_references_allowed"] is True
    assert contract["metric_policy"]["metric_value_computation_allowed"] is False
    assert all(value is False for value in contract["disabled_runtime_guards"].values())


def test_phase80_writer_requires_tmp_output(tmp_path) -> None:
    output = tmp_path / "phase80_research_backtest_artifacts.json"

    payload = write_research_backtest_artifacts(output)
    written = json.loads(output.read_text(encoding="utf-8"))

    assert payload["research_backtest_artifact_generator_ready"] is True
    assert written["research_backtest_artifact_count"] == 10
    assert len(written["research_backtest_artifacts"]) == 10

    with pytest.raises(ResearchBacktestArtifactContractError):
        write_research_backtest_artifacts("phase80_backtest_artifacts.json")


def test_show_research_backtest_artifacts_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_research_backtest_artifacts.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "research_backtest_artifact_generator_ready=true" in completed.stdout
    assert "research_backtest_artifact_count=10" in completed.stdout
    assert "metric_value_count=0" in completed.stdout
    assert "public_output_count=0" in completed.stdout
    assert "result=passed" in completed.stdout


def test_generate_research_backtest_artifacts_script(tmp_path) -> None:
    output = tmp_path / "phase80_research_backtest_artifacts.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/generate_research_backtest_artifacts.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert "research_backtest_artifact_generator_ready=true" in completed.stdout
    assert "research_backtest_artifact_count=10" in completed.stdout
    assert "prohibited_output_field_count=0" in completed.stdout
