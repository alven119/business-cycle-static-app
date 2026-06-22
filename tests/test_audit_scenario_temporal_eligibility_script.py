from __future__ import annotations

from scripts.audit_scenario_temporal_eligibility import main


def test_audit_scenario_temporal_eligibility_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "phase=QA1F" in out
    assert "scenario_id=dotcom_bubble" in out
    assert "scenario_with_silent_horizon_reduction_count=0" in out
