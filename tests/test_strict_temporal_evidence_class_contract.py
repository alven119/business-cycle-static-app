from __future__ import annotations

from business_cycle.audits.temporal_evidence_class import (
    strict_ready_evidence_classes,
    summarize_temporal_evidence_contract,
)


def test_strict_temporal_evidence_class_contract_blocks_proxy_and_initial_release() -> None:
    summary = summarize_temporal_evidence_contract()

    assert summary["temporal_evidence_class_count"] == 7
    assert summary["exact_vintage_interval_strict"] is True
    assert summary["official_release_archive_strict"] is True
    assert summary["official_observational_archive_strict"] is True
    assert summary["initial_release_misclassified_as_vintage_count"] == 0
    assert summary["proxy_misclassified_as_strict_count"] == 0
    assert summary["current_history_plus_lag_misclassified_as_strict_count"] == 0
    assert summary["strict_series_without_source_provenance_count"] == 0
    assert "release_lag_revised_proxy" not in strict_ready_evidence_classes()
