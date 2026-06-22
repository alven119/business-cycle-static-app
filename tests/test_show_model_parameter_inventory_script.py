from __future__ import annotations

from scripts.show_model_parameter_inventory import main


def test_show_model_parameter_inventory_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "phase=QA3" in out
    assert "parameter_inventory_ready=true" in out
    assert "unclassified_parameter_count=0" in out
