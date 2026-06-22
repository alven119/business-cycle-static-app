from __future__ import annotations

from business_cycle.audits.shadow_runtime_end_to_end import (
    validate_shadow_runtime_end_to_end_fixtures,
)


def test_shadow_runtime_end_to_end_tmp_fixtures_pass() -> None:
    summary = validate_shadow_runtime_end_to_end_fixtures()

    assert summary["end_to_end_tmp_fixtures_ready"] is True
    assert summary["end_to_end_fixture_pass_count"] == summary["end_to_end_fixture_count"]
    assert summary["duplicate_record_written_count"] == 0
    assert summary["invalid_fixture_accepted_count"] == 0
    assert summary["correction_chain_fixture_count"] == 1
