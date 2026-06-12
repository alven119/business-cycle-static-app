from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.indicators.catalog import load_indicator_scoring_specs
from business_cycle.phases.catalog import PhaseCatalogError, load_phase_spec, load_phase_specs
from business_cycle.phases.specs import PhaseScoringSpec


def write_yaml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def minimal_phase_yaml(phase_id: str = "recovery") -> str:
    return f"""
phase_id: {phase_id}
phase_name_zh: 復甦期
description_zh: 測試 spec
indicators:
  - indicator_id: unemployment_rate
    weight: 1.0
    role: core
minimum_available_weight: 0.7
confidence_policy:
  minimum_confidence: 0.6
early_mid_late_thresholds:
  early: 55
  mid: 70
  late: 82
"""


def test_can_load_recovery_yaml() -> None:
    spec = load_phase_spec("specs/phases/recovery.yaml")

    assert spec.phase_id == "recovery"
    assert spec.phase_name_zh == "復甦期"
    assert isinstance(spec, PhaseScoringSpec)


def test_missing_phase_id_raises(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "phase.yaml",
        """
phase_name_zh: 測試
description_zh: 測試
indicators:
  - indicator_id: unemployment_rate
    weight: 1
minimum_available_weight: 0.7
confidence_policy: {}
early_mid_late_thresholds: {}
""",
    )

    with pytest.raises(PhaseCatalogError, match="phase_id"):
        load_phase_spec(path)


def test_missing_indicators_raises(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "phase.yaml",
        """
phase_id: recovery
phase_name_zh: 復甦期
description_zh: 測試
minimum_available_weight: 0.7
confidence_policy: {}
early_mid_late_thresholds: {}
""",
    )

    with pytest.raises(PhaseCatalogError, match="indicators"):
        load_phase_spec(path)


def test_indicator_weight_must_be_positive(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "phase.yaml",
        """
phase_id: recovery
phase_name_zh: 復甦期
description_zh: 測試
indicators:
  - indicator_id: unemployment_rate
    weight: 0
minimum_available_weight: 0.7
confidence_policy: {}
early_mid_late_thresholds: {}
""",
    )

    with pytest.raises(PhaseCatalogError, match="weight must be > 0"):
        load_phase_spec(path)


def test_minimum_available_weight_must_be_between_zero_and_one(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "phase.yaml",
        minimal_phase_yaml().replace("minimum_available_weight: 0.7", "minimum_available_weight: 1.5"),
    )

    with pytest.raises(PhaseCatalogError, match="minimum_available_weight"):
        load_phase_spec(path)


def test_duplicate_phase_id_raises(tmp_path: Path) -> None:
    write_yaml(tmp_path / "a.yaml", minimal_phase_yaml("recovery"))
    write_yaml(tmp_path / "b.yaml", minimal_phase_yaml("recovery"))

    with pytest.raises(PhaseCatalogError, match="Duplicate phase_id"):
        load_phase_specs(tmp_path)


def test_load_phase_specs_reads_directory(tmp_path: Path) -> None:
    write_yaml(tmp_path / "recovery.yaml", minimal_phase_yaml("recovery"))
    write_yaml(tmp_path / "growth.yml", minimal_phase_yaml("growth"))

    specs = load_phase_specs(tmp_path)

    assert list(specs) == ["growth", "recovery"]


def test_load_phase_specs_reads_single_file(tmp_path: Path) -> None:
    path = write_yaml(tmp_path / "recovery.yaml", minimal_phase_yaml("recovery"))

    specs = load_phase_specs(path)

    assert list(specs) == ["recovery"]


def test_recovery_yaml_has_at_least_four_indicators() -> None:
    spec = load_phase_spec("specs/phases/recovery.yaml")

    assert len(spec.indicators) >= 4


def test_recovery_yaml_indicator_ids_exist_in_indicator_catalog() -> None:
    phase_spec = load_phase_spec("specs/phases/recovery.yaml")
    indicator_specs = load_indicator_scoring_specs("specs/indicator_catalog.yaml")

    missing = [
        indicator.indicator_id
        for indicator in phase_spec.indicators
        if indicator.indicator_id not in indicator_specs
    ]
    assert missing == []


def test_weights_are_normalized_and_raw_total_weight_is_preserved(tmp_path: Path) -> None:
    path = write_yaml(
        tmp_path / "phase.yaml",
        """
phase_id: recovery
phase_name_zh: 復甦期
description_zh: 測試
indicators:
  - indicator_id: a
    weight: 2
  - indicator_id: b
    weight: 3
minimum_available_weight: 0.7
confidence_policy: {}
early_mid_late_thresholds:
  early: 55
  mid: 70
  late: 82
""",
    )

    spec = load_phase_spec(path)

    assert sum(indicator.weight for indicator in spec.indicators) == pytest.approx(1.0)
    assert spec.details["raw_total_weight"] == 5.0

