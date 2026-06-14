"""Display label helpers for localized dashboard rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_display_labels(path: str | Path) -> dict[str, dict[str, str]]:
    """Load display labels from YAML."""

    label_path = Path(path)
    if not label_path.exists():
        raise FileNotFoundError(f"Display labels YAML does not exist: {label_path}")

    payload = yaml.safe_load(label_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Display labels YAML must be a mapping")

    labels: dict[str, dict[str, str]] = {}
    for category, values in payload.items():
        if not isinstance(values, dict):
            raise ValueError(f"Display label category must be a mapping: {category}")
        labels[str(category)] = {str(key): str(value) for key, value in values.items()}
    return labels


def label_for(
    mapping: dict[str, dict[str, str]],
    category: str,
    key: str | None,
    fallback: str | None = None,
) -> str:
    """Return a localized label, falling back to the original key."""

    if key is None:
        return "" if fallback is None else fallback
    category_labels: Any = mapping.get(category, {})
    if not isinstance(category_labels, dict):
        return fallback if fallback is not None else key
    return str(category_labels.get(key, fallback if fallback is not None else key))
