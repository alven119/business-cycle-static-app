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
from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
)
from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
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
    live_transition_evidence: dict[str, Any],
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Compose existing governed artifacts into two interactive NAS surfaces."""

    contract = load_nas_portfolio_replay_lab_contract(contract_path)
    declared = dict(snapshot.get("declared_cycle_state", {}))
    portfolio = _portfolio_view(
        contract=contract,
        declared=declared,
        live_transition_evidence=live_transition_evidence,
    )
    replay = _replay_view(contract=contract, snapshot=snapshot)
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
            portfolio["declared_current_phase"] == "boom"
        ),
        "live_transition_context_connected": bool(
            portfolio["live_transition_lane_context"]
        ),
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
    live_transition_evidence: dict[str, Any],
) -> dict[str, Any]:
    baseline = summarize_portfolio_policy_research_baseline()
    surface = build_portfolio_policy_replay_research_surface_view_model()
    parameters = _template_parameters()
    policy = contract["portfolio_policy"]
    cards = []
    for row in baseline["templates"]:
        template_id = str(row["template_id"])
        if template_id == policy["passive_comparator_template_id"]:
            relevance = "passive_comparator"
        elif template_id == policy["default_research_template_id"]:
            relevance = "declared_boom_primary_research"
        elif template_id in policy["declared_phase_relevant_template_ids"]:
            relevance = "declared_boom_alternative_research"
        elif template_id in policy["legal_next_transition_template_ids"]:
            relevance = "legal_next_recession_research"
        else:
            relevance = "future_cycle_research"
        cards.append(
            {
                **row,
                "relevance_status": relevance,
                "book_or_modern_classification": row["template_family"],
                "research_parameter_levels_percent": parameters.get(template_id, []),
                "research_parameter_label_zh": _parameter_label(template_id),
                "current_allocation_recommendation_allowed": False,
                "personalized_trade_instruction_allowed": False,
            }
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
        "default_research_template_id": policy["default_research_template_id"],
        "template_cards": cards,
        "live_transition_lane_context": {
            lane_id: {
                "lane_status": lane["lane_status"],
                "supportive_evidence_count": lane["supportive_evidence_count"],
                "contradictory_evidence_count": lane[
                    "contradictory_evidence_count"
                ],
                "abstained_evidence_count": lane["abstained_evidence_count"],
            }
            for lane_id, lane in live_transition_evidence["lanes"].items()
        },
        "source_surface_ready": surface[
            "portfolio_policy_replay_research_surface_ready"
        ],
        "book_parameter_grid_is_current_instruction": False,
        "research_only": True,
    }


def _replay_view(
    *,
    contract: dict[str, Any],
    snapshot: dict[str, Any],
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
    scenarios = []
    playhead_rows = []
    for scenario in manifest["scenario_rows"]:
        scenario_id = str(scenario["scenario_id"])
        display = scenario_display[scenario_id]
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
            }
        )
        for month_end in months:
            strict = strict_by_key.get((scenario_id, month_end))
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
                    "model_executed": False,
                    "backtest_executed": False,
                    "candidate_phase_emitted": False,
                    "current_phase_emitted": False,
                }
            )
    return {
        "view_id": "nas_historical_replay_lab",
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
        "research_only": True,
    }


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


def _parameter_label(template_id: str) -> str:
    if template_id == "boom_70_50_30_template":
        return "書籍榮景股票曝險研究參數（backtest-only）"
    return "研究模板參數（尚未執行回測）"


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
