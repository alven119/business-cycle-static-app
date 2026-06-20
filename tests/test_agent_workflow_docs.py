from __future__ import annotations

from pathlib import Path

import yaml


AGENTS_PATH = Path("AGENTS.md")
WORKFLOW_PATH = Path("docs/agent_workflow.md")
PROMPT_TEMPLATES_PATH = Path("docs/prompt_templates.md")
GATES_PATH = Path("specs/backtests/phase_acceptance_gates.yaml")


def test_agent_workflow_files_exist() -> None:
    assert AGENTS_PATH.exists()
    assert WORKFLOW_PATH.exists()
    assert PROMPT_TEMPLATES_PATH.exists()
    assert GATES_PATH.exists()


def test_agents_contains_self_repair_contract() -> None:
    text = AGENTS_PATH.read_text(encoding="utf-8")

    assert "Self-repair loop" in text
    assert "Do not report intermediate failed results unless blocked" in text


def test_phase_acceptance_gates_yaml_loads() -> None:
    payload = yaml.safe_load(GATES_PATH.read_text(encoding="utf-8"))

    assert isinstance(payload, dict)
    assert "common_hard_gates" in payload
    assert "common_checks" in payload
    assert "phase_specific_gates" in payload


def test_phase_acceptance_gates_include_required_phase_gates() -> None:
    gates = yaml.safe_load(GATES_PATH.read_text(encoding="utf-8"))
    phase_specific = gates["phase_specific_gates"]

    recovery_gates = phase_specific["recovery_refinement_experiment"]["hard_gates"]
    boom_overlay_gates = phase_specific["boom_ending_watch_overlay"]["hard_gates"]
    recovery_overlay_gates = phase_specific["recovery_watch_overlay"]["hard_gates"]
    recovery_integration_gates = phase_specific["recovery_watch_integration_guardrails"]["hard_gates"]
    evidence_architecture_gates = phase_specific["cycle_transition_evidence_architecture"]["hard_gates"]
    badge_schema_gates = phase_specific["transition_evidence_badge_schema"]["hard_gates"]
    badge_fixture_gates = phase_specific["transition_evidence_badge_fixtures"]["hard_gates"]
    renderer_contract_gates = phase_specific["transition_evidence_badge_renderer_contract"]["hard_gates"]
    display_fixture_gates = phase_specific["transition_evidence_badge_display_fixtures"]["hard_gates"]
    readiness_gates = phase_specific["dashboard_evidence_integration_readiness"]["hard_gates"]
    portfolio_plan_gates = phase_specific["portfolio_policy_research_plan"]["hard_gates"]
    portfolio_template_gates = phase_specific["portfolio_policy_template_schema"]["hard_gates"]

    assert "expected_fail_count == 0" in recovery_gates
    assert "fail_count == 0" in boom_overlay_gates
    assert "fail_count == 0" in recovery_overlay_gates
    assert "gfc_has_trough_or_recovery_watch == true" in recovery_overlay_gates
    assert "euro_debt_excessive_recovery_watch == false" in recovery_overlay_gates
    assert "direct_recovery_confirmation_allowed == false" in recovery_integration_gates
    assert "direct_portfolio_action_allowed == false" in recovery_integration_gates
    assert "recommended_next_phase == 7G" in recovery_integration_gates
    assert "formal_phase_change_allowed_now == false" in evidence_architecture_gates
    assert "direct_trade_signal_allowed_now == false" in evidence_architecture_gates
    assert "recommended_next_phase == 7G1" in evidence_architecture_gates
    assert "dashboard_contract_allowed_now == false" in badge_schema_gates
    assert "direct_trade_signal_allowed == false" in badge_schema_gates
    assert "recommended_next_phase == 7G2" in badge_schema_gates
    assert "valid_pass_count == valid_fixture_count" in badge_fixture_gates
    assert "invalid_rejected_count == invalid_fixture_count" in badge_fixture_gates
    assert "result == passed" in badge_fixture_gates
    assert "direct_trade_text_blocked == true" in renderer_contract_gates
    assert "phase_override_field_blocked == true" in renderer_contract_gates
    assert "dashboard_renderer_wiring_allowed_now == false" in renderer_contract_gates
    assert "recommended_next_phase == 7G4" in renderer_contract_gates
    assert "valid_display_pass_count == valid_display_fixture_count" in display_fixture_gates
    assert "invalid_display_rejected_count == invalid_display_fixture_count" in display_fixture_gates
    assert "result == passed" in display_fixture_gates
    assert "dashboard_wiring_allowed_now == false" in readiness_gates
    assert "public_output_allowed_now == false" in readiness_gates
    assert "recommended_next_phase == 8A" in readiness_gates
    assert "live_allocation_allowed_now == false" in portfolio_plan_gates
    assert "trade_signal_generation_allowed_now == false" in portfolio_plan_gates
    assert "recommended_next_phase == 8B" in portfolio_plan_gates
    assert "live_allocation_allowed_now == false" in portfolio_template_gates
    assert "valid_pass_count == valid_template_count" in portfolio_template_gates
    assert "recommended_next_phase == 8C" in portfolio_template_gates


def test_prompt_templates_include_autonomous_policy() -> None:
    text = PROMPT_TEMPLATES_PATH.read_text(encoding="utf-8")

    assert "Autonomous completion policy" in text
    assert "If hard gates fail, inspect root cause, fix, and rerun" in text
