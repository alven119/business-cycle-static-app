"""Portfolio/replay dashboard surface for Phase81."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)
from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)
from business_cycle.portfolio.research_backtest_artifacts import (
    PROHIBITED_BACKTEST_ARTIFACT_FIELDS,
    build_research_backtest_artifact_bundle,
    summarize_research_backtest_artifacts,
)
from business_cycle.validation.historical_replay_runner import (
    summarize_historical_replay_runner_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SURFACE_CONTRACT_PATH = (
    ROOT / "specs/common/portfolio_replay_dashboard_surface.yaml"
)


class PortfolioReplayDashboardSurfaceError(ValueError):
    """Raised when the Phase81 dashboard surface contract is invalid."""


def load_portfolio_replay_dashboard_surface_contract(
    path: str | Path = DEFAULT_SURFACE_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load and validate the Phase81 dashboard surface contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioReplayDashboardSurfaceError("contract YAML must be a mapping")
    contract = payload.get("portfolio_replay_dashboard_surface")
    if not isinstance(contract, dict):
        raise PortfolioReplayDashboardSurfaceError(
            "YAML must contain portfolio_replay_dashboard_surface",
        )
    validate_portfolio_replay_dashboard_surface_contract(contract)
    return contract


def validate_portfolio_replay_dashboard_surface_contract(
    contract: dict[str, Any],
) -> None:
    """Validate Phase81 dashboard surface fields and disabled guards."""

    if int(contract.get("phase_id")) != 81:
        raise PortfolioReplayDashboardSurfaceError("phase_id must be 81")
    if contract.get("status") != "active_research_dashboard_surface_no_public_output":
        raise PortfolioReplayDashboardSurfaceError("unexpected Phase81 status")
    dashboard = contract.get("dashboard_view_model")
    if not isinstance(dashboard, dict):
        raise PortfolioReplayDashboardSurfaceError("dashboard_view_model must exist")
    if dashboard.get("output_mode") != "research_only_dashboard_surface":
        raise PortfolioReplayDashboardSurfaceError("unexpected output mode")
    if dashboard.get("research_only_label") != "RESEARCH ONLY":
        raise PortfolioReplayDashboardSurfaceError("research_only_label must be visible")
    required_sections = dashboard.get("required_sections")
    if not isinstance(required_sections, list) or len(required_sections) < 6:
        raise PortfolioReplayDashboardSurfaceError("required_sections incomplete")
    missing = PROHIBITED_BACKTEST_ARTIFACT_FIELDS - set(
        dashboard.get("prohibited_fields") or [],
    )
    if missing:
        raise PortfolioReplayDashboardSurfaceError(
            f"prohibited_fields missing: {', '.join(sorted(missing))}",
        )
    for key, value in contract.get("disabled_runtime_guards", {}).items():
        if bool(value):
            raise PortfolioReplayDashboardSurfaceError(f"{key} must be false")


def build_portfolio_replay_dashboard_surface_view_model(
    path: str | Path = DEFAULT_SURFACE_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a local dashboard surface from Phase77-80 research artifacts."""

    contract = load_portfolio_replay_dashboard_surface_contract(path)
    replay = summarize_historical_replay_runner_preview()
    schedule = summarize_portfolio_policy_replay_schedule()
    kernel = summarize_cash_flow_backtest_kernel_contract()
    artifacts = summarize_research_backtest_artifacts()
    bundle = build_research_backtest_artifact_bundle()
    artifact_rows = bundle["research_backtest_artifacts"]
    view_model = {
        "view_id": contract["view_id"],
        "view_model_version": contract["view_model_version"],
        "output_mode": contract["dashboard_view_model"]["output_mode"],
        "research_only": True,
        "research_only_label": contract["dashboard_view_model"][
            "research_only_label"
        ],
        "scenario_count": replay["scenario_count"],
        "replay_data_mode_count": replay["replay_data_mode_count"],
        "research_backtest_artifact_count": artifacts[
            "research_backtest_artifact_count"
        ],
        "dashboard_cards": [_dashboard_card(row) for row in artifact_rows],
        "lineage_drilldown_rows": [_lineage_row(row) for row in artifact_rows],
        "policy_schedule_summary": {
            "contract_id": schedule["contract_id"],
            "template_with_schedule_count": schedule["template_with_schedule_count"],
            "execution_allowed_now_count": schedule["execution_allowed_now_count"],
            "policy_replay_execution_count": schedule[
                "portfolio_policy_replay_execution_count"
            ],
        },
        "cash_flow_kernel_summary": {
            "contract_id": kernel["contract_id"],
            "kernel_component_count": kernel["kernel_component_count"],
            "execution_allowed_now_count": kernel["execution_allowed_now_count"],
            "backtest_execution_count": kernel["backtest_execution_count"],
        },
        "metric_formula_reference_family_count": artifacts[
            "metric_formula_reference_family_count"
        ],
        "metric_value_count": 0,
        "risk_metric_value_count": 0,
        "backtest_execution_count": 0,
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "public_output_count": 0,
        "prohibited_output_field_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "source_contract": contract["view_id"],
            "phase80_artifact_contract": artifacts["contract_id"],
            "historical_replay_runner_ready": replay["historical_replay_runner_ready"],
            "policy_replay_schedule_contract_ready": schedule[
                "portfolio_policy_replay_schedule_contract_ready"
            ],
            "cash_flow_kernel_contract_ready": kernel[
                "cash_flow_aware_backtest_kernel_contract_ready"
            ],
            "research_only_label_visible": True,
            "metric_values_computed": False,
            "dashboard_public_output": False,
        },
        "caveats_zh": [
            "此頁只呈現 historical replay/backtest research artifacts。",
            "所有 metric formula 只作為未來計算參考；本階段沒有 metric values。",
            "此頁不得用於目前配置、交易動作、production decision 或模型調參。",
        ],
    }
    summary = summarize_portfolio_replay_dashboard_surface(view_model=view_model)
    view_model["portfolio_replay_dashboard_surface_ready"] = (
        summary["portfolio_replay_dashboard_surface_ready"]
    )
    return view_model


def summarize_portfolio_replay_dashboard_surface(
    path: str | Path = DEFAULT_SURFACE_CONTRACT_PATH,
    *,
    view_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return compact hard-gate fields for the Phase81 dashboard surface."""

    contract = load_portfolio_replay_dashboard_surface_contract(path)
    view_model = view_model or build_portfolio_replay_dashboard_surface_view_model(path)
    summary: dict[str, Any] = {
        "phase": "81",
        "phase_id": 81,
        "portfolio_replay_dashboard_surface_ready": True,
        "portfolio_replay_dashboard_view_model_ready": True,
        "portfolio_replay_dashboard_bundle_integration_ready": True,
        "portfolio_replay_dashboard_runtime_preview_ready": True,
        "research_only_label_visible": (
            view_model.get("research_only_label") == "RESEARCH ONLY"
        ),
        "scenario_count": view_model["scenario_count"],
        "replay_data_mode_count": view_model["replay_data_mode_count"],
        "research_backtest_artifact_count": view_model[
            "research_backtest_artifact_count"
        ],
        "dashboard_card_count": len(view_model["dashboard_cards"]),
        "lineage_drilldown_row_count": len(view_model["lineage_drilldown_rows"]),
        "policy_schedule_reference_count": sum(
            bool(row["source_policy_schedule_contract_id"])
            for row in view_model["lineage_drilldown_rows"]
        ),
        "cash_flow_kernel_reference_count": sum(
            bool(row["source_cash_flow_kernel_contract_id"])
            for row in view_model["lineage_drilldown_rows"]
        ),
        "metric_formula_reference_family_count": view_model[
            "metric_formula_reference_family_count"
        ],
        "metric_value_count": view_model["metric_value_count"],
        "risk_metric_value_count": view_model["risk_metric_value_count"],
        "backtest_execution_count": view_model["backtest_execution_count"],
        "current_allocation_recommendation_count": view_model[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": view_model["trade_signal_output_count"],
        "public_output_count": view_model["public_output_count"],
        "prohibited_output_field_count": _recursive_key_count(
            view_model,
            PROHIBITED_BACKTEST_ARTIFACT_FIELDS,
        ),
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
            "declared_state_preserved_portfolio_replay_dashboard_surface_ready"
        ),
        "portfolio_policy_research_alignment": (
            "dashboard_surface_ready_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "dashboard_surface_ready_research_artifacts_only"
        ),
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 82,
        "phase81_closure_status": (
            "closed_portfolio_replay_dashboard_surface_ready_research_only"
        ),
    }
    summary["result"] = (
        "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    )
    summary["portfolio_replay_dashboard_surface_ready"] = (
        summary["result"] == "passed"
    )
    return summary


def _dashboard_card(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": row["artifact_id"],
        "scenario_id": row["scenario_id"],
        "data_mode": row["data_mode"],
        "window": f"{row['validation_window_start']} to {row['validation_window_end']}",
        "artifact_status": "research_only_ready_no_metric_values",
        "policy_replay_reference_status": row["policy_replay_reference_status"],
        "cash_flow_kernel_reference_status": row["cash_flow_kernel_reference_status"],
        "metric_formula_ref_count": len(row["metric_formula_refs"]),
        "metric_value_status": "not_computed_phase80",
        "abstention_expected": row["trust_metadata"]["abstention_expected"],
        "input_hash": row["input_hash"],
        "caveats_zh": row["caveats_zh"],
    }


def _lineage_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": row["artifact_id"],
        "source_replay_row_id": row["source_replay_row_id"],
        "source_replay_runner_contract_id": row[
            "source_replay_runner_contract_id"
        ],
        "source_policy_schedule_contract_id": row[
            "source_policy_schedule_contract_id"
        ],
        "source_cash_flow_kernel_contract_id": row[
            "source_cash_flow_kernel_contract_id"
        ],
        "source_metric_formula_registry_id": row[
            "source_metric_formula_registry_id"
        ],
        "input_hash": row["input_hash"],
        "source_contract_hash_count": len(
            row["provenance"]["source_contract_hashes"],
        ),
        "blocked_reason_codes": row["provenance"][
            "source_replay_row_blocked_reason_codes"
        ],
    }


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
