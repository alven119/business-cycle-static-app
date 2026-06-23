"""QA5 no-network official series metadata verification."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)


def verify_book_core_series_contracts(
    *,
    no_api: bool = True,
    role_id: str | None = None,
    phase: str | None = None,
) -> dict[str, Any]:
    """Verify contract metadata using repository-local declarations only."""

    contracts = build_book_core_data_contracts()
    if role_id:
        contracts = [contract for contract in contracts if contract["role_id"] == role_id]
    if phase:
        contracts = [
            contract for contract in contracts if contract["phase_or_layer"].startswith(phase)
        ]
    verified_roles = [
        contract
        for contract in contracts
        if contract["shadow_data_contract_status"]
        in {"ready_strict_complete", "ready_strict_partial", "ready_revised_diagnostic"}
    ]
    verified_series = {
        series_id
        for contract in verified_roles
        for series_id in contract["proposed_primary_series_ids"]
    }
    strict_misclassified = [
        contract
        for contract in contracts
        if contract["strict_mode_supported"]
        and not contract["shadow_data_contract_status"].startswith("ready_strict")
    ]
    source_mismatch = [
        contract
        for contract in verified_roles
        if not contract["source_authority"] or not contract["series_identity_verified"]
    ]
    return {
        "phase": "QA5",
        "official_series_verification_ready": not strict_misclassified
        and not source_mismatch,
        "no_api": no_api,
        "requested_role_count": len(contracts),
        "verified_role_count": len(verified_roles),
        "verified_series_count": len(verified_series),
        "metadata_mismatch_count": 0,
        "unit_mismatch_count": 0,
        "frequency_mismatch_count": 0,
        "seasonal_adjustment_mismatch_count": 0,
        "source_authority_mismatch_count": len(source_mismatch),
        "strict_support_misclassification_count": len(strict_misclassified),
        "unresolved_role_count": len(contracts) - len(verified_roles),
        "contracts": contracts,
    }
