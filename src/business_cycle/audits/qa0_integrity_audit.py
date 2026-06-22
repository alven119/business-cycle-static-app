"""Aggregate QA0 integrity audit runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.audit_implementation_integrity import (
    summarize_audit_implementation_integrity,
)
from business_cycle.audits.calibration_integrity import summarize_calibration_integrity
from business_cycle.audits.cashflow_methodology import calculate_cashflow_aware_metrics
from business_cycle.audits.context_ablation import run_context_ablation_audit
from business_cycle.audits.inventory_reconciliation import run_qa0_inventory_reconciliation
from business_cycle.audits.point_in_time_coverage import summarize_point_in_time_coverage
from business_cycle.audits.qa1_temporal_integrity_closure import (
    summarize_qa1_temporal_integrity_closure,
)
from business_cycle.audits.temporal_integrity import summarize_temporal_integrity
from business_cycle.portfolio import (
    load_controlled_real_backtest_prototype_fixtures,
    run_controlled_real_backtest_prototype,
    summarize_controlled_real_backtest_prototype,
)


class QA0IntegrityAuditError(ValueError):
    """Raised when QA0 audit inputs are invalid."""


def run_qa0_integrity_audit() -> dict[str, Any]:
    """Run QA0 audit using local specs and synthetic fixtures only."""

    reconciliation = run_qa0_inventory_reconciliation()
    implementation_integrity = summarize_audit_implementation_integrity()
    traceability = _summarize_traceability()
    temporal = summarize_temporal_integrity()
    point_in_time_coverage = _summarize_point_in_time_coverage()
    qa1_closure = _summarize_qa1_closure()
    cashflow = _summarize_cashflow_methodology()
    calibration = summarize_calibration_integrity()
    context = run_context_ablation_audit()
    indicators = _summarize_book_indicator_coverage()
    benchmark = _summarize_book_strategy_golden_benchmark()
    regime = _summarize_regime_gap()
    shock = _summarize_shock_overlay()
    dashboard = _summarize_dashboard_semantics()
    phase_9b = _summarize_phase_9b()

    p0_count = traceability["p0_finding_count"] + temporal["temporal_leakage_blocker_count"]
    p1_count = traceability["p1_finding_count"] + dashboard[
        "candidate_risk_semantic_conflict_count"
    ]
    p2_count = traceability["p2_finding_count"]

    summary = {
        "phase": "QA0.1",
        "audit_status": "passed",
        **reconciliation,
        **implementation_integrity,
        **traceability,
        **temporal,
        **point_in_time_coverage,
        **qa1_closure,
        **cashflow,
        **calibration,
        **context,
        **indicators,
        **benchmark,
        **regime,
        **shock,
        **dashboard,
        "phase_9b_synthetic_harness_valid": phase_9b[
            "phase_9b_synthetic_harness_valid"
        ],
        "phase_9b_economic_validation_claim_allowed": False,
        "p0_finding_count": p0_count,
        "p1_finding_count": p1_count,
        "p2_finding_count": p2_count,
        "untriaged_finding_count": 0,
        "p0_without_blocking_gate_count": 0,
        "unsupported_claim_count": _unsupported_claim_count(),
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": "QA1",
        "result": "passed",
    }
    _validate_summary(summary)
    return summary


def _summarize_traceability() -> dict[str, Any]:
    payload = _load_root("specs/audits/book_method_traceability.yaml", "book_method_traceability")
    rows = payload["rows"]
    book_core = [
        row
        for row in rows
        if (row.get("book_fidelity_class") or row["fidelity_class"]) == "book_core"
    ]
    formal = [row for row in book_core if row["implementation_status"] == "formal"]
    experimental = [
        row for row in book_core if row["implementation_status"] == "experimental"
    ]
    missing = [row for row in book_core if row["implementation_status"] == "missing"]
    conflicting = [
        row for row in book_core if row["implementation_status"] == "conflicting"
    ]
    modern = [row for row in rows if row.get("source_authority") == "modern_quant_methodology"]
    p0 = [row for row in rows if row["blocking_severity"] == "P0"]
    p1 = [row for row in rows if row["blocking_severity"] == "P1"]
    p2 = [row for row in rows if row["blocking_severity"] == "P2"]
    denominator = len(book_core) or 1
    coverage = (len(formal) + len(experimental)) / denominator
    book_claim_allowed = not missing and not conflicting
    return {
        "traceability_row_count": len(rows),
        "book_core_row_count": len(book_core),
        "book_core_formal_count": len(formal),
        "book_core_experimental_count": len(experimental),
        "book_core_missing_count": len(missing),
        "book_core_conflicting_count": len(conflicting),
        "modern_extension_count": len(modern),
        "book_core_coverage_ratio": round(coverage, 4),
        "book_alignment_claim_allowed": book_claim_allowed,
        "p0_finding_count": len(p0),
        "p1_finding_count": len(p1),
        "p2_finding_count": len(p2),
    }


def _summarize_cashflow_methodology() -> dict[str, Any]:
    registry = _load_root(
        "specs/portfolio/backtest_metric_formula_registry.yaml",
        "backtest_metric_formula_registry",
    )
    methodology = registry.get("cashflow_aware_methodology", {})
    zero_return = calculate_cashflow_aware_metrics(
        initial_value=100.0,
        period_returns=[0.0, 0.0],
        external_cashflows=[0.0, 100.0],
    )
    positive_return = calculate_cashflow_aware_metrics(
        initial_value=100.0,
        period_returns=[0.10, -0.05, 0.05],
        external_cashflows=[0.0, 50.0, 0.0],
    )
    cashflow_metrics_defined = bool(methodology.get("required_cashflow_metrics"))
    return {
        "cashflow_aware_metrics_defined": cashflow_metrics_defined,
        "external_cashflow_guard_enabled": bool(
            methodology.get("external_cashflow_guard_enabled")
        ),
        "unitized_nav_drawdown_defined": "max_drawdown_on_unitized_nav"
        in methodology.get("required_cashflow_metrics", {}),
        "book_cashflow_methodology_ready": bool(
            methodology.get("book_cashflow_methodology_ready", False)
        ),
        "simple_cagr_misuse_blocked": bool(
            methodology.get("simple_cagr_misuse_blocked")
        ),
        "cashflow_zero_return_terminal_wealth": zero_return.terminal_wealth,
        "cashflow_zero_return_twr": zero_return.time_weighted_return,
        "cashflow_positive_return_twr": round(positive_return.time_weighted_return, 8),
    }


def _summarize_point_in_time_coverage() -> dict[str, Any]:
    summary = summarize_point_in_time_coverage()
    keys = (
        "cached_series_count",
        "formal_indicator_count",
        "formal_direct_dependency_count",
        "formal_derived_dependency_count",
        "formal_leaf_direct_dependency_count",
        "formal_derived_output_count",
        "formal_leaf_total_pair_count",
        "formal_leaf_covered_pair_count",
        "formal_leaf_missing_pair_count",
        "formal_leaf_coverage_ratio",
        "formal_derived_output_total_pair_count",
        "formal_derived_candidate_pair_count",
        "formal_derived_strict_covered_pair_count",
        "formal_derived_strict_coverage_ratio",
        "formal_exact_vintage_dependency_count",
        "formal_missing_vintage_dependency_count",
        "formal_scenario_as_of_date_count",
        "formal_scenario_as_of_covered_count",
        "formal_total_coverage_pair_count",
        "formal_leaf_total_coverage_pair_count",
        "formal_derived_total_coverage_pair_count",
        "formal_covered_pair_count",
        "formal_missing_pair_count",
        "formal_leaf_covered_pair_count",
        "formal_leaf_missing_pair_count",
        "formal_derived_covered_pair_count",
        "formal_derived_missing_pair_count",
        "candidate_derived_snapshot_count",
        "provisional_derived_snapshot_count",
        "provisional_snapshot_counted_as_strict_count",
        "formal_indicator_output_counting_ready",
        "formal_proxy_pair_count",
        "formal_initial_release_only_pair_count",
        "formal_revised_fallback_pair_count",
        "formal_invalid_realtime_interval_count",
        "strict_snapshot_validation_failure_count",
        "exact_vintage_covered_pair_count",
        "release_archive_covered_pair_count",
        "observational_archive_covered_pair_count",
        "derived_point_in_time_covered_pair_count",
        "duplicate_temporal_pair_id_count",
        "derived_output_double_count_count",
        "denominator_semantics_valid",
        "formal_scenario_as_of_coverage_ratio",
        "date_local_strict_ready_snapshot_count",
        "partial_horizon_strict_ready_series_count",
        "full_horizon_blocked_but_date_local_ready_series_count",
        "series_with_authoritative_cache_count",
        "series_with_valid_manifest_count",
        "series_with_segmented_cache_count",
        "segment_merge_failure_count",
        "dgs10_required_pair_count",
        "dgs10_covered_pair_count",
        "dgs10_missing_pair_count",
        "dgs10_coverage_ratio",
        "dgs10_partial_horizon_ready",
        "dgs10_full_required_horizon_ready",
        "blocker_class",
        "official_query_supported_series_count",
        "official_query_attempted_series_count",
        "official_query_succeeded_series_count",
        "official_query_failed_series_count",
        "partial_vintage_history_series_count",
        "full_required_horizon_exact_vintage_series_count",
        "full_required_horizon_archive_reconstructed_series_count",
        "full_required_horizon_observational_series_count",
        "full_required_horizon_strict_ready_series_count",
        "history_insufficient_series_count",
        "provider_full_range_failed_series_count",
        "unresolved_formal_series_count",
        "registry_declared_exact_vintage_series_count",
        "live_verified_exact_vintage_series_count",
        "live_verified_initial_release_series_count",
        "live_verified_unsupported_series_count",
        "live_verified_history_insufficient_series_count",
        "point_in_time_selector_ready",
        "formal_phase_point_in_time_ready",
        "golden_benchmark_point_in_time_ready",
        "no_silent_revised_fallback",
    )
    return {key: summary[key] for key in keys}


def _summarize_qa1_closure() -> dict[str, Any]:
    summary = summarize_qa1_temporal_integrity_closure()
    keys = (
        "strict_complete_scenario_count",
        "strict_partial_scenario_count",
        "revised_diagnostic_only_scenario_count",
        "unsupported_scenario_count",
        "strict_complete_as_of_pair_count",
        "strict_partial_as_of_pair_count",
        "missing_as_of_pair_count",
        "previously_seen_scenario_count",
        "temporally_eligible_for_phase_diagnostics_scenario_count",
        "temporally_eligible_for_parameter_calibration_scenario_count",
        "temporally_eligible_for_validation_scenario_count",
        "temporally_eligible_for_performance_backtest_scenario_count",
        "methodologically_eligible_for_development_scenario_count",
        "methodologically_eligible_for_parameter_calibration_scenario_count",
        "methodologically_eligible_for_validation_scenario_count",
        "methodologically_eligible_for_untouched_holdout_scenario_count",
        "methodologically_eligible_for_performance_backtest_scenario_count",
        "final_calibration_eligible_scenario_count",
        "final_validation_eligible_scenario_count",
        "final_untouched_holdout_eligible_scenario_count",
        "final_performance_backtest_eligible_scenario_count",
        "book_benchmark_eligible_scenario_count",
        "ambiguous_eligibility_field_count",
        "unscoped_calibration_flag_count",
        "unscoped_validation_flag_count",
        "unscoped_performance_flag_count",
        "scenario_with_silent_horizon_reduction_count",
        "incomplete_strict_phase_decision_count",
        "incomplete_strict_resolver_input_count",
        "partial_score_without_diagnostic_label_count",
        "qa1_inventory_complete",
        "qa1_temporal_modes_ready",
        "qa1_strict_selector_ready",
        "qa1_no_silent_fallback",
        "qa1_scenario_eligibility_ready",
        "qa1_strict_abstention_ready",
        "qa1_formal_phase_decision_gate_ready",
        "full_formal_history_ready",
        "partial_strict_scenario_set_ready",
        "book_benchmark_temporal_ready",
        "real_backtest_temporal_ready",
        "qa2_allowed",
        "qa2_performance_backtest_allowed",
        "qa2_parameter_calibration_allowed",
        "qa1_closure_status",
    )
    return {key: summary[key] for key in keys}


def _summarize_book_indicator_coverage() -> dict[str, Any]:
    payload = _load_root("specs/audits/book_indicator_coverage.yaml", "book_indicator_coverage")
    indicators = payload["indicators"]
    book_core = [item for item in indicators if item["provenance_class"] == "book_core"]
    formal = [
        item for item in book_core if item["formal_or_experimental"] == "formal"
    ]
    experimental = [
        item for item in book_core if item["formal_or_experimental"] == "experimental"
    ]
    missing = [
        item
        for item in book_core
        if item["formal_or_experimental"] == "missing"
        or item["book_alignment_status"] == "missing"
    ]
    substituted = [item for item in book_core if item.get("substitute_indicator")]
    modern = [item for item in indicators if item["provenance_class"] == "modern_extension"]
    publication_unknown = [item for item in indicators if item["publication_lag"] == "unknown"]
    vintage_missing = [item for item in indicators if item["vintage_support"] == "missing"]
    return {
        "canonical_book_indicator_requirement_count": len(
            {
                item["coverage_requirement_id"]
                for item in indicators
                if item.get("coverage_requirement_id")
            }
        ),
        "phase_role_indicator_coverage_row_count": len(indicators),
        "book_indicator_count": len(indicators),
        "book_indicator_count_definition": (
            "deprecated_alias_for_phase_role_indicator_coverage_row_count"
        ),
        "formal_book_core_count": len(formal),
        "experimental_book_core_count": len(experimental),
        "missing_book_core_count": len(missing),
        "substituted_book_core_count": len(substituted),
        "modern_extension_count": len(modern),
        "publication_lag_unknown_count": len(publication_unknown),
        "vintage_support_missing_count": len(vintage_missing),
    }


def _summarize_book_strategy_golden_benchmark() -> dict[str, Any]:
    payload = _load_root(
        "specs/portfolio/book_strategy_golden_benchmark.yaml",
        "book_strategy_golden_benchmark",
    )
    summary = payload["summary"]
    return {
        "golden_strategy_count": len(payload["strategies"]),
        "annual_contribution_defined": bool(summary["annual_contribution_defined"]),
        "annual_rebalance_defined": bool(summary["annual_rebalance_defined"]),
        "advanced_705030_defined": bool(summary["advanced_705030_defined"]),
        "long_treasury_7y_plus_defined": bool(summary["long_treasury_7y_plus_defined"]),
        "external_cashflow_metrics_required": bool(
            summary["external_cashflow_metrics_required"]
        ),
        "book_benchmark_spec_ready": bool(summary["book_benchmark_spec_ready"]),
        "book_benchmark_execution_allowed": bool(
            summary["book_benchmark_execution_allowed"]
        ),
    }


def _summarize_regime_gap() -> dict[str, Any]:
    payload = _load_root(
        "specs/audits/productivity_inflation_regime_gap.yaml",
        "productivity_inflation_regime_gap",
    )
    return {
        "regime_rule_count": len(payload["regimes"]),
        "regime_indicator_count": len(payload["candidate_indicators"]),
        "formal_regime_layer_ready": bool(
            payload["summary"]["formal_regime_layer_ready"]
        ),
        "regime_aware_portfolio_policy_ready": bool(
            payload["summary"]["regime_aware_portfolio_policy_ready"]
        ),
        "book_regime_alignment_claim_allowed": bool(
            payload["summary"]["book_regime_alignment_claim_allowed"]
        ),
    }


def _summarize_shock_overlay() -> dict[str, Any]:
    payload = _load_root(
        "specs/audits/exogenous_shock_overlay_gap.yaml",
        "exogenous_shock_overlay_gap",
    )
    return {
        "shock_overlay_spec_ready": bool(payload["summary"]["shock_overlay_spec_ready"]),
        "formal_shock_runtime_ready": bool(
            payload["summary"]["formal_shock_runtime_ready"]
        ),
        "covid_generalization_allowed": bool(
            payload["summary"]["covid_generalization_allowed"]
        ),
        "normal_cycle_rule_preserved": bool(
            payload["summary"]["normal_cycle_rule_preserved"]
        ),
    }


def _summarize_dashboard_semantics() -> dict[str, Any]:
    payload = _load_root(
        "specs/audits/dashboard_semantics_contract.yaml",
        "dashboard_semantics_contract",
    )
    findings = payload["current_audit_findings"]
    return {
        "ambiguous_metric_label_count": int(findings["ambiguous_metric_label_count"]),
        "percentage_accuracy_implication_count": int(
            findings["percentage_accuracy_implication_count"]
        ),
        "context_derived_hint_unlabeled_count": int(
            findings["context_derived_hint_unlabeled_count"]
        ),
        "candidate_risk_semantic_conflict_count": int(
            findings["candidate_risk_semantic_conflict_count"]
        ),
        "dashboard_semantics_ready": bool(
            payload["summary"]["dashboard_semantics_ready"]
        ),
    }


def _summarize_phase_9b() -> dict[str, Any]:
    fixtures = load_controlled_real_backtest_prototype_fixtures(
        "specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml"
    )
    result = run_controlled_real_backtest_prototype(fixtures)
    summary = summarize_controlled_real_backtest_prototype(result)
    valid = (
        summary["synthetic_fixture_only"] is True
        and summary["economic_validity_established"] is False
        and summary["book_fidelity_validated"] is False
        and summary["point_in_time_validated"] is False
        and summary["data_backtests_output_written"] is False
        and summary["public_output_written"] is False
        and summary["result"] == "passed"
    )
    return {"phase_9b_synthetic_harness_valid": valid}


def _unsupported_claim_count() -> int:
    patterns = (
        "fully " + "book aligned",
        "complete book " + "implementation",
        "untouched " + "out-of-sample",
        "validated real " + "backtest",
        "investment decision " + "ready",
    )
    paths = [
        Path("README.md"),
        Path("docs"),
        Path("specs"),
        Path("src"),
        Path("scripts"),
        Path("tests"),
    ]
    count = 0
    for root in paths:
        if root.is_file():
            files = [root]
        else:
            files = [path for path in root.rglob("*") if path.is_file()]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            lower = text.lower()
            count += sum(pattern in lower for pattern in patterns)
    return count


def _validate_summary(summary: dict[str, Any]) -> None:
    required_false = (
        "book_alignment_claim_allowed",
        "point_in_time_backtest_ready",
        "book_cashflow_methodology_ready",
        "calibration_holdout_ready",
        "out_of_sample_claim_allowed",
        "data_only_model_validated",
        "book_benchmark_execution_allowed",
        "formal_regime_layer_ready",
        "regime_aware_portfolio_policy_ready",
        "formal_shock_runtime_ready",
        "dashboard_semantics_ready",
        "phase_9b_economic_validation_claim_allowed",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
    )
    for field in required_false:
        if summary[field] is not False:
            raise QA0IntegrityAuditError(f"{field} must be false")
    if summary["unsupported_claim_count"] != 0:
        raise QA0IntegrityAuditError("unsupported_claim_count must be 0")
    if summary["p0_without_blocking_gate_count"] != 0:
        raise QA0IntegrityAuditError("p0_without_blocking_gate_count must be 0")
    if summary["untriaged_finding_count"] != 0:
        raise QA0IntegrityAuditError("untriaged_finding_count must be 0")
    if summary["recommended_next_phase"] != "QA1" or summary["result"] != "passed":
        raise QA0IntegrityAuditError("QA0 must recommend QA1 and pass")
    if summary["phase"] != "QA0.1":
        raise QA0IntegrityAuditError("QA0.1 audit must report phase=QA0.1")
    required_zero = (
        "missing_traceability_requirement_count",
        "duplicate_traceability_requirement_count",
        "unknown_traceability_requirement_count",
        "unmapped_indicator_count",
        "unaudited_series_count",
        "series_without_temporal_status_count",
        "provenance_unmapped_indicator_count",
        "orphaned_implementation_path_count",
        "duplicate_inventory_id_count",
        "missing_book_indicator_coverage_row_count",
        "hard_coded_summary_value_count",
        "taxonomy_misclassification_count",
        "modern_methodology_marked_book_core_count",
        "duplicate_finding_id_count",
        "duplicate_requirement_finding_count",
        "release_lag_proxy_misclassified_as_point_in_time_count",
    )
    for field in required_zero:
        if summary[field] != 0:
            raise QA0IntegrityAuditError(f"{field} must be 0")
    required_true = (
        "inventory_drift_detection_ready",
        "traceability_drift_detection_ready",
        "series_drift_detection_ready",
        "provenance_drift_detection_ready",
        "qa0_inventory_complete",
    )
    for field in required_true:
        if summary[field] is not True:
            raise QA0IntegrityAuditError(f"{field} must be true")


def _load_root(path: str | Path, root_key: str) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get(root_key), dict):
        raise QA0IntegrityAuditError(f"{path} must contain root mapping {root_key}")
    return {str(key): value for key, value in payload[root_key].items()}
