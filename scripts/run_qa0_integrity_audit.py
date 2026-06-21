"""Run QA0 book fidelity, temporal integrity, and methodology audit."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.qa0_integrity_audit import (  # noqa: E402
    QA0IntegrityAuditError,
    run_qa0_integrity_audit,
)


def main() -> int:
    try:
        summary = run_qa0_integrity_audit()
    except QA0IntegrityAuditError as exc:
        print(f"error={exc}", file=sys.stderr)
        return 1
    ordered_fields = [
        "phase",
        "audit_status",
        "traceability_row_count",
        "book_core_row_count",
        "book_core_missing_count",
        "book_core_conflicting_count",
        "book_core_coverage_ratio",
        "book_alignment_claim_allowed",
        "audited_series_count",
        "series_missing_availability_metadata_count",
        "revised_data_only",
        "vintage_data_supported",
        "point_in_time_backtest_ready",
        "temporal_leakage_blocker_count",
        "cashflow_aware_metrics_defined",
        "external_cashflow_guard_enabled",
        "unitized_nav_drawdown_defined",
        "book_cashflow_methodology_ready",
        "simple_cagr_misuse_blocked",
        "previously_seen_scenario_count",
        "untouched_holdout_scenario_count",
        "calibration_holdout_ready",
        "out_of_sample_claim_allowed",
        "external_context_dependency_detected",
        "data_only_model_validated",
        "context_ablation_ready",
        "book_indicator_count",
        "missing_book_core_count",
        "modern_extension_count",
        "golden_strategy_count",
        "book_benchmark_spec_ready",
        "book_benchmark_execution_allowed",
        "formal_regime_layer_ready",
        "regime_aware_portfolio_policy_ready",
        "shock_overlay_spec_ready",
        "formal_shock_runtime_ready",
        "dashboard_semantics_ready",
        "phase_9b_synthetic_harness_valid",
        "phase_9b_economic_validation_claim_allowed",
        "p0_finding_count",
        "p1_finding_count",
        "p2_finding_count",
        "untriaged_finding_count",
        "p0_without_blocking_gate_count",
        "unsupported_claim_count",
        "real_backtest_progression_allowed",
        "phase_9b1_allowed",
        "recommended_next_phase",
        "result",
    ]
    for field in ordered_fields:
        print(f"{field}={_format_value(summary[field])}")
    return 0


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

