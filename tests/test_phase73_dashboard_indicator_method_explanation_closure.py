from __future__ import annotations

import subprocess
import sys

from business_cycle.audits.phase73_dashboard_indicator_method_explanation_closure import (
    summarize_phase73_dashboard_indicator_method_explanation_closure,
)


def test_phase73_dashboard_indicator_method_explanation_closure_passes() -> None:
    summary = summarize_phase73_dashboard_indicator_method_explanation_closure()

    assert summary["result"] == "passed"
    assert summary["phase73_dashboard_indicator_method_explanation_ready"] is True
    assert summary["dashboard_indicator_method_explanation_ready"] is True
    assert summary["role_method_explanation_count"] == 39
    assert summary["method_definition_count"] == 4
    assert summary["legacy_dashboard_method_detail_renderable_count"] == 13
    assert summary["research_dashboard_method_detail_renderable_count"] == 39
    assert summary["computed_diagnostic_value_present_count"] == 0
    assert summary["method_promoted_to_product_answer_count"] == 0
    assert summary["current_data_used_to_infer_declared_phase_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["role_count_voting_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_model_behavior_change_count"] == 0
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0
    assert summary["product_capability_progress_ready"] is True
    assert summary["phase73_closure_status"] == (
        "closed_dashboard_indicator_method_explanation_ready_"
        "no_scoring_logic_change"
    )


def test_show_phase73_dashboard_indicator_method_explanation_closure_script() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/show_phase73_dashboard_indicator_method_explanation_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "phase73_dashboard_indicator_method_explanation_ready=true" in completed.stdout
    assert "dashboard_indicator_method_explanation_ready=true" in completed.stdout
    assert "legacy_dashboard_method_detail_renderable_count=13" in completed.stdout
    assert "phase73_closure_status=closed_dashboard_indicator_method_explanation_ready_no_scoring_logic_change" in completed.stdout
    assert "result=passed" in completed.stdout
