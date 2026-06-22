"""QA5 canonical book-core indicator data contracts."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_major_groups import (
    build_book_phase_subroles,
    major_group_for_role,
)


DEFAULT_DATA_CONTRACT_PATH = Path("specs/audits/book_core_indicator_data_contracts.yaml")
COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")
MANIFEST_PATH = Path("specs/audits/canonical_book_requirement_manifest.yaml")

ROLE_SERIES_METADATA = {
    "initial_jobless_claims": ("weekly", "persons", "seasonally_adjusted"),
    "short_term_unemployment": (
        "monthly",
        "thousands_of_persons",
        "seasonally_adjusted",
    ),
    "real_retail_sales": (
        "monthly",
        "millions_of_1982_84_cpi_adjusted_dollars",
        "seasonally_adjusted",
    ),
    "real_pce_durable_goods": (
        "monthly",
        "billions_of_chained_2017_dollars",
        "seasonally_adjusted_annual_rate",
    ),
    "real_private_fixed_investment": (
        "quarterly",
        "billions_of_chained_2017_dollars",
        "seasonally_adjusted_annual_rate",
    ),
    "durable_goods_orders": ("monthly", "millions_of_dollars", "seasonally_adjusted"),
    "imports_goods_services": (
        "quarterly",
        "billions_of_chained_2017_dollars",
        "seasonally_adjusted_annual_rate",
    ),
    "exports_goods_services": (
        "quarterly",
        "billions_of_chained_2017_dollars",
        "seasonally_adjusted_annual_rate",
    ),
    "industrial_production": ("monthly", "index", "seasonally_adjusted"),
    "continuing_jobless_claims": ("weekly", "persons", "seasonally_adjusted"),
    "real_personal_consumption_expenditures": (
        "monthly",
        "billions_of_chained_2017_dollars",
        "seasonally_adjusted_annual_rate",
    ),
    "credit_spread_baa_aaa": ("monthly", "percentage_points", "not_seasonally_adjusted"),
    "initial_jobless_claims_peak_reversal": (
        "weekly",
        "persons",
        "seasonally_adjusted",
    ),
    "short_term_unemployment_peak_reversal": (
        "monthly",
        "thousands_of_persons",
        "seasonally_adjusted",
    ),
    "industrial_production_bottoming": ("monthly", "index", "seasonally_adjusted"),
}


def build_book_core_data_contracts(
    path: str | Path = DEFAULT_DATA_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Build one data contract per canonical indicator role."""

    spec = _load_spec(path)
    manifest = {row["requirement_id"]: row for row in _manifest_rows()}
    subroles = {row["role_id"]: row for row in build_book_phase_subroles()}
    contracts = []
    for coverage in _coverage_rows():
        role_id = coverage["coverage_requirement_id"]
        requirement = manifest[role_id]
        status = _contract_status(coverage, role_id, spec)
        frequency, units, seasonal = ROLE_SERIES_METADATA.get(
            coverage["indicator_id"], ("not_verified", "not_verified", "not_verified")
        )
        contracts.append(
            {
                "role_id": role_id,
                "requirement_id": role_id,
                "phase_or_layer": coverage["phase"],
                "major_group_id": major_group_for_role(role_id),
                "book_section": requirement["book_section"],
                "book_page_reference": requirement["book_page_reference"],
                "economic_concept": coverage["book_role"],
                "book_fidelity_class": coverage["provenance_class"],
                "role_type": subroles[role_id]["role_type"],
                "current_indicator_ids": _current_indicator_ids(coverage),
                "current_series_ids": _current_series_ids(coverage),
                "proposed_primary_series_ids": _proposed_series_ids(coverage),
                "proposed_alternative_series_ids": [],
                "source_authority": _source_authority(coverage, role_id),
                "official_source_required": True,
                "frequency": frequency,
                "units": units,
                "nominal_or_real": _nominal_or_real(role_id),
                "level_rate_or_growth": _level_rate_or_growth(role_id),
                "seasonal_adjustment": seasonal,
                "required_transformation": _required_transformation(role_id),
                "transformation_status": _transformation_status(status),
                "expected_direction_by_phase": _direction_for(role_id),
                "minimum_history_requirement": "full_cycle_history_required",
                "release_lag_rule": "registry_required",
                "publication_frequency": frequency,
                "temporal_evidence_class": _temporal_class(status),
                "revised_mode_supported": status
                in {
                    "ready_strict_complete",
                    "ready_strict_partial",
                    "ready_revised_diagnostic",
                },
                "strict_mode_supported": status
                in {"ready_strict_complete", "ready_strict_partial"},
                "strict_history_status": _strict_history_status(status),
                "license_or_access_status": _license_status(status),
                "economic_equivalence_status": _equivalence_status(status),
                "substitution_status": "no_substitution",
                "current_implementation_status": coverage["formal_or_experimental"],
                "shadow_data_contract_status": status,
                "production_promotion_status": "not_promoted",
                "unresolved_reason": _unresolved_reason(coverage, status),
                "blocker_class": _blocker_class(status),
                "derived_input_series_ids": _derived_inputs(coverage["indicator_id"]),
                "series_identity_verified": status
                in {
                    "ready_strict_complete",
                    "ready_strict_partial",
                    "ready_revised_diagnostic",
                },
            }
        )
    return contracts


def summarize_book_core_indicator_data_contracts() -> dict[str, Any]:
    """Return data contract hard-gate counts."""

    contracts = build_book_core_data_contracts()
    role_ids = _canonical_role_ids()
    contract_ids = {contract["role_id"] for contract in contracts}
    statuses = Counter(contract["shadow_data_contract_status"] for contract in contracts)
    blocker_counts = Counter(
        contract["blocker_class"]
        for contract in contracts
        if contract["blocker_class"] != "none"
    )
    role_without_contract = sorted(role_ids - contract_ids)
    contract_without_role = sorted(contract_ids - role_ids)
    silent_substitution = [
        contract
        for contract in contracts
        if contract["substitution_status"] != "no_substitution"
    ]
    unverified_series_identity = [
        contract
        for contract in contracts
        if not contract["series_identity_verified"]
        and contract["shadow_data_contract_status"].startswith("ready")
    ]
    return {
        "phase": "QA5",
        "book_core_data_contract_registry_ready": len(contracts) == len(role_ids)
        and not role_without_contract
        and not contract_without_role
        and not silent_substitution
        and not unverified_series_identity,
        "canonical_indicator_role_count": len(role_ids),
        "data_contract_row_count": len(contracts),
        "ready_strict_complete_count": statuses["ready_strict_complete"],
        "ready_strict_partial_count": statuses["ready_strict_partial"],
        "ready_revised_diagnostic_count": statuses["ready_revised_diagnostic"],
        "blocked_temporal_count": statuses["blocked_temporal_history"],
        "blocked_source_identity_count": statuses["blocked_source_identity"],
        "blocked_access_count": statuses["blocked_license_or_access"],
        "blocked_equivalence_count": statuses["blocked_economic_equivalence"],
        "blocked_transformation_count": statuses["blocked_transformation"],
        "spec_only_count": statuses["spec_only"],
        "unsupported_count": statuses["unsupported"],
        "blocked_role_count": sum(
            count
            for status, count in statuses.items()
            if status.startswith("blocked") or status in {"spec_only", "unsupported"}
        ),
        "role_without_data_contract_count": len(role_without_contract),
        "data_contract_without_role_count": len(contract_without_role),
        "silent_substitution_count": len(silent_substitution),
        "unverified_series_identity_count": len(unverified_series_identity),
        "blocked_roles_by_blocker_class": dict(blocker_counts),
        "contracts": contracts,
    }


def _contract_status(
    coverage: dict[str, Any],
    role_id: str,
    spec: dict[str, Any],
) -> str:
    if role_id == "growth_adp_employment":
        return "blocked_license_or_access"
    if role_id in {
        "growth_sustainable_inflation_interpretation",
        "recovery_publication_lag_awareness",
    }:
        return "blocked_transformation"
    if coverage["formal_or_experimental"] == "formal":
        return spec["status_policy"]["formal_current_book_core"]
    if coverage["formal_or_experimental"] == "experimental":
        return spec["status_policy"]["experimental_current_book_core"]
    if coverage["formal_or_experimental"] == "missing":
        return spec["status_policy"]["missing_role_default"]
    return "unsupported"


def _current_indicator_ids(coverage: dict[str, Any]) -> list[str]:
    return [] if coverage["formal_or_experimental"] == "missing" else [coverage["indicator_id"]]


def _current_series_ids(coverage: dict[str, Any]) -> list[str]:
    return [] if coverage["formal_or_experimental"] == "missing" else [coverage["series_id"]]


def _proposed_series_ids(coverage: dict[str, Any]) -> list[str]:
    return _derived_inputs(coverage["indicator_id"]) or [coverage["series_id"]]


def _derived_inputs(indicator_id: str) -> list[str]:
    if indicator_id == "credit_spread_baa_aaa":
        return ["BAA", "AAA"]
    return []


def _source_authority(coverage: dict[str, Any], role_id: str) -> str:
    if role_id == "growth_adp_employment":
        return "blocked_non_repository_official_or_licensed_source_required"
    if coverage["formal_or_experimental"] == "missing":
        return "official_source_required_not_yet_bound"
    return "repository_existing_official_series_mapping"


def _nominal_or_real(role_id: str) -> str:
    if "real" in role_id or "inflation" in role_id:
        return "real_or_inflation_adjusted"
    if "rate" in role_id or "claims" in role_id or "unemployment" in role_id:
        return "rate_or_count"
    return "concept_specific"


def _level_rate_or_growth(role_id: str) -> str:
    if "rate" in role_id or "claims" in role_id:
        return "level_and_trend"
    return "growth_or_momentum"


def _required_transformation(role_id: str) -> str:
    if "noise_filter" in role_id:
        return "moving_average_persistence"
    if "reversal" in role_id or "trough" in role_id:
        return "peak_trough_reversal"
    if "inflation" in role_id:
        return "core_inflation_sustainable_interpretation"
    return "trend_momentum_or_breadth"


def _transformation_status(status: str) -> str:
    if status in {"ready_strict_complete", "ready_strict_partial", "ready_revised_diagnostic"}:
        return "defined_for_shadow"
    if status == "blocked_transformation":
        return "blocked"
    return "spec_only"


def _direction_for(role_id: str) -> str:
    if "recession" in role_id and "trough" not in role_id:
        return "deterioration_supports_recession"
    if "boom" in role_id:
        return "late_cycle_pressure_or_slowdown_supports_boom_ending_evidence"
    return "improvement_supports_phase_or_reversal_evidence"


def _temporal_class(status: str) -> str:
    if status == "ready_strict_complete":
        return "strict_complete"
    if status == "ready_strict_partial":
        return "strict_partial"
    if status == "ready_revised_diagnostic":
        return "revised_diagnostic_only"
    return "unavailable_or_spec_only"


def _strict_history_status(status: str) -> str:
    if status == "ready_strict_complete":
        return "full_strict_ready"
    if status == "ready_strict_partial":
        return "partial_strict_ready"
    if status == "ready_revised_diagnostic":
        return "not_strict_revised_diagnostic"
    return "blocked"


def _license_status(status: str) -> str:
    return "blocked" if status == "blocked_license_or_access" else "repository_allowed"


def _equivalence_status(status: str) -> str:
    if status == "blocked_economic_equivalence":
        return "blocked"
    if status.startswith("ready"):
        return "verified_for_shadow_role"
    return "not_yet_verified"


def _unresolved_reason(coverage: dict[str, Any], status: str) -> str:
    if status.startswith("ready"):
        return "none"
    if status == "blocked_license_or_access":
        return "legal reproducible ADP source not available in repository"
    if coverage.get("missing_reason"):
        return str(coverage["missing_reason"])
    return "book-core role lacks complete data contract"


def _blocker_class(status: str) -> str:
    return {
        "ready_strict_complete": "none",
        "ready_strict_partial": "none",
        "ready_revised_diagnostic": "none",
        "blocked_temporal_history": "temporal_history",
        "blocked_source_identity": "source_identity",
        "blocked_license_or_access": "license_or_access",
        "blocked_economic_equivalence": "economic_equivalence",
        "blocked_transformation": "transformation",
        "spec_only": "spec_only",
        "unsupported": "unsupported",
    }[status]


def _canonical_role_ids() -> set[str]:
    return {
        row["requirement_id"]
        for row in _manifest_rows()
        if row.get("requires_indicator_coverage") is True
    }


def _coverage_rows() -> list[dict[str, Any]]:
    rows = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]["indicators"]
    return [row for row in rows if row.get("coverage_requirement_id")]


def _manifest_rows() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))[
        "canonical_book_requirement_manifest"
    ]["requirements"]


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_indicator_data_contracts"
    ]

