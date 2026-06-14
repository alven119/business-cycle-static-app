"""Load educational explanations used by the static dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_phase_score_explanations(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load phase score explanation YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("phase_score_explanations", payload)
    if not isinstance(raw, dict):
        raise ValueError("phase score explanations must be a mapping")
    return {str(key): _mapping(value) for key, value in raw.items()}


def load_indicator_explanations(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load indicator explanation YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("indicators", payload)
    if not isinstance(raw, dict):
        raise ValueError("indicator explanations must be a mapping")
    return {str(key): _mapping(value) for key, value in raw.items()}


def get_phase_score_explanation(
    mapping: dict[str, dict[str, Any]],
    phase_id: str | None,
) -> dict[str, Any]:
    """Return one phase explanation or an empty fallback mapping."""

    if phase_id is None:
        return {}
    return mapping.get(phase_id, {})


def get_indicator_explanation(
    mapping: dict[str, dict[str, Any]],
    indicator_id: str | None,
) -> dict[str, Any]:
    """Return one indicator explanation or an empty fallback mapping."""

    if indicator_id is None:
        return {}
    return mapping.get(indicator_id, {})


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        return {}
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f"YAML file must be a mapping: {yaml_path}")
    return payload


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
