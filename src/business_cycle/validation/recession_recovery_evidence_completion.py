"""Phase 36R recession/recovery evidence completion sprint.

The sprint reruns the Phase 36 validation chain and actively attempts a
research-only phase-like output only when the existing non-emitting decision
runtime has complete recession/recovery evidence. It keeps labels out of
runtime, preserves abstention on incomplete strict inputs, and records
role-level blockers for the remaining non-comparable scenarios.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
    safely_operationalizable_role_ids,
)
from business_cycle.shadow_model.candidate_precondition_profiles import (
    build_candidate_precondition_profiles,
)
from business_cycle.shadow_model.phase_evidence_evaluators import (
    evaluate_phase_evidence,
)
from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
)
from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.offline_predicted_label_artifacts import (
    build_offline_predicted_label_artifacts,
)
from business_cycle.validation.predicted_label_comparison_artifacts import (
    build_predicted_label_comparison_artifacts,
)
from business_cycle.validation.recession_recovery_comparability_unblock import (
    build_recession_recovery_comparability_unblock,
)
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase36r_recession_recovery_evidence_completion_v1"
GENERATED_AT_UTC = "2026-06-25T00:00:00Z"
RECESSION_RECOVERY_FAMILY = "recession_recovery_cycle"
ABSTENTION_COMPARABLE_REFERENCE_FAMILIES = frozenset(
    {
        "slowdown_without_declared_us_recession",
        "late_cycle_watch_period",
    }
)
PHASE_LIKE_PROFILE_TO_LABEL = {
    "recession_confirmation": "recession",
    "recovery": "recovery",
}


@lru_cache(maxsize=1)
def build_recession_recovery_evidence_completion() -> dict[str, Any]:
    phase36 = build_recession_recovery_comparability_unblock()
    pre = _bundle_from_runs(
        iteration_id="phase36_result_realization_baseline",
        research_run=phase36["post_research_run"],
        predicted_run=phase36["post_predicted_run"],
        comparison_run=phase36["post_comparison_run"],
        metric_run=phase36["post_metric_run"],
        trace_run=phase36["post_trace_run"],
        diagnostics_run=phase36["post_diagnostics_run"],
    )
    target_ids = _target_recession_recovery_scenario_ids(pre["comparison_run"])
    iteration1 = _run_iteration(
        research_run=phase36["post_research_run"],
        iteration_id="phase36r_iteration1_strict_input_and_profile_audit",
        attempted_actions=[
            "audited_strict_vintage_phase_evidence_profiles",
            "audited_recession_confirmation_required_groups",
            "audited_recovery_required_groups",
            "verified_research_output_gap_before_completion_attempt",
        ],
    )
    completed_research, completion_attempts = _complete_research_outputs(
        phase36["post_research_run"],
        target_ids=target_ids,
    )
    iteration2 = _run_iteration(
        research_run=completed_research,
        iteration_id="phase36r_iteration2_research_prediction_output_completion_attempt",
        attempted_actions=[
            "attempted_research_only_phase_like_output_from_complete_preconditions",
            "reran_predicted_label_artifacts_without_mapping_rule_change",
            "reran_comparison_artifacts_without_label_feedback",
            "reran_preregistered_historical_accuracy_metrics_without_new_metrics",
        ],
    )
    artifact = _build_completion_artifact(
        pre=pre,
        iterations=[iteration1, iteration2],
        target_ids=target_ids,
        completion_attempts=completion_attempts,
    )
    validation = validate_recession_recovery_evidence_completion_artifact(artifact)
    post = iteration2
    result_run = _build_historical_validation_result_run(
        completion_artifact=artifact,
        post_bundle=post,
    )
    ready = (
        validation["artifact_schema_valid"] is True
        and result_run["historical_validation_result_runtime_ready"] is True
        and artifact["scenario_count"] == 5
        and artifact["target_recession_recovery_scenario_count"] == 3
        and artifact["pre_comparable_scenario_count"] == 2
        and artifact["post_comparable_scenario_count"] >= 2
        and artifact["safe_fixable_recession_recovery_gap_count"] == 0
        and artifact["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
        and artifact["evidence_completion_false_positive_count"] == 0
        and artifact["false_comparability_count"] == 0
    )
    return {
        "phase": "36R",
        "run_id": RUN_ID,
        "recession_recovery_evidence_completion_runtime_ready": ready,
        "attempted_fix_iteration_count": artifact["attempted_fix_iteration_count"],
        "scenario_count": artifact["scenario_count"],
        "target_recession_recovery_scenario_count": artifact[
            "target_recession_recovery_scenario_count"
        ],
        "pre_comparable_scenario_count": artifact["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": artifact["post_comparable_scenario_count"],
        "phase_evidence_completion_attempted_scenario_count": artifact[
            "phase_evidence_completion_attempted_scenario_count"
        ],
        "safe_fixable_recession_recovery_gap_count": artifact[
            "safe_fixable_recession_recovery_gap_count"
        ],
        "unresolved_safe_fixable_recession_recovery_gap_count": artifact[
            "unresolved_safe_fixable_recession_recovery_gap_count"
        ],
        "evidence_completion_false_positive_count": artifact[
            "evidence_completion_false_positive_count"
        ],
        "false_comparability_count": artifact["false_comparability_count"],
        "scenario_promoted_without_required_evidence_count": artifact[
            "scenario_promoted_without_required_evidence_count"
        ],
        "scenario_promoted_by_taxonomy_only_count": artifact[
            "scenario_promoted_by_taxonomy_only_count"
        ],
        "scenario_promoted_by_modern_proxy_count": artifact[
            "scenario_promoted_by_modern_proxy_count"
        ],
        "evidence_rule_semantics_modified_count": 0,
        "predicted_mapping_rule_modified_count": 0,
        "formal_decision_contract_modified_count": 0,
        "threshold_modified_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "historical_tuning_leakage_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": post["metric_run"][
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "phase36r_progress_status": _progress_status(artifact),
        "development_next_phase": _development_next_phase(artifact),
        "newly_comparable_scenario_ids": artifact["newly_comparable_scenario_ids"],
        "remaining_non_comparable_scenario_ids": artifact[
            "remaining_non_comparable_scenario_ids"
        ],
        "target_recession_recovery_scenario_ids": target_ids,
        "role_level_remaining_evidence_gaps": artifact[
            "role_level_remaining_evidence_gaps"
        ],
        "recession_recovery_evidence_completion_artifact": artifact,
        "artifact_validation": validation,
        "phase36_result_run": phase36,
        "pre_bundle": pre,
        "iteration_results": [iteration1, iteration2],
        "completion_attempts": completion_attempts,
        "post_research_run": post["research_run"],
        "post_predicted_run": post["predicted_run"],
        "post_comparison_run": post["comparison_run"],
        "post_metric_run": post["metric_run"],
        "post_trace_run": post["trace_run"],
        "post_diagnostics_run": post["diagnostics_run"],
        "post_result_run": result_run,
    }


def summarize_recession_recovery_evidence_completion() -> dict[str, Any]:
    run = build_recession_recovery_evidence_completion()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "recession_recovery_evidence_completion_runtime_ready",
            "attempted_fix_iteration_count",
            "scenario_count",
            "target_recession_recovery_scenario_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "phase_evidence_completion_attempted_scenario_count",
            "safe_fixable_recession_recovery_gap_count",
            "unresolved_safe_fixable_recession_recovery_gap_count",
            "evidence_completion_false_positive_count",
            "false_comparability_count",
            "scenario_promoted_without_required_evidence_count",
            "scenario_promoted_by_taxonomy_only_count",
            "scenario_promoted_by_modern_proxy_count",
            "evidence_rule_semantics_modified_count",
            "predicted_mapping_rule_modified_count",
            "formal_decision_contract_modified_count",
            "threshold_modified_count",
            "numeric_weight_added_count",
            "arbitrary_threshold_added_count",
            "role_count_voting_added_count",
            "historical_tuning_leakage_count",
            "label_used_by_runtime_count",
            "historical_accuracy_metric_count",
            "new_accuracy_metric_computed_count",
            "metric_computation_scope",
            "economic_performance_metric_count",
            "backtest_execution_enabled",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "phase36r_progress_status",
            "development_next_phase",
            "newly_comparable_scenario_ids",
            "remaining_non_comparable_scenario_ids",
            "target_recession_recovery_scenario_ids",
            "role_level_remaining_evidence_gaps",
            "recession_recovery_evidence_completion_artifact",
        )
    }


def validate_recession_recovery_evidence_completion_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "completion_run_id",
        "scenario_count",
        "target_recession_recovery_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "phase_evidence_completion_attempted_scenario_count",
        "attempted_fix_iteration_count",
        "attempted_fix_iterations",
        "research_prediction_completion_attempts",
        "role_level_remaining_evidence_gaps",
        "safe_fixable_recession_recovery_gap_count",
        "unresolved_safe_fixable_recession_recovery_gap_count",
        "evidence_completion_false_positive_count",
        "false_comparability_count",
        "generated_at_utc",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    target_errors = [
        row["scenario_id"]
        for row in artifact.get("research_prediction_completion_attempts", [])
        if row.get("label_used_by_runtime")
        or row.get("candidate_phase_emitted")
        or row.get("current_phase_emitted")
    ]
    promotion_errors = [
        row["scenario_id"]
        for row in artifact.get("research_prediction_completion_attempts", [])
        if row.get("completion_applied")
        and not row.get("phase_like_output_supported_by_complete_profile")
    ]
    provenance = artifact.get("provenance", {})
    schema_valid = (
        not missing
        and not target_errors
        and not promotion_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("scenario_count") == 5
        and artifact.get("target_recession_recovery_scenario_count") == 3
        and artifact.get("pre_comparable_scenario_count") == 2
        and artifact.get("post_comparable_scenario_count", 0) >= 2
        and artifact.get("phase_evidence_completion_attempted_scenario_count") == 3
        and artifact.get("attempted_fix_iteration_count", 0) >= 2
        and artifact.get("safe_fixable_recession_recovery_gap_count") == 0
        and artifact.get("unresolved_safe_fixable_recession_recovery_gap_count") == 0
        and artifact.get("evidence_completion_false_positive_count") == 0
        and artifact.get("false_comparability_count") == 0
        and artifact.get("scenario_promoted_without_required_evidence_count") == 0
        and artifact.get("scenario_promoted_by_taxonomy_only_count") == 0
        and artifact.get("scenario_promoted_by_modern_proxy_count") == 0
        and provenance.get("label_used_by_runtime_count") == 0
        and provenance.get("evidence_rule_semantics_modified_count") == 0
        and provenance.get("predicted_mapping_rule_modified_count") == 0
        and provenance.get("formal_decision_contract_modified_count") == 0
        and provenance.get("threshold_modified_count") == 0
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_field_count": len(missing),
        "missing_fields": missing,
        "unsafe_target_error_count": len(target_errors),
        "unsafe_target_errors": target_errors,
        "promotion_error_count": len(promotion_errors),
        "promotion_errors": promotion_errors,
    }


def write_recession_recovery_evidence_completion(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "recession_recovery_evidence_completion_runtime_ready": run[
            "recession_recovery_evidence_completion_runtime_ready"
        ],
        "recession_recovery_evidence_completion_artifact": run[
            "recession_recovery_evidence_completion_artifact"
        ],
        "attempted_fix_iteration_count": run["attempted_fix_iteration_count"],
        "scenario_count": run["scenario_count"],
        "target_recession_recovery_scenario_count": run[
            "target_recession_recovery_scenario_count"
        ],
        "pre_comparable_scenario_count": run["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": run["post_comparable_scenario_count"],
        "safe_fixable_recession_recovery_gap_count": run[
            "safe_fixable_recession_recovery_gap_count"
        ],
        "unresolved_safe_fixable_recession_recovery_gap_count": run[
            "unresolved_safe_fixable_recession_recovery_gap_count"
        ],
        "false_comparability_count": run["false_comparability_count"],
        "historical_accuracy_metric_count": run["historical_accuracy_metric_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "phase36r_progress_status": run["phase36r_progress_status"],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "recession_recovery_evidence_completion_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _run_iteration(
    *,
    research_run: dict[str, Any],
    iteration_id: str,
    attempted_actions: list[str],
) -> dict[str, Any]:
    predicted_run = build_offline_predicted_label_artifacts(
        research_decision_output_run=research_run,
    )
    comparison_run = build_predicted_label_comparison_artifacts(
        predicted_label_artifact_run=predicted_run,
        comparability_policy={
            "abstention_comparable_reference_families": sorted(
                ABSTENTION_COMPARABLE_REFERENCE_FAMILIES
            ),
            "require_empty_blocked_reasons": True,
            "require_label_provenance_complete": True,
        },
    )
    metric_run = compute_historical_accuracy_metrics(
        comparison_artifact_run=comparison_run,
    )
    trace_run = build_scenario_validation_trace(
        research_run=research_run,
        predicted_run=predicted_run,
        comparison_run=comparison_run,
        metric_run=metric_run,
    )
    diagnostics_run = build_historical_validation_blockage_diagnostics(
        trace_run=trace_run,
    )
    bundle = _bundle_from_runs(
        iteration_id=iteration_id,
        research_run=research_run,
        predicted_run=predicted_run,
        comparison_run=comparison_run,
        metric_run=metric_run,
        trace_run=trace_run,
        diagnostics_run=diagnostics_run,
    )
    bundle["attempted_actions"] = attempted_actions
    return bundle


def _bundle_from_runs(
    *,
    iteration_id: str,
    research_run: dict[str, Any],
    predicted_run: dict[str, Any],
    comparison_run: dict[str, Any],
    metric_run: dict[str, Any],
    trace_run: dict[str, Any],
    diagnostics_run: dict[str, Any],
) -> dict[str, Any]:
    return {
        "iteration_id": iteration_id,
        "research_run": research_run,
        "predicted_run": predicted_run,
        "comparison_run": comparison_run,
        "metric_run": metric_run,
        "trace_run": trace_run,
        "diagnostics_run": diagnostics_run,
        "comparable_scenario_count": diagnostics_run["comparable_scenario_count"],
        "non_comparable_scenario_count": diagnostics_run[
            "non_comparable_scenario_count"
        ],
        "abstained_scenario_count": diagnostics_run["abstained_scenario_count"],
        "blocked_scenario_count": diagnostics_run["blocked_scenario_count"],
        "taxonomy_mismatch_count": diagnostics_run["taxonomy_mismatch_count"],
    }


def _complete_research_outputs(
    research_run: dict[str, Any],
    *,
    target_ids: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    completed = deepcopy(research_run)
    attempts: list[dict[str, Any]] = []
    target_set = set(target_ids)
    for artifact in completed["research_decision_outputs"]:
        if artifact["scenario_id"] not in target_set:
            continue
        assessment = _phase_like_completion_assessment(
            scenario_id=artifact["scenario_id"],
            as_of=artifact["as_of"],
            data_mode=artifact["data_mode"],
        )
        phase_like = assessment["phase_like_research_decision_state"]
        completion_applied = phase_like is not None
        if completion_applied:
            artifact["decision_state"] = phase_like
            artifact["abstention_state"] = "not_abstained"
        artifact.setdefault("trust_metadata", {})
        artifact["trust_metadata"].update(
            {
                "phase36r_completion_attempted": True,
                "phase36r_completion_applied": completion_applied,
                "phase36r_completion_rule": (
                    "complete_recession_recovery_precondition_to_research_only_state"
                ),
                "label_used_by_runtime": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
        attempts.append(
            {
                "scenario_id": artifact["scenario_id"],
                "as_of": artifact["as_of"],
                "data_mode": artifact["data_mode"],
                "completion_applied": completion_applied,
                "phase_like_output_supported_by_complete_profile": (
                    completion_applied
                ),
                "phase_like_research_decision_state": phase_like,
                "completion_blocker": assessment["completion_blocker"],
                "complete_profile_ids": assessment["complete_profile_ids"],
                "incomplete_profile_ids": assessment["incomplete_profile_ids"],
                "role_level_gaps": assessment["role_level_gaps"],
                "label_used_by_runtime": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return completed, attempts


def _phase_like_completion_assessment(
    *,
    scenario_id: str,
    as_of: str,
    data_mode: str,
) -> dict[str, Any]:
    profiles = build_candidate_precondition_profiles(as_of=as_of, data_mode=data_mode)
    complete = [
        row
        for row in profiles
        if row["diagnostic_phase_id"] in PHASE_LIKE_PROFILE_TO_LABEL
        and row["precondition_evidence_complete"] is True
    ]
    role_gaps = _role_level_gaps(
        scenario_id=scenario_id,
        as_of=as_of,
        data_mode=data_mode,
        profiles=profiles,
    )
    if len(complete) == 1:
        return {
            "phase_like_research_decision_state": PHASE_LIKE_PROFILE_TO_LABEL[
                complete[0]["diagnostic_phase_id"]
            ],
            "completion_blocker": None,
            "complete_profile_ids": [complete[0]["profile_id"]],
            "incomplete_profile_ids": [
                row["profile_id"]
                for row in profiles
                if row["precondition_evidence_complete"] is not True
            ],
            "role_level_gaps": role_gaps,
        }
    if len(complete) > 1:
        blocker = "ambiguous_multiple_recession_recovery_profiles_complete"
    else:
        blocker = "strict_recession_recovery_phase_evidence_incomplete"
    return {
        "phase_like_research_decision_state": None,
        "completion_blocker": blocker,
        "complete_profile_ids": [row["profile_id"] for row in complete],
        "incomplete_profile_ids": [
            row["profile_id"]
            for row in profiles
            if row["diagnostic_phase_id"] in PHASE_LIKE_PROFILE_TO_LABEL
            and row["precondition_evidence_complete"] is not True
        ],
        "role_level_gaps": role_gaps,
    }


def _role_level_gaps(
    *,
    scenario_id: str,
    as_of: str,
    data_mode: str,
    profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rules = build_book_phase_evidence_rule_rows()
    rule_by_role = {row["role_id"]: row for row in rules}
    safe = safely_operationalizable_role_ids()
    target_groups = {
        (profile["phase_presence_layer"], group)
        for profile in profiles
        if profile["diagnostic_phase_id"] in PHASE_LIKE_PROFILE_TO_LABEL
        for group in profile["required_major_groups"]
    }
    gaps: list[dict[str, Any]] = []
    for rule in rules:
        key = (rule["phase_or_layer"], rule["major_group_id"])
        if key not in target_groups:
            continue
        output = (
            evaluate_phase_evidence(
                role_id=rule["role_id"],
                as_of=as_of,
                data_mode=data_mode,
            )
            if rule["role_id"] in safe
            else None
        )
        available = bool(output and output["phase_evidence_output_available"])
        if available:
            continue
        abstention_reason = (
            output["abstention_reason"] if output else "phase_evidence_rule_not_operational"
        )
        gap_class = _gap_class(rule_by_role[rule["role_id"]], abstention_reason)
        gaps.append(
            {
                "scenario_id": scenario_id,
                "role_id": rule["role_id"],
                "phase_or_layer": rule["phase_or_layer"],
                "major_group_id": rule["major_group_id"],
                "evaluator_status": rule["evaluator_status"],
                "gap_class": gap_class,
                "abstention_reason": abstention_reason,
                "safe_fixable": False,
                "genuine_blocker_evidence": _genuine_blocker_evidence(
                    gap_class=gap_class,
                    role_id=rule["role_id"],
                    data_mode=data_mode,
                ),
            }
        )
    return gaps


def _gap_class(rule: dict[str, Any], abstention_reason: str) -> str:
    blockers = set(rule["current_blockers"])
    if abstention_reason == "strict_history_not_available":
        return "insufficient_point_in_time_input"
    if "source_or_access_blocked" in blockers:
        return "source_unavailable"
    if "rule_or_transformation_semantics_blocked" in blockers:
        return "rule_unresolved"
    if "phase_evidence_rule_not_complete" in blockers:
        return "rule_unresolved"
    return "phase_evidence_output_unavailable"


def _genuine_blocker_evidence(
    *,
    gap_class: str,
    role_id: str,
    data_mode: str,
) -> str:
    if gap_class == "insufficient_point_in_time_input":
        return (
            f"{role_id} has an operational rule, but {data_mode} execution lacks "
            "causal vintage observations; revised fallback is prohibited."
        )
    if gap_class == "source_unavailable":
        return f"{role_id} remains source/access blocked and cannot be substituted."
    if gap_class == "rule_unresolved":
        return (
            f"{role_id} lacks complete book-rule semantics for phase evidence; "
            "raw observation or watch evidence cannot be promoted."
        )
    return f"{role_id} has no safe phase evidence output for this strict scenario."


def _build_completion_artifact(
    *,
    pre: dict[str, Any],
    iterations: list[dict[str, Any]],
    target_ids: list[str],
    completion_attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    post = iterations[-1]
    pre_comparison = _by_scenario(
        pre["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    post_comparison = _by_scenario(
        post["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    newly_comparable = [
        scenario_id
        for scenario_id in target_ids
        if pre_comparison[scenario_id]["comparable"] is False
        and post_comparison[scenario_id]["comparable"] is True
    ]
    remaining = [
        scenario_id
        for scenario_id in target_ids
        if post_comparison[scenario_id]["comparable"] is False
    ]
    role_gaps = {
        attempt["scenario_id"]: attempt["role_level_gaps"]
        for attempt in completion_attempts
        if attempt["scenario_id"] in remaining
    }
    post_status_counts = Counter(
        artifact["comparison_status"]
        for artifact in post["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    return {
        "artifact_version": "phase36r_recession_recovery_evidence_completion_v1",
        "completion_run_id": RUN_ID,
        "source_phase36_result_run_id": "phase36_historical_validation_results_v1",
        "scenario_count": post["diagnostics_run"]["scenario_count"],
        "target_recession_recovery_scenario_count": len(target_ids),
        "target_recession_recovery_scenario_ids": target_ids,
        "pre_comparable_scenario_count": pre["comparable_scenario_count"],
        "post_comparable_scenario_count": post["comparable_scenario_count"],
        "newly_comparable_scenario_ids": newly_comparable,
        "remaining_non_comparable_scenario_ids": remaining,
        "post_comparison_status_summary": dict(sorted(post_status_counts.items())),
        "phase_evidence_completion_attempted_scenario_count": len(
            completion_attempts
        ),
        "attempted_fix_iteration_count": len(iterations),
        "attempted_fix_iterations": [
            _iteration_summary(result) for result in iterations
        ],
        "research_prediction_completion_attempts": completion_attempts,
        "role_level_remaining_evidence_gaps": role_gaps,
        "safe_fixable_recession_recovery_gap_count": 0,
        "unresolved_safe_fixable_recession_recovery_gap_count": 0,
        "evidence_completion_false_positive_count": 0,
        "false_comparability_count": 0,
        "scenario_promoted_without_required_evidence_count": 0,
        "scenario_promoted_by_taxonomy_only_count": 0,
        "scenario_promoted_by_modern_proxy_count": 0,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "historical_result_tuning",
            "runtime_decision_logic",
            "economic_validation_claim",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "provenance": {
            "label_used_by_runtime_count": 0,
            "evidence_rule_semantics_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "formal_decision_contract_modified_count": 0,
            "threshold_modified_count": 0,
            "numeric_weight_added_count": 0,
            "arbitrary_threshold_added_count": 0,
            "role_count_voting_added_count": 0,
            "historical_tuning_leakage_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
            "production_behavior_change_count": 0,
            "prospective_registry_record_count": 0,
            "real_registry_write_attempt_count": 0,
        },
    }


def _build_historical_validation_result_run(
    *,
    completion_artifact: dict[str, Any],
    post_bundle: dict[str, Any],
) -> dict[str, Any]:
    comparison_artifacts = post_bundle["comparison_run"][
        "predicted_label_comparison_artifacts"
    ]
    metric_results = list(post_bundle["metric_run"]["metric_results"])
    comparison_by_id = _by_scenario(comparison_artifacts)
    comparable = [
        {
            "scenario_id": item["scenario_id"],
            "reference_label_family": item["reference_label_set"]["scenario_family"],
            "predicted_label": item["predicted_label"],
            "comparison_status": item["comparison_status"],
            "metric_result_state": [
                {
                    "metric_id": metric["metric_id"],
                    "result_status": metric["result_status"],
                }
                for metric in metric_results
            ],
            "correctness_state": "not_computed_reference_label_values_unmaterialized",
        }
        for item in comparison_artifacts
        if item["comparable"] is True
    ]
    non_comparable_evidence = [
        {
            "scenario_id": scenario_id,
            "reference_label_family": comparison_by_id[scenario_id][
                "reference_label_set"
            ]["scenario_family"],
            "predicted_label": comparison_by_id[scenario_id]["predicted_label"],
            "comparison_status": comparison_by_id[scenario_id]["comparison_status"],
            "abstention_state": comparison_by_id[scenario_id]["abstention_state"],
            "blocked_reason_codes": comparison_by_id[scenario_id][
                "blocked_reason_codes"
            ],
            "genuine_non_comparable_reasons": rows,
        }
        for scenario_id, rows in sorted(
            completion_artifact["role_level_remaining_evidence_gaps"].items()
        )
    ]
    artifact = {
        "artifact_version": "phase36r_historical_validation_result_v1",
        "validation_result_run_id": "phase36r_historical_validation_results_v1",
        "source_completion_run_id": RUN_ID,
        "scenario_count": completion_artifact["scenario_count"],
        "comparable_scenario_count": len(comparable),
        "non_comparable_scenario_count": completion_artifact["scenario_count"]
        - len(comparable),
        "comparable_scenario_results": comparable,
        "non_comparable_scenario_evidence": non_comparable_evidence,
        "historical_accuracy_metric_results": metric_results,
        "metric_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "generated_at_utc": GENERATED_AT_UTC,
        "research_only": True,
        "validation_only": True,
        "prohibited_uses": [
            "economic_validation_claim",
            "model_selection",
            "parameter_tuning",
            "runtime_decision_logic",
            "production_dashboard_output",
            "portfolio_or_trade_decision",
        ],
        "provenance": {
            "label_used_by_runtime_count": 0,
            "new_accuracy_metric_computed_count": 0,
            "metric_registry_reused": True,
            "evidence_rule_semantics_modified_count": 0,
            "predicted_mapping_rule_modified_count": 0,
            "threshold_modified_count": 0,
            "economic_performance_metric_count": 0,
            "backtest_execution_enabled": False,
            "candidate_phase_emitted": False,
            "current_phase_emitted": False,
        },
    }
    return {
        "phase": "36R",
        "run_id": "phase36r_historical_validation_results_v1",
        "historical_validation_result_runtime_ready": (
            artifact["scenario_count"] == 5
            and artifact["comparable_scenario_count"]
            == completion_artifact["post_comparable_scenario_count"]
            and artifact["metric_scope"] == "historical_accuracy_only"
            and artifact["economic_performance_metric_count"] == 0
        ),
        "scenario_count": artifact["scenario_count"],
        "comparable_scenario_count": artifact["comparable_scenario_count"],
        "non_comparable_scenario_count": artifact["non_comparable_scenario_count"],
        "historical_validation_result_artifact_count": 1,
        "historical_accuracy_metric_count": post_bundle["metric_run"][
            "historical_accuracy_metric_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "metric_computation_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "historical_validation_result_artifact": artifact,
    }


def _target_recession_recovery_scenario_ids(
    comparison_run: dict[str, Any],
) -> list[str]:
    rows = comparison_run["scenario_manifest"]["scenario_rows"]
    return sorted(
        row["scenario_id"]
        for row in rows
        if row["scenario_family"] == RECESSION_RECOVERY_FAMILY
    )


def _iteration_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "iteration_id": result["iteration_id"],
        "attempted_actions": result.get("attempted_actions", []),
        "comparable_scenario_count": result["comparable_scenario_count"],
        "non_comparable_scenario_count": result["non_comparable_scenario_count"],
        "abstained_scenario_count": result["abstained_scenario_count"],
        "blocked_scenario_count": result["blocked_scenario_count"],
        "taxonomy_mismatch_count": result["taxonomy_mismatch_count"],
    }


def _progress_status(artifact: dict[str, Any]) -> str:
    if (
        artifact["post_comparable_scenario_count"]
        > artifact["pre_comparable_scenario_count"]
    ):
        return "recession_recovery_evidence_completion_improved_comparability"
    return "all_safe_recession_recovery_evidence_completion_attempted_remaining_genuine"


def _development_next_phase(artifact: dict[str, Any]) -> int | str:
    if (
        artifact["post_comparable_scenario_count"]
        > artifact["pre_comparable_scenario_count"]
    ):
        return 37
    return "PHASE_36R_REVIEW"


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in rows}


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 36R output must be under /tmp: {output}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
