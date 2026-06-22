from __future__ import annotations

from scripts.show_qa3_calibration_integrity_closure import main


def test_show_qa3_calibration_integrity_closure_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "phase=QA3" in out
    assert "result=passed" in out
    assert "qa3_closure_status=closed_precalibration_governance_ready" in out
