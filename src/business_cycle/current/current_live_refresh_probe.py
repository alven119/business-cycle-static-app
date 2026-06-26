"""Phase 41 live current refresh environment probe."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
from typing import Any

from business_cycle.current.current_data_refresh import (
    DEFAULT_SERIES_REGISTRY_PATH,
    IGNORED_CACHE_ROOT,
    KEY_ENV_NAME,
    _load_series_rows,
)


TMP_ROOT = Path("/tmp")


def probe_current_live_refresh_environment(
    *,
    output: str | Path | None = None,
    cache_dir: str | Path = IGNORED_CACHE_ROOT,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
) -> dict[str, Any]:
    cache_path = Path(cache_dir)
    output_path = Path(output) if output is not None else TMP_ROOT / "phase41_live_probe.json"
    key_present = bool(os.getenv(KEY_ENV_NAME))
    cache_ignored = _path_is_ignored(cache_path)
    safe_output = _is_under_tmp(output_path)
    rows = _load_series_rows(registry_path)
    fetchable_rows = [
        row
        for row in rows
        if row.get("source") == "FRED/ALFRED"
        and row.get("current_refresh_fetch_enabled", True) is not False
        and row.get("point_in_time_eligible") is True
        and row.get("release_lag_rule") not in {None, "", "unsupported"}
    ]
    provider_config_ready = key_present and cache_ignored and safe_output
    summary = {
        "phase": "41",
        "live_refresh_probe_ready": True,
        "live_refresh_environment_ready": provider_config_ready,
        "fred_api_key_present": key_present,
        "provider_config_ready": provider_config_ready,
        "live_fetch_opt_in_required": True,
        "cache_dir": str(cache_path),
        "cache_dir_ignored": cache_ignored,
        "cache_dir_must_be_ignored": True,
        "safe_output_dir_ready": safe_output,
        "required_series_count": len(rows),
        "fetchable_provider_series_count": len(fetchable_rows),
        "unsupported_missing_provider_count": len(rows) - len(fetchable_rows),
        "secret_logged_count": 0,
        "raw_data_committed_count": _tracked_raw_cache_count(cache_path),
        "raw_data_commit_forbidden": True,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    if output is not None:
        write_current_live_refresh_probe(summary, output=output_path)
    return summary


def write_current_live_refresh_probe(
    summary: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = Path(output)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase 41 live refresh probe output must be under /tmp")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {"output": str(output_path), "probe_artifact_count": 1}


def _is_under_tmp(path: Path) -> bool:
    resolved = path.resolve()
    tmp = TMP_ROOT.resolve()
    return resolved == tmp or tmp in resolved.parents


def _path_is_ignored(path: Path) -> bool:
    completed = subprocess.run(
        ["git", "check-ignore", "-q", str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return True
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        return False
    text = gitignore.read_text(encoding="utf-8")
    return "data/raw/" in text and str(path).startswith("data/raw/")


def _tracked_raw_cache_count(path: Path) -> int:
    completed = subprocess.run(
        ["git", "ls-files", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return len([line for line in completed.stdout.splitlines() if line.strip()])
