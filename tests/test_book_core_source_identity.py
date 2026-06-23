from __future__ import annotations

from business_cycle.audits.book_core_source_identity import (
    PROHIBITED_SUBSTITUTIONS,
    build_book_core_source_identity_rows,
    summarize_book_core_source_identities,
)


def test_book_core_source_identity_covers_all_roles_without_substitution() -> None:
    summary = summarize_book_core_source_identities()
    rows = build_book_core_source_identity_rows()
    by_role = {row["role_id"]: row for row in rows}

    assert summary["source_identity_contract_ready"] is True
    assert summary["canonical_role_count"] == 40
    assert summary["source_identity_contract_count"] == 40
    assert summary["unresolved_source_identity_count"] == 0
    assert summary["economic_equivalence_unverified_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert by_role["growth_adp_employment"]["verification_status"] == (
        "proprietary_access_blocked"
    )
    assert by_role["boom_consumer_confidence"]["verification_status"] == (
        "no_public_official_equivalent"
    )
    assert "headline_cpi_for_core_cpi_or_core_pce" in PROHIBITED_SUBSTITUTIONS
    assert "nominal_measure_for_real_measure" in PROHIBITED_SUBSTITUTIONS
