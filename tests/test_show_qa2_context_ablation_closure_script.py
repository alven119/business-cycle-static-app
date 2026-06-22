from __future__ import annotations

from scripts.show_qa2_context_ablation_closure import main


def test_show_qa2_context_ablation_closure_script(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "phase=QA2" in out
    assert "data_only_path_structurally_validated=true" in out
    assert "qa2_closure_status=closed_context_dependency_measured" in out
    assert "recommended_next_phase=QA3" in out
