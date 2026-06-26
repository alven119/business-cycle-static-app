from __future__ import annotations

from business_cycle.current.current_data_refresh_contract import (
    summarize_current_data_refresh_contract,
)


def test_current_data_refresh_contract_gates() -> None:
    summary = summarize_current_data_refresh_contract()

    assert summary["current_data_refresh_contract_ready"] is True
    assert summary["ci_requires_network"] is False
    assert summary["ci_requires_fred_key"] is False
    assert summary["live_fetch_allowed_only_when_key_present"] is True
    assert summary["raw_data_commit_forbidden"] is True
    assert summary["secret_redaction_required"] is True
    assert summary["revised_data_labeled_as_revised"] is True
    assert summary["point_in_time_not_claimed_for_latest_revised"] is True
