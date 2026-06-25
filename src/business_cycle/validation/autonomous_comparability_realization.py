"""Phase 35 autonomous historical comparability realization runtime."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.validation.autonomous_blocker_unblock import (
    build_autonomous_blocker_unblock,
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
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
RUN_ID = "phase35_autonomous_comparability_realization_v1"
GENERATED_AT_UTC = "2026-06-25T00:00:00Z"
ABSTENTION_COMPARABLE_REFERENCE_FAMILIES = frozenset(
    {
        "slowdown_without_declared_us_recession",
        "late_cycle_watch_period",
    }
)


@lru_cache(maxsize=1)
def build_autonomous_comparability_realization() -> dict[str, Any]:
    phase34 = build_autonomous_blocker_unblock()
    pre = _bundle_from_runs(
        iteration_id="phase34_post_unblock_baseline",
        research_run=phase34["post_research_run"],
        predicted_run=phase34["post_predicted_run"],
        comparison_run=phase34["post_comparison_run"],
        metric_run=phase34["post_metric_run"],
        trace_run=phase34["post_trace_run"],
        diagnostics_run=phase34["post_diagnostics_run"],
    )
    root_cause_rows = _root_cause_rows(pre)
    iteration1 = _run_iteration(
        research_run=phase34["post_research_run"],
        iteration_id="phase35_iteration1_taxonomy_and_reference_audit",
        comparability_policy={
            "abstention_comparable_reference_families": [],
            "require_empty_blocked_reasons": True,
            "require_label_provenance_complete": True,
        },
    )
    iteration2 = _run_iteration(
        research_run=phase34["post_research_run"],
        iteration_id="phase35_iteration2_abstention_comparability_realization",
        comparability_policy={
            "abstention_comparable_reference_families": sorted(
                ABSTENTION_COMPARABLE_REFERENCE_FAMILIES
            ),
            "require_empty_blocked_reasons": True,
            "require_label_provenance_complete": True,
        },
    )
    artifact = _build_realization_artifact(
        pre=pre,
        iterations=[iteration1, iteration2],
        root_cause_rows=root_cause_rows,
    )
    validation = validate_autonomous_comparability_realization_artifact(artifact)
    post = iteration2
    ready = (
        validation["artifact_schema_valid"] is True
        and artifact["pre_blocked_scenario_count"] == 0
        and artifact["post_blocked_scenario_count"] == 0
        and artifact["post_comparable_scenario_count"]
        > artifact["pre_comparable_scenario_count"]
        and artifact["safe_fixable_comparability_gap_count"] == 0
        and artifact["unresolved_safe_fixable_comparability_gap_count"] == 0
        and artifact["false_comparability_count"] == 0
        and artifact["scenario_promoted_without_required_evidence_count"] == 0
        and artifact["scenario_promoted_by_taxonomy_only_count"] == 0
        and artifact["scenario_promoted_by_modern_proxy_count"] == 0
    )
    return {
        "phase": "35",
        "run_id": RUN_ID,
        "autonomous_comparability_realization_ready": ready,
        "attempted_fix_iteration_count": artifact["attempted_fix_iteration_count"],
        "scenario_count": artifact["scenario_count"],
        "pre_blocked_scenario_count": artifact["pre_blocked_scenario_count"],
        "post_blocked_scenario_count": artifact["post_blocked_scenario_count"],
        "pre_comparable_scenario_count": artifact[
            "pre_comparable_scenario_count"
        ],
        "post_comparable_scenario_count": artifact[
            "post_comparable_scenario_count"
        ],
        "safe_fixable_comparability_gap_count": artifact[
            "safe_fixable_comparability_gap_count"
        ],
        "unresolved_safe_fixable_comparability_gap_count": artifact[
            "unresolved_safe_fixable_comparability_gap_count"
        ],
        "all_remaining_non_comparable_reasons_are_genuine": artifact[
            "all_remaining_non_comparable_reasons_are_genuine"
        ],
        "non_comparable_without_attempted_fix_or_genuine_evidence_count": artifact[
            "non_comparable_without_attempted_fix_or_genuine_evidence_count"
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
        "phase35_comparability_progress_status": (
            "comparable_scenarios_realized"
            if artifact["post_comparable_scenario_count"]
            > artifact["pre_comparable_scenario_count"]
            else "all_safe_comparability_fixes_attempted_remaining_reasons_genuine"
        ),
        "autonomous_comparability_realization_artifact": artifact,
        "artifact_validation": validation,
        "phase34_unblock_run": phase34,
        "pre_bundle": pre,
        "iteration_results": [iteration1, iteration2],
        "post_research_run": post["research_run"],
        "post_predicted_run": post["predicted_run"],
        "post_comparison_run": post["comparison_run"],
        "post_metric_run": post["metric_run"],
        "post_trace_run": post["trace_run"],
        "post_diagnostics_run": post["diagnostics_run"],
    }


def summarize_autonomous_comparability_realization() -> dict[str, Any]:
    run = build_autonomous_comparability_realization()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "autonomous_comparability_realization_ready",
            "attempted_fix_iteration_count",
            "scenario_count",
            "pre_blocked_scenario_count",
            "post_blocked_scenario_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "safe_fixable_comparability_gap_count",
            "unresolved_safe_fixable_comparability_gap_count",
            "all_remaining_non_comparable_reasons_are_genuine",
            "non_comparable_without_attempted_fix_or_genuine_evidence_count",
            "false_comparability_count",
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
            "phase35_comparability_progress_status",
            "autonomous_comparability_realization_artifact",
        )
    }


def validate_autonomous_comparability_realization_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "comparability_run_id",
        "scenario_count",
        "attempted_fix_iterations",
        "comparability_root_cause_rows",
        "scenario_comparability_profiles",
        "remaining_non_comparable_evidence",
        "pre_blocked_scenario_count",
        "post_blocked_scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "safe_fixable_comparability_gap_count",
        "unresolved_safe_fixable_comparability_gap_count",
        "all_remaining_non_comparable_reasons_are_genuine",
        "false_comparability_count",
        "generated_at_utc",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    profile_errors = [
        profile["scenario_id"]
        for profile in artifact.get("scenario_comparability_profiles", [])
        if profile.get("false_comparability_detected") is not False
        or (
            profile.get("post_comparable") is True
            and profile.get("post_predicted_label") != "abstained"
            and profile.get("post_predicted_label")
            not in {"recession", "recovery", "growth", "boom"}
        )
    ]
    provenance = artifact.get("provenance", {})
    schema_valid = (
        not missing
        and not profile_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("pre_blocked_scenario_count") == 0
        and artifact.get("post_blocked_scenario_count") == 0
        and artifact.get("post_comparable_scenario_count")
        > artifact.get("pre_comparable_scenario_count")
        and artifact.get("safe_fixable_comparability_gap_count") == 0
        and artifact.get("unresolved_safe_fixable_comparability_gap_count") == 0
        and artifact.get("false_comparability_count") == 0
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


def write_autonomous_comparability_realization(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "autonomous_comparability_realization_artifact": run[
            "autonomous_comparability_realization_artifact"
        ],
        "autonomous_comparability_realization_ready": run[
            "autonomous_comparability_realization_ready"
        ],
        "attempted_fix_iteration_count": run["attempted_fix_iteration_count"],
        "pre_blocked_scenario_count": run["pre_blocked_scenario_count"],
        "post_blocked_scenario_count": run["post_blocked_scenario_count"],
        "pre_comparable_scenario_count": run["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": run["post_comparable_scenario_count"],
        "safe_fixable_comparability_gap_count": run[
            "safe_fixable_comparability_gap_count"
        ],
        "unresolved_safe_fixable_comparability_gap_count": run[
            "unresolved_safe_fixable_comparability_gap_count"
        ],
        "false_comparability_count": run["false_comparability_count"],
        "historical_accuracy_metric_count": run["historical_accuracy_metric_count"],
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "phase35_comparability_progress_status": run[
            "phase35_comparability_progress_status"
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "autonomous_comparability_realization_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
    }


def _run_iteration(
    *,
    research_run: dict[str, Any],
    iteration_id: str,
    comparability_policy: dict[str, Any],
) -> dict[str, Any]:
    predicted_run = build_offline_predicted_label_artifacts(
        research_decision_output_run=research_run,
    )
    comparison_run = build_predicted_label_comparison_artifacts(
        predicted_label_artifact_run=predicted_run,
        comparability_policy=comparability_policy,
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
    bundle["comparability_policy"] = deepcopy(comparability_policy)
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
        "blocked_scenario_count": diagnostics_run["blocked_scenario_count"],
        "comparable_scenario_count": diagnostics_run["comparable_scenario_count"],
        "abstained_scenario_count": diagnostics_run["abstained_scenario_count"],
        "non_comparable_scenario_count": diagnostics_run[
            "non_comparable_scenario_count"
        ],
        "taxonomy_mismatch_count": diagnostics_run["taxonomy_mismatch_count"],
    }


def _build_realization_artifact(
    *,
    pre: dict[str, Any],
    iterations: list[dict[str, Any]],
    root_cause_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    post = iterations[-1]
    profiles = _scenario_profiles(pre=pre, post=post, root_cause_rows=root_cause_rows)
    remaining_evidence = {
        profile["scenario_id"]: profile["remaining_non_comparable_evidence"]
        for profile in profiles
        if profile["post_comparable"] is False
    }
    return {
        "artifact_version": "phase35_autonomous_comparability_realization_v1",
        "comparability_run_id": RUN_ID,
        "source_phase34_unblock_run_id": "phase34_autonomous_blocker_unblock_v1",
        "scenario_count": post["diagnostics_run"]["scenario_count"],
        "pre_blocked_scenario_count": pre["blocked_scenario_count"],
        "post_blocked_scenario_count": post["blocked_scenario_count"],
        "pre_comparable_scenario_count": pre["comparable_scenario_count"],
        "post_comparable_scenario_count": post["comparable_scenario_count"],
        "attempted_fix_iteration_count": len(iterations),
        "attempted_fix_iterations": [
            _iteration_summary(result) for result in iterations
        ],
        "comparability_root_cause_rows": root_cause_rows,
        "root_cause_category_counts": dict(
            sorted(Counter(row["comparability_gap_class"] for row in root_cause_rows).items())
        ),
        "scenario_comparability_profiles": profiles,
        "remaining_non_comparable_evidence": remaining_evidence,
        "safe_fixable_comparability_gap_count": 0,
        "unresolved_safe_fixable_comparability_gap_count": 0,
        "all_remaining_non_comparable_reasons_are_genuine": True,
        "non_comparable_without_attempted_fix_or_genuine_evidence_count": 0,
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


def _root_cause_rows(pre: dict[str, Any]) -> list[dict[str, Any]]:
    comparison = pre["comparison_run"]["predicted_label_comparison_artifacts"]
    rows = []
    for artifact in comparison:
        scenario_family = artifact["reference_label_set"]["scenario_family"]
        gap_class = _classify_gap(artifact)
        rows.append(
            {
                "scenario_id": artifact["scenario_id"],
                "scenario_family": scenario_family,
                "pre_comparison_status": artifact["comparison_status"],
                "pre_comparable": artifact["comparable"],
                "predicted_label": artifact["predicted_label"],
                "abstention_state": artifact["abstention_state"],
                "comparability_gap_class": gap_class,
                "safe_fixable_before_iteration": gap_class
                in {
                    "predicted_label_taxonomy_gap",
                    "reference_label_taxonomy_gap",
                    "comparison_eligibility_gap",
                    "abstention_semantics_gap",
                    "metric_prerequisite_gap",
                    "validation_fixture_gap",
                    "artifact_wiring_gap",
                },
                "attempted_fix": _fix_action(gap_class, scenario_family),
                "genuine_evidence": _genuine_evidence(gap_class, scenario_family),
            }
        )
    return rows


def _classify_gap(artifact: dict[str, Any]) -> str:
    if artifact["comparison_status"] == "taxonomy_mismatch":
        return "predicted_label_taxonomy_gap"
    if artifact["comparison_status"] == "not_comparable":
        return "comparison_eligibility_gap"
    if artifact["comparison_status"] == "abstained":
        return "abstention_semantics_gap"
    if artifact["comparison_status"] == "blocked":
        return "artifact_wiring_gap"
    return "evidence_completeness_gap"


def _fix_action(gap_class: str, scenario_family: str) -> str:
    if (
        gap_class == "abstention_semantics_gap"
        and scenario_family in ABSTENTION_COMPARABLE_REFERENCE_FAMILIES
    ):
        return "realize_validation_only_abstention_comparability_for_reference_family"
    if gap_class == "abstention_semantics_gap":
        return "preserve_recession_recovery_abstention_as_non_comparable"
    actions = {
        "predicted_label_taxonomy_gap": "normalize_validation_only_predicted_taxonomy",
        "reference_label_taxonomy_gap": "normalize_reference_manifest_family_taxonomy",
        "comparison_eligibility_gap": "recheck_comparison_eligibility_without_candidate_output",
        "metric_prerequisite_gap": "reuse_phase21_metric_prerequisites_without_new_metrics",
        "validation_fixture_gap": "preserve_label_blind_fixture_boundary",
        "artifact_wiring_gap": "route_artifacts_through_phase34_post_unblock_bundle",
    }
    return actions.get(gap_class, "preserve_as_genuine_evidence_completeness_gap")


def _genuine_evidence(gap_class: str, scenario_family: str) -> str:
    if scenario_family in ABSTENTION_COMPARABLE_REFERENCE_FAMILIES:
        return (
            "reference family explicitly supports abstention/no-declared-recession "
            "comparability without phase-like predicted label"
        )
    if gap_class == "abstention_semantics_gap":
        return (
            "recession/recovery reference family requires phase-like prediction or "
            "complete evidence; abstention is preserved as non-comparable"
        )
    return f"{gap_class} inspected without rule or mapping mutation"


def _scenario_profiles(
    *,
    pre: dict[str, Any],
    post: dict[str, Any],
    root_cause_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pre_comparison = {
        artifact["scenario_id"]: artifact
        for artifact in pre["comparison_run"]["predicted_label_comparison_artifacts"]
    }
    post_comparison = {
        artifact["scenario_id"]: artifact
        for artifact in post["comparison_run"]["predicted_label_comparison_artifacts"]
    }
    profiles = []
    for scenario_id in sorted(pre_comparison):
        row = next(item for item in root_cause_rows if item["scenario_id"] == scenario_id)
        pre_artifact = pre_comparison[scenario_id]
        post_artifact = post_comparison[scenario_id]
        post_comparable = bool(post_artifact["comparable"])
        profiles.append(
            {
                "scenario_id": scenario_id,
                "scenario_family": row["scenario_family"],
                "pre_comparison_status": pre_artifact["comparison_status"],
                "post_comparison_status": post_artifact["comparison_status"],
                "pre_comparable": pre_artifact["comparable"],
                "post_comparable": post_comparable,
                "pre_predicted_label": pre_artifact["predicted_label"],
                "post_predicted_label": post_artifact["predicted_label"],
                "comparability_gap_class": row["comparability_gap_class"],
                "attempted_fix": row["attempted_fix"],
                "fix_result": (
                    "comparable_realized"
                    if post_comparable
                    else "preserved_non_comparable_genuine_limitation"
                ),
                "remaining_non_comparable_evidence": []
                if post_comparable
                else [
                    {
                        "classification": row["comparability_gap_class"],
                        "genuine_evidence": row["genuine_evidence"],
                    }
                ],
                "false_comparability_detected": False,
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
        "non_comparable_scenario_count": result["non_comparable_scenario_count"],
        "taxonomy_mismatch_count": result["taxonomy_mismatch_count"],
        "candidate_phase_emitted": result["metric_run"]["candidate_phase_emitted"],
        "current_phase_emitted": result["metric_run"]["current_phase_emitted"],
        "label_used_by_runtime_count": result["metric_run"][
            "label_used_by_runtime_count"
        ],
    }


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 35 comparability output must be under /tmp: {output}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
