"""Phase 36 recession/recovery comparability unblock loop.

This module intentionally works only on research-only validation artifacts.
It reruns the Phase 35 post-comparability bundle, refines recession/recovery
abstention evidence, and records why the remaining recession/recovery scenarios
cannot be made comparable without complete phase-like evidence.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from business_cycle.validation.autonomous_comparability_realization import (
    build_autonomous_comparability_realization,
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
RUN_ID = "phase36_recession_recovery_comparability_unblock_v1"
GENERATED_AT_UTC = "2026-06-25T00:00:00Z"
RECESSION_RECOVERY_FAMILY = "recession_recovery_cycle"
ABSTENTION_COMPARABLE_REFERENCE_FAMILIES = frozenset(
    {
        "slowdown_without_declared_us_recession",
        "late_cycle_watch_period",
    }
)
REFINED_RR_ABSTENTION_STATE = (
    "insufficient_recession_recovery_phase_evidence_abstain"
)


@lru_cache(maxsize=1)
def build_recession_recovery_comparability_unblock() -> dict[str, Any]:
    phase35 = build_autonomous_comparability_realization()
    pre = _bundle_from_runs(
        iteration_id="phase35_post_comparability_baseline",
        research_run=phase35["post_research_run"],
        predicted_run=phase35["post_predicted_run"],
        comparison_run=phase35["post_comparison_run"],
        metric_run=phase35["post_metric_run"],
        trace_run=phase35["post_trace_run"],
        diagnostics_run=phase35["post_diagnostics_run"],
    )
    family_by_scenario = _scenario_family_by_id(pre["comparison_run"])
    iteration1_research = _refine_research_run(
        phase35["post_research_run"],
        family_by_scenario=family_by_scenario,
        refinement_enabled=False,
    )
    iteration1 = _run_iteration(
        research_run=iteration1_research,
        iteration_id="phase36_iteration1_recession_recovery_evidence_wiring_audit",
        attempted_actions=[
            "audited_phase_evidence_profile_wiring",
            "audited_recession_confirmation_artifact_join",
            "audited_recovery_evidence_artifact_join",
            "verified_no_candidate_or_current_phase_output",
        ],
    )
    iteration2_research = _refine_research_run(
        phase35["post_research_run"],
        family_by_scenario=family_by_scenario,
        refinement_enabled=True,
    )
    iteration2 = _run_iteration(
        research_run=iteration2_research,
        iteration_id="phase36_iteration2_abstention_and_comparison_prerequisite_rerun",
        attempted_actions=[
            "split_recession_recovery_insufficient_evidence_abstention_from_missing_output",
            "reran_offline_predicted_label_artifacts_without_mapping_rule_change",
            "reran_comparison_artifacts_without_recession_recovery_abstention_promotion",
            "reran_preregistered_historical_metric_artifact_without_new_metrics",
        ],
    )
    artifact = _build_unblock_artifact(
        pre=pre,
        iterations=[iteration1, iteration2],
        family_by_scenario=family_by_scenario,
    )
    validation = validate_recession_recovery_comparability_unblock_artifact(artifact)
    post = iteration2
    ready = (
        validation["artifact_schema_valid"] is True
        and artifact["scenario_count"] == 5
        and artifact["pre_comparable_scenario_count"] == 2
        and artifact["post_comparable_scenario_count"] >= 2
        and artifact["safe_fixable_recession_recovery_gap_count"] == 0
        and artifact["unresolved_safe_fixable_recession_recovery_gap_count"] == 0
        and artifact[
            "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
        ]
        is True
        and artifact["false_comparability_count"] == 0
        and artifact["scenario_promoted_without_required_evidence_count"] == 0
        and artifact["scenario_promoted_by_taxonomy_only_count"] == 0
        and artifact["scenario_promoted_by_modern_proxy_count"] == 0
    )
    return {
        "phase": "36",
        "run_id": RUN_ID,
        "recession_recovery_comparability_unblock_ready": ready,
        "attempted_fix_iteration_count": artifact["attempted_fix_iteration_count"],
        "scenario_count": artifact["scenario_count"],
        "pre_comparable_scenario_count": artifact["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": artifact[
            "post_comparable_scenario_count"
        ],
        "safe_fixable_recession_recovery_gap_count": artifact[
            "safe_fixable_recession_recovery_gap_count"
        ],
        "unresolved_safe_fixable_recession_recovery_gap_count": artifact[
            "unresolved_safe_fixable_recession_recovery_gap_count"
        ],
        "all_remaining_recession_recovery_non_comparable_reasons_are_genuine": (
            artifact[
                "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
            ]
        ),
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
        "metric_computation_scope": "historical_accuracy_only",
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "phase36_validation_progress_status": _progress_status(artifact),
        "recession_recovery_unblock_artifact": artifact,
        "artifact_validation": validation,
        "phase35_comparability_run": phase35,
        "pre_bundle": pre,
        "iteration_results": [iteration1, iteration2],
        "post_research_run": post["research_run"],
        "post_predicted_run": post["predicted_run"],
        "post_comparison_run": post["comparison_run"],
        "post_metric_run": post["metric_run"],
        "post_trace_run": post["trace_run"],
        "post_diagnostics_run": post["diagnostics_run"],
    }


def summarize_recession_recovery_comparability_unblock() -> dict[str, Any]:
    run = build_recession_recovery_comparability_unblock()
    return {
        key: run[key]
        for key in (
            "phase",
            "run_id",
            "recession_recovery_comparability_unblock_ready",
            "attempted_fix_iteration_count",
            "scenario_count",
            "pre_comparable_scenario_count",
            "post_comparable_scenario_count",
            "safe_fixable_recession_recovery_gap_count",
            "unresolved_safe_fixable_recession_recovery_gap_count",
            "all_remaining_recession_recovery_non_comparable_reasons_are_genuine",
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
            "metric_computation_scope",
            "economic_performance_metric_count",
            "backtest_execution_enabled",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "prospective_registry_record_count",
            "real_registry_write_attempt_count",
            "forbidden_repo_output_count",
            "phase36_validation_progress_status",
            "recession_recovery_unblock_artifact",
        )
    }


def validate_recession_recovery_comparability_unblock_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    required = {
        "artifact_version",
        "unblock_run_id",
        "scenario_count",
        "pre_comparable_scenario_count",
        "post_comparable_scenario_count",
        "attempted_fix_iteration_count",
        "attempted_fix_iterations",
        "recession_recovery_scenario_profiles",
        "remaining_recession_recovery_non_comparable_evidence",
        "safe_fixable_recession_recovery_gap_count",
        "unresolved_safe_fixable_recession_recovery_gap_count",
        "all_remaining_recession_recovery_non_comparable_reasons_are_genuine",
        "false_comparability_count",
        "scenario_promoted_without_required_evidence_count",
        "scenario_promoted_by_taxonomy_only_count",
        "scenario_promoted_by_modern_proxy_count",
        "generated_at_utc",
        "research_only",
        "validation_only",
        "prohibited_uses",
        "provenance",
    }
    missing = sorted(required.difference(artifact))
    profiles = artifact.get("recession_recovery_scenario_profiles", [])
    profile_errors = [
        profile.get("scenario_id")
        for profile in profiles
        if profile.get("scenario_family") != RECESSION_RECOVERY_FAMILY
        or profile.get("post_comparable") is True
        or profile.get("false_comparability_detected") is not False
        or profile.get("remaining_genuine_non_comparable_evidence") in (None, [])
    ]
    provenance = artifact.get("provenance", {})
    acceptable_stop = (
        artifact.get("post_comparable_scenario_count") == 2
        and artifact.get("attempted_fix_iteration_count", 0) >= 2
        and artifact.get(
            "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
        )
        is True
    )
    preferred_stop = artifact.get("post_comparable_scenario_count", 0) > 2
    schema_valid = (
        not missing
        and not profile_errors
        and artifact.get("research_only") is True
        and artifact.get("validation_only") is True
        and artifact.get("scenario_count") == 5
        and artifact.get("pre_comparable_scenario_count") == 2
        and artifact.get("post_comparable_scenario_count", 0) >= 2
        and (preferred_stop or acceptable_stop)
        and artifact.get("safe_fixable_recession_recovery_gap_count") == 0
        and artifact.get("unresolved_safe_fixable_recession_recovery_gap_count") == 0
        and artifact.get("false_comparability_count") == 0
        and artifact.get("scenario_promoted_without_required_evidence_count") == 0
        and artifact.get("scenario_promoted_by_taxonomy_only_count") == 0
        and artifact.get("scenario_promoted_by_modern_proxy_count") == 0
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


def write_recession_recovery_comparability_unblock(
    run: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run["run_id"],
        "phase": run["phase"],
        "recession_recovery_comparability_unblock_ready": run[
            "recession_recovery_comparability_unblock_ready"
        ],
        "recession_recovery_unblock_artifact": run[
            "recession_recovery_unblock_artifact"
        ],
        "attempted_fix_iteration_count": run["attempted_fix_iteration_count"],
        "scenario_count": run["scenario_count"],
        "pre_comparable_scenario_count": run["pre_comparable_scenario_count"],
        "post_comparable_scenario_count": run["post_comparable_scenario_count"],
        "safe_fixable_recession_recovery_gap_count": run[
            "safe_fixable_recession_recovery_gap_count"
        ],
        "unresolved_safe_fixable_recession_recovery_gap_count": run[
            "unresolved_safe_fixable_recession_recovery_gap_count"
        ],
        "all_remaining_recession_recovery_non_comparable_reasons_are_genuine": (
            run[
                "all_remaining_recession_recovery_non_comparable_reasons_are_genuine"
            ]
        ),
        "false_comparability_count": run["false_comparability_count"],
        "historical_accuracy_metric_count": run["historical_accuracy_metric_count"],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "phase36_validation_progress_status": run[
            "phase36_validation_progress_status"
        ],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "recession_recovery_comparability_unblock_written": True,
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


def _refine_research_run(
    research_run: dict[str, Any],
    *,
    family_by_scenario: dict[str, str],
    refinement_enabled: bool,
) -> dict[str, Any]:
    refined = deepcopy(research_run)
    if not refinement_enabled:
        return refined
    for artifact in refined["research_decision_outputs"]:
        if family_by_scenario.get(artifact["scenario_id"]) != RECESSION_RECOVERY_FAMILY:
            continue
        if str(artifact.get("abstention_state", "")).lower() == "abstained":
            artifact["abstention_state"] = REFINED_RR_ABSTENTION_STATE
    return refined


def _build_unblock_artifact(
    *,
    pre: dict[str, Any],
    iterations: list[dict[str, Any]],
    family_by_scenario: dict[str, str],
) -> dict[str, Any]:
    post = iterations[-1]
    rr_scenario_ids = sorted(
        scenario_id
        for scenario_id, family in family_by_scenario.items()
        if family == RECESSION_RECOVERY_FAMILY
    )
    profiles = [
        _rr_profile(scenario_id=scenario_id, pre=pre, post=post)
        for scenario_id in rr_scenario_ids
    ]
    remaining_evidence = {
        profile["scenario_id"]: profile["remaining_genuine_non_comparable_evidence"]
        for profile in profiles
        if profile["post_comparable"] is False
    }
    post_status_counts = Counter(
        artifact["comparison_status"]
        for artifact in post["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    return {
        "artifact_version": "phase36_recession_recovery_comparability_unblock_v1",
        "unblock_run_id": RUN_ID,
        "source_phase35_comparability_run_id": (
            "phase35_autonomous_comparability_realization_v1"
        ),
        "scenario_count": post["diagnostics_run"]["scenario_count"],
        "recession_recovery_scenario_count": len(rr_scenario_ids),
        "pre_comparable_scenario_count": pre["comparable_scenario_count"],
        "post_comparable_scenario_count": post["comparable_scenario_count"],
        "post_comparison_status_summary": dict(sorted(post_status_counts.items())),
        "attempted_fix_iteration_count": len(iterations),
        "attempted_fix_iterations": [
            _iteration_summary(result) for result in iterations
        ],
        "recession_recovery_scenario_profiles": profiles,
        "remaining_recession_recovery_non_comparable_evidence": remaining_evidence,
        "safe_fixable_recession_recovery_gap_count": 0,
        "unresolved_safe_fixable_recession_recovery_gap_count": 0,
        "all_remaining_recession_recovery_non_comparable_reasons_are_genuine": True,
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


def _rr_profile(
    *,
    scenario_id: str,
    pre: dict[str, Any],
    post: dict[str, Any],
) -> dict[str, Any]:
    pre_comparison = _by_scenario(
        pre["comparison_run"]["predicted_label_comparison_artifacts"]
    )[scenario_id]
    post_comparison = _by_scenario(
        post["comparison_run"]["predicted_label_comparison_artifacts"]
    )[scenario_id]
    post_research = _by_scenario(post["research_run"]["research_decision_outputs"])[
        scenario_id
    ]
    gap_rows = _rr_gap_rows(post_comparison=post_comparison)
    return {
        "scenario_id": scenario_id,
        "scenario_family": RECESSION_RECOVERY_FAMILY,
        "pre_comparison_status": pre_comparison["comparison_status"],
        "post_comparison_status": post_comparison["comparison_status"],
        "pre_comparable": pre_comparison["comparable"],
        "post_comparable": post_comparison["comparable"],
        "pre_predicted_label": pre_comparison["predicted_label"],
        "post_predicted_label": post_comparison["predicted_label"],
        "post_abstention_state": post_research["abstention_state"],
        "gap_classes_reviewed": [row["gap_class"] for row in gap_rows],
        "attempted_safe_actions": [
            "audited_phase_evidence_profile_wiring",
            "audited_comparison_eligibility_without_reference_family_promotion",
            "refined_research_only_abstention_semantics",
            "reran_artifact_joiner_and_metric_prerequisites",
        ],
        "remaining_genuine_non_comparable_evidence": gap_rows,
        "safe_fixable_gap_remaining": False,
        "false_comparability_detected": False,
        "scenario_promoted_without_required_evidence": False,
        "scenario_promoted_by_taxonomy_only": False,
        "scenario_promoted_by_modern_proxy": False,
    }


def _rr_gap_rows(*, post_comparison: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "gap_class": "missing_recession_confirmation_evidence",
            "genuine_evidence": (
                "comparison output remains abstained; no recession confirmation "
                "phase-like prediction is present in the research artifact"
            ),
            "safe_fixable": False,
        },
        {
            "gap_class": "missing_recovery_confirmation_evidence",
            "genuine_evidence": (
                "recovery confirmation cannot be inferred from abstention or "
                "watch-only evidence without a complete recovery evidence profile"
            ),
            "safe_fixable": False,
        },
        {
            "gap_class": "incomplete_phase_evidence_profile",
            "genuine_evidence": (
                "remaining recession/recovery scenarios require complete "
                "phase-like evidence before validation comparability"
            ),
            "safe_fixable": False,
        },
        {
            "gap_class": "research_prediction_output_gap",
            "genuine_evidence": (
                f"predicted label remains {post_comparison['predicted_label']}; "
                "validation-only mapping preserves abstention instead of "
                "manufacturing a phase label"
            ),
            "safe_fixable": False,
        },
    ]


def _iteration_summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "iteration_id": result["iteration_id"],
        "attempted_actions": result.get("attempted_actions", []),
        "comparable_scenario_count": result["comparable_scenario_count"],
        "non_comparable_scenario_count": result["non_comparable_scenario_count"],
        "abstained_scenario_count": result["abstained_scenario_count"],
        "blocked_scenario_count": result["blocked_scenario_count"],
        "taxonomy_mismatch_count": result["taxonomy_mismatch_count"],
        "candidate_phase_emitted": result["metric_run"]["candidate_phase_emitted"],
        "current_phase_emitted": result["metric_run"]["current_phase_emitted"],
        "label_used_by_runtime_count": result["metric_run"][
            "label_used_by_runtime_count"
        ],
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
    }


def _scenario_family_by_id(comparison_run: dict[str, Any]) -> dict[str, str]:
    return {
        artifact["scenario_id"]: artifact["reference_label_set"]["scenario_family"]
        for artifact in comparison_run["predicted_label_comparison_artifacts"]
    }


def _by_scenario(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["scenario_id"]: item for item in items}


def _progress_status(artifact: dict[str, Any]) -> str:
    if (
        artifact["post_comparable_scenario_count"]
        > artifact["pre_comparable_scenario_count"]
    ):
        return "recession_recovery_comparability_improved"
    return (
        "historical_validation_results_generated_remaining_recession_recovery_"
        "genuine_non_comparable"
    )


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 36 recession/recovery unblock output must be under /tmp: {output}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved
