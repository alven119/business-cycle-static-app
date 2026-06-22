from __future__ import annotations

from pathlib import Path

import yaml


def test_manual_start_runbook_has_required_controls() -> None:
    spec = yaml.safe_load(
        Path("specs/audits/prospective_manual_start_runbook.yaml").read_text(
            encoding="utf-8"
        )
    )["prospective_manual_start_runbook"]
    doc = Path("docs/audits/prospective_manual_start_runbook.md").read_text(
        encoding="utf-8"
    )

    assert spec["explicit_user_command_required"] is True
    assert spec["delete_or_overwrite_records_allowed"] is False
    assert spec["append_when_period_incomplete_allowed"] is False
    assert spec["preview_as_registry_allowed"] is False
    assert spec["candidate_monitoring_start_allowed"] is False
    assert "Verify freeze lineage" in doc
    assert "Do not use preview files as registry records" in doc

