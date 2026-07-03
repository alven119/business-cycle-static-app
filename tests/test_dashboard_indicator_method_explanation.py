from __future__ import annotations

import subprocess
import sys

from business_cycle.render.dashboard_indicator_method_explanation import (
    build_dashboard_indicator_method_explanation,
    build_dashboard_indicator_method_explanation_view_model,
    summarize_dashboard_indicator_method_explanation,
)


def test_phase73_dashboard_indicator_method_explanation_passes() -> None:
    summary = summarize_dashboard_indicator_method_explanation()

    assert summary["result"] == "passed"
    assert summary["dashboard_indicator_method_explanation_ready"] is True
    assert summary["role_method_explanation_count"] == 39
    assert summary["method_definition_count"] == 4
    assert summary["role_with_required_input_count"] == 39
    assert summary["role_with_frequency_handling_count"] == 39
    assert summary["role_with_missing_value_policy_count"] == 39
    assert summary["role_with_window_rule_count"] == 39
    assert summary["role_with_directionality_count"] == 39
    assert summary["role_with_score_interpretation_count"] == 39
    assert summary["role_with_confidence_reducer_count"] == 39
    assert summary["role_with_pseudo_code_count"] == 39
    assert summary["legacy_dashboard_method_detail_renderable_count"] == 13
    assert summary["research_dashboard_method_detail_renderable_count"] == 39
    assert summary["computed_diagnostic_value_present_count"] == 0
    assert summary["method_promoted_to_product_answer_count"] == 0
    assert summary["standalone_classifier_added_count"] == 0
    assert summary["phase_rank_or_score_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase73_method_rows_explain_recipe_without_runtime_decision() -> None:
    artifact = build_dashboard_indicator_method_explanation()

    for row in artifact["role_method_explanation_rows"]:
        assert row["method_id"]
        assert row["method_purpose_zh"]
        assert row["frequency_handling_zh"]
        assert row["missing_value_handling_zh"]
        assert row["directionality_detail"]
        assert "分數越高" in row["score_interpretation_zh"]["high_score_zh"]
        assert "分數越低" in row["score_interpretation_zh"]["low_score_zh"]
        assert "分數接近 0" in row["score_interpretation_zh"]["neutral_score_zh"]
        assert row["confidence_reduce_when"]
        assert row["pseudo_code_zh"]
        assert row["computed_diagnostic_value_present"] is False
        assert "未使用歷史答案" in row["method_assignment_basis_zh"]
        assert "產品答案" in row["why_not_product_answer_zh"]


def test_phase73_view_model_is_dashboard_ready_and_research_only() -> None:
    view_model = build_dashboard_indicator_method_explanation_view_model()

    assert view_model["view_id"] == "dashboard_indicator_method_explanation"
    assert view_model["research_only"] is True
    assert view_model["role_method_explanation_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0


def test_show_dashboard_indicator_method_explanation_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_dashboard_indicator_method_explanation.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "dashboard_indicator_method_explanation_ready=true" in completed.stdout
    assert "role_method_explanation_count=39" in completed.stdout
    assert "legacy_dashboard_method_detail_renderable_count=13" in completed.stdout
    assert "result=passed" in completed.stdout
