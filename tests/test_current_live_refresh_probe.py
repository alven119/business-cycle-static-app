from __future__ import annotations

import json
import os
import subprocess
import sys

from business_cycle.current.current_live_refresh_probe import (
    probe_current_live_refresh_environment,
)


def test_live_refresh_probe_is_secret_safe_without_key(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    output = tmp_path / "probe.json"

    summary = probe_current_live_refresh_environment(output=output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert summary["live_refresh_probe_ready"] is True
    assert summary["fred_api_key_present"] is False
    assert summary["provider_config_ready"] is False
    assert summary["live_fetch_opt_in_required"] is True
    assert summary["cache_dir_ignored"] is True
    assert summary["safe_output_dir_ready"] is True
    assert summary["secret_logged_count"] == 0
    assert "secret-token" not in json.dumps(payload)


def test_probe_script_uses_current_interpreter_and_writes_tmp(tmp_path) -> None:
    output = tmp_path / "phase41_live_probe.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/probe_current_live_refresh_environment.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        env={**os.environ, "FRED_API_KEY": ""},
        text=True,
    )

    assert output.is_file()
    assert "live_refresh_probe_ready=true" in result.stdout
    assert "result=passed" in result.stdout
