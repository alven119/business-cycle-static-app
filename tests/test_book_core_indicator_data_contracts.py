from __future__ import annotations

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
    summarize_book_core_indicator_data_contracts,
)


def test_each_canonical_role_has_one_data_contract() -> None:
    summary = summarize_book_core_indicator_data_contracts()

    assert summary["book_core_data_contract_registry_ready"] is True
    assert summary["canonical_indicator_role_count"] == 40
    assert summary["data_contract_row_count"] == 40
    assert summary["role_without_data_contract_count"] == 0
    assert summary["data_contract_without_role_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["unverified_series_identity_count"] == 0


def test_blocked_roles_are_explicit_not_silent_substitutions() -> None:
    contracts = build_book_core_data_contracts()
    adp = next(contract for contract in contracts if contract["role_id"] == "growth_adp_employment")
    core_cpi = next(contract for contract in contracts if contract["role_id"] == "growth_core_cpi")

    assert adp["shadow_data_contract_status"] == "blocked_license_or_access"
    assert adp["current_indicator_ids"] == []
    assert core_cpi["substitution_status"] == "no_substitution"
    assert core_cpi["strict_mode_supported"] is False


def test_derived_dependencies_are_complete() -> None:
    credit = next(
        contract
        for contract in build_book_core_data_contracts()
        if contract["role_id"] == "recession_credit_financial_confirmation"
    )

    assert credit["derived_input_series_ids"] == ["BAA", "AAA"]

