from __future__ import annotations

from scripts.run_data_only_shadow_evaluation import main


def test_run_data_only_shadow_evaluation_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "data_only_shadow_evaluation_ready=true" in out
    assert "parameter_selection_from_shadow_result_count=0" in out
    assert "performance_metric_computed_count=0" in out
