"""Research-only alternative source inventory for missing macro evidence roles."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ALTERNATIVE_SPEC_PATH = (
    ROOT / "specs/common/macro_indicator_gap_alternative_sources.yaml"
)

PHASES = ("recovery", "growth", "boom", "recession")
PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_score",
    "phase_rank",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
}

SERIES_ALTERNATIVES: dict[str, list[dict[str, Any]]] = {
    "initial_jobless_claims": [
        {
            "candidate_id": "dol_weekly_initial_claims_release",
            "source_family": "DOL",
            "source_title": "Weekly unemployment insurance initial claims release",
            "source_credibility_tier": "official_public_release",
            "substitution_degree": "direct_official",
            "automation_feasibility": "new_adapter_needed",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
        {
            "candidate_id": "fred_icsa",
            "source_family": "FRED",
            "source_title": "ICSA initial claims series",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_redistribution",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "initial_jobless_claims_peak_reversal": [
        {
            "candidate_id": "derived_from_initial_claims",
            "source_family": "DOL/FRED",
            "source_title": "Initial claims peak-reversal derived from official claims",
            "source_credibility_tier": "official_derived",
            "substitution_degree": "derived_from_direct_official",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
    "continuing_jobless_claims": [
        {
            "candidate_id": "fred_ccsa",
            "source_family": "FRED/DOL",
            "source_title": "Continued claims insured unemployment",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "near_direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "short_term_unemployment": [
        {
            "candidate_id": "bls_unemployed_less_than_5_weeks",
            "source_family": "BLS/FRED",
            "source_title": "Unemployed less than 5 weeks",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "short_term_unemployment_peak_reversal": [
        {
            "candidate_id": "derived_from_short_term_unemployment",
            "source_family": "BLS/FRED",
            "source_title": "Short-term unemployment peak-reversal transform",
            "source_credibility_tier": "official_derived",
            "substitution_degree": "derived_from_direct_official",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
    "durable_goods_orders": [
        {
            "candidate_id": "census_durable_goods_orders_release",
            "source_family": "Census",
            "source_title": "Manufacturers' shipments, inventories, and orders",
            "source_credibility_tier": "official_public_release",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "exports_goods_services": [
        {
            "candidate_id": "bea_exports_goods_services",
            "source_family": "BEA/FRED",
            "source_title": "Exports of goods and services",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "imports_goods_services": [
        {
            "candidate_id": "bea_imports_goods_services",
            "source_family": "BEA/FRED",
            "source_title": "Imports of goods and services",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "real_private_fixed_investment": [
        {
            "candidate_id": "bea_real_private_fixed_investment",
            "source_family": "BEA/FRED",
            "source_title": "Real private fixed investment",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_low_frequency",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "real_pce_durable_goods": [
        {
            "candidate_id": "bea_real_pce_durable_goods",
            "source_family": "BEA/FRED",
            "source_title": "Real personal consumption expenditures: durable goods",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "real_retail_sales": [
        {
            "candidate_id": "fred_rrsfs",
            "source_family": "FRED/Census",
            "source_title": "Real retail and food services sales",
            "source_credibility_tier": "official_derived_redistribution",
            "substitution_degree": "near_direct_official_derived",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
        {
            "candidate_id": "census_retail_sales_plus_deflator",
            "source_family": "Census/BEA",
            "source_title": "Retail sales release deflated with official price index",
            "source_credibility_tier": "official_composite",
            "substitution_degree": "official_composite",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
    "PAYEMS": [
        {
            "candidate_id": "fred_payems",
            "source_family": "BLS/FRED",
            "source_title": "All employees, total nonfarm payrolls",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "CPILFESL": [
        {
            "candidate_id": "fred_core_cpi",
            "source_family": "BLS/FRED",
            "source_title": "Core CPI excluding food and energy",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "PCEPILFE": [
        {
            "candidate_id": "fred_core_pce",
            "source_family": "BEA/FRED",
            "source_title": "Core PCE price index",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "PSAVERT": [
        {
            "candidate_id": "fred_personal_saving_rate",
            "source_family": "BEA/FRED",
            "source_title": "Personal saving rate",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "DSPIC96": [
        {
            "candidate_id": "fred_real_disposable_personal_income",
            "source_family": "BEA/FRED",
            "source_title": "Real disposable personal income",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "PCECC96": [
        {
            "candidate_id": "fred_real_pce",
            "source_family": "BEA/FRED",
            "source_title": "Real personal consumption expenditures",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "PRFIC1": [
        {
            "candidate_id": "bea_real_residential_fixed_investment",
            "source_family": "BEA/FRED",
            "source_title": "Real private residential fixed investment",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_low_frequency",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "DRBLACBS": [
        {
            "candidate_id": "fred_business_loan_delinquency",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Delinquency rate on business loans",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "near_direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "DRCLACBS": [
        {
            "candidate_id": "fred_consumer_loan_delinquency",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Delinquency rate on consumer loans",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "near_direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "W006RC1Q027SBEA": [
        {
            "candidate_id": "bea_government_current_receipts",
            "source_family": "BEA/FRED",
            "source_title": "Government current receipts",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_low_frequency",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "CBIC1": [
        {
            "candidate_id": "bea_change_private_inventories",
            "source_family": "BEA/FRED",
            "source_title": "Change in private inventories",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_low_frequency",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "BUSINV": [
        {
            "candidate_id": "census_business_inventories",
            "source_family": "Census/FRED",
            "source_title": "Total business inventories",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "SLCEC1": [
        {
            "candidate_id": "bea_state_local_consumption_expenditures",
            "source_family": "BEA/FRED",
            "source_title": "State and local consumption expenditures and investment",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official_low_frequency",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "industrial_production": [
        {
            "candidate_id": "fred_indpro",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Industrial production index",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "industrial_production_bottoming": [
        {
            "candidate_id": "derived_from_indpro",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Industrial production bottoming transform",
            "source_credibility_tier": "official_derived",
            "substitution_degree": "derived_from_direct_official",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
    "real_personal_consumption_expenditures": [
        {
            "candidate_id": "fred_real_pce",
            "source_family": "BEA/FRED",
            "source_title": "Real personal consumption expenditures",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "direct_official",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "low_medium",
            "planned_resolution_phase": "Phase52",
            "book_core_replacement_allowed": True,
        },
    ],
    "credit_spread_baa_aaa": [
        {
            "candidate_id": "fred_baa_minus_aaa",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Moody's BAA minus AAA corporate yield spread",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "modern_supporting_only",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": False,
        },
    ],
    "fed_policy_easing_signal": [
        {
            "candidate_id": "fred_federal_funds_or_target_range",
            "source_family": "Federal Reserve/FRED",
            "source_title": "Federal funds or target range policy signal",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "supporting_only",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": False,
        },
    ],
}

ROLE_ALTERNATIVE_OVERRIDES: dict[str, list[dict[str, Any]]] = {
    "growth_adp_employment": [
        {
            "candidate_id": "adp_national_employment_report",
            "source_family": "ADP",
            "source_title": "ADP National Employment Report",
            "source_credibility_tier": "licensed_or_authorized_private",
            "substitution_degree": "direct_if_authorized",
            "automation_feasibility": "manual_or_license_required",
            "data_risk_level": "high_until_license_confirmed",
            "planned_resolution_phase": "Phase54",
            "book_core_replacement_allowed": False,
        },
        {
            "candidate_id": "fred_payems_supporting_not_adp",
            "source_family": "BLS/FRED",
            "source_title": "Nonfarm payrolls as supporting employment context",
            "source_credibility_tier": "official_public_redistribution",
            "substitution_degree": "supporting_only_not_adp",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium_high",
            "planned_resolution_phase": "Phase54",
            "book_core_replacement_allowed": False,
        },
    ],
    "growth_real_disposable_income_vs_consumption": [
        {
            "candidate_id": "fred_dspic96_pcecc96_same_as_of_composite",
            "source_family": "BEA/FRED",
            "source_title": "Real disposable income versus real PCE same-as-of relation",
            "source_credibility_tier": "official_composite",
            "substitution_degree": "official_composite",
            "automation_feasibility": "composite_transformation_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
    "growth_sustainable_inflation_interpretation": [
        {
            "candidate_id": "core_cpi_core_pce_sustainability_composite",
            "source_family": "BLS/BEA/FRED",
            "source_title": "Core CPI and core PCE sustainability interpretation",
            "source_credibility_tier": "official_composite",
            "substitution_degree": "rule_semantics_required",
            "automation_feasibility": "rule_preregistration_required",
            "data_risk_level": "medium_high",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": False,
        },
    ],
    "boom_consumer_confidence": [
        {
            "candidate_id": "conference_board_consumer_confidence",
            "source_family": "Conference Board",
            "source_title": "Consumer Confidence Index",
            "source_credibility_tier": "reputable_licensed_source",
            "substitution_degree": "direct_if_licensed",
            "automation_feasibility": "manual_or_license_required",
            "data_risk_level": "high_until_license_confirmed",
            "planned_resolution_phase": "Phase54",
            "book_core_replacement_allowed": False,
        },
        {
            "candidate_id": "fred_umich_sentiment_supporting",
            "source_family": "University of Michigan/FRED",
            "source_title": "Consumer sentiment as supporting confidence proxy",
            "source_credibility_tier": "reputable_public_proxy",
            "substitution_degree": "supporting_proxy_only",
            "automation_feasibility": "adapter_reuse",
            "data_risk_level": "medium_high",
            "planned_resolution_phase": "Phase54",
            "book_core_replacement_allowed": False,
        },
    ],
    "recovery_weekly_claim_noise_filter": [
        {
            "candidate_id": "initial_claims_calendar_noise_filter",
            "source_family": "DOL/FRED",
            "source_title": "Initial claims with preregistered weekly noise filter",
            "source_credibility_tier": "official_derived",
            "substitution_degree": "rule_semantics_required",
            "automation_feasibility": "rule_preregistration_required",
            "data_risk_level": "medium",
            "planned_resolution_phase": "Phase53",
            "book_core_replacement_allowed": True,
        },
    ],
}


def build_macro_indicator_gap_alternative_source_rows(
    *,
    current_evidence: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build one row per current missing or observation-only evidence role."""

    _load_spec()
    current_evidence = current_evidence or build_current_evidence_readiness()
    rows: list[dict[str, Any]] = []
    for role in current_evidence["role_readiness_rows"]:
        if role["phase"] not in PHASES:
            continue
        if not (role["unavailable"] or role["observation_only"]):
            continue
        alternatives = _alternatives_for_role(role)
        preferred = alternatives[0]
        gap_type = _gap_type(role)
        rows.append(
            {
                "role_id": role["role_id"],
                "phase_or_layer": role["phase"],
                "major_group_id": role["major_group_id"],
                "gap_type": gap_type,
                "required_series_ids": role["required_series_ids"],
                "blocker_reason_codes": role["blocker_reason_codes"],
                "observation_only": role["observation_only"],
                "current_evidence_status": role["current_evidence_status"],
                "alternative_source_candidates": alternatives,
                "preferred_candidate_id": preferred["candidate_id"],
                "source_credibility_tier": preferred["source_credibility_tier"],
                "substitution_degree": preferred["substitution_degree"],
                "automation_feasibility": preferred["automation_feasibility"],
                "data_risk_level": preferred["data_risk_level"],
                "planned_resolution_phase": preferred["planned_resolution_phase"],
                "book_core_replacement_allowed": preferred[
                    "book_core_replacement_allowed"
                ],
                "silent_substitution": False,
                "alternative_promoted_to_core": False,
                "display_policy": _display_policy(preferred),
            }
        )
    return rows


def summarize_macro_indicator_gap_alternative_sources() -> dict[str, Any]:
    """Summarize Phase51 macro gap alternatives."""

    rows = build_macro_indicator_gap_alternative_source_rows()
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    planned_counts = Counter(row["planned_resolution_phase"] for row in rows)
    substitution_counts = Counter(row["substitution_degree"] for row in rows)
    automation_counts = Counter(row["automation_feasibility"] for row in rows)
    source_risk_missing = [
        row for row in rows if not row["data_risk_level"]
    ]
    substitution_missing = [
        row for row in rows if not row["substitution_degree"]
    ]
    phase_missing = [
        row for row in rows if not row["planned_resolution_phase"]
    ]
    candidate_missing = [
        row for row in rows if not row["alternative_source_candidates"]
    ]
    summary = {
        "macro_gap_alternative_registry_ready": (
            bool(rows)
            and not source_risk_missing
            and not substitution_missing
            and not phase_missing
            and not candidate_missing
        ),
        "gap_role_count": len(rows),
        "gap_with_alternative_candidate_count": len(rows) - len(candidate_missing),
        "phase_gap_counts": dict(sorted(phase_counts.items())),
        "planned_resolution_phase_counts": dict(sorted(planned_counts.items())),
        "substitution_degree_counts": dict(sorted(substitution_counts.items())),
        "automation_feasibility_counts": dict(sorted(automation_counts.items())),
        "source_risk_label_missing_count": len(source_risk_missing),
        "substitution_degree_missing_count": len(substitution_missing),
        "planned_resolution_phase_missing_count": len(phase_missing),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "alternative_promoted_to_core_count": sum(
            row["alternative_promoted_to_core"] for row in rows
        ),
        "book_core_replacement_allowed_role_count": sum(
            row["book_core_replacement_allowed"] for row in rows
        ),
        "supporting_or_proxy_only_role_count": sum(
            not row["book_core_replacement_allowed"] for row in rows
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prohibited_output_field_count": _contains_prohibited_field(rows),
        "top_rows": rows[:12],
        "rows": rows,
    }
    summary["result"] = "passed" if _passes(summary) else "blocked"
    return summary


def _alternatives_for_role(role: dict[str, Any]) -> list[dict[str, Any]]:
    if role["role_id"] in ROLE_ALTERNATIVE_OVERRIDES:
        return ROLE_ALTERNATIVE_OVERRIDES[role["role_id"]]
    alternatives: list[dict[str, Any]] = []
    for series_id in role["required_series_ids"]:
        alternatives.extend(SERIES_ALTERNATIVES.get(series_id, []))
    if alternatives:
        return alternatives
    return [
        {
            "candidate_id": f"{role['role_id']}_manual_source_review",
            "source_family": "source_review_required",
            "source_title": "Manual source review required",
            "source_credibility_tier": "unverified_until_review",
            "substitution_degree": "unverified",
            "automation_feasibility": "manual_or_license_required",
            "data_risk_level": "high",
            "planned_resolution_phase": "Phase54",
            "book_core_replacement_allowed": False,
        },
    ]


def _gap_type(role: dict[str, Any]) -> str:
    blockers = role["blocker_reason_codes"]
    has_missing = any(item.startswith("missing_data:") for item in blockers)
    has_rule = "phase_evidence_rule_not_operational" in blockers
    if has_missing and has_rule:
        return "missing_input_and_rule_unresolved"
    if has_rule:
        return "rule_unresolved"
    if role["observation_only"]:
        return "observation_only"
    return "missing_input"


def _display_policy(candidate: dict[str, Any]) -> str:
    if candidate["book_core_replacement_allowed"]:
        return "can_be_displayed_as_high_confidence_candidate_until_adapter_wired"
    if "supporting" in candidate["substitution_degree"]:
        return "display_only_as_supporting_proxy_with_visible_risk"
    return "requires_user_or_license_review_before_use"


def _passes(summary: dict[str, Any]) -> bool:
    return (
        summary["macro_gap_alternative_registry_ready"] is True
        and summary["gap_role_count"] > 0
        and summary["gap_with_alternative_candidate_count"] == summary["gap_role_count"]
        and summary["source_risk_label_missing_count"] == 0
        and summary["substitution_degree_missing_count"] == 0
        and summary["planned_resolution_phase_missing_count"] == 0
        and summary["silent_substitution_count"] == 0
        and summary["alternative_promoted_to_core_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["production_behavior_change_count"] == 0
        and summary["prohibited_output_field_count"] == 0
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_spec(path: str | Path = DEFAULT_ALTERNATIVE_SPEC_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "macro_indicator_gap_alternative_sources"
    ]
