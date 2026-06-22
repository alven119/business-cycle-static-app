"""QA8 book-explicit evaluator and forward protocol closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_explicit_evaluator_eligibility import (
    summarize_book_explicit_evaluator_eligibility,
)
from business_cycle.audits.book_explicit_evaluator_leakage import (
    summarize_book_explicit_evaluator_leakage,
)
from business_cycle.audits.contextual_numeric_generalization import (
    summarize_contextual_numeric_generalization,
)
from business_cycle.audits.evidence_evaluability import (
    summarize_evidence_evaluability_status_contract,
    summarize_shadow_role_readiness_recalculation,
)
from business_cycle.audits.prospective_shadow_protocol import (
    summarize_prospective_shadow_candidate_protocol,
)
from business_cycle.audits.shadow_evaluator_freeze import (
    summarize_shadow_evaluator_freeze,
)
from business_cycle.audits.shadow_evaluator_production_isolation import (
    summarize_shadow_evaluator_production_isolation,
)
from business_cycle.audits.shadow_evidence_diagnostics import (
    summarize_required_shadow_evidence_diagnostics,
)
from business_cycle.shadow_model.evaluator_primitives import (
    summarize_evaluator_primitive_guards,
)
from business_cycle.shadow_model.evidence_evaluators import (
    summarize_book_explicit_evaluators,
    validate_evidence_evaluator_metamorphic_fixtures,
)
from business_cycle.shadow_model.prospective_gate import (
    summarize_prospective_gate_fixtures,
)


DEFAULT_QA8_CLOSURE_PATH = Path(
    "specs/audits/qa8_book_explicit_evaluator_closure.yaml"
)


def summarize_qa8_book_explicit_evaluator_closure(
    path: str | Path = DEFAULT_QA8_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA8 hard gates."""

    expected = _load_expected(path)
    blocker = summarize_evidence_evaluability_status_contract()
    eligibility = summarize_book_explicit_evaluator_eligibility()
    contextual = summarize_contextual_numeric_generalization()
    primitives = summarize_evaluator_primitive_guards()
    evaluators = summarize_book_explicit_evaluators()
    metamorphic = validate_evidence_evaluator_metamorphic_fixtures()
    readiness = summarize_shadow_role_readiness_recalculation()
    diagnostics = summarize_required_shadow_evidence_diagnostics()
    protocol = summarize_prospective_shadow_candidate_protocol()
    gate = summarize_prospective_gate_fixtures()
    freeze = summarize_shadow_evaluator_freeze()
    leakage = summarize_book_explicit_evaluator_leakage()
    isolation = summarize_shadow_evaluator_production_isolation()
    retrospective_ready = all(
        row["retrospective_candidate_selection_enabled"] is False
        and row["candidate_phase_emitted"] is False
        and row["known_label_used"] is False
        and row["performance_metric_computed"] is False
        and row["context_prior_used"] is False
        and row["strict_fallback_count"] == 0
        for row in diagnostics.values()
    )
    retrospective_candidate_phase_count = sum(
        row["candidate_phase_emitted"] for row in diagnostics.values()
    )
    summary = {
        "phase": "QA8",
        "blocker_accounting_reconciled": blocker[
            "blocker_accounting_reconciled"
        ],
        "explicit_rule_eligibility_ready": eligibility[
            "explicit_rule_eligibility_ready"
        ],
        "contextual_numeric_guard_ready": contextual[
            "contextual_numeric_guard_ready"
        ],
        "evaluator_primitive_library_ready": primitives[
            "evaluator_primitive_library_ready"
        ],
        "book_explicit_evaluators_implemented": evaluators[
            "book_explicit_evaluators_implemented"
        ],
        "evaluator_metamorphic_coverage_ready": metamorphic[
            "evaluator_metamorphic_coverage_ready"
        ],
        "role_readiness_recalculated": readiness["role_readiness_recalculated"],
        "retrospective_evidence_diagnostics_ready": retrospective_ready,
        "prospective_protocol_registered": protocol[
            "prospective_protocol_registered"
        ],
        "prospective_clock_gate_ready": gate["prospective_clock_gate_ready"],
        "evaluator_freeze_ready": freeze["evaluator_freeze_ready"],
        "evaluator_leakage_guard_ready": leakage[
            "evaluator_leakage_guard_ready"
        ],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "role_count": blocker["role_count"],
        "operationally_complete_explicit_rule_count": eligibility[
            "operationally_complete_explicit_rule_count"
        ],
        "implemented_explicit_evaluator_count": evaluators[
            "implemented_explicit_evaluator_count"
        ],
        "operationally_incomplete_explicit_rule_count": eligibility[
            "operationally_incomplete_explicit_rule_count"
        ],
        "evidence_evaluable_role_count": readiness[
            "evidence_evaluable_role_count"
        ],
        "candidate_selection_eligible_role_count": readiness[
            "candidate_selection_eligible_role_count"
        ],
        "unresolved_rule_count": eligibility["rules"]
        and sum(row["rule_source"] == "unresolved" for row in eligibility["rules"]),
        "contextual_numeric_generalization_count": contextual[
            "contextual_numeric_generalization_count"
        ],
        "non_book_threshold_added_count": freeze[
            "non_book_threshold_added_count"
        ],
        "copied_historical_threshold_count": leakage[
            "copied_historical_threshold_count"
        ],
        "retrospective_candidate_selection_enabled": False,
        "retrospective_candidate_phase_emitted_count": retrospective_candidate_phase_count,
        "prospective_protocol_started": protocol["prospective_protocol_started"],
        "prospective_result_inspected": protocol["prospective_result_inspected"],
        "holdout_registered": freeze["holdout_registered"],
        "formal_candidate_phase_computed_on_historical_data": False,
        "formal_current_phase_decision_enabled": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa9_allowed": True,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa8_closure_status": expected["qa8_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "blocker": blocker,
        "eligibility": eligibility,
        "contextual": contextual,
        "primitives": primitives,
        "evaluators": evaluators,
        "metamorphic": metamorphic,
        "readiness": readiness,
        "diagnostics": diagnostics,
        "protocol": protocol,
        "gate": gate,
        "freeze": freeze,
        "leakage": leakage,
        "isolation": isolation,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != value:
            return False
    return (
        summary["role_count"] == 40
        and summary["implemented_explicit_evaluator_count"]
        == summary["operationally_complete_explicit_rule_count"]
        and summary["blocker"]["primary_status_count_sum"] == 40
        and summary["eligibility"]["explicit_rule_silently_skipped_count"] == 0
        and summary["eligibility"]["ineligible_rule_implemented_count"] == 0
        and summary["primitives"]["future_data_used_count"] == 0
        and summary["metamorphic"]["metamorphic_fixture_pass_count"]
        == summary["metamorphic"]["metamorphic_fixture_count"]
        and summary["readiness"]["fully_gated_role_still_not_evaluable_count"] == 0
        and summary["readiness"]["incompletely_gated_role_marked_evaluable_count"] == 0
        and summary["freeze"]["freeze_hash_valid"] is True
        and summary["leakage"]["scenario_id_reference_count"] == 0
        and summary["isolation"]["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa8_book_explicit_evaluator_closure"
    ]["expected_status"]
