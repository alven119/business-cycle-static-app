from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase82_replay_backtest_lineage_closure import (
    summarize_phase82_replay_backtest_lineage_closure,
)


def test_phase82_replay_backtest_lineage_closure_passes() -> None:
    summary = summarize_phase82_replay_backtest_lineage_closure()

    assert summary["result"] == "passed"
    assert summary["phase82_closure_ready"] is True
    assert summary["replay_backtest_lineage_ready"] is True
    assert summary["scenario_count"] == 5
    assert summary["replay_row_count"] == 10
    assert summary["research_backtest_artifact_count"] == 10
    assert summary["artifact_replay_row_link_count"] == 10
    assert summary["source_contract_hash_coverage_complete"] is True
    assert summary["source_contract_hash_mismatch_count"] == 0
    assert summary["input_hash_coverage_complete"] is True
    assert summary["input_hash_mismatch_count"] == 0
    assert summary["silent_fallback_count"] == 0
    assert summary["metric_value_count"] == 0
    assert summary["risk_metric_value_count"] == 0
    assert summary["backtest_execution_count"] == 0
    assert summary["current_allocation_recommendation_count"] == 0
    assert summary["trade_signal_output_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["product_capability_progress_ready"] is True
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_doctrine_alignment_status"] == "aligned"
    assert summary["legal_transition_semantics_preserved"] is True
    assert summary["development_next_phase"] == 83
    assert (
        summary["phase82_closure_status"]
        == "closed_replay_backtest_lineage_hardened_no_silent_fallback"
    )


def test_show_phase82_replay_backtest_lineage_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase82_replay_backtest_lineage_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase82_closure_ready=true" in completed.stdout
    assert "replay_backtest_lineage_ready=true" in completed.stdout
    assert "input_hash_coverage_complete=true" in completed.stdout
    assert "silent_fallback_count=0" in completed.stdout
    assert "phase82_closure_status=closed_replay_backtest_lineage_hardened_no_silent_fallback" in completed.stdout
    assert "result=passed" in completed.stdout
