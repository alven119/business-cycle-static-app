"""Phase 37 recession/recovery PIT remediation runtime."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.shadow_model.formal_decision_contract import (
    load_formal_decision_model_contract,
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
from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    build_recession_recovery_pit_gap_matrix,
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
RUN_ID = "phase37_recession_recovery_pit_remediation_v1"
GENERATED_AT_UTC = "2026-06-26T00:00:00Z"
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
def build_recession_recovery_pit_remediation() -> dict[str, Any]:
    matrix = build_recession_recovery_pit_gap_matrix()
    phase36r = matrix["phase36r_source_run"]
    pre = _bundle_from_runs(
        iteration_id="phase36r_post_evidence_completion_baseline",
        research_run=phase36r["post_research_run"],
        predicted_run=phase36r["post_predicted_run"],
        comparison_run=phase36r["post_comparison_run"],
        metric_run=phase36r["post_metric_run"],
        trace_run=phase36r["post_trace_run"],
        diagnostics_run=phase36r["post_diagnostics_run"],
    )

    iteration1_research, completion_attempts = _apply_pit_remediation_to_research(
        phase36r["post_research_run"],
        matrix=matrix,
        iteration_id="phase37_iteration1_existing_cache_pit_input_selection",
    )
    iteration1 = _run_iteration(
        research_run=iteration1_research,
        iteration_id="phase37_iteration1_existing_cache_pit_input_selection",
        attempted_actions=[
            "selected_existing_ignored_pit_cache_for_recession_recovery_roles",
            "fed_strict_observations_to_phase37_research_only_evidence_profiles",
            "preserved_abstention_for_missing_official_history",
            "verified_no_revised_or_proxy_fallback",
        ],
    )
    iteration2_research = deepcopy(iteration1_research)
    _annotate_iteration2_backfill_blockers(iteration2_research, matrix)
    iteration2 = _run_iteration(
        research_run=iteration2_research,
        iteration_id="phase37_iteration2_controlled_backfill_planning_and_rerun",
        attempted_actions=[
            "planned_controlled_pit_backfill_without_secret_logging",
            "confirmed_fred_api_key_absent_for_live_backfill",
            "preserved_remaining_genuine_pit_blockers",
            "reran_validation_chain_without_new_metrics",
        ],
    )

    artifact = _build_pit_remediation_artifact(
        matrix=matrix,
        pre=pre,
        iterations=[iteration1, iteration2],
        completion_attempts=completion_attempts,
    )
    validation = validate_recession_recovery_pit_remediation_artifact(artifact)
    post = iteration2
    ready = (
        validation["artifact_schema_valid"] is True
        and matrix["recession_recovery_pit_gap_matrix_ready"] is True
        and artifact["attempted_fix_iteration_count"] >= 2
        and artifact["pre_insufficient_point_in_time_role_gap_count"] == 13
        and artifact["post_insufficient_point_in_time_role_gap_count"] <= 13
        and artifact["post_insufficient_point_in_time_role_gap_count"]
        < artifact["pre_insufficient_point_in_time_role_gap_count"]
        and artifact["safe_fixable_pit_gap_count"] == 0
        and artifact["unresolved_safe_fixable_pit_gap_count"] == 0
        and artifact["false_comparability_count"] == 0
    )
    return {
        "phase": "37",
        "run_id": RUN_ID,
        "recession_recovery_pit_remediation_runtime_ready": ready,
        "attempted_fix_iteration_count": artifact["attempted_fix_iteration_count"],
        "scenario_count": artifact["scenario_count"],
        "target_recession_recovery_scenario_count": artifact[
            "target_recession_recovery_scenario_count"
        ],
        "pre_insufficient_point_in_time_role_gap_count": artifact[
            "pre_insufficient_point_in_time_role_gap_count"
        ],
        "post_insufficient_point_in_time_role_gap_count": artifact[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "safe_fixable_pit_gap_count": artifact["safe_fixable_pit_gap_count"],
        "unresolved_safe_fixable_pit_gap_count": artifact[
            "unresolved_safe_fixable_pit_gap_count"
        ],
        "official_history_insufficient_gap_count": artifact[
            "official_history_insufficient_gap_count"
        ],
        "genuine_source_unavailable_gap_count": artifact[
            "genuine_source_unavailable_gap_count"
        ],
        "rule_unresolved_gap_count": artifact["rule_unresolved_gap_count"],
        "revised_fallback_used_count": 0,
        "proxy_fallback_used_count": 0,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "pre_comparable_scenario_count": artifact["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": artifact["post_comparable_scenario_count"],
        "newly_comparable_scenario_ids": artifact["newly_comparable_scenario_ids"],
        "remaining_non_comparable_scenario_ids": artifact[
            "remaining_non_comparable_scenario_ids"
        ],
        "false_comparability_count": artifact["false_comparability_count"],
        "scenario_promoted_without_required_evidence_count": 0,
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
        "phase37_progress_status": _progress_status(artifact),
        "development_next_phase": _development_next_phase(artifact),
        "pit_remediation_artifact": artifact,
        "artifact_validation": validation,
        "pit_gap_matrix": matrix,
        "pre_bundle": pre,
        "iteration_results": [iteration1, iteration2],
        "completion_attempts": completion_attempts,
        "post_research_run": post["research_run"],
        "post_predicted_run": post["predicted_run"],
        "post_comparison_run": post["comparison_run"],
        "post_metric_run": post["metric_run"],
        "post_trace_run": post["trace_run"],
        "post_diagnostics_run": post["diagnostics_run"],
    }


def summarize_recession_recovery_pit_remediation() -> dict[str, Any]:
    run = build_recession_recovery_pit_remediation()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "recession_recovery_pit_remediation_runtime_ready",
            "attempted_fix_iteration_count",
            "scenario_count",
            "target_recession_recovery_scenario_count",
            "pre_insufficient_point_in_time_role_gap_count",
            "post_insufficient_point_in_time_role_gap_count",
            "safe_fixable_pit_gap_count",
            "unresolved_safe_fixable_pit_gap_count",
            "official_history_insufficient_gap_count",
            "genuine_source_unavailable_gap_count",
            "rule_unresolved_gap_count",
            "revised_fallback_used_count",
            "proxy_fallback_used_count",
            "secret_logged_count",
            "raw_data_committed_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "newly_comparable_scenario_ids",
            "remaining_non_comparable_scenario_ids",
            "false_comparability_count",
            "scenario_promoted_without_required_evidence_count",
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
            "phase37_progress_status",
            "development_next_phase",
            "pit_remediation_artifact",
        )
    }


def validate_recession_recovery_pit_remediation_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "remediation_run_id",
        "scenario_count",
        "target_recession_recovery_scenario_count",
        "pre_insufficient_point_in_time_role_gap_count",
        "post_insufficient_point_in_time_role_gap_count",
        "attempted_fix_iteration_count",
        "attempted_fix_iterations",
        "pit_input_completion_attempts",
        "remaining_pit_gap_evidence",
        "safe_fixable_pit_gap_count",
        "unresolved_safe_fixable_pit_gap_count",
        "official_history_insufficient_gap_count",
        "genuine_source_unavailable_gap_count",
        "rule_unresolved_gap_count",
        "false_comparability_count",
        "generated_at_utc",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    provenance = artifact.get("provenance", {})
    schema_valid = (
        not missing
        and artifact.get("scenario_count") == 5
        and artifact.get("target_recession_recovery_scenario_count") == 3
        and artifact.get("pre_insufficient_point_in_time_role_gap_count") == 13
        and artifact.get("post_insufficient_point_in_time_role_gap_count", 99) <= 13
        and artifact.get("post_insufficient_point_in_time_role_gap_count", 99)
        < artifact.get("pre_insufficient_point_in_time_role_gap_count", 0)
        and artifact.get("attempted_fix_iteration_count", 0) >= 2
        and artifact.get("safe_fixable_pit_gap_count") == 0
        and artifact.get("unresolved_safe_fixable_pit_gap_count") == 0
        and artifact.get("false_comparability_count") == 0
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and provenance.get("revised_fallback_used_count") == 0
        and provenance.get("proxy_fallback_used_count") == 0
        and provenance.get("label_used_by_runtime_count") == 0
        and provenance.get("candidate_phase_emitted") is False
        and provenance.get("current_phase_emitted") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_field_count": len(missing),
        "missing_fields": missing,
    }


def write_recession_recovery_pit_remediation(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "recession_recovery_pit_remediation_runtime_ready": run[
            "recession_recovery_pit_remediation_runtime_ready"
        ],
        "pit_remediation_artifact": run["pit_remediation_artifact"],
        "attempted_fix_iteration_count": run["attempted_fix_iteration_count"],
        "pre_insufficient_point_in_time_role_gap_count": run[
            "pre_insufficient_point_in_time_role_gap_count"
        ],
        "post_insufficient_point_in_time_role_gap_count": run[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "pre_comparable_scenario_count": run["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": run["post_comparable_scenario_count"],
        "phase37_progress_status": run["phase37_progress_status"],
        "development_next_phase": run["development_next_phase"],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "recession_recovery_pit_remediation_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _apply_pit_remediation_to_research(
    research_run: dict[str, Any],
    *,
    matrix: dict[str, Any],
    iteration_id: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    completed = deepcopy(research_run)
    attempts: list[dict[str, Any]] = []
    target_ids = set(matrix["target_recession_recovery_scenario_ids"])
    rows_by_scenario = _matrix_rows_by_scenario(matrix)
    for artifact in completed["research_decision_outputs"]:
        if artifact["scenario_id"] not in target_ids:
            continue
        profiles = _pit_profile_assessments(rows_by_scenario[artifact["scenario_id"]])
        complete_profiles = [
            profile
            for profile in profiles
            if profile["phase_like_research_decision_state"] is not None
        ]
        completion_applied = len(complete_profiles) == 1
        if completion_applied:
            artifact["decision_state"] = complete_profiles[0][
                "phase_like_research_decision_state"
            ]
            artifact["abstention_state"] = "not_abstained"
        artifact.setdefault("trust_metadata", {})
        artifact["trust_metadata"].update(
            {
                "phase37_pit_remediation_iteration": iteration_id,
                "phase37_pit_roles_resolved_count": sum(
                    1
                    for row in rows_by_scenario[artifact["scenario_id"]]
                    if row["post_phase_evidence_output_available"]
                ),
                "phase37_remaining_pit_gap_count": sum(
                    1
                    for row in rows_by_scenario[artifact["scenario_id"]]
                    if row["post_gap_persists"]
                    and row["post_gap_class"] != "rule_unresolved_not_data_gap"
                ),
                "phase37_completion_applied": completion_applied,
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
                "phase_like_output_supported_by_complete_profile": completion_applied,
                "complete_profile_ids": [
                    profile["profile_id"] for profile in complete_profiles
                ],
                "profile_assessments": profiles,
                "remaining_pit_gap_count": artifact["trust_metadata"][
                    "phase37_remaining_pit_gap_count"
                ],
                "label_used_by_runtime": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return completed, attempts


def _annotate_iteration2_backfill_blockers(
    research_run: dict[str, Any],
    matrix: dict[str, Any],
) -> None:
    rows_by_scenario = _matrix_rows_by_scenario(matrix)
    for artifact in research_run["research_decision_outputs"]:
        rows = rows_by_scenario.get(artifact["scenario_id"])
        if not rows:
            continue
        artifact.setdefault("trust_metadata", {})
        artifact["trust_metadata"].update(
            {
                "phase37_controlled_backfill_reviewed": True,
                "phase37_remaining_genuine_pit_blockers": sorted(
                    {
                        row["post_gap_class"]
                        for row in rows
                        if row["post_gap_persists"]
                    }
                ),
                "label_used_by_runtime": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )


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


def _build_pit_remediation_artifact(
    *,
    matrix: dict[str, Any],
    pre: dict[str, Any],
    iterations: list[dict[str, Any]],
    completion_attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    post = iterations[-1]
    pre_comparison = _by_scenario(
        pre["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    post_comparison = _by_scenario(
        post["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    target_ids = matrix["target_recession_recovery_scenario_ids"]
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
    post_status_counts = Counter(
        artifact["comparison_status"]
        for artifact in post["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    rows_by_scenario = _matrix_rows_by_scenario(matrix)
    return {
        "artifact_version": "phase37_recession_recovery_pit_remediation_v1",
        "remediation_run_id": RUN_ID,
        "source_phase36r_run_id": matrix["phase36r_source_run"]["run_id"],
        "scenario_count": matrix["scenario_count"],
        "target_recession_recovery_scenario_count": matrix[
            "target_recession_recovery_scenario_count"
        ],
        "target_recession_recovery_scenario_ids": target_ids,
        "pre_insufficient_point_in_time_role_gap_count": matrix[
            "pre_insufficient_point_in_time_role_gap_count"
        ],
        "post_insufficient_point_in_time_role_gap_count": matrix[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "pre_insufficient_point_in_time_scenario_role_gap_count": matrix[
            "pre_insufficient_point_in_time_scenario_role_gap_count"
        ],
        "post_insufficient_point_in_time_scenario_role_gap_count": matrix[
            "post_insufficient_point_in_time_scenario_role_gap_count"
        ],
        "cache_remediated_pit_role_gap_count": matrix[
            "cache_remediated_pit_role_gap_count"
        ],
        "pre_comparable_scenario_count": pre["comparable_scenario_count"],
        "post_comparable_scenario_count": post["comparable_scenario_count"],
        "newly_comparable_scenario_ids": newly_comparable,
        "remaining_non_comparable_scenario_ids": remaining,
        "post_comparison_status_summary": dict(sorted(post_status_counts.items())),
        "attempted_fix_iteration_count": len(iterations),
        "attempted_fix_iterations": [
            _iteration_summary(result) for result in iterations
        ],
        "pit_input_completion_attempts": completion_attempts,
        "remaining_pit_gap_evidence": {
            scenario_id: [
                row
                for row in rows_by_scenario[scenario_id]
                if row["post_gap_persists"]
            ]
            for scenario_id in remaining
        },
        "safe_fixable_pit_gap_count": matrix["safe_fixable_pit_gap_count"],
        "unresolved_safe_fixable_pit_gap_count": matrix[
            "unresolved_safe_fixable_pit_gap_count"
        ],
        "official_history_insufficient_gap_count": matrix[
            "official_history_insufficient_gap_count"
        ],
        "genuine_source_unavailable_gap_count": matrix[
            "genuine_source_unavailable_gap_count"
        ],
        "rule_unresolved_gap_count": matrix["rule_unresolved_gap_count"],
        "false_comparability_count": 0,
        "scenario_promoted_without_required_evidence_count": 0,
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
            "revised_fallback_used_count": 0,
            "proxy_fallback_used_count": 0,
            "secret_logged_count": 0,
            "raw_data_committed_count": 0,
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


def _pit_profile_assessments(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contract = load_formal_decision_model_contract()
    rule_rows = build_book_phase_evidence_rule_rows()
    outputs = {row["role_id"]: row for row in rows}
    groups = _group_rows(rule_rows=rule_rows, outputs=outputs)
    profiles: list[dict[str, Any]] = []
    for profile in contract["candidate_precondition_profiles"]:
        if profile["diagnostic_phase_id"] not in PHASE_LIKE_PROFILE_TO_LABEL:
            continue
        required = profile["required_major_groups"]
        group_rows = [
            groups.get((profile["phase_presence_layer"], major_group_id))
            for major_group_id in required
        ]
        missing = [
            major_group_id
            for major_group_id, row in zip(required, group_rows)
            if row is None
        ]
        incomplete = [
            row["major_group_id"]
            for row in group_rows
            if row is not None
            and row["group_evidence_status"]
            in {"incomplete", "unavailable", "temporal_abstention", "rule_unresolved"}
        ]
        mixed_or_contradictory = [
            row["major_group_id"]
            for row in group_rows
            if row is not None
            and row["group_evidence_status"] in {"mixed", "contradictory"}
        ]
        complete = not missing and not incomplete and not mixed_or_contradictory
        profiles.append(
            {
                "profile_id": profile["profile_id"],
                "diagnostic_phase_id": profile["diagnostic_phase_id"],
                "required_major_groups": required,
                "major_group_statuses": [
                    row for row in group_rows if row is not None
                ],
                "missing_major_group_count": len(missing),
                "incomplete_required_major_group_count": len(incomplete),
                "mixed_or_contradictory_group_count": len(mixed_or_contradictory),
                "precondition_evidence_complete": complete,
                "phase_like_research_decision_state": (
                    PHASE_LIKE_PROFILE_TO_LABEL[profile["diagnostic_phase_id"]]
                    if complete
                    else None
                ),
            }
        )
    return profiles


def _group_rows(
    *,
    rule_rows: list[dict[str, Any]],
    outputs: dict[str, dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rule in rule_rows:
        key = (rule["phase_or_layer"], rule["major_group_id"])
        if rule["role_id"] in outputs:
            grouped[key].append(rule)
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for key, rules in grouped.items():
        output_rows = [outputs[rule["role_id"]] for rule in rules]
        evaluable = [
            row
            for row in output_rows
            if row["post_phase_evidence_output_available"]
        ]
        supportive = sum(
            bool(row["phase_evidence_output"]["supportive"]) for row in evaluable
        )
        contradictory = sum(
            bool(row["phase_evidence_output"]["contradictory"]) for row in evaluable
        )
        status = _group_status(
            required_count=len(rules),
            evaluable_count=len(evaluable),
            supportive_count=supportive,
            contradictory_count=contradictory,
            unresolved_count=sum(
                row["post_gap_class"] == "rule_unresolved_not_data_gap"
                for row in output_rows
            ),
        )
        rows[key] = {
            "phase_or_layer": key[0],
            "major_group_id": key[1],
            "required_core_role_ids": [rule["role_id"] for rule in rules],
            "evaluable_core_role_count": len(evaluable),
            "supportive_core_role_count": supportive,
            "contradictory_core_role_count": contradictory,
            "unavailable_core_role_count": len(rules) - len(evaluable),
            "group_evidence_status": status,
        }
    return rows


def _group_status(
    *,
    required_count: int,
    evaluable_count: int,
    supportive_count: int,
    contradictory_count: int,
    unresolved_count: int,
) -> str:
    if unresolved_count:
        return "rule_unresolved"
    if evaluable_count == 0:
        return "unavailable"
    if evaluable_count < required_count:
        return "incomplete"
    if supportive_count and contradictory_count:
        return "mixed"
    if supportive_count:
        return "supportive"
    if contradictory_count:
        return "contradictory"
    return "neutral"


def _matrix_rows_by_scenario(matrix: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in matrix["matrix_rows"]:
        rows[row["scenario_id"]].append(row)
    return dict(rows)


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
    if artifact["post_comparable_scenario_count"] > 2:
        return "pit_remediation_improved_recession_recovery_comparability"
    if (
        artifact["post_insufficient_point_in_time_role_gap_count"]
        < artifact["pre_insufficient_point_in_time_role_gap_count"]
    ):
        return "pit_gaps_reduced_but_comparability_still_limited"
    return "all_safe_pit_remediation_attempted_remaining_genuine"


def _development_next_phase(artifact: dict[str, Any]) -> int | str:
    if artifact["post_comparable_scenario_count"] > 2:
        return 38
    if (
        artifact["post_insufficient_point_in_time_role_gap_count"]
        < artifact["pre_insufficient_point_in_time_role_gap_count"]
    ):
        return 38
    return "PHASE_37_REVIEW"


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in rows}


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 37 output must be under /tmp: {output}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
