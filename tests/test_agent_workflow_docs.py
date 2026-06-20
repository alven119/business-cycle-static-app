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

    assert "expected_fail_count == 0" in recovery_gates
    assert "fail_count == 0" in boom_overlay_gates


def test_prompt_templates_include_autonomous_policy() -> None:
    text = PROMPT_TEMPLATES_PATH.read_text(encoding="utf-8")

    assert "Autonomous completion policy" in text
    assert "If hard gates fail, inspect root cause, fix, and rerun" in text
