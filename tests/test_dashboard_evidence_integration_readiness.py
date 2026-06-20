from __future__ import annotations

from pathlib import Path

from business_cycle.render.dashboard_evidence_readiness import (
    load_dashboard_evidence_integration_readiness,
    summarize_dashboard_evidence_integration_readiness,
    validate_dashboard_evidence_integration_readiness,
)

READINESS_PATH = Path("specs/common/dashboard_evidence_integration_readiness.yaml")


def test_dashboard_evidence_integration_readiness_yaml_can_be_loaded() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)

    assert readiness.version == 1
    assert readiness.status == "draft"
    validate_dashboard_evidence_integration_readiness(readiness)


def test_dashboard_evidence_integration_readiness_summary_counts() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)
    summary = summarize_dashboard_evidence_integration_readiness(readiness)

    assert summary["artifact_count"] > 0
    assert summary["validator_count"] > 0
    assert summary["active_blocker_count"] > 0


def test_dashboard_evidence_integration_required_blockers_are_active() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)
    active_ids = {
        blocker["blocker_id"]
        for blocker in readiness.dashboard_integration_blockers
        if blocker["active"] is True
    }

    assert "dashboard_renderer_not_wired" in active_ids
    assert "generated_site_validation_not_updated" in active_ids
    assert "no_phase_decision_impact_allowed" in active_ids


def test_dashboard_evidence_integration_closure_and_next_phase() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)
    summary = summarize_dashboard_evidence_integration_readiness(readiness)

    assert summary["phase_7g_closure_status"] == "ready_to_close_after_validation"
    assert summary["recommended_next_phase"] == "8A"


def test_dashboard_evidence_integration_blocks_wiring_public_output_and_decisions() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)
    summary = summarize_dashboard_evidence_integration_readiness(readiness)

    assert summary["dashboard_wiring_allowed_now"] is False
    assert summary["public_output_allowed_now"] is False
    assert summary["formal_decision_impact_allowed"] is False


def test_dashboard_evidence_integration_contains_required_wiring_prerequisites() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)
    target_ids = {target["target_id"] for target in readiness.required_before_dashboard_wiring}

    assert "generated_site_validation_updated" in target_ids
    assert "html_text_safety_tests_added" in target_ids
    assert "no_formal_decision_impact" in target_ids


def test_dashboard_evidence_integration_contains_no_investment_advice_caveat() -> None:
    readiness = load_dashboard_evidence_integration_readiness(READINESS_PATH)

    assert any("不構成投資建議" in caveat for caveat in readiness.caveats_zh)
