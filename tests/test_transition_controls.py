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


def test_invalid_required_groups_subset_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(minimal_breadth_yaml(required_groups=["missing_group"]), encoding="utf-8")

    with pytest.raises(TransitionControlsConfigError, match="required_groups"):
        load_transition_controls_config(path)


def test_invalid_core_non_core_overlap_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        minimal_breadth_yaml(
            core_groups=["employment", "consumption"],
            non_core_groups=["employment"],
        ),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="must not overlap"):
        load_transition_controls_config(path)


def test_invalid_min_core_group_count_raises(tmp_path: Path) -> None:
    path = tmp_path / "controls.yaml"
    path.write_text(
        minimal_breadth_yaml(
            min_core_group_count=4,
            core_groups=["employment", "consumption", "investment"],
        ),
        encoding="utf-8",
    )

    with pytest.raises(TransitionControlsConfigError, match="min_core_group_count"):
        load_transition_controls_config(path)


def minimal_breadth_yaml(
    *,
    min_core_group_count: int = 2,
    required_groups: list[str] | None = None,
    core_groups: list[str] | None = None,
    non_core_groups: list[str] | None = None,
) -> str:
    def lines(items: list[str] | None, indent: str) -> str:
        if not items:
            return ""
        return "".join(f"{indent}- {item}\n" for item in items)

    required = f"      required_groups:\n{lines(required_groups, '        ')}" if required_groups else ""
    core = f"      core_groups:\n{lines(core_groups, '        ')}" if core_groups else ""
    non_core = f"      non_core_groups:\n{lines(non_core_groups, '        ')}" if non_core_groups else ""
    return f"""
transition_controls:
  version: 1
  enabled: true
  controls:
    transition_watch_required:
      enabled: false
    confirmation_period:
      enabled: false
    hysteresis_margin:
      enabled: false
    cooldown_period:
      enabled: false
    breadth_confirmation:
      enabled: true
      target_phases:
        - recession
      min_group_count: 3
      min_core_group_count: {min_core_group_count}
      min_indicator_count: 4
      min_phase_signal_score: 55.0
      min_indicator_confidence: 0.5
{required}{core}{non_core}      allowed_groups:
        - employment
        - consumption
        - investment
        - trade
  caveats_zh:
    - 使用修訂後歷史資料。
    - 不構成投資建議。
""".lstrip()
