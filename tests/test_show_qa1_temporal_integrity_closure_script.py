from __future__ import annotations

from scripts.show_qa1_temporal_integrity_closure import main


def test_show_qa1_temporal_integrity_closure_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "qa1_closure_status=closed_with_explicit_historical_gaps" in out
    assert "qa2_allowed=true" in out
    assert "real_backtest_progression_allowed=false" in out
