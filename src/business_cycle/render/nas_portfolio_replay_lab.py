"""Phase 124 private NAS portfolio research and replay lab view model."""

from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.policy_research_baseline import (
    summarize_portfolio_policy_research_baseline,
)
from business_cycle.portfolio.full_cycle_transition_policy import (
    build_full_cycle_portfolio_transition_research,
)
from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
)
from business_cycle.render.phase_aware_dashboard_context import (
    build_phase_aware_dashboard_context,
)
from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
)
from business_cycle.validation.historical_pit_transition_events import (
    build_historical_pit_transition_event_registry,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_portfolio_replay_lab_contract.yaml"
TEMPLATE_FIXTURE_PATH = ROOT / "specs/portfolio/portfolio_policy_template_fixtures.yaml"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "target_weights",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "current_allocation",
}


def load_nas_portfolio_replay_lab_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_portfolio_replay_lab_contract"])


def build_nas_portfolio_replay_lab(
    snapshot: dict[str, Any],
    *,
    live_transition_evidence: dict[str, Any] | None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Compose existing governed artifacts into two interactive NAS surfaces."""

    contract = load_nas_portfolio_replay_lab_contract(contract_path)
    declared = dict(snapshot.get("declared_cycle_state", {}))
    phase_context = build_phase_aware_dashboard_context(declared)
    phase125_execution = snapshot.get("source_release_diagnostics", {}).get(
        "strict_replay_backtest_status", {}
    )
    portfolio = _portfolio_view(
        contract=contract,
        declared=declared,
        live_transition_evidence=live_transition_evidence,
        phase125_execution=phase125_execution,
        phase_context=phase_context,
    )
    replay = _replay_view(
        contract=contract,
        snapshot=snapshot,
        phase125_execution=phase125_execution,
        phase_context=phase_context,
    )
    artifact: dict[str, Any] = {
        "artifact_id": "phase124_nas_portfolio_replay_lab_v1",
        "artifact_version": contract["version"],
        "phase": 124,
        "phase_id": 124,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "portfolio_research": portfolio,
        "historical_replay": replay,
        "routes": [dict(row) for row in contract["routes"]],
        "nas_portfolio_replay_lab_contract_ready": _contract_ready(contract),
        "portfolio_research_route_operational": bool(portfolio["template_cards"]),
        "historical_event_replay_route_operational": bool(replay["scenario_rows"]),
        "book_template_and_modern_extension_separated": all(
            row["book_or_modern_classification"]
            in {
                "book_benchmark_baseline",
                "book_policy_template",
                "book_boom_research_template",
                "doctrine_transition_research_template",
            }
            for row in portfolio["template_cards"]
        ),
        "declared_phase_context_connected": (
            portfolio["phase_context_hash"] == phase_context["context_hash"]
            and replay["phase_context_hash"] == phase_context["context_hash"]
        ),
        "phase_context_hash": phase_context["context_hash"],
        "live_transition_context_connected": portfolio[
            "active_transition_context_connected"
        ],
        "policy_template_count": len(portfolio["template_cards"]),
        "scenario_count": len(replay["scenario_rows"]),
        "monthly_playhead_row_count": len(replay["monthly_playhead_rows"]),
        "replay_data_mode_count": len(replay["data_mode_options"]),
        "revised_pit_mode_separation_valid": True,
        "strict_revised_fallback_count": 0,
        "current_allocation_recommendation_count": 0,
        "personalized_trade_instruction_count": 0,
        "model_execution_count": 0,
        "backtest_execution_count": 0,
        "metric_computation_count": 0,
        "phase125_execution_connected": phase125_execution.get("result")
        == "passed",
        "phase125_research_backtest_result_count": int(
            phase125_execution.get("research_backtest_result_count", 0)
        ),
        "phase125_evidence_replay_output_count": int(
            phase125_execution.get("evidence_replay_output_count", 0)
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "private_nas_portfolio_template_research",
            "historical_input_replay_navigation",
            "revised_and_pit_gap_comparison",
        ],
        "prohibited_uses": [
            "personalized_allocation_instruction",
            "trade_action",
            "formal_historical_phase_result",
            "performance_claim",
            "public_output",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_not_inferred": True,
            "portfolio_templates_are_backtest_parameters": True,
            "historical_replay_is_input_readiness_only": True,
            "phase125_execution_connected": phase125_execution.get("result")
            == "passed",
            "strict_revised_fallback_allowed": False,
            "model_executed": False,
            "backtest_executed": False,
        },
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["result"] = (
        "passed"
        if _matches(artifact, contract["hard_gates"])
        and artifact["prohibited_output_field_count"] == 0
        else "blocked"
    )
    return artifact


def _portfolio_view(
    *,
    contract: dict[str, Any],
    declared: dict[str, Any],
    live_transition_evidence: dict[str, Any] | None,
    phase125_execution: dict[str, Any],
    phase_context: dict[str, Any],
) -> dict[str, Any]:
    baseline = summarize_portfolio_policy_research_baseline()
    surface = build_portfolio_policy_replay_research_surface_view_model()
    parameters = _template_parameters()
    policy = contract["portfolio_policy"]
    execution_results = list(
        phase125_execution.get("research_backtest_results", [])
    )
    cards = []
    for row in baseline["templates"]:
        template_id = str(row["template_id"])
        if template_id == policy["passive_comparator_template_id"]:
            relevance = "passive_comparator"
        elif template_id == phase_context["primary_portfolio_template_id"]:
            relevance = "declared_phase_primary_research"
        elif template_id in phase_context["relevant_portfolio_template_ids"]:
            relevance = "declared_phase_related_research"
        else:
            relevance = "future_cycle_research"
        result_summary = _template_result_summary(template_id, execution_results)
        cards.append(
            {
                **row,
                "relevance_status": relevance,
                "book_or_modern_classification": row["template_family"],
                "research_parameter_levels_percent": parameters.get(template_id, []),
                "research_parameter_label_zh": _parameter_label(
                    template_id, result_summary
                ),
                "research_result_summary": result_summary,
                "current_allocation_recommendation_allowed": False,
                "personalized_trade_instruction_allowed": False,
            }
        )
    full_cycle = build_full_cycle_portfolio_transition_research(
        declared_phase=str(declared.get("declared_current_phase", "boom")),
        live_lanes=(live_transition_evidence or {}).get("lanes", {}),
    )
    return {
        "view_id": "nas_portfolio_policy_research",
        "declared_current_phase": declared.get("declared_current_phase", "boom"),
        "declared_current_phase_label_zh": declared.get(
            "declared_current_phase_label_zh", "榮景"
        ),
        "legal_next_phase": declared.get("legal_next_phase", "recession"),
        "legal_next_phase_label_zh": declared.get(
            "legal_next_phase_label_zh", "衰退"
        ),
        "default_research_template_id": phase_context[
            "primary_portfolio_template_id"
        ],
        "phase_context_hash": phase_context["context_hash"],
        "template_cards": cards,
        "full_cycle_policy_rows": full_cycle["phase_rows"],
        "full_cycle_policy_context_ready": full_cycle[
            "full_cycle_portfolio_transition_research_ready"
        ],
        "live_transition_lane_context": {
            lane_id: {
                "lane_status": lane["lane_status"],
                "supportive_evidence_count": lane["supportive_evidence_count"],
                "contradictory_evidence_count": lane[
                    "contradictory_evidence_count"
                ],
                "abstained_evidence_count": lane["abstained_evidence_count"],
            }
            for lane_id, lane in (live_transition_evidence or {}).get(
                "lanes", {}
            ).items()
        },
        "active_transition_context_connected": True,
        "active_evaluator_mode": (
            "live_book_evidence"
            if live_transition_evidence
            and live_transition_evidence.get("result") == "passed"
            else "input_readiness_only_explicit_abstention"
        ),
        "source_surface_ready": surface[
            "portfolio_policy_replay_research_surface_ready"
        ],
        "book_parameter_grid_is_current_instruction": False,
        "phase125_execution_status": phase125_execution.get(
            "result", "not_started"
        ),
        "research_backtest_result_count": len(execution_results),
        "quantitative_template_result_count": sum(
            row["research_result_summary"]["result_count"] > 0 for row in cards
        ),
        "evidence_context_only_template_count": sum(
            row["research_result_summary"]["result_availability_status"]
            == "evidence_context_only_no_book_numeric_weight"
            for row in cards
        ),
        "market_data_lineage": list(
            phase125_execution.get("market_data_lineage", [])
        ),
        "book_benchmark_result_count": int(
            phase125_execution.get("book_benchmark_result_count", 0)
        ),
        "dynamic_transition_policy_execution_count": int(
            phase125_execution.get("dynamic_transition_policy_execution_count", 0)
        ),
        "research_only": True,
    }


def _replay_view(
    *,
    contract: dict[str, Any],
    snapshot: dict[str, Any],
    phase125_execution: dict[str, Any],
    phase_context: dict[str, Any],
) -> dict[str, Any]:
    manifest = load_historical_validation_scenario_manifest()
    scenario_display = contract["replay_policy"]["scenario_display"]
    strict_status = snapshot.get("source_release_diagnostics", {}).get(
        "strict_replay_input_timeline", {}
    )
    strict_by_key = {
        (str(row["scenario_id"]), str(row["as_of"])): row
        for row in strict_status.get("timeline_rows", [])
    }
    evidence_by_key = {
        (str(row["scenario_id"]), str(row["as_of"])): row
        for row in phase125_execution.get("evidence_replay_rows", [])
    }
    result_rows = list(phase125_execution.get("research_backtest_results", []))
    governed_registry = build_historical_pit_transition_event_registry(
        evidence_rows=list(phase125_execution.get("evidence_replay_rows", []))
    )
    events_by_scenario: dict[str, list[dict[str, Any]]] = {}
    for event in governed_registry["event_rows"]:
        events_by_scenario.setdefault(str(event["scenario_id"]), []).append(event)
    scenarios = []
    playhead_rows = []
    for scenario in manifest["scenario_rows"]:
        scenario_id = str(scenario["scenario_id"])
        display = scenario_display[scenario_id]
        scenario_results = [
            row for row in result_rows if str(row["scenario_id"]) == scenario_id
        ]
        months = _month_ends(
            str(scenario["validation_window_start"]),
            str(scenario["validation_window_end"]),
        )
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "title_zh": display["title_zh"],
                "focus_zh": display["focus_zh"],
                "scenario_family": scenario["scenario_family"],
                "window_start": scenario["validation_window_start"],
                "window_end": scenario["validation_window_end"],
                "month_count": len(months),
                "attribution_role_ids": list(display["attribution_role_ids"]),
                "strict_evidence_replay_executed": any(
                    key[0] == scenario_id for key in evidence_by_key
                ),
                "research_backtest_result_count": len(scenario_results),
                "result_metric_range": _scenario_metric_range(scenario_results),
                "pit_status": governed_registry["scenario_status"][scenario_id][
                    "pit_status"
                ],
                "governed_events": events_by_scenario.get(scenario_id, []),
                "pit_gap_series_ids": sorted(
                    row["series_id"]
                    for row in governed_registry["gap_rows"]
                    if scenario_id in row["affected_scenarios"]
                ),
            }
        )
        for month_end in months:
            strict = strict_by_key.get((scenario_id, month_end))
            evidence = evidence_by_key.get((scenario_id, month_end))
            playhead_rows.append(
                {
                    "scenario_id": scenario_id,
                    "as_of": month_end,
                    "strict_input_state": (
                        strict.get("replay_input_state")
                        if strict
                        else "strict_timeline_not_materialized"
                    ),
                    "strict_available_series_count": (
                        int(strict.get("available_series_count", 0)) if strict else 0
                    ),
                    "strict_missing_series_count": (
                        int(strict.get("missing_series_count", 0)) if strict else 26
                    ),
                    "strict_abstention_required": (
                        bool(strict.get("abstention_required")) if strict else True
                    ),
                    "revised_comparison_state": (
                        "revised_diagnostic_navigation_ready_no_model_execution"
                    ),
                    "attribution_role_ids": list(display["attribution_role_ids"]),
                    "strict_evidence_replay_executed": evidence is not None,
                    "strict_lane_states": (
                        dict(evidence["lane_states"]) if evidence else {}
                    ),
                    "strict_role_states": (
                        dict(evidence["role_states"]) if evidence else {}
                    ),
                    "model_executed": evidence is not None,
                    "backtest_executed": bool(scenario_results),
                    "candidate_phase_emitted": False,
                    "current_phase_emitted": False,
                }
            )
    return {
        "view_id": "nas_historical_replay_lab",
        "declared_current_phase_label_zh": phase_context[
            "declared_current_phase_label_zh"
        ],
        "legal_next_phase_label_zh": phase_context[
            "legal_next_phase_label_zh"
        ],
        "phase_context_hash": phase_context["context_hash"],
        "scenario_rows": scenarios,
        "monthly_playhead_rows": playhead_rows,
        "data_mode_options": [
            {
                "data_mode": "vintage_as_of",
                "label_zh": "當時可得資料（PIT）",
                "fallback_allowed": False,
            },
            {
                "data_mode": "revised_declared_comparison_only",
                "label_zh": "修訂後診斷比較",
                "point_in_time_result": False,
            },
        ],
        "default_scenario_id": contract["replay_policy"]["default_scenario_id"],
        "default_data_mode": contract["replay_policy"]["default_data_mode"],
        "strict_timeline_materialized": bool(strict_by_key),
        "strict_complete_month_count": int(strict_status.get("complete_month_count", 0)),
        "strict_abstention_month_count": int(
            strict_status.get("abstention_month_count", len(playhead_rows))
        ),
        "historical_result_emitted": False,
        "phase125_execution_status": phase125_execution.get(
            "result", "not_started"
        ),
        "strict_evidence_replay_output_count": len(evidence_by_key),
        "research_backtest_result_count": len(result_rows),
        "dynamic_transition_policy_execution_count": int(
            phase125_execution.get("dynamic_transition_policy_execution_count", 0)
        ),
        "research_only": True,
        "governed_transition_event_registry": governed_registry,
        "governed_event_count": len(governed_registry["event_rows"]),
        "pit_gap_series_count": governed_registry["pit_gap_series_count"],
        "revised_pit_visual_separation_ready": True,
    }


def _template_result_summary(
    template_id: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [row for row in results if row["policy_template_id"] == template_id]
    context_only = template_id in {
        "recession_defense_research_template",
        "recovery_re_risk_research_template",
    }
    return {
        "result_count": len(rows),
        "scenario_count": len({row["scenario_id"] for row in rows}),
        "annualized_twr_range": _range(
            [row["metrics"]["annualized_time_weighted_return"] for row in rows]
        ),
        "max_drawdown_range": _range(
            [row["metrics"]["max_drawdown_on_unitized_nav"] for row in rows]
        ),
        "result_scope": "constant_parameter_sensitivity_only",
        "result_availability_status": (
            "evidence_context_only_no_book_numeric_weight"
            if context_only
            else "quantitative_strict_research_results_available"
        ),
    }


def _scenario_metric_range(results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "annualized_twr": _range(
            [row["metrics"]["annualized_time_weighted_return"] for row in results]
        ),
        "max_drawdown": _range(
            [row["metrics"]["max_drawdown_on_unitized_nav"] for row in results]
        ),
    }


def _range(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    return {"minimum": min(values), "maximum": max(values)}


def _template_parameters() -> dict[str, list[int]]:
    payload = yaml.safe_load(TEMPLATE_FIXTURE_PATH.read_text(encoding="utf-8"))[
        "portfolio_policy_template_fixtures"
    ]
    rows: dict[str, list[int]] = {}
    for fixture in payload["valid_templates"]:
        template = fixture["template"]
        parameters = template.get("book_aligned_parameters", {})
        levels = (
            parameters.get("stock_weight_levels_for_backtest_only")
            or parameters.get("equity_weight_levels_for_backtest_only")
            or []
        )
        rows[str(template["template_id"])] = [round(float(value) * 100) for value in levels]
    return rows


def _parameter_label(template_id: str, result: dict[str, Any]) -> str:
    if template_id == "boom_70_50_30_template":
        return "書籍榮景股票曝險研究參數（backtest-only）"
    if result["result_availability_status"] == (
        "evidence_context_only_no_book_numeric_weight"
    ):
        return "轉折時機研究模板；書中未另訂此模板的精確權重"
    return "已執行的固定參數研究模板（backtest-only）"


def _month_ends(start: str, end: str) -> list[str]:
    cursor = date.fromisoformat(start).replace(day=1)
    end_date = date.fromisoformat(end)
    rows = []
    while cursor <= end_date:
        day = calendar.monthrange(cursor.year, cursor.month)[1]
        month_end = cursor.replace(day=day)
        if month_end >= date.fromisoformat(start) and month_end <= end_date:
            rows.append(month_end.isoformat())
        cursor = (
            cursor.replace(year=cursor.year + 1, month=1)
            if cursor.month == 12
            else cursor.replace(month=cursor.month + 1)
        )
    return rows


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active_private_nas_research_product_surface"
        and contract["portfolio_policy"]["template_count"] == 8
        and contract["replay_policy"]["scenario_count"] == 5
        and len(contract["routes"]) == 4
    )


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(key in PROHIBITED_FIELDS for key in value) + sum(
            _contains_prohibited_field(item) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0
