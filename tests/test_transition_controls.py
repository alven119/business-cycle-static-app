from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.phases.transition_controls import (
    TransitionControlsConfigError,
    load_transition_controls_config,
)

CONTROLS_PATH = Path("specs/backtests/transition_controls_experiment.yaml")
BREADTH_CONTROLS_PATH = Path("specs/backtests/transition_controls_recession_breadth_experiment.yaml")


def test_load_transition_controls_experiment_yaml() -> None:
    config = load_transition_controls_config(CONTROLS_PATH)

    assert config.version == 1
    assert config.enabled is False
    assert config.transition_watch_required.enabled is True
    assert config.confirmation_period.required_periods == 2
    assert config.hysteresis_margin.min_score_margin == 5.0
    assert config.cooldown_period.periods_after_confirmed == 2


def test_transition_controls_caveats_are_present() -> None:
    config = load_transition_controls_config(CONTROLS_PATH)

    assert any("修訂後歷史資料" in caveat for caveat in config.caveats_zh)
    assert any("不構成投資建議" in caveat for caveat in config.caveats_zh)


def test_invalid_required_periods_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        CONTROLS_PATH.read_text(encoding="utf-8").replace("required_periods: 2", "required_periods: 0"),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="required_periods"):
        load_transition_controls_config(path)


def test_invalid_hysteresis_margin_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        CONTROLS_PATH.read_text(encoding="utf-8").replace("min_score_margin: 5.0", "min_score_margin: -1"),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_score_margin"):
        load_transition_controls_config(path)


def test_invalid_cooldown_period_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        CONTROLS_PATH.read_text(encoding="utf-8").replace("periods_after_confirmed: 2", "periods_after_confirmed: -1"),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="periods_after_confirmed"):
        load_transition_controls_config(path)


def test_invalid_breadth_min_group_count_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        CONTROLS_PATH.read_text(encoding="utf-8").replace("min_group_count: 2", "min_group_count: 0"),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_group_count"):
        load_transition_controls_config(path)


def test_recession_breadth_controls_yaml_fields() -> None:
    config = load_transition_controls_config(BREADTH_CONTROLS_PATH)
    breadth = config.breadth_confirmation

    assert config.enabled is True
    assert breadth.enabled is True
    assert breadth.target_phases == ["recession"]
    assert breadth.min_group_count == 3
    assert breadth.min_core_group_count == 2
    assert breadth.min_indicator_count == 4
    assert breadth.min_phase_signal_score == 55.0
    assert breadth.min_indicator_confidence == 0.5
    assert "employment" in breadth.allowed_groups


def test_invalid_breadth_min_indicator_count_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        BREADTH_CONTROLS_PATH.read_text(encoding="utf-8").replace("min_indicator_count: 4", "min_indicator_count: 0"),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_indicator_count"):
        load_transition_controls_config(path)


def test_invalid_breadth_min_confidence_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        BREADTH_CONTROLS_PATH.read_text(encoding="utf-8").replace(
            "min_indicator_confidence: 0.5",
            "min_indicator_confidence: 1.5",
        ),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_indicator_confidence"):
        load_transition_controls_config(path)


def test_invalid_breadth_min_phase_signal_score_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        BREADTH_CONTROLS_PATH.read_text(encoding="utf-8").replace(
            "min_phase_signal_score: 55.0",
            "min_phase_signal_score: 101",
        ),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_phase_signal_score"):
        load_transition_controls_config(path)
