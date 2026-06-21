from __future__ import annotations

from business_cycle.audits.audit_implementation_integrity import (
    summarize_audit_implementation_integrity,
)


def test_audit_implementation_integrity_reports_no_hardcoded_summary_values() -> None:
    summary = summarize_audit_implementation_integrity()

    assert summary["hard_coded_summary_value_count"] == 0
    assert summary["inventory_drift_detection_ready"] is True
    assert summary["traceability_drift_detection_ready"] is True
    assert summary["series_drift_detection_ready"] is True
    assert summary["provenance_drift_detection_ready"] is True
