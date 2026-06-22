from __future__ import annotations

from pathlib import Path

from business_cycle.audits.production_hardcoding import (
    scan_production_hardcoding,
    summarize_production_hardcoding,
)


def test_production_hardcoding_audit_default_scope_is_clean() -> None:
    summary = summarize_production_hardcoding()

    assert summary["production_hard_coded_scenario_id_count"] == 0
    assert summary["production_hard_coded_date_count"] == 0
    assert summary["production_scenario_name_branch_count"] == 0
    assert summary["production_event_specific_override_count"] == 0
    assert summary["unreviewed_hard_coding_count"] == 0


def test_production_scenario_hardcoding_is_detected(tmp_path: Path) -> None:
    source = tmp_path / "resolver.py"
    source.write_text(
        'if scenario_id == "covid_recession":\n    current_phase = "recession"\n',
        encoding="utf-8",
    )

    findings = scan_production_hardcoding([source])

    assert any(finding.finding_type == "scenario_id" for finding in findings)
    assert any(finding.finding_type == "scenario_branch" for finding in findings)
