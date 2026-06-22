"""QA audit helpers for methodology and safety gates."""

from business_cycle.audits.calibration_integrity import summarize_calibration_integrity
from business_cycle.audits.cashflow_methodology import (
    CashflowMethodologyError,
    calculate_cashflow_aware_metrics,
    guard_simple_return_usage,
)
from business_cycle.audits.context_ablation import run_context_ablation_audit
from business_cycle.audits.context_dependency_governance import (
    summarize_context_dependency_governance,
)
from business_cycle.audits.data_only_model_freeze import (
    summarize_data_only_model_baseline_freeze,
)
from business_cycle.audits.data_only_shadow_evaluation import (
    run_data_only_shadow_evaluation,
)
from business_cycle.audits.book_faithful_scope import (
    summarize_book_faithful_formal_model_scope,
    summarize_boom_formal_scope,
    summarize_growth_formal_scope,
    summarize_recession_trough_formal_scope,
    summarize_recovery_formal_scope,
)
from business_cycle.audits.formal_indicator_scope_matrix import (
    summarize_formal_indicator_scope_matrix,
)
from business_cycle.audits.formal_model_layers import (
    summarize_formal_model_layer_architecture,
)
from business_cycle.audits.formal_scope_diff import summarize_formal_model_scope_diff
from business_cycle.audits.formal_scope_freeze import (
    summarize_book_faithful_formal_scope_freeze,
)
from business_cycle.audits.indicator_promotion import (
    summarize_indicator_promotion_readiness,
)
from business_cycle.audits.inventory_reconciliation import run_qa0_inventory_reconciliation
from business_cycle.audits.model_freeze_semantics import (
    summarize_model_freeze_and_holdout_semantics,
)
from business_cycle.audits.model_parameter_drift import summarize_model_parameter_drift
from business_cycle.audits.model_parameter_inventory import (
    summarize_model_parameter_inventory,
)
from business_cycle.audits.point_in_time_coverage import summarize_point_in_time_coverage
from business_cycle.audits.pre_registered_validation import (
    summarize_pre_registered_validation_protocol,
)
from business_cycle.audits.production_hardcoding import summarize_production_hardcoding
from business_cycle.audits.qa0_integrity_audit import run_qa0_integrity_audit
from business_cycle.audits.qa3_calibration_integrity_closure import (
    summarize_qa3_calibration_integrity_closure,
)
from business_cycle.audits.qa4_book_fidelity_scope_closure import (
    summarize_qa4_book_fidelity_scope_closure,
)
from business_cycle.audits.qa4_scope_contracts import (
    summarize_book_normal_cycle_state_machine_contract,
    summarize_book_portfolio_rule_scope,
    summarize_exogenous_shock_overlay_scope,
    summarize_secular_regime_scope,
)
from business_cycle.audits.repository_inventory import collect_repository_inventory
from business_cycle.audits.scenario_exposure import summarize_scenario_exposure_registry
from business_cycle.audits.temporal_integrity import (
    TemporalIntegrityError,
    filter_point_in_time_records,
    summarize_temporal_integrity,
)

__all__ = [
    "CashflowMethodologyError",
    "TemporalIntegrityError",
    "calculate_cashflow_aware_metrics",
    "filter_point_in_time_records",
    "guard_simple_return_usage",
    "collect_repository_inventory",
    "run_context_ablation_audit",
    "run_data_only_shadow_evaluation",
    "run_qa0_integrity_audit",
    "run_qa0_inventory_reconciliation",
    "summarize_book_faithful_formal_model_scope",
    "summarize_book_normal_cycle_state_machine_contract",
    "summarize_book_portfolio_rule_scope",
    "summarize_boom_formal_scope",
    "summarize_calibration_integrity",
    "summarize_context_dependency_governance",
    "summarize_data_only_model_baseline_freeze",
    "summarize_exogenous_shock_overlay_scope",
    "summarize_formal_indicator_scope_matrix",
    "summarize_formal_model_layer_architecture",
    "summarize_formal_model_scope_diff",
    "summarize_book_faithful_formal_scope_freeze",
    "summarize_growth_formal_scope",
    "summarize_indicator_promotion_readiness",
    "summarize_model_freeze_and_holdout_semantics",
    "summarize_model_parameter_drift",
    "summarize_model_parameter_inventory",
    "summarize_point_in_time_coverage",
    "summarize_pre_registered_validation_protocol",
    "summarize_production_hardcoding",
    "summarize_qa3_calibration_integrity_closure",
    "summarize_qa4_book_fidelity_scope_closure",
    "summarize_recession_trough_formal_scope",
    "summarize_recovery_formal_scope",
    "summarize_scenario_exposure_registry",
    "summarize_secular_regime_scope",
    "summarize_temporal_integrity",
]
