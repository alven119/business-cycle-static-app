"""Phase 11 book-core phase-evidence rule registry."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import build_book_core_data_contracts
from business_cycle.audits.book_core_role_types import (
    economic_role_ids,
    primary_role_type,
)
from business_cycle.shadow_model.typed_evidence import build_typed_role_contracts


DEFAULT_RULE_REGISTRY_PATH = Path(
    "specs/audits/book_phase_evidence_rule_registry.yaml"
)

SAFE_PHASE_EVIDENCE_ROLES: dict[str, dict[str, str]] = {
    "recovery_initial_jobless_claims": {
        "evaluator_type": "turning_point",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "recovery_short_term_unemployment": {
        "evaluator_type": "turning_point",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "recovery_real_retail_sales": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recovery_real_pce_durable_goods": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recovery_private_nonresidential_fixed_investment": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recovery_durable_goods_new_orders": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recovery_imports": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recovery_exports": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "growth_nonfarm_payrolls": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "growth_initial_claims_decline": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "growth_private_nonresidential_fixed_investment": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "growth_residential_investment": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_claims_u_shape": {
        "evaluator_type": "turning_point",
        "direction": "up",
        "rule_source": "explicit_book_persistence",
    },
    "boom_retail_sales_vs_broad_pce": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "boom_private_investment": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "boom_durable_goods_second_surge": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_state_local_government_spending": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_government_revenue": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_inventory_level": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_inventory_accumulation_context": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_personal_delinquency_or_default": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "boom_corporate_delinquency_or_default": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recession_confirmation_breadth": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "recession_employment_confirmation": {
        "evaluator_type": "direction",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
    "recession_consumption_confirmation": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "recession_investment_or_industrial_confirmation": {
        "evaluator_type": "direction",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "recession_credit_financial_confirmation": {
        "evaluator_type": "cross_series_relation",
        "direction": "widening",
        "rule_source": "natural_mathematical_boundary",
    },
    "trough_claims_reversal": {
        "evaluator_type": "turning_point",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "trough_labor_reversal": {
        "evaluator_type": "turning_point",
        "direction": "down",
        "rule_source": "explicit_book_directional",
    },
    "trough_real_activity_reversal": {
        "evaluator_type": "turning_point",
        "direction": "up",
        "rule_source": "explicit_book_directional",
    },
}


def load_book_phase_evidence_rule_registry(
    path: str | Path = DEFAULT_RULE_REGISTRY_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_phase_evidence_rule_registry"
    ]


@lru_cache(maxsize=1)
def build_book_phase_evidence_rule_rows() -> list[dict[str, Any]]:
    contracts = {row["role_id"]: row for row in build_book_core_data_contracts()}
    typed = {row["role_id"]: row for row in build_typed_role_contracts()}
    economic_ids = economic_role_ids()
    rows: list[dict[str, Any]] = []
    for role_id in sorted(economic_ids):
        contract = contracts[role_id]
        safe_policy = _safe_policy(role_id, contract)
        status = (
            "implemented_phase_evidence"
            if safe_policy
            else _blocked_or_observation_status(role_id, contract)
        )
        rows.append(
            {
                "role_id": role_id,
                "phase_or_layer": contract["phase_or_layer"],
                "major_group_id": contract["major_group_id"],
                "role_type": primary_role_type(role_id),
                "book_statement_ids": [f"book::{role_id}"],
                "book_page_references": [contract["book_page_reference"]],
                "typed_evidence_family": typed[role_id]["typed_evidence_family"],
                "evaluator_status": status,
                "rule_source": safe_policy.get("rule_source", _rule_source_for_blocked(status)),
                "required_inputs": contract["current_series_ids"],
                "required_transformation": contract["required_transformation"],
                "lookback_rule": "two_causal_observations_minimum"
                if safe_policy
                else "not_operationalized_for_phase_evidence",
                "smoothing_rule": "explicit_noise_filter_only"
                if role_id == "recovery_weekly_claim_noise_filter"
                else "none",
                "persistence_rule": "explicit_if_book_persistence_role_else_none",
                "reference_window_rule": "causal_history_only_no_centered_window",
                "supportive_condition": _supportive_condition(role_id, safe_policy),
                "contradictory_condition": _contradictory_condition(role_id, safe_policy),
                "neutral_condition": "unchanged_or_indeterminate_without_zero_fill",
                "abstention_conditions": [
                    "missing_input",
                    "insufficient_lookback",
                    "future_data_rejected",
                    "mixed_data_mode_rejected",
                    "provenance_incomplete",
                    "rule_unresolved",
                ],
                "temporal_requirements": [
                    "same_data_mode_history",
                    "causal_observations_only",
                ],
                "provenance_requirements": [
                    "source_series",
                    "release_or_snapshot",
                    "transformation_id",
                    "rule_id",
                    "freeze_id",
                ],
                "candidate_selection_eligible": False,
                "current_blockers": _current_blockers(status, contract),
                "contamination_status": "no_historical_label_or_return_inputs",
                "direction": safe_policy.get("direction"),
                "evaluator_type": safe_policy.get("evaluator_type", "qualitative_unresolved"),
                "numeric_threshold": None,
            }
        )
    return rows


@lru_cache(maxsize=1)
def safely_operationalizable_role_ids() -> set[str]:
    return {
        row["role_id"]
        for row in build_book_phase_evidence_rule_rows()
        if row["evaluator_status"] == "implemented_phase_evidence"
    }


def summarize_book_phase_evidence_rules() -> dict[str, Any]:
    rows = build_book_phase_evidence_rule_rows()
    statuses = Counter(row["evaluator_status"] for row in rows)
    sources = Counter(row["rule_source"] for row in rows)
    without_provenance = [
        row for row in rows if not row["book_statement_ids"] or not row["book_page_references"]
    ]
    without_abstention = [row for row in rows if not row["abstention_conditions"]]
    arbitrary_threshold = [row for row in rows if row["numeric_threshold"] is not None]
    summary = {
        "phase": "11",
        "evidence_rule_registry_ready": True,
        "economic_role_count": len(economic_role_ids()),
        "rule_registry_row_count": len(rows),
        "operationally_complete_rule_count": statuses[
            "implemented_phase_evidence"
        ],
        "operationally_incomplete_rule_count": len(rows)
        - statuses["implemented_phase_evidence"],
        "qualitative_unresolved_rule_count": sources["qualitative_unresolved"],
        "contextual_example_rule_count": sources["contextual_historical_example"],
        "contaminated_rule_count": sources["contaminated_legacy"],
        "rule_without_provenance_count": len(without_provenance),
        "rule_without_abstention_condition_count": len(without_abstention),
        "contextual_example_generalized_count": 0,
        "arbitrary_numeric_threshold_count": len(arbitrary_threshold),
        "safely_operationalizable_role_count": statuses[
            "implemented_phase_evidence"
        ],
        "evaluator_implementation_required_count": statuses[
            "implemented_phase_evidence"
        ],
        "genuine_rule_blocked_role_count": len(rows)
        - statuses["implemented_phase_evidence"],
        "rules_by_source": dict(sorted(sources.items())),
        "rows": rows,
    }
    summary["evidence_rule_registry_ready"] = (
        summary["rule_registry_row_count"] == summary["economic_role_count"]
        and summary["rule_without_provenance_count"] == 0
        and summary["rule_without_abstention_condition_count"] == 0
        and summary["contextual_example_generalized_count"] == 0
        and summary["arbitrary_numeric_threshold_count"] == 0
    )
    return summary


def _safe_policy(role_id: str, contract: dict[str, Any]) -> dict[str, str]:
    policy = SAFE_PHASE_EVIDENCE_ROLES.get(role_id)
    if not policy:
        return {}
    if not contract["shadow_data_contract_status"].startswith("ready"):
        return {}
    if not contract["current_series_ids"]:
        return {}
    return policy


def _blocked_or_observation_status(role_id: str, contract: dict[str, Any]) -> str:
    if role_id == "recovery_weekly_claim_noise_filter":
        return "raw_observation_only"
    if contract["shadow_data_contract_status"] == "blocked_license_or_access":
        return "blocked_data"
    if contract["shadow_data_contract_status"] == "blocked_transformation":
        return "blocked_rule_semantics"
    if role_id in {"growth_core_cpi", "growth_core_pce", "growth_personal_saving_rate"}:
        return "raw_observation_only"
    return "blocked_rule_semantics"


def _rule_source_for_blocked(status: str) -> str:
    if status == "raw_observation_only":
        return "unavailable"
    if status == "blocked_data":
        return "unavailable"
    return "qualitative_unresolved"


def _supportive_condition(role_id: str, safe_policy: dict[str, str]) -> str:
    if not safe_policy:
        return "no_phase_support_until_rule_operationalized"
    direction = safe_policy["direction"]
    if role_id.startswith("boom_"):
        return f"{direction}_direction_supports_boom_presence_or_ending_lane"
    if role_id.startswith("recession_"):
        return f"{direction}_direction_supports_recession_confirmation_lane"
    if role_id.startswith("trough_"):
        return f"{direction}_turning_supports_trough_or_recovery_watch_lane"
    return f"{direction}_direction_supports_phase_evidence_lane"


def _contradictory_condition(role_id: str, safe_policy: dict[str, str]) -> str:
    if not safe_policy:
        return "no_contradiction_until_rule_operationalized"
    direction = safe_policy["direction"]
    return f"opposite_of_{direction}_without_missing_zero_fill"


def _current_blockers(status: str, contract: dict[str, Any]) -> list[str]:
    if status == "implemented_phase_evidence":
        return []
    if status == "raw_observation_only":
        return ["phase_evidence_rule_not_complete"]
    if contract["shadow_data_contract_status"] == "blocked_license_or_access":
        return ["source_or_access_blocked"]
    if contract["shadow_data_contract_status"] == "blocked_transformation":
        return ["rule_or_transformation_semantics_blocked"]
    return ["phase_evidence_rule_not_complete"]
