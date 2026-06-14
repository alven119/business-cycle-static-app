from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.phases.cycle_context import (
    CurrentCycleContextError,
    load_current_cycle_context,
)


def test_current_cycle_context_yaml_can_be_loaded() -> None:
    context = load_current_cycle_context("specs/common/current_cycle_context.yaml")

    assert context is not None
    assert context.baseline_phase_id == "boom"
    assert context.baseline_stage_note_zh == "榮景期第一年剛結束"
    assert context.use_as_default_previous_phase is True


def test_current_cycle_context_rejects_invalid_baseline_phase(tmp_path: Path) -> None:
    path = tmp_path / "context.yaml"
    path.write_text(
        "\n".join(
            [
                "baseline_phase_id: expansion",
                "baseline_phase_name_zh: 擴張",
                "baseline_stage_note_zh: 測試",
                "source_type: test",
                "source_note_zh: 測試",
                "use_as_default_previous_phase: true",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(CurrentCycleContextError, match="baseline_phase_id"):
        load_current_cycle_context(path)


def test_current_cycle_context_requires_boolean_default_flag(tmp_path: Path) -> None:
    path = tmp_path / "context.yaml"
    path.write_text(
        "\n".join(
            [
                "baseline_phase_id: boom",
                "baseline_phase_name_zh: 榮景期",
                "baseline_stage_note_zh: 測試",
                "source_type: test",
                "source_note_zh: 測試",
                "use_as_default_previous_phase: 'true'",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(CurrentCycleContextError, match="use_as_default_previous_phase"):
        load_current_cycle_context(path)
