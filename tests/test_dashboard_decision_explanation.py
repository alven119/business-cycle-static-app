from __future__ import annotations

import subprocess
import sys

from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation,
    build_dashboard_decision_explanation_view_model,
    summarize_dashboard_decision_explanation,
)


def test_dashboard_decision_explanation_passes() -> None:
    summary = summarize_dashboard_decision_explanation()

    assert summary["result"] == "passed"
    assert summary["dashboard_decision_explanation_ready"] is True
    assert summary["declared_current_phase"] == "boom"
    assert summary["legal_next_phase"] == "recession"
    assert summary["narrative_card_count"] == 5
    assert summary["role_drilldown_count"] == 39
    assert summary["major_group_drilldown_count"] == 24
    assert summary["current_numeric_context_role_count"] == 37
    assert summary["chart_available_role_count"] == 37
    assert summary["unavailable_chart_role_count"] == 2
    assert summary["group_ready_for_formal_phase_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["semantic_drift_count"] == 0


def test_dashboard_decision_explanation_preserves_doctrine_boundaries() -> None:
    artifact = build_dashboard_decision_explanation()

    assert artifact["research_only"] is True
    assert artifact["output_mode"] == "research_only_dashboard_decision_explanation"
    assert artifact["trust_metadata"]["current_data_used_to_infer_declared_phase"] is False
    assert artifact["trust_metadata"]["missing_values_are_neutral"] is False
    assert artifact["trust_metadata"]["selector_or_rank_output_enabled"] is False
    assert artifact["current_data_used_to_infer_declared_phase_count"] == 0
    assert artifact["standalone_classifier_added_count"] == 0
    assert artifact["phase_rank_or_score_added_count"] == 0
    assert artifact["role_count_voting_added_count"] == 0
    assert "formal_current_phase_decision" in artifact["prohibited_uses"]
    assert len({card["card_id"] for card in artifact["narrative_cards"]}) == 5
    assert artifact["declared_state_summary_zh"]
    assert artifact["legal_next_transition_summary_zh"]
    assert artifact["support_contradiction_summary_zh"]
    assert artifact["missing_evidence_summary_zh"]
    assert artifact["why_not_formal_summary_zh"]


def test_dashboard_decision_explanation_view_model_is_bundle_ready() -> None:
    view_model = build_dashboard_decision_explanation_view_model()

    assert view_model["view_id"] == "dashboard_decision_explanation"
    assert view_model["dashboard_decision_explanation_ready"] is True
    assert view_model["prohibited_output_field_count"] == 0
    assert view_model["narrative_card_count"] == 5
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False


def test_show_dashboard_decision_explanation_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_dashboard_decision_explanation.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "dashboard_decision_explanation_ready=true" in completed.stdout
    assert "declared_current_phase=boom" in completed.stdout
    assert "legal_next_phase=recession" in completed.stdout
    assert "narrative_card_count=5" in completed.stdout
    assert "result=passed" in completed.stdout
