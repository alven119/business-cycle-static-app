from __future__ import annotations

from business_cycle.audits.book_core_series_verification import (
    verify_book_core_series_contracts,
)


def test_series_verification_no_api_has_no_silent_mismatch() -> None:
    summary = verify_book_core_series_contracts(no_api=True)

    assert summary["official_series_verification_ready"] is True
    assert summary["requested_role_count"] == 40
    assert summary["verified_role_count"] == 24
    assert summary["metadata_mismatch_count"] == 0
    assert summary["source_authority_mismatch_count"] == 0
    assert summary["strict_support_misclassification_count"] == 0

