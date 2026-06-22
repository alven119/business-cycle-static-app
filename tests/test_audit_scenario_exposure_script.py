from __future__ import annotations

from scripts.audit_scenario_exposure import main


def test_audit_scenario_exposure_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "phase=QA3" in out
    assert "previously_seen_scenario_count=5" in out
    assert "untouched_holdout_scenario_count=0" in out
