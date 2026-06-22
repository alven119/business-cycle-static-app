from __future__ import annotations

from scripts.run_context_ablation_audit import main


def test_run_context_ablation_audit_script_reports_qa2_gates(capsys) -> None:
    assert main() == 0
    out = capsys.readouterr().out
    assert "data_only_context_mutation_change_count=0" in out
    assert "display_hint_decision_change_count=0" in out
    assert "production_context_dependency_measured=true" in out
