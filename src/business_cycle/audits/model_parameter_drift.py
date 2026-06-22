"""QA3 model parameter inventory drift detection."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from business_cycle.audits.model_parameter_inventory import (
    DEFAULT_REGISTRY_PATH,
    ModelParameter,
    compute_parameter_manifest_hash,
    discover_model_parameters,
    load_model_parameter_registry,
)


def summarize_model_parameter_drift(
    *,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    additional_yaml_paths: list[str | Path] | None = None,
    additional_python_paths: list[str | Path] | None = None,
    expected_parameter_hash: str | None = None,
) -> dict[str, Any]:
    """Summarize QA3 drift gates for the current parameter inventory."""

    registry = load_model_parameter_registry(registry_path)
    parameters = discover_model_parameters(
        registry_path=registry_path,
        additional_yaml_paths=additional_yaml_paths,
        additional_python_paths=additional_python_paths,
    )
    source_paths = {str(path) for path in registry.get("registered_source_paths", [])}
    required_ids = set(registry.get("required_parameter_ids") or [])
    discovered_ids = {parameter.parameter_id for parameter in parameters}
    unmapped = [
        parameter
        for parameter in parameters
        if parameter.parameter_layer == "unclassified"
        or parameter.source_path not in source_paths
    ]
    orphaned = sorted(required_ids - discovered_ids)
    current_hash = compute_parameter_manifest_hash(parameters)
    hash_mismatch = expected_parameter_hash is not None and current_hash != expected_parameter_hash
    classification_drift = [
        parameter for parameter in parameters if parameter.formal_or_experimental == "unknown"
    ]
    return {
        "phase": "QA3",
        "parameter_inventory_drift_detection_ready": True,
        "unmapped_parameter_count": len(unmapped),
        "parameter_hash_mismatch_count": 1 if hash_mismatch else 0,
        "parameter_classification_drift_count": len(classification_drift),
        "orphaned_registry_parameter_count": len(orphaned),
        "parameter_manifest_hash": current_hash,
        "unmapped_parameters": [parameter.to_dict() for parameter in unmapped],
        "orphaned_parameter_ids": orphaned,
    }


def parameter_hash_changes_when_value_changes(parameter: ModelParameter) -> bool:
    """Return true when mutating one parameter value changes the manifest hash."""

    original = [parameter]
    replacement = replace(parameter, value=_changed_value(parameter.value))
    return compute_parameter_manifest_hash(original) != compute_parameter_manifest_hash([replacement])


def detect_classification_change(
    before: ModelParameter,
    after_formal_or_experimental: str,
) -> bool:
    """Detect experimental/formal classification drift for one parameter."""

    after = replace(before, formal_or_experimental=after_formal_or_experimental)
    return before.formal_or_experimental != after.formal_or_experimental


def _changed_value(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int | float):
        return value + 1
    if isinstance(value, str):
        return f"{value}_changed"
    if isinstance(value, list):
        return [*value, "__changed__"]
    if isinstance(value, dict):
        return {**value, "__changed__": True}
    return "__changed__"
