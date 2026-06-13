from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.phases.state_machine_catalog import (
    PhaseStateMachineConfigError,
    load_phase_state_machine_config,
)


def write_config(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def valid_config() -> str:
    return """
phase_order:
  - recession
  - recovery
  - growth
  - boom
min_phase_confidence: 0.65
min_available_weight: 0.70
min_score_for_initial_estimate: 65
min_score_margin: 8
transition_score_margin: 5
allow_initial_estimate: true
"""


def test_can_load_phase_state_machine_config() -> None:
    config = load_phase_state_machine_config("specs/common/phase_state_machine.yaml")

    assert config.phase_order == ["recession", "recovery", "growth", "boom"]
    assert config.allow_initial_estimate is True


def test_missing_phase_order_raises(tmp_path: Path) -> None:
    path = write_config(tmp_path / "config.yaml", valid_config().replace("phase_order:", "missing:"))

    with pytest.raises(PhaseStateMachineConfigError, match="phase_order"):
        load_phase_state_machine_config(path)


def test_phase_order_missing_required_phase_raises(tmp_path: Path) -> None:
    path = write_config(tmp_path / "config.yaml", valid_config().replace("  - boom\n", ""))

    with pytest.raises(PhaseStateMachineConfigError, match="missing required phase"):
        load_phase_state_machine_config(path)


def test_threshold_out_of_range_raises(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "config.yaml",
        valid_config().replace("min_phase_confidence: 0.65", "min_phase_confidence: 1.5"),
    )

    with pytest.raises(PhaseStateMachineConfigError, match="min_phase_confidence"):
        load_phase_state_machine_config(path)


def test_allow_initial_estimate_is_parsed(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "config.yaml",
        valid_config().replace("allow_initial_estimate: true", "allow_initial_estimate: false"),
    )

    config = load_phase_state_machine_config(path)

    assert config.allow_initial_estimate is False
