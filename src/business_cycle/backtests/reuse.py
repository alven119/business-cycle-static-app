"""Helpers for conservative reuse of generated backtest outputs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def existing_json_is_valid(path: str | Path) -> bool:
    """Return true when path exists and contains parseable JSON."""

    json_path = Path(path)
    if not json_path.exists() or not json_path.is_file():
        return False
    try:
        json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


def required_outputs_exist(paths: list[str | Path]) -> bool:
    """Return true only when every required JSON output exists and parses."""

    return bool(paths) and all(existing_json_is_valid(path) for path in paths)


def should_reuse_outputs(
    paths: list[str | Path],
    *,
    reuse_existing: bool = False,
    force: bool = False,
) -> bool:
    """Decide whether existing generated outputs can be reused."""

    if force:
        return False
    if not reuse_existing:
        return False
    return required_outputs_exist(paths)


def write_run_metadata(path: str | Path, metadata: dict[str, Any]) -> Path:
    """Write run metadata JSON with generated_at when absent."""

    output = Path(path)
    payload = dict(metadata)
    payload.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def load_run_metadata(path: str | Path) -> dict[str, Any]:
    """Load run metadata JSON."""

    metadata_path = Path(path)
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Run metadata must be a mapping: {metadata_path}")
    return payload
