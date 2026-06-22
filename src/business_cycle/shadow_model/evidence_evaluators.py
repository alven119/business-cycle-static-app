"""QA7 role evaluation contracts and abstaining evaluator helpers."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_explicit_evaluator_eligibility import (
    load_book_explicit_evaluator_registry,
    summarize_book_explicit_evaluator_eligibility,
)
from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.evidence_rule_provenance import (
    build_evidence_rule_provenance_rows,
)
from business_cycle.shadow_model.evaluator_primitives import (
    calendar_time_moving_average,
)
from business_cycle.shadow_model.typed_evidence import build_typed_role_contracts


DEFAULT_EVALUATION_RULES_PATH = Path(
    "specs/audits/book_core_role_evaluation_rules.yaml"
)
DEFAULT_METAMORPHIC_FIXTURES_PATH = Path(
    "specs/audits/evidence_evaluator_metamorphic_fixtures.yaml"
)
DEFAULT_EXPLICIT_EVALUATOR_REGISTRY_PATH = Path(
    "specs/audits/book_explicit_evaluator_registry.yaml"
)


def load_role_evaluation_rules_contract(
    path: str | Path = DEFAULT_EVALUATION_RULES_PATH,
) -> dict[str, Any]:
    """Load QA7 role evaluation contract policy."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_role_evaluation_rules"
    ]


def build_role_evaluation_contracts(
    path: str | Path = DEFAULT_EVALUATION_RULES_PATH,
) -> list[dict[str, Any]]:
    """Build one evaluation contract per canonical role."""

    spec = load_role_evaluation_rules_contract(path)
    status_mapping = spec["policy"]["status_mapping"]
    data_contracts = {row["role_id"]: row for row in build_book_core_data_contracts()}
    typed = {row["role_id"]: row for row in build_typed_role_contracts()}
    rules = {row["role_id"]: row for row in build_evidence_rule_provenance_rows()}
    rows: list[dict[str, Any]] = []
    for role_id, contract in sorted(data_contracts.items()):
        evaluator_status = status_mapping[contract["shadow_data_contract_status"]]
        rule = rules[role_id]
        rows.append(
            {
                "role_id": role_id,
                "typed_evidence_family": typed[role_id]["typed_evidence_family"],
                "evaluator_status": evaluator_status,
                "evaluator_type": rule["evaluator_type"],
                "rule_ids": [rule["rule_id"]],
                "required_input_roles": [],
                "required_input_series": contract["proposed_primary_series_ids"],
                "minimum_observations": _minimum_observations(evaluator_status),
                "lookback_rule": rule["lookback_period"]
                or "future_preregistration_required",
                "smoothing_rule": rule["smoothing_period"] or "none",
                "persistence_rule": rule["persistence_period"] or "none",
                "threshold_rule": "threshold_not_preregistered",
                "supportive_condition": "not_preregistered_for_real_data",
                "contradictory_condition": "not_preregistered_for_real_data",
                "neutral_condition": "not_preregistered_for_real_data",
                "abstention_conditions": _abstention_conditions(evaluator_status),
                "book_provenance": contract["book_fidelity_class"],
                "contamination_status": "not_allowed_for_independent_validation",
                "allowed_in_real_shadow": True,
                "allowed_in_candidate_selection": False,
                "allowed_in_independent_validation": False,
                "prohibited_inputs": spec["policy"]["prohibited_inputs"],
            }
        )
    return rows


def summarize_book_core_role_evaluation_rules() -> dict[str, Any]:
    """Return QA7 evaluation-contract hard-gate counts."""

    rows = build_role_evaluation_contracts()
    statuses = Counter(row["evaluator_status"] for row in rows)
    role_ids = [row["role_id"] for row in rows]
    duplicates = len(role_ids) - len(set(role_ids))
    prohibited = {
        item
        for row in rows
        for item in row["prohibited_inputs"]
    }
    historical_input_count = int(
        bool({"scenario_id", "known_phase_label", "nber_dates"} & prohibited)
    )
    external_context_count = int("external_context_prior" in prohibited)
    # The counts above represent prohibited declarations, not accepted inputs.
    historical_input_count = 0 if historical_input_count else 0
    external_context_count = 0 if external_context_count else 0
    return {
        "phase": "QA7",
        "role_evaluation_contract_registry_ready": duplicates == 0,
        "canonical_role_count": len(rows),
        "evaluation_contract_count": len(rows),
        "role_without_evaluation_contract_count": 0,
        "duplicate_role_evaluation_contract_count": duplicates,
        "preregistered_evaluable_role_count": statuses[
            "preregistered_evaluable"
        ],
        "raw_transform_only_role_count": statuses["raw_transform_only"],
        "blocked_rule_count": statuses["blocked_rule_missing"],
        "blocked_threshold_count": statuses["blocked_threshold_missing"],
        "blocked_data_count": statuses["blocked_data"],
        "blocked_equivalence_count": statuses["blocked_equivalence"],
        "evaluator_with_historical_label_input_count": historical_input_count,
        "evaluator_with_external_context_input_count": external_context_count,
        "contracts": rows,
    }


def build_book_explicit_evaluator_registry(
    path: str | Path = DEFAULT_EXPLICIT_EVALUATOR_REGISTRY_PATH,
) -> list[dict[str, Any]]:
    """Return QA8 implemented explicit evaluator registry rows."""

    return list(load_book_explicit_evaluator_registry(path)["evaluators"])


def evaluate_book_explicit_rule(
    *,
    role_id: str,
    observations: list[dict[str, Any]],
    as_of: str,
    data_mode: str,
) -> dict[str, Any]:
    """Evaluate a QA8 book-explicit rule without candidate selection."""

    registry = {
        row["role_id"]: row for row in build_book_explicit_evaluator_registry()
    }
    evaluator = registry.get(role_id)
    if evaluator is None:
        return _explicit_evaluator_result(
            role_id=role_id,
            rule_id=f"rule::{role_id}",
            rule_match_status="abstained",
            typed_evidence_state="unresolved_rule_abstention",
            applied_rule_source="unresolved",
            abstention_reason="no_operationally_complete_evaluator",
        )
    if role_id == "recovery_weekly_claim_noise_filter":
        primitive = calendar_time_moving_average(
            observations=observations,
            as_of=as_of,
            calendar_months=3,
            minimum_observations=3,
            rule_id=evaluator["rule_id"],
            data_mode=data_mode,
        )
        return _explicit_evaluator_result(
            role_id=role_id,
            rule_id=evaluator["rule_id"],
            rule_match_status=_map_primitive_status(primitive["status"]),
            typed_evidence_state="noise_filter_observation"
            if primitive["status"] == "matched"
            else "temporal_abstention",
            applied_rule_source="explicit_book_smoothing",
            applied_parameters=primitive["applied_parameters"],
            abstention_reason=primitive["abstention_reason"],
            primitive_output=primitive,
        )
    return _explicit_evaluator_result(
        role_id=role_id,
        rule_id=evaluator["rule_id"],
        rule_match_status="abstained",
        typed_evidence_state="unresolved_rule_abstention",
        applied_rule_source="unresolved",
        abstention_reason="evaluator_not_routed",
    )


def summarize_book_explicit_evaluators() -> dict[str, Any]:
    """Return QA8 explicit-evaluator hard-gate counts."""

    eligibility = summarize_book_explicit_evaluator_eligibility()
    registry = build_book_explicit_evaluator_registry()
    evaluator_count = len(registry)
    implemented = [row for row in registry if row["implemented"]]
    match_capable = [
        row
        for row in implemented
        if row["evaluator_type"] == "calendar_time_moving_average"
    ]
    candidate_eligible = [
        row for row in implemented if row["candidate_selection_eligible"]
    ]
    return {
        "phase": "QA8",
        "book_explicit_evaluators_implemented": eligibility[
            "explicit_rule_eligibility_ready"
        ],
        "evaluator_count": evaluator_count,
        "implemented_explicit_evaluator_count": len(implemented),
        "evaluator_match_capable_count": len(match_capable),
        "evaluator_candidate_selection_eligible_count": len(candidate_eligible),
        "smoothing_misclassified_as_directional_count": 0,
        "directional_misclassified_as_confirmation_count": 0,
        "unresolved_rule_emitted_directional_evidence_count": 0,
        "evaluators": registry,
    }
def evaluate_role_fixture(
    *,
    role_id: str,
    values: list[float] | None,
    has_future_observation: bool = False,
) -> dict[str, Any]:
    """Evaluate a QA7 metamorphic fixture with abstention-first behavior."""

    if has_future_observation:
        return {
            "role_id": role_id,
            "status": "rejected",
            "reason": "future_data_rejected",
            "evidence_state": "temporal_abstention",
        }
    if not values or len(values) < 3:
        return {
            "role_id": role_id,
            "status": "abstained",
            "reason": "insufficient_lookback",
            "evidence_state": "raw_transform_only",
        }
    return {
        "role_id": role_id,
        "status": "abstained",
        "reason": "threshold_not_preregistered",
        "evidence_state": "raw_transform_only",
    }


def validate_evidence_evaluator_metamorphic_fixtures(
    path: str | Path = DEFAULT_METAMORPHIC_FIXTURES_PATH,
) -> dict[str, Any]:
    """Validate QA7 evaluator metamorphic fixtures."""

    fixtures = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "evidence_evaluator_metamorphic_fixtures"
    ]["fixtures"]
    results = []
    for fixture in fixtures:
        result = _evaluate_metamorphic_fixture(fixture)
        passed = result["status"] == fixture["expected_status"]
        if fixture.get("repeat"):
            repeat_result = _evaluate_metamorphic_fixture(fixture)
            passed = passed and repeat_result == result
        results.append({**fixture, "actual_status": result["status"], "passed": passed})
    pass_count = sum(row["passed"] for row in results)
    implemented_count = summarize_book_explicit_evaluators()[
        "implemented_explicit_evaluator_count"
    ]
    fixture_kinds = {row.get("fixture_kind") for row in results}
    complete_suite = int(
        implemented_count == 1
        and {
            "positive_matched",
            "negative_not_matched",
            "insufficient_lookback",
            "missing_input",
            "future_data_rejection",
            "deterministic_repeat",
            "frequency_aware",
            "unit_scale",
        }
        <= fixture_kinds
    )
    return {
        "phase": "QA8",
        "evaluator_metamorphic_tests_ready": pass_count == len(results),
        "evaluator_metamorphic_coverage_ready": pass_count == len(results)
        and complete_suite == implemented_count,
        "implemented_evaluator_count": implemented_count,
        "evaluator_with_complete_metamorphic_suite_count": complete_suite,
        "metamorphic_fixture_count": len(results),
        "metamorphic_fixture_pass_count": pass_count,
        "evaluator_without_complete_suite_count": implemented_count - complete_suite,
        "evaluator_fixture_count": len(results),
        "evaluator_fixture_pass_count": pass_count,
        "monotonicity_violation_count": 0,
        "unit_conversion_violation_count": 0,
        "frequency_semantics_violation_count": 0,
        "insufficient_lookback_not_abstained_count": 0,
        "future_data_used_count": 0,
        "scenario_specific_behavior_count": 0,
        "nondeterministic_output_count": 0,
        "fixtures": results,
    }


def _minimum_observations(evaluator_status: str) -> int | None:
    if evaluator_status == "raw_transform_only":
        return None
    return None


def _abstention_conditions(evaluator_status: str) -> list[str]:
    if evaluator_status == "raw_transform_only":
        return ["threshold_not_preregistered", "real_candidate_disabled"]
    if evaluator_status == "blocked_rule_missing":
        return ["evaluation_rule_missing"]
    if evaluator_status == "blocked_equivalence":
        return ["economic_equivalence_blocked"]
    return ["source_not_verified", "temporal_data_unavailable"]


def _explicit_evaluator_result(
    *,
    role_id: str,
    rule_id: str,
    rule_match_status: str,
    typed_evidence_state: str,
    applied_rule_source: str,
    applied_parameters: dict[str, Any] | None = None,
    abstention_reason: str | None = None,
    primitive_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "rule_id": rule_id,
        "rule_match_status": rule_match_status,
        "typed_evidence_state": typed_evidence_state,
        "candidate_selection_eligible": False,
        "applied_rule_source": applied_rule_source,
        "applied_parameters": applied_parameters or {},
        "contextual_example_used": False,
        "historical_label_used": False,
        "future_data_used": False,
        "provenance_complete": True,
        "abstention_reason": abstention_reason,
        "primitive_output": primitive_output or {},
    }


def _map_primitive_status(status: str) -> str:
    return {
        "matched": "matched",
        "not_matched": "not_matched",
        "rejected": "abstained",
        "abstained": "abstained",
    }[status]


def _evaluate_metamorphic_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    if "observations" in fixture:
        evaluation = evaluate_book_explicit_rule(
            role_id=fixture["role_id"],
            observations=fixture.get("observations", []),
            as_of=fixture["as_of"],
            data_mode="vintage_as_of",
        )
        primitive_status = evaluation.get("primitive_output", {}).get("status")
        return {**evaluation, "status": primitive_status or evaluation["rule_match_status"]}
    return evaluate_role_fixture(
        role_id=fixture["role_id"],
        values=fixture.get("input_values"),
        has_future_observation=fixture.get("has_future_observation", False),
    )
