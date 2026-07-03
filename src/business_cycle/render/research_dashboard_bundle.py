"""Phase 38 research validation dashboard bundle builder."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.qa12_major_group_manual_start_closure import (
    summarize_qa12_major_group_manual_start_closure,
)
from business_cycle.render.phase_evidence_view_models import (
    build_data_lineage_view_model,
    build_indicator_explorer_view_model,
    build_phase_analysis_view_model,
    build_transition_risk_view_model,
)
from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
)
from business_cycle.render.boom_to_recession_transition_surface import (
    build_boom_to_recession_transition_surface_view_model,
)
from business_cycle.render.ordered_cycle_transition_lane_templates import (
    build_full_ordered_cycle_transition_lane_template_view_model,
)
from business_cycle.render.evidence_freshness_release_value_continuity import (
    build_evidence_freshness_release_value_continuity_view_model,
)
from business_cycle.render.major_group_evidence_profile_readiness import (
    build_major_group_evidence_profile_readiness_view_model,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)
from business_cycle.validation.post_pit_remediation_validation_rerun import (
    build_post_pit_remediation_validation_rerun,
)
from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    summarize_recession_recovery_pit_gap_matrix,
)


DEFAULT_DASHBOARD_CONTRACT_PATH = Path(
    "specs/common/research_validation_dashboard_contract.yaml"
)
DEFAULT_SCENARIO_MANIFEST_PATH = Path(
    "specs/audits/historical_validation_scenario_manifest.yaml"
)
ALPHA34_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha34_recession_recovery_pit_remediation_freeze.yaml"
)
ALPHA33_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha33_recession_recovery_evidence_completion_freeze.yaml"
)
GENERATED_AT_UTC = "2026-06-26T00:00:00Z"
SCHEMA_VERSION = "phase38_research_dashboard_v1"
FREEZE_ID = "book_faithful_shadow_v2_alpha35"
PARENT_FREEZE_ID = "book_faithful_shadow_v2_alpha34"
COMPARABLE_SCENARIO_IDS = (
    "euro_debt_slowdown_2011_2012",
    "late_cycle_2018_2019",
)
NON_COMPARABLE_SCENARIO_IDS = (
    "dotcom_cycle_2000_2003",
    "global_financial_crisis_2007_2009",
    "covid_recession_2020",
)
VIEW_IDS = (
    "research_overview",
    "historical_scenarios",
    "validation_results",
    "evidence_explorer",
    "data_lineage_governance",
    "pit_gap_view",
    "scenario_detail",
)
CURRENT_SNAPSHOT_VIEW_ID = "current_research_snapshot"
BOOM_TRANSITION_VIEW_ID = "declared_boom_transition_monitor"
MACRO_COVERAGE_VIEW_ID = "macro_indicator_coverage_readiness"
INDICATOR_DETAIL_VIEW_ID = "indicator_detail_source_risk_value_cards"
BOOM_TO_RECESSION_COMPLETION_VIEW_ID = "boom_to_recession_transition_surface_completion"
ORDERED_CYCLE_TRANSITION_TEMPLATES_VIEW_ID = (
    "full_ordered_cycle_transition_lane_templates"
)
EVIDENCE_FRESHNESS_RELEASE_VALUE_CONTINUITY_VIEW_ID = (
    "evidence_freshness_release_value_continuity"
)
MAJOR_GROUP_EVIDENCE_PROFILE_READINESS_VIEW_ID = (
    "major_group_evidence_profile_readiness"
)
INDICATOR_DASHBOARD_EXPLANATION_DRILLDOWN_VIEW_ID = (
    "indicator_dashboard_explanation_drilldown"
)
TRANSITION_TIMING_REPLAY_PREVIEW_VIEW_ID = "transition_timing_replay_preview"
PROHIBITED_ACTION_FIELDS = {
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
    "guaranteed_return",
    "portfolio_return",
    "sharpe",
    "drawdown",
    "production_phase",
}


def load_research_validation_dashboard_contract(
    path: str | Path = DEFAULT_DASHBOARD_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("research validation dashboard contract must map")
    contract = payload.get("research_validation_dashboard_contract")
    if not isinstance(contract, dict):
        raise ValueError("research_validation_dashboard_contract must be a mapping")
    return contract


def build_research_dashboard_bundle(
    *,
    current_snapshot: dict[str, Any] | None = None,
    boom_transition_surface: dict[str, Any] | None = None,
    boom_to_recession_transition_surface: dict[str, Any] | None = None,
    ordered_cycle_transition_lane_templates: dict[str, Any] | None = None,
    evidence_freshness_release_value_continuity: dict[str, Any] | None = None,
    major_group_evidence_profile_readiness: dict[str, Any] | None = None,
    indicator_dashboard_explanation_drilldown: dict[str, Any] | None = None,
    transition_timing_replay_preview: dict[str, Any] | None = None,
    macro_coverage_matrix: dict[str, Any] | None = None,
    indicator_detail_cards: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = load_research_validation_dashboard_contract()
    run = build_post_pit_remediation_validation_rerun()
    matrix = run["remediation_run"]["pit_gap_matrix"]
    matrix_summary = summarize_recession_recovery_pit_gap_matrix()
    scenario_manifest = _load_scenario_manifest()
    scenarios = _scenario_summaries(run=run, scenario_manifest=scenario_manifest)
    comparable = [item for item in scenarios if item["comparable"] is True]
    non_comparable = [item for item in scenarios if item["comparable"] is False]
    evidence_rows = _evidence_summaries(matrix)
    pit_rows = _pit_gap_rows(matrix)
    metrics = _metric_summaries(run["metric_run"]["metric_results"])
    alpha34 = _lightweight_alpha34_lineage_summary()
    qa12 = summarize_qa12_major_group_manual_start_closure()
    comparison_status_counts = Counter(
        scenario["comparison_status"] for scenario in scenarios
    )
    view_ids = _view_ids(
        current_snapshot=current_snapshot,
        boom_transition_surface=boom_transition_surface,
        boom_to_recession_transition_surface=boom_to_recession_transition_surface,
        ordered_cycle_transition_lane_templates=ordered_cycle_transition_lane_templates,
        evidence_freshness_release_value_continuity=(
            evidence_freshness_release_value_continuity
        ),
        major_group_evidence_profile_readiness=(
            major_group_evidence_profile_readiness
        ),
        indicator_dashboard_explanation_drilldown=(
            indicator_dashboard_explanation_drilldown
        ),
        transition_timing_replay_preview=transition_timing_replay_preview,
        macro_coverage_matrix=macro_coverage_matrix,
        indicator_detail_cards=indicator_detail_cards,
    )
    bundle = {
        "dashboard_schema_version": SCHEMA_VERSION,
        "generated_at": GENERATED_AT_UTC,
        "output_mode": "research_only",
        "model_id": FREEZE_ID,
        "freeze_id": FREEZE_ID,
        "parent_freeze_id": PARENT_FREEZE_ID,
        "data_mode": "vintage_as_of",
        "scenario_count": len(scenarios),
        "comparable_scenario_count": len(comparable),
        "non_comparable_scenario_count": len(non_comparable),
        "comparable_scenario_ids": [item["scenario_id"] for item in comparable],
        "non_comparable_scenario_ids": [
            item["scenario_id"] for item in non_comparable
        ],
        "dashboard_view_count": len(view_ids),
        "views": [{"view_id": view_id, "title": _view_title(view_id)} for view_id in view_ids],
        "scenarios": scenarios,
        "evidence_summaries": evidence_rows,
        "comparison_summaries": {
            "status_counts": dict(sorted(comparison_status_counts.items())),
            "artifact_count": run["comparison_run"][
                "label_comparison_artifact_count"
            ],
            "label_comparison_executed": True,
            "label_used_by_runtime_count": run["comparison_run"][
                "label_used_by_runtime_count"
            ],
        },
        "historical_metric_summaries": metrics,
        "pit_readiness_summaries": {
            "pre_insufficient_point_in_time_role_gap_count": run[
                "pre_insufficient_point_in_time_role_gap_count"
            ],
            "post_insufficient_point_in_time_role_gap_count": run[
                "post_insufficient_point_in_time_role_gap_count"
            ],
            "cache_remediated_pit_role_gap_count": matrix_summary[
                "cache_remediated_pit_role_gap_count"
            ],
            "official_history_insufficient_gap_count": matrix_summary[
                "official_history_insufficient_gap_count"
            ],
            "genuine_source_unavailable_gap_count": matrix_summary[
                "genuine_source_unavailable_gap_count"
            ],
            "rule_unresolved_gap_count": matrix_summary["rule_unresolved_gap_count"],
            "pit_gap_rows": pit_rows,
        },
        "blocker_summaries": {
            "remaining_non_comparable_scenario_ids": run["remediation_run"][
                "remaining_non_comparable_scenario_ids"
            ],
            "blockage_reason_summary": run["diagnostics_run"][
                "blockage_diagnostics_artifact"
            ]["blockage_reason_summary"],
            "abstention_reason_summary": run["diagnostics_run"][
                "blockage_diagnostics_artifact"
            ]["abstention_reason_summary"],
            "metric_skip_reason_summary": run["diagnostics_run"][
                "blockage_diagnostics_artifact"
            ]["metric_skip_reason_summary"],
        },
        "lineage_summaries": {
            "freeze_id": FREEZE_ID,
            "parent_freeze_id": PARENT_FREEZE_ID,
            "parent_freeze_hash": alpha34["freeze_manifest_hash"],
            "alpha34_parent_preserved": alpha34["alpha33_parent_preserved"],
            "qa12_freeze_unchanged": qa12["manual_start_freeze_ready"] is True,
            "qa12_recommended_next_action": qa12["recommended_next_action"],
            "prospective_registry_record_count": qa12["real_registry_record_count"],
            "real_registry_write_attempt_count": qa12[
                "real_registry_write_attempt_count"
            ],
            "production_behavior_change_count": 0,
        },
        "phase_evidence_view_models": {
            "phase_analysis": build_phase_analysis_view_model(),
            "transition_risk": build_transition_risk_view_model(),
            "indicator_explorer": build_indicator_explorer_view_model(),
            "data_lineage": build_data_lineage_view_model(),
        },
        "allowed_uses": [
            "local_research_dashboard",
            "historical_validation_diagnostics",
            "evidence_review",
            "lineage_review",
        ],
        "prohibited_uses": [
            "production_decision",
            "candidate_or_current_phase_selection",
            "portfolio_or_trade_decision",
            "economic_validation_claim",
            "public_output",
        ],
        "caveats": [
            "research-only local dashboard",
            "partial comparability: two comparable and three not comparable scenarios",
            "economic performance metrics are not computed",
            "candidate and current phase outputs remain disabled",
            "production dashboard remains isolated",
        ],
        "trust_metadata": {
            "data_last_updated_at": GENERATED_AT_UTC,
            "data_completeness": "partial_comparability",
            "stale_or_missing_status": "explicit_pit_and_rule_gaps",
            "model_version": FREEZE_ID,
            "freeze_id": FREEZE_ID,
            "validation_status": (
                "research_dashboard_available_partial_comparability_no_performance"
            ),
            "output_label": "research_only",
            "allowed_uses": ["local_research_dashboard", "diagnostics"],
            "prohibited_uses": [
                "production_decision",
                "portfolio_or_trade_decision",
                "economic_validation_claim",
            ],
        },
        "safety_counters": {
            "economic_performance_metric_count": run[
                "economic_performance_metric_count"
            ],
            "candidate_output_emitted": False,
            "current_output_emitted": False,
            "label_used_by_runtime_count": run["label_used_by_runtime_count"],
            "production_behavior_change_count": 0,
            "prospective_registry_record_count": 0,
            "real_registry_write_attempt_count": 0,
        },
        "source_runs": {
            "phase37_post_pit": run["run_id"],
            "phase37_pit_remediation": run["remediation_run"]["run_id"],
            "phase37_pit_gap_matrix": matrix["run_id"],
        },
        "contract": contract,
    }
    if current_snapshot is not None:
        bundle["current_snapshot"] = current_snapshot
        bundle["source_runs"]["phase39_current_snapshot"] = current_snapshot[
            "artifact_schema_version"
        ]
        if str(current_snapshot["artifact_schema_version"]).startswith("phase40"):
            bundle["source_runs"]["phase40_current_data_refresh"] = current_snapshot[
                "refresh_metadata"
            ].get("refresh_manifest_hash")
    if boom_transition_surface is not None:
        bundle["boom_transition_dashboard"] = boom_transition_surface
        bundle["source_runs"]["phase49_boom_transition_dashboard"] = (
            boom_transition_surface["surface_id"]
        )
    if boom_to_recession_transition_surface is not None:
        bundle["boom_to_recession_transition_surface_completion"] = (
            boom_to_recession_transition_surface
        )
        bundle["source_runs"]["phase57_boom_to_recession_transition_surface"] = (
            boom_to_recession_transition_surface["view_id"]
        )
    if ordered_cycle_transition_lane_templates is not None:
        bundle["full_ordered_cycle_transition_lane_templates"] = (
            ordered_cycle_transition_lane_templates
        )
        bundle["source_runs"]["phase58_ordered_cycle_transition_lane_templates"] = (
            ordered_cycle_transition_lane_templates["view_id"]
        )
    if evidence_freshness_release_value_continuity is not None:
        bundle["evidence_freshness_release_value_continuity"] = (
            evidence_freshness_release_value_continuity
        )
        bundle["source_runs"]["phase60_evidence_freshness_release_value_continuity"] = (
            evidence_freshness_release_value_continuity["view_id"]
        )
    if major_group_evidence_profile_readiness is not None:
        bundle["major_group_evidence_profile_readiness"] = (
            major_group_evidence_profile_readiness
        )
        bundle["source_runs"]["phase61_major_group_evidence_profile_readiness"] = (
            major_group_evidence_profile_readiness["view_id"]
        )
    if indicator_dashboard_explanation_drilldown is not None:
        bundle["indicator_dashboard_explanation_drilldown"] = (
            indicator_dashboard_explanation_drilldown
        )
        bundle["source_runs"]["phase62_indicator_dashboard_explanation_drilldown"] = (
            indicator_dashboard_explanation_drilldown["view_id"]
        )
    if transition_timing_replay_preview is not None:
        bundle["transition_timing_replay_preview"] = transition_timing_replay_preview
        bundle["source_runs"]["phase67_transition_timing_replay_preview"] = (
            transition_timing_replay_preview["view_id"]
        )
    if macro_coverage_matrix is not None:
        bundle["macro_indicator_coverage_readiness"] = macro_coverage_matrix
        bundle["source_runs"]["phase55_macro_indicator_coverage_readiness"] = (
            macro_coverage_matrix["view_id"]
        )
    if indicator_detail_cards is not None:
        bundle["indicator_detail_source_risk_value_cards"] = indicator_detail_cards
        bundle["source_runs"]["phase56_indicator_detail_source_risk_values"] = (
            indicator_detail_cards["view_id"]
        )
    validation = validate_research_dashboard_bundle(bundle, contract=contract)
    bundle["artifact_consistency"] = validation
    return bundle


def _lightweight_alpha34_lineage_summary() -> dict[str, Any]:
    freeze = yaml.safe_load(ALPHA34_FREEZE_PATH.read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha34_recession_recovery_pit_remediation_freeze"
    ]
    component_paths = [Path(item) for item in freeze["component_paths"]]
    source_paths = [Path(item) for item in freeze["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in all_paths
        if item.exists()
    }
    freeze_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode()
    ).hexdigest()
    return {
        "freeze_manifest_hash": freeze_hash,
        "alpha33_parent_preserved": (
            not missing
            and ALPHA33_FREEZE_PATH.exists()
            and freeze["parent_freeze_id"] == "book_faithful_shadow_v2_alpha33"
        ),
    }


def summarize_research_dashboard_bundle() -> dict[str, Any]:
    bundle = build_research_dashboard_bundle()
    validation = bundle["artifact_consistency"]
    return {
        "research_dashboard_contract_ready": validate_research_dashboard_contract(
            bundle["contract"]
        )["contract_schema_valid"],
        "research_dashboard_bundle_ready": validation["bundle_schema_valid"],
        "dashboard_view_count": bundle["dashboard_view_count"],
        "scenario_count": bundle["scenario_count"],
        "comparable_scenario_count": bundle["comparable_scenario_count"],
        "non_comparable_scenario_count": bundle["non_comparable_scenario_count"],
        "comparable_scenario_ids": bundle["comparable_scenario_ids"],
        "non_comparable_scenario_ids": bundle["non_comparable_scenario_ids"],
        "remaining_pit_role_gap_count": bundle["pit_readiness_summaries"][
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "rule_unresolved_gap_count": bundle["pit_readiness_summaries"][
            "rule_unresolved_gap_count"
        ],
        "historical_accuracy_metric_registry_count": len(
            bundle["historical_metric_summaries"]
        ),
        "economic_performance_metric_count": bundle["safety_counters"][
            "economic_performance_metric_count"
        ],
        "artifact_consistency_error_count": validation[
            "artifact_consistency_error_count"
        ],
        "missing_trust_metadata_count": validation["missing_trust_metadata_count"],
        "prohibited_action_field_count": validation["prohibited_action_field_count"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "label_used_by_runtime_count": bundle["safety_counters"][
            "label_used_by_runtime_count"
        ],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "current_dashboard_view_ready": bool(bundle.get("current_snapshot"))
        and bundle["dashboard_view_count"] >= 8,
        "current_snapshot_artifact_count": int(bool(bundle.get("current_snapshot"))),
        "boom_transition_dashboard_view_ready": bool(
            bundle.get("boom_transition_dashboard")
        )
        and bundle["dashboard_view_count"] >= 8,
        "boom_transition_dashboard_artifact_count": int(
            bool(bundle.get("boom_transition_dashboard"))
        ),
        "bundle": bundle,
    }


def validate_research_dashboard_contract(contract: dict[str, Any]) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "dashboard_schema_version",
        "output_mode",
        "required_views",
        "allowed_inputs",
        "prohibited_inputs",
        "required_bundle_fields",
        "prohibited_dashboard_fields",
        "prohibited_claims",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    output = contract.get("output_policy", {})
    guards = contract.get("disabled_runtime_guards", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "local_research_dashboard_allowed_no_public_output"
        and contract.get("output_mode") == "research_only"
        and len(contract.get("required_views", [])) >= 7
        and output.get("tmp_output_required") is True
        and output.get("public_output_allowed") is False
        and output.get("remote_assets_allowed") is False
        and all(value is False for value in guards.values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_research_dashboard_bundle(
    bundle: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_research_validation_dashboard_contract()
    missing_fields = [
        field for field in contract["required_bundle_fields"] if field not in bundle
    ]
    consistency_errors: list[str] = []
    if bundle.get("scenario_count") != 5:
        consistency_errors.append("scenario_count")
    if bundle.get("comparable_scenario_count") != 2:
        consistency_errors.append("comparable_scenario_count")
    if bundle.get("non_comparable_scenario_count") != 3:
        consistency_errors.append("non_comparable_scenario_count")
    if tuple(bundle.get("comparable_scenario_ids", ())) != COMPARABLE_SCENARIO_IDS:
        consistency_errors.append("comparable_scenario_ids")
    if tuple(bundle.get("non_comparable_scenario_ids", ())) != NON_COMPARABLE_SCENARIO_IDS:
        consistency_errors.append("non_comparable_scenario_ids")
    pit = bundle.get("pit_readiness_summaries", {})
    if pit.get("post_insufficient_point_in_time_role_gap_count") != 6:
        consistency_errors.append("remaining_pit_role_gap_count")
    if pit.get("rule_unresolved_gap_count") != 1:
        consistency_errors.append("rule_unresolved_gap_count")
    if len(bundle.get("historical_metric_summaries", [])) != 5:
        consistency_errors.append("historical_metric_registry_count")
    if bundle.get("safety_counters", {}).get("economic_performance_metric_count") != 0:
        consistency_errors.append("economic_performance_metric_count")
    trust_missing = 0 if bundle.get("trust_metadata") else 1
    prohibited_count = _contains_prohibited_action_field(bundle)
    schema_valid = (
        not missing_fields
        and not consistency_errors
        and trust_missing == 0
        and prohibited_count == 0
        and bundle.get("output_mode") == "research_only"
    )
    return {
        "bundle_schema_valid": schema_valid,
        "missing_bundle_field_count": len(missing_fields),
        "missing_bundle_fields": missing_fields,
        "artifact_consistency_error_count": len(consistency_errors),
        "artifact_consistency_errors": consistency_errors,
        "missing_trust_metadata_count": trust_missing,
        "prohibited_action_field_count": prohibited_count,
    }


def _scenario_summaries(
    *,
    run: dict[str, Any],
    scenario_manifest: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    research = _by_scenario(run["research_run"]["research_decision_outputs"])
    predicted = _by_scenario(run["predicted_run"]["offline_predicted_label_artifacts"])
    comparison = _by_scenario(
        run["comparison_run"]["predicted_label_comparison_artifacts"]
    )
    traces = _by_scenario(run["trace_run"]["scenario_validation_traces"])
    pit_gaps = _pit_gaps_by_scenario(run["remediation_run"]["pit_gap_matrix"])
    scenarios: list[dict[str, Any]] = []
    for scenario_id in sorted(scenario_manifest):
        manifest_row = scenario_manifest[scenario_id]
        comparison_row = comparison[scenario_id]
        trace = traces[scenario_id]
        gaps = pit_gaps.get(scenario_id, [])
        comparable = bool(comparison_row["comparable"])
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "scenario_name": _scenario_title(scenario_id),
                "window_start": manifest_row["validation_window_start"],
                "window_end": manifest_row["validation_window_end"],
                "scenario_family": manifest_row["scenario_family"],
                "reference_family": comparison_row["reference_label_set"][
                    "scenario_family"
                ],
                "as_of": comparison_row["as_of"],
                "data_mode": comparison_row["data_mode"],
                "research_decision_state": research[scenario_id]["decision_state"],
                "predicted_label": predicted[scenario_id]["predicted_label"],
                "comparison_status": comparison_row["comparison_status"],
                "comparison_status_reason": comparison_row[
                    "comparison_status_reason"
                ],
                "comparable": comparable,
                "comparability_label": "comparable" if comparable else "not_comparable",
                "abstention_state": comparison_row["abstention_state"],
                "blocked_reason_codes": comparison_row["blocked_reason_codes"],
                "metric_result_states": trace["metric_result_states"],
                "evidence_completeness_summary": predicted[scenario_id][
                    "evidence_completeness_summary"
                ],
                "pit_gap_count": len(gaps),
                "rule_unresolved_gap_count": sum(
                    1
                    for gap in gaps
                    if gap["post_gap_class"] == "rule_unresolved_not_data_gap"
                ),
                "pit_gaps": gaps,
                "provenance_chain": trace["provenance_chain"],
                "detail_href": f"scenario-{scenario_id}.html",
                "allowed_uses": research[scenario_id]["allowed_uses"],
                "prohibited_uses": research[scenario_id]["prohibited_uses"],
                "trust_metadata": research[scenario_id]["trust_metadata"],
            }
        )
    return _ordered_scenarios(scenarios)


def _view_ids(
    *,
    current_snapshot: dict[str, Any] | None,
    boom_transition_surface: dict[str, Any] | None,
    boom_to_recession_transition_surface: dict[str, Any] | None,
    ordered_cycle_transition_lane_templates: dict[str, Any] | None,
    evidence_freshness_release_value_continuity: dict[str, Any] | None,
    major_group_evidence_profile_readiness: dict[str, Any] | None,
    indicator_dashboard_explanation_drilldown: dict[str, Any] | None,
    transition_timing_replay_preview: dict[str, Any] | None,
    macro_coverage_matrix: dict[str, Any] | None,
    indicator_detail_cards: dict[str, Any] | None,
) -> tuple[str, ...]:
    view_ids = list(VIEW_IDS)
    if current_snapshot is not None:
        view_ids.append(CURRENT_SNAPSHOT_VIEW_ID)
    if boom_transition_surface is not None:
        view_ids.append(BOOM_TRANSITION_VIEW_ID)
    if boom_to_recession_transition_surface is not None:
        view_ids.append(BOOM_TO_RECESSION_COMPLETION_VIEW_ID)
    if ordered_cycle_transition_lane_templates is not None:
        view_ids.append(ORDERED_CYCLE_TRANSITION_TEMPLATES_VIEW_ID)
    if evidence_freshness_release_value_continuity is not None:
        view_ids.append(EVIDENCE_FRESHNESS_RELEASE_VALUE_CONTINUITY_VIEW_ID)
    if major_group_evidence_profile_readiness is not None:
        view_ids.append(MAJOR_GROUP_EVIDENCE_PROFILE_READINESS_VIEW_ID)
    if indicator_dashboard_explanation_drilldown is not None:
        view_ids.append(INDICATOR_DASHBOARD_EXPLANATION_DRILLDOWN_VIEW_ID)
    if transition_timing_replay_preview is not None:
        view_ids.append(TRANSITION_TIMING_REPLAY_PREVIEW_VIEW_ID)
    if macro_coverage_matrix is not None:
        view_ids.append(MACRO_COVERAGE_VIEW_ID)
    if indicator_detail_cards is not None:
        view_ids.append(INDICATOR_DETAIL_VIEW_ID)
    return tuple(view_ids)


def _ordered_scenarios(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {
        "dotcom_cycle_2000_2003": 0,
        "global_financial_crisis_2007_2009": 1,
        "covid_recession_2020": 2,
        "euro_debt_slowdown_2011_2012": 3,
        "late_cycle_2018_2019": 4,
    }
    return sorted(scenarios, key=lambda row: order[row["scenario_id"]])


def _evidence_summaries(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in matrix["matrix_rows"]:
        output = row.get("phase_evidence_output") or {}
        rows.append(
            {
                "scenario_id": row["scenario_id"],
                "as_of": row["as_of"],
                "data_mode": row["data_mode"],
                "phase_or_layer": row["phase_or_layer"],
                "major_group_id": row["major_group_id"],
                "role_id": row["role_id"],
                "required_series_ids": row["required_series_ids"],
                "book_rule_status": row["book_rule_status"],
                "evidence_state": row["post_evidence_status"],
                "supportive": bool(output.get("supportive")),
                "contradictory": bool(output.get("contradictory")),
                "post_gap_class": row["post_gap_class"],
                "post_gap_persists": row["post_gap_persists"],
                "post_abstention_reason": row["post_abstention_reason"],
                "provenance": output.get("provenance", {}),
                "source_artifact_ids": _source_artifact_ids(output),
                "classification": _role_classification(row),
            }
        )
    return rows


def _pit_gap_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in matrix["matrix_rows"]:
        if not row["post_gap_persists"]:
            continue
        rows.append(
            {
                "scenario_id": row["scenario_id"],
                "role_id": row["role_id"],
                "phase_or_layer": row["phase_or_layer"],
                "major_group_id": row["major_group_id"],
                "required_series_ids": row["required_series_ids"],
                "required_observation_window": row["required_observation_window"],
                "post_gap_class": row["post_gap_class"],
                "genuine_blocker_evidence": row["genuine_blocker_evidence"],
                "series_checks": row["series_checks"],
            }
        )
    return rows


def _metric_summaries(metric_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for metric in metric_results:
        summaries.append(
            {
                "metric_id": metric["metric_id"],
                "result_status": metric["result_status"],
                "value": metric.get("value"),
                "numerator": metric.get("numerator"),
                "denominator": metric.get("denominator"),
                "denominator_definition": metric.get("denominator_definition"),
                "numerator_definition": metric.get("numerator_definition"),
                "skip_reason": metric.get("skip_reason"),
                "notes": metric.get("notes", []),
                "prohibited_uses": metric.get("prohibited_uses", []),
            }
        )
    return summaries


def _load_scenario_manifest(
    path: str | Path = DEFAULT_SCENARIO_MANIFEST_PATH,
) -> dict[str, dict[str, Any]]:
    rows = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "historical_validation_scenario_manifest"
    ]["scenario_rows"]
    return {row["scenario_id"]: row for row in rows}


def _by_scenario(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in rows}


def _pit_gaps_by_scenario(matrix: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _pit_gap_rows(matrix):
        grouped[row["scenario_id"]].append(row)
    return dict(grouped)


def _source_artifact_ids(output: dict[str, Any]) -> list[str]:
    provenance = output.get("provenance", {})
    if isinstance(provenance, dict):
        artifacts = provenance.get("source_artifact_ids")
        if isinstance(artifacts, list):
            return [str(item) for item in artifacts]
        artifact = provenance.get("source_artifact_id")
        if artifact:
            return [str(artifact)]
    return []


def _role_classification(row: dict[str, Any]) -> str:
    if row["book_rule_status"] == "operational":
        return "book_core_phase_evidence"
    if row["post_gap_class"] == "rule_unresolved_not_data_gap":
        return "raw_observation_only_rule_unresolved"
    return "book_core_missing_or_abstained"


def _contains_prohibited_action_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_ACTION_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_action_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_action_field(item) for item in value))
    return 0


def _view_title(view_id: str) -> str:
    return {
        "research_overview": "Research Overview",
        "historical_scenarios": "Historical Scenarios",
        "validation_results": "Validation Results",
        "evidence_explorer": "Evidence Explorer",
        "data_lineage_governance": "Data Lineage / Governance",
        "pit_gap_view": "PIT Gap View",
        "scenario_detail": "Scenario Detail",
        "current_research_snapshot": "Current Research Snapshot",
        "declared_boom_transition_monitor": "Declared Boom Transition Monitor",
        "macro_indicator_coverage_readiness": "Macro Indicator Coverage Readiness",
        "indicator_detail_source_risk_value_cards": (
            "Indicator Detail Source Risk and Value Context"
        ),
        "boom_to_recession_transition_surface_completion": (
            "Boom to Recession Transition Surface"
        ),
        "full_ordered_cycle_transition_lane_templates": (
            "Full Ordered-Cycle Transition Lane Templates"
        ),
        "evidence_freshness_release_value_continuity": (
            "Evidence Freshness, Release Timing, and Value Continuity"
        ),
        "major_group_evidence_profile_readiness": (
            "Major-Group Evidence Profile and Readiness Explanation"
        ),
        "indicator_dashboard_explanation_drilldown": (
            "Indicator-to-Dashboard Explanation Drill-down"
        ),
        "transition_timing_replay_preview": "Transition Timing Replay Preview",
    }[view_id]


def build_research_dashboard_bundle_with_boom_transition() -> dict[str, Any]:
    """Build a bundle including the Phase49 transition dashboard surface."""

    return build_research_dashboard_bundle(
        boom_transition_surface=build_boom_transition_dashboard_surface(),
    )


def build_research_dashboard_bundle_with_boom_to_recession_surface() -> dict[str, Any]:
    """Build a bundle including the Phase57 completed transition surface."""

    return build_research_dashboard_bundle(
        boom_to_recession_transition_surface=(
            build_boom_to_recession_transition_surface_view_model()
        ),
    )


def build_research_dashboard_bundle_with_evidence_continuity() -> dict[str, Any]:
    """Build a bundle including the Phase60 continuity surface."""

    return build_research_dashboard_bundle(
        evidence_freshness_release_value_continuity=(
            build_evidence_freshness_release_value_continuity_view_model()
        ),
    )


def build_research_dashboard_bundle_with_major_group_evidence_profiles() -> dict[str, Any]:
    """Build a bundle including the Phase61 major-group profile surface."""

    return build_research_dashboard_bundle(
        major_group_evidence_profile_readiness=(
            build_major_group_evidence_profile_readiness_view_model()
        ),
    )


def build_research_dashboard_bundle_with_indicator_drilldown() -> dict[str, Any]:
    """Build a bundle including the Phase62 indicator explanation drill-down."""

    return build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=(
            build_indicator_dashboard_explanation_drilldown_view_model()
        ),
    )


def build_research_dashboard_bundle_with_transition_timing_replay_preview() -> dict[str, Any]:
    """Build a bundle including the Phase67 transition timing preview."""

    return build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=(
            build_indicator_dashboard_explanation_drilldown_view_model()
        ),
        transition_timing_replay_preview=(
            build_transition_timing_replay_preview_view_model()
        ),
    )


def build_research_dashboard_bundle_with_ordered_cycle_transition_templates() -> dict[str, Any]:
    """Build a bundle including the Phase58 full ordered-cycle lane templates."""

    return build_research_dashboard_bundle(
        ordered_cycle_transition_lane_templates=(
            build_full_ordered_cycle_transition_lane_template_view_model()
        ),
    )


def _scenario_title(scenario_id: str) -> str:
    return scenario_id.replace("_", " ").title()
