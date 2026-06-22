from __future__ import annotations

from pathlib import Path

import yaml

from business_cycle.audits.model_parameter_drift import (
    detect_classification_change,
    parameter_hash_changes_when_value_changes,
    summarize_model_parameter_drift,
)
from business_cycle.audits.model_parameter_inventory import (
    DEFAULT_REGISTRY_PATH,
    discover_model_parameters,
)


def test_temp_spec_threshold_without_registry_mapping_is_detected(tmp_path: Path) -> None:
    temp_spec = tmp_path / "unmapped_threshold.yaml"
    temp_spec.write_text("experimental_threshold: 0.42\n", encoding="utf-8")

    summary = summarize_model_parameter_drift(additional_yaml_paths=[temp_spec])

    assert summary["parameter_inventory_drift_detection_ready"] is True
    assert summary["unmapped_parameter_count"] > 0


def test_temp_python_decision_constant_without_registry_mapping_is_detected(
    tmp_path: Path,
) -> None:
    temp_source = tmp_path / "decision_constants.py"
    temp_source.write_text("DECISION_THRESHOLD = 0.7\n", encoding="utf-8")

    summary = summarize_model_parameter_drift(additional_python_paths=[temp_source])

    assert summary["unmapped_parameter_count"] > 0


def test_parameter_value_change_changes_model_hash() -> None:
    parameter = discover_model_parameters()[0]

    assert parameter_hash_changes_when_value_changes(parameter)


def test_removed_registered_parameter_creates_orphan(tmp_path: Path) -> None:
    payload = yaml.safe_load(DEFAULT_REGISTRY_PATH.read_text(encoding="utf-8"))
    payload["model_parameter_registry"]["required_parameter_ids"] = [
        "missing::parameter"
    ]
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    summary = summarize_model_parameter_drift(registry_path=registry)

    assert summary["orphaned_registry_parameter_count"] == 1


def test_experimental_to_formal_classification_change_is_detected() -> None:
    parameter = next(
        row
        for row in discover_model_parameters()
        if row.formal_or_experimental == "experimental"
    )

    assert detect_classification_change(parameter, "formal")


def test_default_parameter_drift_summary_has_zero_hard_gate_counts() -> None:
    summary = summarize_model_parameter_drift()

    assert summary["parameter_inventory_drift_detection_ready"] is True
    assert summary["unmapped_parameter_count"] == 0
    assert summary["parameter_hash_mismatch_count"] == 0
    assert summary["parameter_classification_drift_count"] == 0
