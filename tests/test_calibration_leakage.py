from __future__ import annotations

from business_cycle.audits.calibration_leakage import summarize_calibration_leakage


def test_calibration_leakage_is_acknowledged_without_false_claims() -> None:
    summary = summarize_calibration_leakage()

    assert summary["calibration_leakage_audit_ready"] is True
    assert summary["parameter_selected_after_result_observation_count"] > 0
    assert summary["contaminated_parameter_count"] > 0
    assert summary["unacknowledged_contaminated_parameter_count"] == 0
    assert summary["false_out_of_sample_claim_count"] == 0
    assert summary["calibration_leakage_detected"] is True
