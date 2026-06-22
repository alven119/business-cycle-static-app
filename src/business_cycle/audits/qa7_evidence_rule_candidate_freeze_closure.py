"""QA7 evidence-rule and candidate-selection freeze closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_statement_operationalization import (
    summarize_book_statement_operationalization_registry,
)
from business_cycle.audits.evidence_evaluability import summarize_evidence_evaluability
from business_cycle.audits.evidence_rule_leakage import summarize_evidence_rule_leakage
from business_cycle.audits.evidence_rule_provenance import (
    summarize_evidence_rule_provenance_contract,
)
from business_cycle.audits.shadow_candidate_diagnostics import (
    summarize_required_shadow_candidate_diagnostics,
)
from business_cycle.audits.shadow_candidate_production_isolation import (
    summarize_shadow_candidate_production_isolation,
)
from business_cycle.audits.shadow_candidate_selection_fixtures import (
    validate_shadow_candidate_selection_fixtures,
)
from business_cycle.audits.shadow_candidate_selection_freeze import (
    summarize_shadow_candidate_selection_freeze,
)
from business_cycle.shadow_model.candidate_selection import (
    summarize_shadow_candidate_selection_contract,
)
from business_cycle.shadow_model.evidence_evaluators import (
    summarize_book_core_role_evaluation_rules,
    validate_evidence_evaluator_metamorphic_fixtures,
)


DEFAULT_QA7_CLOSURE_PATH = Path(
    "specs/audits/qa7_evidence_rule_candidate_freeze_closure.yaml"
)


def summarize_qa7_evidence_rule_candidate_freeze_closure(
    path: str | Path = DEFAULT_QA7_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA7 hard gates."""

    expected = _load_expected(path)
    evaluability = summarize_evidence_evaluability()
    statements = summarize_book_statement_operationalization_registry()
    provenance = summarize_evidence_rule_provenance_contract()
    evaluation = summarize_book_core_role_evaluation_rules()
    metamorphic = validate_evidence_evaluator_metamorphic_fixtures()
    selection = summarize_shadow_candidate_selection_contract()
    fixtures = validate_shadow_candidate_selection_fixtures()
    diagnostics = summarize_required_shadow_candidate_diagnostics()
    leakage = summarize_evidence_rule_leakage()
    freeze = summarize_shadow_candidate_selection_freeze()
    isolation = summarize_shadow_candidate_production_isolation()
    real_phase_count = sum(
        item["candidate_phase"] is not None for item in diagnostics.values()
    )
    real_ready = all(
        item["real_data_candidate_selection_enabled"] is False
        and item["candidate_phase"] is None
        and item["context_prior_used"] is False
        and item["known_label_used"] is False
        and item["performance_metric_computed"] is False
        and item["public_output_written"] is False
        and item["strict_fallback_count"] == 0
        for item in diagnostics.values()
    )
    summary = {
        "phase": "QA7",
        "evaluability_root_cause_audit_ready": evaluability[
            "evaluability_root_cause_audit_ready"
        ],
        "book_statement_operationalization_ready": statements[
            "book_statement_operationalization_ready"
        ],
        "evidence_rule_provenance_ready": provenance[
            "evidence_rule_provenance_ready"
        ],
        "role_evaluation_contract_registry_ready": evaluation[
            "role_evaluation_contract_registry_ready"
        ],
        "evaluator_metamorphic_tests_ready": metamorphic[
            "evaluator_metamorphic_tests_ready"
        ],
        "candidate_selection_contract_ready": selection[
            "candidate_selection_contract_ready"
        ],
        "synthetic_candidate_selection_validated": fixtures[
            "synthetic_candidate_selection_validated"
        ],
        "real_data_candidate_diagnostics_ready": real_ready,
        "evidence_rule_leakage_guard_ready": leakage[
            "evidence_rule_leakage_guard_ready"
        ],
        "candidate_selection_freeze_ready": freeze[
            "candidate_selection_freeze_ready"
        ],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "canonical_role_count": evaluation["canonical_role_count"],
        "evaluation_contract_count": evaluation["evaluation_contract_count"],
        "preregistered_evaluable_role_count": evaluation[
            "preregistered_evaluable_role_count"
        ],
        "raw_transform_only_role_count": evaluation["raw_transform_only_role_count"],
        "blocked_rule_count": evaluation["blocked_rule_count"],
        "blocked_threshold_count": evaluation["blocked_threshold_count"],
        "blocked_data_count": evaluation["blocked_data_count"],
        "blocked_equivalence_count": evaluation["blocked_equivalence_count"],
        "explicit_book_rule_count": provenance["explicit_book_rule_count"],
        "contextual_example_count": statements["contextual_example_count"],
        "contextual_example_generalized_count": provenance[
            "contextual_example_generalized_count"
        ],
        "qualitative_statement_given_arbitrary_threshold_count": statements[
            "qualitative_statement_given_arbitrary_threshold_count"
        ],
        "contaminated_rule_allowed_for_independent_validation_count": provenance[
            "contaminated_rule_allowed_for_independent_validation_count"
        ],
        "synthetic_candidate_selection_enabled": selection[
            "synthetic_candidate_selection_enabled"
        ],
        "synthetic_candidate_fixture_count": fixtures["fixture_count"],
        "synthetic_candidate_fixture_pass_count": fixtures["fixture_pass_count"],
        "real_data_candidate_selection_enabled": False,
        "real_data_candidate_phase_emitted_count": real_phase_count,
        "formal_candidate_phase_computed_on_real_data": False,
        "formal_current_phase_decision_enabled": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "holdout_registered": freeze["holdout_registered"],
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa8_allowed": True,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa7_closure_status": expected["qa7_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "evaluability": evaluability,
        "statements": statements,
        "provenance": provenance,
        "evaluation": evaluation,
        "metamorphic": metamorphic,
        "selection": selection,
        "fixtures": fixtures,
        "diagnostics": diagnostics,
        "leakage": leakage,
        "freeze": freeze,
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
    checks = (
        summary["evaluability"]["role_count"] == 40
        and summary["evaluability"]["reason_classified_role_count"] == 40
        and summary["evaluability"]["unclassified_non_evaluable_reason_count"] == 0
        and summary["statements"]["contextual_example_used_as_universal_rule_count"] == 0
        and summary["provenance"]["rule_without_provenance_count"] == 0
        and summary["evaluation"]["evaluation_contract_count"]
        == summary["evaluation"]["canonical_role_count"]
        and summary["metamorphic"]["evaluator_fixture_pass_count"]
        == summary["metamorphic"]["evaluator_fixture_count"]
        and summary["fixtures"]["fixture_pass_count"] == summary["fixtures"]["fixture_count"]
        and summary["leakage"]["scenario_id_reference_count"] == 0
        and summary["freeze"]["freeze_hash_valid"] is True
        and summary["isolation"]["production_behavior_change_count"] == 0
    )
    return checks


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa7_evidence_rule_candidate_freeze_closure"
    ]["expected_status"]
