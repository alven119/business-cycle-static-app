"""QA4 supporting scope contract summaries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


NORMAL_CYCLE_PATH = Path("specs/audits/book_normal_cycle_state_machine_contract.yaml")
SHOCK_OVERLAY_PATH = Path("specs/audits/exogenous_shock_overlay_scope.yaml")
SECULAR_REGIME_PATH = Path("specs/audits/secular_regime_formal_scope.yaml")
BOOK_PORTFOLIO_PATH = Path("specs/audits/book_portfolio_rule_scope.yaml")


def summarize_book_normal_cycle_state_machine_contract(
    path: str | Path = NORMAL_CYCLE_PATH,
) -> dict[str, Any]:
    """Return proposed normal-cycle state machine scope gates."""

    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_normal_cycle_state_machine_contract"
    ]
    counts = spec["hard_gate_counts"]
    return {
        "phase": "QA4",
        "normal_cycle_contract_ready": all(value == 0 for value in counts.values()),
        **counts,
        "normal_sequence": spec["normal_sequence"],
        "book_normal_rules": spec["book_normal_rules"],
    }


def summarize_exogenous_shock_overlay_scope(
    path: str | Path = SHOCK_OVERLAY_PATH,
) -> dict[str, Any]:
    """Return exogenous shock overlay scope status."""

    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "exogenous_shock_overlay_scope"
    ]
    rules = spec["rules"]
    return {
        "phase": "QA4",
        "shock_overlay_scope_ready": spec["overlay_classification"]
        == "modern_extension",
        "shock_overlay_scope_defined": True,
        "shock_overlay_formal_runtime_ready": bool(spec["formal_runtime_ready"]),
        "shock_overlay_direct_phase_override_allowed": bool(
            rules["direct_phase_override_allowed"]
        ),
        "shock_overlay_direct_portfolio_action_allowed": bool(
            rules["direct_portfolio_action_allowed"]
        ),
        "covid_specific_general_rule_count": 0
        if not rules["covid_specific_general_rule_allowed"]
        else 1,
        "status_states": spec["status_states"],
    }


def summarize_secular_regime_scope(
    path: str | Path = SECULAR_REGIME_PATH,
) -> dict[str, Any]:
    """Return secular regime formal scope status."""

    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "secular_regime_formal_scope"
    ]
    return {
        "phase": "QA4",
        "secular_regime_scope_ready": True,
        "regime_scope_item_count": len(spec["regimes"]),
        "regime_indicator_role_count": len(spec["candidate_evidence"]),
        "regime_formal_runtime_ready": bool(spec["formal_runtime_ready"]),
        "regime_phase_score_integration_allowed": bool(
            spec["phase_score_integration_allowed"]
        ),
        "regime_portfolio_research_input_allowed": bool(
            spec["portfolio_research_input_allowed"]
        ),
        "regime_live_allocation_allowed": bool(spec["live_allocation_allowed"]),
        "regimes": spec["regimes"],
    }


def summarize_book_portfolio_rule_scope(
    path: str | Path = BOOK_PORTFOLIO_PATH,
) -> dict[str, Any]:
    """Return book portfolio rule scope status."""

    spec = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_portfolio_rule_scope"
    ]
    prohibited = spec["prohibited_misclassifications"]
    return {
        "phase": "QA4",
        "book_portfolio_rule_scope_ready": bool(spec["rule_spec_ready"]),
        "book_strategy_count": len(spec["strategy_ids"]),
        "book_portfolio_rule_count": len(spec["required_book_rules"]),
        "book_rule_spec_ready": bool(spec["rule_spec_ready"]),
        "book_rule_data_contract_ready": bool(spec["rule_data_contract_ready"]),
        "book_rule_execution_ready": bool(spec["rule_execution_ready"]),
        "generic_bond_substitution_count": 1
        if prohibited["generic_bond_as_long_treasury"]
        else 0,
        "monthly_rebalance_misclassified_as_book_baseline_count": 1
        if prohibited["monthly_rebalance_as_book_baseline"]
        else 0,
        "boom_year_schedule_used_as_phase_transition_count": 1
        if prohibited["boom_elapsed_schedule_as_phase_transition"]
        else 0,
        "strategy_ids": spec["strategy_ids"],
    }

