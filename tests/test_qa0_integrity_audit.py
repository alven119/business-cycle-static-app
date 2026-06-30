from __future__ import annotations

from pathlib import Path

import yaml

from business_cycle.audits.qa0_integrity_audit import run_qa0_integrity_audit


def test_qa0_integrity_audit_blocks_9b1_and_real_backtest_progression() -> None:
    summary = run_qa0_integrity_audit()

    assert summary["phase"] == "QA0.1"
    assert summary["audit_status"] == "passed"
    assert summary["untriaged_finding_count"] == 0
    assert summary["p0_without_blocking_gate_count"] == 0
    assert summary["unsupported_claim_count"] == 0
    assert summary["phase_9b_synthetic_harness_valid"] is True
    assert summary["phase_9b_economic_validation_claim_allowed"] is False
    assert summary["real_backtest_progression_allowed"] is False
    assert summary["phase_9b1_allowed"] is False
    assert summary["recommended_next_phase"] == "QA1"
    assert summary["result"] == "passed"
    assert summary["canonical_requirement_count"] > 22
    assert summary["traceability_row_count"] == summary["canonical_requirement_count"]
    assert summary["taxonomy_misclassification_count"] == 0
    assert summary["modern_methodology_marked_book_core_count"] == 0
    assert summary["book_core_requirement_count"] < summary["canonical_requirement_count"]
    assert summary["canonical_book_indicator_requirement_count"] == 40
    assert summary["phase_role_indicator_coverage_row_count"] == 63
    assert summary["duplicate_finding_id_count"] == 0
    assert summary["unmapped_indicator_count"] == 0
    assert summary["unaudited_series_count"] == 0
    assert summary["hard_coded_summary_value_count"] == 0
    assert summary["qa0_inventory_complete"] is True


def test_qa0_integrity_audit_reports_open_blocked_methodology_gaps() -> None:
    summary = run_qa0_integrity_audit()
    registry_count = _series_registry_count()

    assert summary["p0_finding_count"] > 0
    assert summary["book_core_missing_count"] > 0
    assert summary["series_missing_availability_metadata_count"] == 0
    assert summary["availability_metadata_complete_count"] == registry_count
    assert summary["book_benchmark_execution_allowed"] is False
    assert summary["point_in_time_backtest_ready"] is False
    assert summary["out_of_sample_claim_allowed"] is False


def _series_registry_count() -> int:
    payload = yaml.safe_load(
        Path("specs/common/series_release_lag_registry.yaml").read_text(
            encoding="utf-8"
        )
    )
    return len(payload["series_release_lag_registry"]["series"])
