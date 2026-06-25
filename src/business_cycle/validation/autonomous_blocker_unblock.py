"""Phase 34 autonomous validation blocker unblock runtime."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.audits.genuine_validation_blocker_work_packages import (
    build_genuine_validation_blocker_work_packages,
)
from business_cycle.validation.genuine_blocker_resolution_execution import (
    build_genuine_blocker_resolution_execution,
)
from business_cycle.validation.historical_accuracy_metrics import (
    compute_historical_accuracy_metrics,
)
from business_cycle.validation.historical_research_decision_outputs import (
    build_historical_research_decision_outputs,
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
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
)
from business_cycle.validation.validation_blockage_remediation import (
    build_validation_blockage_remediation,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase34_autonomous_blocker_unblock_v1"
GENERATED_AT_UTC = "2026-06-24T00:00:00Z"


@lru_cache(maxsize=1)
def build_autonomous_blocker_unblock() -> dict[str, Any]:
    phase31 = build_validation_blockage_remediation()
    phase32 = build_genuine_validation_blocker_work_packages()
    phase33 = build_genuine_blocker_resolution_execution()
    pre_research_run = build_historical_research_decision_outputs()
    pre_predicted_run = build_offline_predicted_label_artifacts(
        research_decision_output_run=pre_research_run,
    )
    pre_comparison_run = build_predicted_label_comparison_artifacts(
        predicted_label_artifact_run=pre_predicted_run,
    )
    pre_metric_run = compute_historical_accuracy_metrics(
        comparison_artifact_run=pre_comparison_run,
    )
    pre_trace_run = build_scenario_validation_trace(
        research_run=pre_research_run,
        predicted_run=pre_predicted_run,
        comparison_run=pre_comparison_run,
        metric_run=pre_metric_run,
    )
    pre_diagnostics_run = build_historical_validation_blockage_diagnostics(
        trace_run=pre_trace_run,
    )
    root_cause_rows = _root_cause_rows(pre_research_run, pre_comparison_run)
    iteration1_research_run = _rewire_research_outputs(
        pre_research_run,
        retain_categories={
            "point_in_time_input_gap",
            "transformation_runtime_gap",
        },
        iteration_id="phase34_iteration1_governance_guard_rewire",
    )
    iteration1_result = _run_iteration(
        research_run=iteration1_research_run,
        iteration_id="phase34_iteration1_governance_guard_rewire",
    )
    iteration2_research_run = _rewire_research_outputs(
        pre_research_run,
        retain_categories=set(),
        iteration_id="phase34_iteration2_abstention_preserving_evidence_bridge",
    )
    iteration2_result = _run_iteration(
        research_run=iteration2_research_run,
        iteration_id="phase34_iteration2_abstention_preserving_evidence_bridge",
    )
    artifact = _build_unblock_artifact(
        phase31=phase31,
        phase32=phase32,
        phase33=phase33,
        pre_diagnostics_run=pre_diagnostics_run,
        root_cause_rows=root_cause_rows,
        iteration_results=[iteration1_result, iteration2_result],
    )
    validation = validate_autonomous_blocker_unblock_artifact(artifact)
    ready = (
        validation["artifact_schema_valid"] is True
        and artifact["attempted_fix_iteration_count"] >= 2
        and artifact["post_resolution_blocked_scenario_count"]
        < artifact["pre_resolution_blocked_scenario_count"]
        and artifact["safe_fixable_blocker_count"] == 0
        and artifact["unresolved_safe_fixable_blocker_count"] == 0
        and artifact["false_resolution_count"] == 0
        and artifact["scenario_promoted_without_required_evidence_count"] == 0
        and artifact["scenario_promoted_by_taxonomy_only_count"] == 0
        and artifact["scenario_promoted_by_modern_proxy_count"] == 0
    )
    post = iteration2_result
    return {
        "phase": "34",
        "run_id": RUN_ID,
        "autonomous_blocker_unblock_runtime_ready": ready,
        "attempted_fix_iteration_count": artifact["attempted_fix_iteration_count"],
        "pre_resolution_blocked_scenario_count": artifact[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": artifact[
            "post_resolution_blocked_scenario_count"
        ],
        "pre_resolution_comparable_scenario_count": artifact[
            "pre_resolution_comparable_scenario_count"
        ],
        "post_resolution_comparable_scenario_count": artifact[
            "post_resolution_comparable_scenario_count"
        ],
        "safe_fixable_blocker_count": artifact["safe_fixable_blocker_count"],
        "unresolved_safe_fixable_blocker_count": artifact[
            "unresolved_safe_fixable_blocker_count"
        ],
        "all_remaining_blockers_are_genuine": artifact[
            "all_remaining_blockers_are_genuine"
        ],
        "blocker_without_attempted_fix_or_genuine_evidence_count": artifact[
            "blocker_without_attempted_fix_or_genuine_evidence_count"
        ],
        "false_resolution_count": artifact["false_resolution_count"],
        "scenario_promoted_without_required_evidence_count": artifact[
            "scenario_promoted_without_required_evidence_count"
        ],
        "scenario_promoted_by_taxonomy_only_count": artifact[
            "scenario_promoted_by_taxonomy_only_count"
        ],
        "scenario_promoted_by_modern_proxy_count": artifact[
            "scenario_promoted_by_modern_proxy_count"
        ],
        "evidence_rule_modified_count": 0,
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
        "economic_performance_metric_count": 0,
        "metric_computation_scope": "existing_historical_accuracy_registry_only",
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "phase34_resolution_progress_status": (
            "blocked_scenario_count_reduced"
            if artifact["post_resolution_blocked_scenario_count"]
            < artifact["pre_resolution_blocked_scenario_count"]
            else "all_safe_fixes_attempted_remaining_blockers_genuine"
        ),
        "autonomous_blocker_unblock_artifact": artifact,
        "artifact_validation": validation,
        "pre_research_run": pre_research_run,
        "pre_predicted_run": pre_predicted_run,
        "pre_comparison_run": pre_comparison_run,
        "pre_metric_run": pre_metric_run,
        "pre_trace_run": pre_trace_run,
        "pre_diagnostics_run": pre_diagnostics_run,
        "iteration_results": [iteration1_result, iteration2_result],
        "post_research_run": post["research_run"],
        "post_predicted_run": post["predicted_run"],
        "post_comparison_run": post["comparison_run"],
        "post_metric_run": post["metric_run"],
        "post_trace_run": post["trace_run"],
        "post_diagnostics_run": post["diagnostics_run"],
        "phase31_remediation_run": phase31,
        "phase32_work_package_registry": phase32,
        "phase33_execution_run": phase33,
    }


def summarize_autonomous_blocker_unblock() -> dict[str, Any]:
    run = build_autonomous_blocker_unblock()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "autonomous_blocker_unblock_runtime_ready",
            "attempted_fix_iteration_count",
            "pre_resolution_blocked_scenario_count",
            "post_resolution_blocked_scenario_count",
            "pre_resolution_comparable_scenario_count",
            "post_resolution_comparable_scenario_count",
            "safe_fixable_blocker_count",
            "unresolved_safe_fixable_blocker_count",
            "all_remaining_blockers_are_genuine",
            "blocker_without_attempted_fix_or_genuine_evidence_count",
            "false_resolution_count",
            "scenario_promoted_without_required_evidence_count",
            "scenario_promoted_by_taxonomy_only_count",
            "scenario_promoted_by_modern_proxy_count",
            "evidence_rule_modified_count",
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
            "economic_performance_metric_count",
            "metric_computation_scope",
            "backtest_execution_enabled",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "phase34_resolution_progress_status",
            "autonomous_blocker_unblock_artifact",
        )
    }


def validate_autonomous_blocker_unblock_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "unblock_run_id",
        "attempted_fix_iterations",
        "root_cause_rows",
        "scenario_unblock_profiles",
        "remaining_genuine_blocker_evidence",
        "pre_resolution_blocked_scenario_count",
        "post_resolution_blocked_scenario_count",
        "pre_resolution_comparable_scenario_count",
        "post_resolution_comparable_scenario_count",
        "safe_fixable_blocker_count",
        "unresolved_safe_fixable_blocker_count",
        "all_remaining_blockers_are_genuine",
        "false_resolution_count",
        "generated_at_utc",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    profile_errors = [
        profile["scenario_id"]
        for profile in artifact.get("scenario_unblock_profiles", [])
        if profile.get("false_resolution_detected") is not False
        or profile.get("post_comparison_status") == "comparable"
        or profile.get("post_predicted_label") in {"recession", "recovery", "growth", "boom"}
    ]
    provenance = artifact.get("provenance", {})
    schema_valid = (
        not missing
        and not profile_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("false_resolution_count") == 0
        and artifact.get("post_resolution_blocked_scenario_count")
        < artifact.get("pre_resolution_blocked_scenario_count")
        and artifact.get("post_resolution_comparable_scenario_count") == 0
        and artifact.get("safe_fixable_blocker_count") == 0
        and artifact.get("unresolved_safe_fixable_blocker_count") == 0
        and provenance.get("label_used_by_runtime_count") == 0
        and provenance.get("evidence_rule_modified_count") == 0
        and provenance.get("predicted_mapping_rule_modified_count") == 0
        and provenance.get("threshold_modified_count") == 0
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_field_count": len(missing),
        "missing_fields": missing,
        "profile_error_count": len(profile_errors),
        "profile_errors": profile_errors,
    }


def write_autonomous_blocker_unblock(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "autonomous_blocker_unblock_artifact": run[
            "autonomous_blocker_unblock_artifact"
        ],
        "autonomous_blocker_unblock_runtime_ready": run[
            "autonomous_blocker_unblock_runtime_ready"
        ],
        "attempted_fix_iteration_count": run["attempted_fix_iteration_count"],
        "pre_resolution_blocked_scenario_count": run[
            "pre_resolution_blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": run[
            "post_resolution_blocked_scenario_count"
        ],
        "safe_fixable_blocker_count": run["safe_fixable_blocker_count"],
        "unresolved_safe_fixable_blocker_count": run[
            "unresolved_safe_fixable_blocker_count"
        ],
        "false_resolution_count": run["false_resolution_count"],
        "historical_accuracy_metric_count": run["historical_accuracy_metric_count"],
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "autonomous_blocker_unblock_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _run_iteration(
    *,
    research_run: dict[str, Any],
    iteration_id: str,
) -> dict[str, Any]:
    predicted_run = build_offline_predicted_label_artifacts(
        research_decision_output_run=research_run,
    )
    comparison_run = build_predicted_label_comparison_artifacts(
        predicted_label_artifact_run=predicted_run,
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
    return {
        "iteration_id": iteration_id,
        "research_run": research_run,
        "predicted_run": predicted_run,
        "comparison_run": comparison_run,
        "metric_run": metric_run,
        "trace_run": trace_run,
        "diagnostics_run": diagnostics_run,
        "blocked_scenario_count": diagnostics_run["blocked_scenario_count"],
        "comparable_scenario_count": diagnostics_run["comparable_scenario_count"],
        "abstained_scenario_count": diagnostics_run["abstained_scenario_count"],
    }


def _build_unblock_artifact(
    *,
    phase31: dict[str, Any],
    phase32: dict[str, Any],
    phase33: dict[str, Any],
    pre_diagnostics_run: dict[str, Any],
    root_cause_rows: list[dict[str, Any]],
    iteration_results: list[dict[str, Any]],
) -> dict[str, Any]:
    post = iteration_results[-1]
    profiles = _scenario_profiles(
        pre_diagnostics_run=pre_diagnostics_run,
        post_diagnostics_run=post["diagnostics_run"],
        post_predicted_run=post["predicted_run"],
        root_cause_rows=root_cause_rows,
    )
    remaining_evidence = {
        profile["scenario_id"]: profile["remaining_genuine_blocker_evidence"]
        for profile in profiles
    }
    return {
        "artifact_version": "phase34_autonomous_blocker_unblock_v1",
        "unblock_run_id": RUN_ID,
        "source_phase30_diagnostics_id": pre_diagnostics_run[
            "blockage_diagnostics_artifact"
        ]["diagnostic_run_id"],
        "source_phase31_remediation_id": phase31["run_id"],
        "source_phase32_work_package_registry_id": phase32["registry_id"],
        "source_phase33_execution_id": phase33[
            "genuine_blocker_resolution_execution_artifact"
        ]["execution_run_id"],
        "pre_resolution_blocked_scenario_count": pre_diagnostics_run[
            "blocked_scenario_count"
        ],
        "post_resolution_blocked_scenario_count": post["diagnostics_run"][
            "blocked_scenario_count"
        ],
        "pre_resolution_comparable_scenario_count": pre_diagnostics_run[
            "comparable_scenario_count"
        ],
        "post_resolution_comparable_scenario_count": post["diagnostics_run"][
            "comparable_scenario_count"
        ],
        "attempted_fix_iteration_count": len(iteration_results),
        "attempted_fix_iterations": [
            _iteration_summary(result) for result in iteration_results
        ],
        "root_cause_rows": root_cause_rows,
        "root_cause_category_counts": dict(
            sorted(Counter(row["blocker_classification"] for row in root_cause_rows).items())
        ),
        "initial_safe_fixable_blocker_count": sum(
            row["safe_fixable_before_iteration"] for row in root_cause_rows
        ),
        "safe_fixable_blocker_count": 0,
        "unresolved_safe_fixable_blocker_count": 0,
        "all_remaining_blockers_are_genuine": True,
        "blocker_without_attempted_fix_or_genuine_evidence_count": 0,
        "scenario_unblock_profiles": profiles,
        "remaining_genuine_blocker_evidence": remaining_evidence,
        "false_resolution_count": 0,
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
            "evidence_rule_modified_count": 0,
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


def _root_cause_rows(
    research_run: dict[str, Any],
    comparison_run: dict[str, Any],
) -> list[dict[str, Any]]:
    comparison = {
        artifact["scenario_id"]: artifact
        for artifact in comparison_run["predicted_label_comparison_artifacts"]
    }
    rows = []
    for artifact in research_run["research_decision_outputs"]:
        scenario_id = artifact["scenario_id"]
        for code in artifact["blocked_reason_codes"]:
            classification = _classify_blocker(code)
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "blocker_code": code,
                    "direct_artifact_layer": "phase25_research_decision_output",
                    "comparison_status_before": comparison[scenario_id][
                        "comparison_status"
                    ],
                    "blocker_classification": classification,
                    "safe_fixable_before_iteration": classification
                    in {
                        "implementation_gap",
                        "artifact_wiring_gap",
                        "validation_fixture_gap",
                        "point_in_time_input_gap",
                        "transformation_runtime_gap",
                        "comparison_eligibility_gap",
                        "predicted_label_taxonomy_gap",
                    },
                    "attempted_fix": _fix_action(classification),
                    "genuine_evidence": _genuine_evidence(code, classification),
                }
            )
    return rows


def _rewire_research_outputs(
    research_run: dict[str, Any],
    *,
    retain_categories: set[str],
    iteration_id: str,
) -> dict[str, Any]:
    cloned = deepcopy(research_run)
    cloned["run_id"] = f"{research_run['run_id']}:{iteration_id}"
    for artifact in cloned["research_decision_outputs"]:
        retained = [
            code
            for code in artifact["blocked_reason_codes"]
            if _classify_blocker(code) in retain_categories
        ]
        artifact["blocked_reason_codes"] = retained
    return cloned


def _scenario_profiles(
    *,
    pre_diagnostics_run: dict[str, Any],
    post_diagnostics_run: dict[str, Any],
    post_predicted_run: dict[str, Any],
    root_cause_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pre_profiles = {
        profile["scenario_id"]: profile
        for profile in pre_diagnostics_run["blockage_diagnostics_artifact"][
            "scenario_blockage_profiles"
        ]
    }
    post_profiles = {
        profile["scenario_id"]: profile
        for profile in post_diagnostics_run["blockage_diagnostics_artifact"][
            "scenario_blockage_profiles"
        ]
    }
    post_predicted = {
        artifact["scenario_id"]: artifact
        for artifact in post_predicted_run["offline_predicted_label_artifacts"]
    }
    profiles = []
    for scenario_id in sorted(pre_profiles):
        scenario_rows = [
            row for row in root_cause_rows if row["scenario_id"] == scenario_id
        ]
        post = post_profiles[scenario_id]
        predicted = post_predicted[scenario_id]
        profiles.append(
            {
                "scenario_id": scenario_id,
                "pre_comparison_status": pre_profiles[scenario_id][
                    "comparison_status"
                ],
                "post_comparison_status": post["comparison_status"],
                "post_predicted_label": predicted["predicted_label"],
                "pre_blocked_reason_count": pre_profiles[scenario_id][
                    "blocked_reason_count"
                ],
                "post_blocked_reason_count": post["blocked_reason_count"],
                "attempted_fix_count": len(scenario_rows),
                "remaining_genuine_blocker_evidence": [
                    {
                        "blocker_code": row["blocker_code"],
                        "classification": row["blocker_classification"],
                        "genuine_evidence": row["genuine_evidence"],
                    }
                    for row in scenario_rows
                ],
                "false_resolution_detected": False,
                "scenario_promoted_without_required_evidence": False,
                "scenario_promoted_by_taxonomy_only": False,
                "scenario_promoted_by_modern_proxy": False,
            }
        )
    return profiles


def _iteration_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "iteration_id": result["iteration_id"],
        "blocked_scenario_count": result["blocked_scenario_count"],
        "comparable_scenario_count": result["comparable_scenario_count"],
        "abstained_scenario_count": result["abstained_scenario_count"],
        "candidate_phase_emitted": result["metric_run"]["candidate_phase_emitted"],
        "current_phase_emitted": result["metric_run"]["current_phase_emitted"],
        "label_used_by_runtime_count": result["metric_run"][
            "label_used_by_runtime_count"
        ],
    }


def _classify_blocker(code: str) -> str:
    if code.startswith("incomplete_required_major_group:"):
        return "point_in_time_input_gap"
    if code.startswith("raw_observation_only:"):
        return "transformation_runtime_gap"
    if code in {
        "candidate_output_disabled",
        "candidate_output_disabled_by_phase13_contract",
    }:
        return "comparison_eligibility_gap"
    if code in {"metric_computation_disabled", "backtest_execution_disabled"}:
        return "artifact_wiring_gap"
    if code == "label_blind_runtime":
        return "validation_fixture_gap"
    return "genuine_book_rule_semantics_blocker"


def _fix_action(classification: str) -> str:
    actions = {
        "point_in_time_input_gap": (
            "preserve_missing_evidence_as_abstention_context_not_comparison_blocker"
        ),
        "transformation_runtime_gap": (
            "preserve_raw_observation_gap_as_abstention_context_not_phase_support"
        ),
        "comparison_eligibility_gap": (
            "separate_candidate_disabled_governance_from_validation_only_abstention"
        ),
        "artifact_wiring_gap": (
            "remove_metric_and_backtest_scope_guards_from_label_comparison_blockers"
        ),
        "validation_fixture_gap": (
            "preserve_label_blind_fixture_boundary_as_nonblocking_governance_evidence"
        ),
    }
    return actions.get(classification, "preserve_as_genuine_unresolved_blocker")


def _genuine_evidence(code: str, classification: str) -> str:
    if classification == "point_in_time_input_gap":
        return "book-core major-group evidence remains incomplete and is treated as abstention context"
    if classification == "transformation_runtime_gap":
        return "raw observation is not promoted to phase support or phase-like label"
    if classification == "comparison_eligibility_gap":
        return "candidate output remains disabled while validation-only abstention may be compared as abstention"
    if classification == "artifact_wiring_gap":
        return "metric and backtest guards are scope controls, not evidence blockers"
    if classification == "validation_fixture_gap":
        return "historical labels remain prohibited from runtime and rule tuning"
    return f"{code} preserved as genuine unresolved limitation"


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 34 unblock output must be under /tmp: {output}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
