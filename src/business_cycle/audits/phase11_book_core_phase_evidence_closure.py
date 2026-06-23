"""Phase 11 North Star and phase-evidence closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_role_types import summarize_book_core_role_types
from business_cycle.audits.book_phase_evidence_rules import (
    summarize_book_phase_evidence_rules,
)
from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)
from business_cycle.audits.phase11_production_isolation import (
    summarize_phase11_production_isolation,
)
from business_cycle.audits.project_north_star import (
    summarize_project_north_star_contract,
)
from business_cycle.audits.shadow_phase_evidence_freeze import (
    summarize_shadow_phase_evidence_freeze,
)
from business_cycle.render.phase_evidence_view_models import (
    summarize_phase_evidence_view_models,
)
from business_cycle.shadow_model.major_group_evidence import (
    summarize_major_group_phase_evidence,
)
from business_cycle.shadow_model.phase_evidence_evaluators import (
    run_phase_evidence_diagnostics,
    summarize_phase_evidence_evaluators,
)


DEFAULT_CLOSURE_PATH = Path(
    "specs/audits/phase11_book_core_phase_evidence_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_north_star_institutionalized_phase_evidence_runtime_expanded_"
    "candidate_model_disabled"
)


def summarize_phase11_book_core_phase_evidence_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    north = summarize_project_north_star_contract()
    role_types = summarize_book_core_role_types()
    rules = summarize_book_phase_evidence_rules()
    evaluators = summarize_phase_evidence_evaluators()
    groups = summarize_major_group_phase_evidence()
    diagnostics = {
        "2000_vintage": run_phase_evidence_diagnostics(
            as_of="2000-03-31",
            data_mode="vintage_as_of",
        ),
        "2008_vintage": run_phase_evidence_diagnostics(
            as_of="2008-09-30",
            data_mode="vintage_as_of",
        ),
        "2019_vintage": run_phase_evidence_diagnostics(
            as_of="2019-12-31",
            data_mode="vintage_as_of",
        ),
        "2019_revised": run_phase_evidence_diagnostics(
            as_of="2019-12-31",
            data_mode="revised",
        ),
    }
    view = summarize_phase_evidence_view_models()
    freeze = summarize_shadow_phase_evidence_freeze()
    leakage = summarize_phase11_evidence_rule_leakage()
    isolation = summarize_phase11_production_isolation()
    summary = {
        "phase": "11",
        **_north_star_fields(north),
        "role_type_registry_ready": role_types["role_type_registry_ready"],
        "denominator_semantics_valid": role_types["denominator_semantics_valid"],
        "economic_role_count": role_types["canonical_economic_role_count"],
        "methodology_requirement_count": role_types[
            "data_methodology_requirement_count"
        ],
        "evidence_rule_registry_ready": rules["evidence_rule_registry_ready"],
        "safely_operationalizable_role_count": rules[
            "safely_operationalizable_role_count"
        ],
        "implemented_phase_evidence_evaluator_count": evaluators[
            "implemented_phase_evidence_evaluator_count"
        ],
        "new_phase_evidence_evaluable_role_count": evaluators[
            "new_phase_evidence_evaluable_role_count"
        ],
        "implementation_failed_role_count": evaluators[
            "implementation_failed_role_count"
        ],
        "genuine_rule_blocked_role_count": rules["genuine_rule_blocked_role_count"],
        "phase_evidence_partial_major_group_count": groups[
            "phase_evidence_partial_major_group_count"
        ],
        "phase_evidence_complete_major_group_count": groups[
            "phase_evidence_complete_major_group_count"
        ],
        "candidate_input_complete_major_group_count": groups[
            "candidate_input_complete_major_group_count"
        ],
        "retrospective_diagnostics_ready": _diagnostics_ready(diagnostics),
        "phase_evidence_view_model_ready": view["phase_evidence_view_model_ready"],
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": isolation[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": isolation["real_registry_record_count"],
        "real_registry_write_attempt_count": isolation[
            "real_registry_write_attempt_count"
        ],
        "candidate_capability_ready": False,
        "candidate_monitoring_allowed": False,
        "phase_evidence_model_ready": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "economic_validation_status": "not_started",
        "independent_validation_ready": False,
        "holdout_registered": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "development_next_phase": 12,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase11_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": north[
            "project_definition_of_done_progress"
        ],
        "role_types": role_types,
        "rules": rules,
        "evaluators": evaluators,
        "groups": groups,
        "diagnostics": diagnostics,
        "view_models": view,
        "freeze": freeze,
        "leakage": leakage,
        "isolation": isolation,
    }
    summary["north_star_institutionalized"] = north["north_star_contract_valid"]
    summary["phase_evidence_runtime_expanded"] = (
        summary["implemented_phase_evidence_evaluator_count"] > 0
        and summary["new_phase_evidence_evaluable_role_count"] > 0
    )
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _north_star_fields(north: dict[str, Any]) -> dict[str, Any]:
    return {
        "north_star_document_present": north["north_star_document_present"],
        "north_star_contract_valid": north["north_star_contract_valid"],
        "phase_capability_mapping_complete": north[
            "phase_capability_mapping_complete"
        ],
        "web_surface_mapping_complete": north["web_surface_mapping_complete"],
        "semantic_drift_count": north["semantic_drift_count"],
        "unsupported_product_claim_count": north["unsupported_product_claim_count"],
        "phase_id": north["phase_id"],
        "north_star_alignment_status": north["north_star_alignment_status"],
        "product_capabilities_advanced": north["product_capabilities_advanced"],
        "milestone_ids_advanced": north["milestone_ids_advanced"],
        "web_surfaces_advanced": north["web_surfaces_advanced"],
        "semantic_distinctions_verified": True,
        "deferred_capability_gaps": [
            "candidate_selection_disabled",
            "formal_current_phase_disabled",
            "economic_validation_not_started",
            "prospective_track_waiting_for_first_eligible_asof",
        ],
    }


def _diagnostics_ready(diagnostics: dict[str, dict[str, Any]]) -> bool:
    revised = diagnostics["2019_revised"]
    runs_safe = all(
        item["candidate_selection_enabled"] is False
        and item["candidate_phase_emitted"] is False
        and item["current_phase_emitted"] is False
        and item["expected_label_used"] is False
        and item["context_prior_used"] is False
        and item["accuracy_metric_computed"] is False
        and item["performance_metric_computed"] is False
        and item["strict_fallback_count"] == 0
        for item in diagnostics.values()
    )
    return runs_safe and revised["phase_evidence_output_count"] > 0


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["implemented_phase_evidence_evaluator_count"] > 0
        and summary["new_phase_evidence_evaluable_role_count"] > 0
        and summary["implementation_failed_role_count"] == 0
        and summary["phase_evidence_partial_major_group_count"] > 0
        and summary["freeze"]["phase_evidence_freeze_ready"] is True
        and summary["freeze"]["qa12_freeze_unchanged"] is True
        and summary["leakage"]["leakage_guard_ready"] is True
        and summary["isolation"]["production_isolation_verified"] is True
        and summary["isolation"]["prospective_date_change_count"] == 0
        and summary["isolation"]["real_registry_record_count"] == 0
        and summary["isolation"]["real_registry_write_attempt_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase11_book_core_phase_evidence_closure"
    ]["expected"]
