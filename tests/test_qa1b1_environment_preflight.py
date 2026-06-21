from __future__ import annotations

from pathlib import Path

import scripts.update_point_in_time_data as updater


def test_env_file_entry_present_reports_boolean_without_value(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    key_name = "FRED_" + "API_KEY"
    env_path.write_text(f"{key_name}=very-secret-value\n", encoding="utf-8")

    assert updater._env_file_entry_present(env_path) is True


def test_env_file_entry_missing_is_false(tmp_path: Path) -> None:
    assert updater._env_file_entry_present(tmp_path / ".env") is False
