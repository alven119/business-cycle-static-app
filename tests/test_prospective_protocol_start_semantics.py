from __future__ import annotations

from business_cycle.audits.prospective_protocol_start_semantics import (
    summarize_protocol_start_semantics,
)


def test_protocol_registered_but_not_started() -> None:
    summary = summarize_protocol_start_semantics()

    assert summary["protocol_registered"] is True
    assert summary["registry_armed"] is True
    assert summary["protocol_started"] is False
    assert summary["first_record_written"] is False
    assert summary["real_record_count"] == 0
    assert summary["prospective_result_inspected"] is False
    assert summary["holdout_registered"] is False
