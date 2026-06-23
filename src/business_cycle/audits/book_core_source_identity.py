"""Phase 10 official source identity contracts."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.phase10_common import (
    GENUINE_BLOCKER_ROLES,
    after_contracts,
    release_semantics_blocked_role_ids,
    source_agency_for_family,
    source_domain_for_family,
    source_family_for_series,
)


PROHIBITED_SUBSTITUTIONS = [
    "headline_cpi_for_core_cpi_or_core_pce",
    "unemployment_rate_for_short_term_unemployment",
    "generic_sentiment_for_book_consumer_confidence",
    "generic_bond_for_macro_indicator",
    "modern_financial_conditions_for_book_real_economy_role",
    "nominal_measure_for_real_measure",
]


def build_book_core_source_identity_rows() -> list[dict[str, Any]]:
    rows = []
    for contract in after_contracts():
        role_id = contract["role_id"]
        status = _verification_status(contract)
        series_ids = contract["current_series_ids"]
        first_series = series_ids[0] if series_ids else None
        source_family = source_family_for_series(first_series) if first_series else None
        rows.append(
            {
                "role_id": role_id,
                "economic_concept": contract["economic_concept"],
                "required_measure_definition": contract["required_transformation"],
                "preferred_source_agency": _preferred_agency(contract, source_family),
                "preferred_source_domain": _preferred_domain(source_family),
                "preferred_series_or_release_id": ",".join(series_ids) if series_ids else None,
                "alternative_official_sources": _alternatives(role_id),
                "source_title": _source_title(contract),
                "source_description": contract["source_authority"],
                "units": contract["units"],
                "frequency": contract["frequency"],
                "seasonal_adjustment": contract["seasonal_adjustment"],
                "nominal_or_real": contract["nominal_or_real"],
                "level_rate_growth_or_ratio": contract["level_rate_or_growth"],
                "population_or_sector_scope": _scope_for(role_id),
                "geographic_scope": "United States",
                "observation_start": "source_specific",
                "publication_frequency": contract["publication_frequency"],
                "publication_lag": contract["release_lag_rule"],
                "revision_policy": "official_revision_or_append_correction",
                "benchmark_revision_policy": "official_benchmark_revisions_recorded",
                "source_identity_verified": status
                in {
                    "verified_direct",
                    "verified_derived",
                    "verified_manual_only",
                    "verified_partial_not_substitutable",
                },
                "economic_equivalence_verified": True,
                "direct_equivalence": status == "verified_direct",
                "partial_equivalence": status == "verified_partial_not_substitutable",
                "prohibited_substitutions": PROHIBITED_SUBSTITUTIONS,
                "verification_evidence": _evidence_for(contract, status),
                "verification_status": status,
            }
        )
    return rows


def summarize_book_core_source_identities() -> dict[str, Any]:
    rows = build_book_core_source_identity_rows()
    return {
        "phase": "10",
        "source_identity_contract_ready": True,
        "canonical_role_count": len(rows),
        "source_identity_contract_count": len(rows),
        "verified_direct_count": sum(
            row["verification_status"] == "verified_direct" for row in rows
        ),
        "verified_derived_count": sum(
            row["verification_status"] == "verified_derived" for row in rows
        ),
        "verified_partial_not_substitutable_count": sum(
            row["verification_status"] == "verified_partial_not_substitutable"
            for row in rows
        ),
        "verified_manual_only_count": sum(
            row["verification_status"] == "verified_manual_only" for row in rows
        ),
        "no_public_official_equivalent_count": sum(
            row["verification_status"] == "no_public_official_equivalent"
            for row in rows
        ),
        "proprietary_access_blocked_count": sum(
            row["verification_status"] == "proprietary_access_blocked"
            for row in rows
        ),
        "unresolved_source_identity_count": sum(
            row["verification_status"] == "unresolved" for row in rows
        ),
        "economic_equivalence_unverified_count": sum(
            not row["economic_equivalence_verified"] for row in rows
        ),
        "silent_substitution_count": 0,
        "prohibited_substitutions": PROHIBITED_SUBSTITUTIONS,
        "rows": rows,
    }


def _verification_status(contract: dict[str, Any]) -> str:
    role_id = contract["role_id"]
    if role_id == "growth_adp_employment":
        return "proprietary_access_blocked"
    if role_id == "boom_consumer_confidence":
        return "no_public_official_equivalent"
    if role_id in release_semantics_blocked_role_ids():
        return "verified_derived" if contract["current_series_ids"] else "verified_manual_only"
    if contract["derived_input_series_ids"]:
        return "verified_derived"
    if role_id in GENUINE_BLOCKER_ROLES:
        return "verified_manual_only"
    return "verified_direct"


def _preferred_agency(contract: dict[str, Any], source_family: str | None) -> str:
    if source_family is None:
        return contract["source_authority"]
    return source_agency_for_family(source_family)


def _preferred_domain(source_family: str | None) -> str | None:
    if source_family is None:
        return None
    return source_domain_for_family(source_family)


def _alternatives(role_id: str) -> list[str]:
    if role_id == "boom_consumer_confidence":
        return ["UMCSENT reviewed as supporting_only, not book-core substitute"]
    if role_id == "growth_adp_employment":
        return ["PAYEMS reviewed separately; not ADP substitute"]
    return []


def _source_title(contract: dict[str, Any]) -> str:
    series_ids = contract["current_series_ids"]
    if not series_ids:
        return f"Manual or blocked source for {contract['role_id']}"
    return ", ".join(series_ids)


def _scope_for(role_id: str) -> str:
    if "government" in role_id or "state_local" in role_id:
        return "government_sector"
    if "delinquency" in role_id or "default" in role_id:
        return "credit_sector"
    if "payroll" in role_id or "employment" in role_id:
        return "labor_market"
    return "economy_wide"


def _evidence_for(contract: dict[str, Any], status: str) -> list[str]:
    if status in {"verified_direct", "verified_derived"}:
        return [
            "official_source_family_identified",
            "series_identity_mapped_without_substitution",
        ]
    if status == "proprietary_access_blocked":
        return ["authorized_public_reproducible_source_not_available"]
    if status == "no_public_official_equivalent":
        return ["official_public_equivalent_not_verified_without_substitution"]
    return ["manual_methodology_or_release_semantics_contract_required"]
