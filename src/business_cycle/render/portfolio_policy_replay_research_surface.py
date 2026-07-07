"""Phase88 portfolio policy replay research surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)
from business_cycle.portfolio.policy_replay_schedule import (
    load_portfolio_policy_replay_schedule_contract,
    summarize_portfolio_policy_replay_schedule,
)
from business_cycle.portfolio.policy_research_baseline import (
    REQUIRED_TEMPLATE_IDS,
    summarize_portfolio_policy_research_baseline,
)
from business_cycle.portfolio.research_backtest_artifacts import (
    build_research_backtest_artifact_bundle,
    summarize_research_backtest_artifacts,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SURFACE_PATH = (
    ROOT / "specs/common/portfolio_policy_replay_research_surface.yaml"
)


class PortfolioPolicyReplayResearchSurfaceError(ValueError):
    """Raised when the Phase88 research surface contract is invalid."""


def load_portfolio_policy_replay_research_surface_contract(
    path: str | Path = DEFAULT_SURFACE_PATH,
) -> dict[str, Any]:
    """Load and validate the Phase88 portfolio policy replay research surface."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioPolicyReplayResearchSurfaceError(
            "portfolio policy replay research surface YAML must be a mapping",
        )
    contract = payload.get("portfolio_policy_replay_research_surface")
    if not isinstance(contract, dict):
        raise PortfolioPolicyReplayResearchSurfaceError(
            "YAML must contain portfolio_policy_replay_research_surface",
        )
    validate_portfolio_policy_replay_research_surface_contract(contract)
    return contract


def validate_portfolio_policy_replay_research_surface_contract(
    contract: dict[str, Any],
) -> None:
    """Validate Phase88 surface contract and disabled runtime guards."""

    if int(contract.get("phase_id")) != 88:
        raise PortfolioPolicyReplayResearchSurfaceError("phase_id must be 88")
    if contract.get("status") != "active_research_surface_no_execution":
        raise PortfolioPolicyReplayResearchSurfaceError("unexpected Phase88 status")
    output = _mapping(contract.get("output_policy"), "output_policy")
    if output.get("output_mode") != "research_only_dashboard_surface":
        raise PortfolioPolicyReplayResearchSurfaceError("unexpected output mode")
    if output.get("research_only_label") != "RESEARCH ONLY":
        raise PortfolioPolicyReplayResearchSurfaceError("research label must be visible")
    template_ids = set(_string_list(contract.get("required_policy_templates")))
    if template_ids != REQUIRED_TEMPLATE_IDS:
        raise PortfolioPolicyReplayResearchSurfaceError(
            "required_policy_templates must match the eight governed templates",
        )
    if len(_string_list(contract.get("scenario_ids"))) != 5:
        raise PortfolioPolicyReplayResearchSurfaceError("scenario_ids must contain five rows")
    if len(_string_list(contract.get("renderer_caveats_zh"))) != 6:
        raise PortfolioPolicyReplayResearchSurfaceError("six renderer caveats required")
    for key, value in _mapping(contract.get("disabled_runtime_guards"), "guards").items():
        if bool(value):
            raise PortfolioPolicyReplayResearchSurfaceError(f"{key} must be false")


def build_portfolio_policy_replay_research_surface_view_model(
    path: str | Path = DEFAULT_SURFACE_PATH,
) -> dict[str, Any]:
    """Build a dashboard-ready research-only portfolio policy surface."""

    contract = load_portfolio_policy_replay_research_surface_contract(path)
    baseline = summarize_portfolio_policy_research_baseline()
    schedule = summarize_portfolio_policy_replay_schedule()
    schedule_contract = load_portfolio_policy_replay_schedule_contract()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    artifacts = summarize_research_backtest_artifacts()
    backtest_bundle = build_research_backtest_artifact_bundle()
    template_rows = _template_rows(baseline["templates"], schedule_contract.schedule_rows)
    scenario_rows = _scenario_policy_coverage_rows(
        contract["scenario_ids"],
        schedule_contract.schedule_rows,
    )
    view_model: dict[str, Any] = {
        "view_id": contract["view_id"],
        "view_model_version": contract["view_model_version"],
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "research_only_label": contract["output_policy"]["research_only_label"],
        "template_catalog_rows": template_rows,
        "replay_schedule_matrix_rows": [
            _schedule_matrix_row(row) for row in schedule_contract.schedule_rows
        ],
        "scenario_policy_coverage_rows": scenario_rows,
        "cost_turnover_assumption_rows": [
            _cost_turnover_row(row) for row in schedule_contract.schedule_rows
        ],
        "renderer_caveats_zh": contract["renderer_caveats_zh"],
        "policy_template_count": baseline["required_policy_template_count"],
        "replay_schedule_row_count": schedule["schedule_row_count"],
        "scenario_count": len(contract["scenario_ids"]),
        "scenario_policy_coverage_row_count": len(scenario_rows),
        "cost_assumption_visible_count": len(schedule_contract.schedule_rows),
        "turnover_status_visible_count": len(schedule_contract.schedule_rows),
        "renderer_caveat_count": len(contract["renderer_caveats_zh"]),
        "research_allocation_template_allowed": True,
        "research_allocation_template_count": baseline[
            "required_policy_template_count"
        ],
        "research_backtest_artifact_count": artifacts["research_backtest_artifact_count"],
        "metric_formula_reference_family_count": artifacts[
            "metric_formula_reference_family_count"
        ],
        "input_artifact_count": len(backtest_bundle["research_backtest_artifacts"]),
        "policy_replay_execution_count": schedule["portfolio_policy_replay_execution_count"],
        "backtest_execution_count": max(
            int(schedule["backtest_execution_count"]),
            int(kernel["backtest_execution_count"]),
        ),
        "metric_value_count": 0,
        "economic_performance_metric_count": 0,
        "current_allocation_recommendation_count": 0,
        "personalized_trade_instruction_count": 0,
        "trade_signal_output_count": 0,
        "public_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": contract["output_policy"]["allowed_uses"],
        "prohibited_uses": contract["output_policy"]["prohibited_uses"],
        "trust_metadata": {
            "surface_contract": contract["view_id"],
            "baseline_contract": baseline["contract_id"],
            "policy_schedule_contract": schedule["contract_id"],
            "cash_flow_kernel_contract": kernel["contract_id"],
            "research_backtest_artifact_contract": artifacts["contract_id"],
            "policy_replay_execution_enabled": False,
            "backtest_execution_enabled": False,
            "metric_value_computation_enabled": False,
            "current_allocation_recommendation_enabled": False,
            "research_allocation_template_display_allowed": True,
            "personalized_trade_instruction_enabled": False,
        },
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
    }
    summary = summarize_portfolio_policy_replay_research_surface(
        view_model=view_model,
        path=path,
    )
    view_model["portfolio_policy_replay_research_surface_ready"] = summary[
        "portfolio_policy_replay_research_surface_ready"
    ]
    return view_model


def summarize_portfolio_policy_replay_research_surface(
    path: str | Path = DEFAULT_SURFACE_PATH,
    *,
    view_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return Phase88 hard-gate summary fields."""

    contract = load_portfolio_policy_replay_research_surface_contract(path)
    view_model = view_model or build_portfolio_policy_replay_research_surface_view_model(path)
    prohibited_count = _recursive_key_count(
        view_model,
        set(contract["prohibited_fields"]),
    )
    summary: dict[str, Any] = {
        "phase": "88",
        "phase_id": 88,
        "portfolio_policy_replay_research_surface_ready": True,
        "template_catalog_ready": bool(view_model["template_catalog_rows"]),
        "replay_schedule_matrix_ready": bool(view_model["replay_schedule_matrix_rows"]),
        "cost_turnover_assumption_panel_ready": bool(
            view_model["cost_turnover_assumption_rows"],
        ),
        "scenario_policy_coverage_ready": bool(
            view_model["scenario_policy_coverage_rows"],
        ),
        "safety_caveat_panel_ready": len(view_model["renderer_caveats_zh"]) == 6,
        "no_advice_validator_ready": prohibited_count == 0,
        "policy_template_count": view_model["policy_template_count"],
        "research_allocation_template_allowed": view_model[
            "research_allocation_template_allowed"
        ],
        "research_allocation_template_count": view_model[
            "research_allocation_template_count"
        ],
        "replay_schedule_row_count": view_model["replay_schedule_row_count"],
        "scenario_count": view_model["scenario_count"],
        "scenario_policy_coverage_row_count": view_model[
            "scenario_policy_coverage_row_count"
        ],
        "cost_assumption_visible_count": view_model["cost_assumption_visible_count"],
        "turnover_status_visible_count": view_model["turnover_status_visible_count"],
        "renderer_caveat_count": view_model["renderer_caveat_count"],
        "policy_replay_execution_count": view_model["policy_replay_execution_count"],
        "backtest_execution_count": view_model["backtest_execution_count"],
        "metric_value_count": view_model["metric_value_count"],
        "economic_performance_metric_count": view_model[
            "economic_performance_metric_count"
        ],
        "current_allocation_recommendation_count": view_model[
            "current_allocation_recommendation_count"
        ],
        "personalized_trade_instruction_count": view_model[
            "personalized_trade_instruction_count"
        ],
        "trade_signal_output_count": view_model["trade_signal_output_count"],
        "prohibited_output_field_count": prohibited_count,
        "public_output_count": view_model["public_output_count"],
        "candidate_phase_emitted": view_model["candidate_phase_emitted"],
        "current_phase_emitted": view_model["current_phase_emitted"],
        "standalone_classifier_added_count": view_model[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": view_model[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": view_model["role_count_voting_added_count"],
        "production_behavior_change_count": view_model[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": view_model["semantic_drift_count"],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_policy_replay_surface_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_allocation_templates_ready_no_personalized_trade_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "policy_replay_surface_ready_no_execution_or_metric_values"
        ),
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 89,
        "phase88_surface_status": (
            "portfolio_policy_replay_research_surface_ready_no_execution"
        ),
    }
    summary["result"] = (
        "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    )
    summary["portfolio_policy_replay_research_surface_ready"] = (
        summary["result"] == "passed"
    )
    return summary


def _template_rows(
    templates: list[dict[str, Any]],
    schedule_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    schedule_by_template = {row["template_id"]: row for row in schedule_rows}
    rows: list[dict[str, Any]] = []
    for template in templates:
        schedule = schedule_by_template[template["template_id"]]
        rows.append(
            {
                "template_id": template["template_id"],
                "template_name_zh": template["description_zh"],
                "template_family": template["template_family"],
                "book_or_modern_classification": template["template_family"],
                "research_use_zh": template["description_zh"],
                "schedule_family": schedule["schedule_family"],
                "research_trigger_context_zh": schedule[
                    "research_trigger_context_zh"
                ],
                "required_transition_inputs": schedule["required_transition_inputs"],
                "execution_allowed_now": False,
                "current_allocation_recommendation_allowed": False,
                "trade_signal_allowed": False,
                "caveats_zh": schedule["caveats_zh"],
            },
        )
    return rows


def _schedule_matrix_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schedule_id": row["schedule_id"],
        "template_id": row["template_id"],
        "schedule_family": row["schedule_family"],
        "research_trigger_context_zh": row["research_trigger_context_zh"],
        "allowed_state_inputs": row["allowed_state_inputs"],
        "required_transition_inputs": row["required_transition_inputs"],
        "data_mode_policy": row["data_mode_policy"],
        "rebalance_clock_policy": row["rebalance_clock_policy"],
        "cost_assumption_policy": row["cost_assumption_policy"],
        "execution_allowed_now": False,
        "backtest_execution_allowed": False,
    }


def _cost_turnover_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": row["template_id"],
        "cost_assumption_policy": row["cost_assumption_policy"],
        "rebalance_clock_policy": row["rebalance_clock_policy"],
        "turnover_status": "not_computed_research_surface_only",
        "false_signal_cost_status": "not_computed_research_surface_only",
        "missed_recovery_cost_status": "not_computed_research_surface_only",
    }


def _scenario_policy_coverage_rows(
    scenario_ids: list[str],
    schedule_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario_id in scenario_ids:
        for schedule in schedule_rows:
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "template_id": schedule["template_id"],
                    "coverage_status": "mapped_for_future_replay_no_execution",
                    "data_mode_policy": schedule["data_mode_policy"],
                    "research_trigger_context_zh": schedule[
                        "research_trigger_context_zh"
                    ],
                    "execution_allowed_now": False,
                },
            )
    return rows


def _mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioPolicyReplayResearchSurfaceError(f"{field_name} must map")
    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise PortfolioPolicyReplayResearchSurfaceError("expected list[str]")
    return value


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(
            int(key in prohibited) + _recursive_key_count(item, prohibited)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())
