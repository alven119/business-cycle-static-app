from __future__ import annotations

import json
from pathlib import Path

from business_cycle.backtests.reuse import (
    existing_json_is_valid,
    load_run_metadata,
    required_outputs_exist,
    should_reuse_outputs,
    write_run_metadata,
)


def test_valid_json_can_be_reused(tmp_path: Path) -> None:
    path = tmp_path / "valid.json"
    path.write_text('{"ok": true}', encoding="utf-8")

    assert existing_json_is_valid(path) is True
    assert should_reuse_outputs([path], reuse_existing=True) is True


def test_missing_file_does_not_reuse(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    assert existing_json_is_valid(path) is False
    assert required_outputs_exist([path]) is False
    assert should_reuse_outputs([path], reuse_existing=True) is False


def test_invalid_json_does_not_reuse(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text("{invalid", encoding="utf-8")

    assert existing_json_is_valid(path) is False
    assert should_reuse_outputs([path], reuse_existing=True) is False


def test_force_overrides_reuse(tmp_path: Path) -> None:
    path = tmp_path / "valid.json"
    path.write_text("{}", encoding="utf-8")

    assert should_reuse_outputs([path], reuse_existing=True, force=True) is False


def test_all_required_outputs_must_exist(tmp_path: Path) -> None:
    valid = tmp_path / "valid.json"
    missing = tmp_path / "missing.json"
    valid.write_text("{}", encoding="utf-8")

    assert required_outputs_exist([valid, missing]) is False
    assert should_reuse_outputs([valid, missing], reuse_existing=True) is False


def test_run_metadata_round_trip(tmp_path: Path) -> None:
    path = write_run_metadata(tmp_path / "metadata.json", {"experiment_id": "test"})

    payload = load_run_metadata(path)
    assert payload["experiment_id"] == "test"
    assert "generated_at" in payload
    assert json.loads(path.read_text(encoding="utf-8"))["experiment_id"] == "test"
