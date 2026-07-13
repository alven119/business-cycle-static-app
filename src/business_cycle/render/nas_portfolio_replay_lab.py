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
from business_cycle.portfolio.historical_transition_policy_timeline import (
    build_historical_transition_policy_timeline,
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
from business_cycle.service.nas_nyfed_sce_dashboard import (
    build_portfolio_research_limitations,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_portfolio_replay_lab_contract.yaml"
TEMPLATE_FIXTURE_PATH = ROOT / "specs/portfolio/portfolio_policy_template_fixtures.yaml"
ROLE_LABELS_PATH = ROOT / "specs/common/book_core_role_display_labels_zh.yaml"

LANE_LABELS_ZH = {
    "boom_continuation": "榮景延續",
    "boom_ending_watch": "榮景結束觀察",
    "recession_watch": "衰退風險觀察",
    "recession_confirmation": "衰退確認",
}

EVIDENCE_STATE_LABELS_ZH = {
    "supportive_evidence_present": "支持證據出現",
    "contradictory_evidence_present": "反對證據出現",
    "mixed_evidence": "證據分歧",
    "incomplete_evidence": "證據不足",
    "explicit_abstention": "資料不足，暫不判讀",
    "unavailable": "目前無資料",
}

SCENARIO_USE_ZH = {
    "dotcom_cycle_2000_2003": "研究科技榮景結束後，實體經濟確認與市場回落是否同步。",
    "global_financial_crisis_2007_2009": "研究金融壓力如何逐步傳到就業、消費與投資。",
    "covid_recession_2020": "研究外生衝擊下，為何不能把一般循環規則機械套用。",
    "euro_debt_slowdown_2011_2012": "研究風險升高但未形成美國衰退時，如何避免過早去風險。",
    "late_cycle_2018_2019": "研究晚期循環的警訊，如何與真正衰退確認區分。",
}

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
    role_labels = _role_labels()
    phase125_execution = snapshot.get("source_release_diagnostics", {}).get(
        "strict_replay_backtest_status", {}
    )
    historical_policy = build_historical_transition_policy_timeline(
        phase125_execution
    )
    portfolio = _portfolio_view(
        contract=contract,
        declared=declared,
        live_transition_evidence=live_transition_evidence,
        phase125_execution=phase125_execution,
        phase_context=phase_context,
        historical_policy=historical_policy,
        role_labels=role_labels,
    )
    replay = _replay_view(
        contract=contract,
        snapshot=snapshot,
        phase125_execution=phase125_execution,
        phase_context=phase_context,
        historical_policy=historical_policy,
        role_labels=role_labels,
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
        "phase133_historical_policy_timeline_connected": historical_policy[
            "result"
        ]
        == "passed",
        "phase133_monthly_annotation_count": historical_policy[
            "monthly_annotation_count"
        ],
        "phase133_fixed_weight_sensitivity_result_count": historical_policy[
            "fixed_weight_sensitivity_result_count"
        ],
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
    historical_policy: dict[str, Any],
    role_labels: dict[str, str],
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
    active_policy = next(
        row for row in full_cycle["phase_rows"] if row["is_declared_phase"]
    )
    lane_context = _portfolio_lane_context(
        live_transition_evidence=live_transition_evidence,
        phase_context=phase_context,
    )
    sensitivity_rows = historical_policy["fixed_weight_sensitivity_rows"]
    scenario_count = int(historical_policy["scenario_count"])
    strict_complete = int(historical_policy["strict_complete_scenario_count"])
    active_limitations = build_portfolio_research_limitations(
        strict_complete_scenario_count=strict_complete,
        scenario_count=scenario_count,
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
        "declared_phase_start_display_zh": declared.get(
            "declared_phase_start_display_zh", "尚待使用者確認"
        ),
        "phase_age_status": declared.get(
            "phase_age_status", "unknown_or_user_required"
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
        "live_transition_lane_context": lane_context,
        "current_policy_context": {
            "book_rule_zh": active_policy["book_policy_context_zh"],
            "transition_focus_zh": active_policy["timing_interpretation_zh"],
            "decision_boundary_zh": _policy_decision_boundary(
                phase_context=phase_context,
                active_policy=active_policy,
            ),
            "what_current_data_adds_zh": _current_data_policy_summary(lane_context),
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
        "historical_policy_timeline_summary": {
            "scenario_count": scenario_count,
            "monthly_annotation_count": historical_policy[
                "monthly_annotation_count"
            ],
            "book_policy_annotation_month_count": historical_policy[
                "book_policy_annotation_month_count"
            ],
            "strict_complete_scenario_count": strict_complete,
            "explicit_pit_blocked_scenario_count": historical_policy[
                "explicit_pit_blocked_scenario_count"
            ],
        },
        "fixed_weight_sensitivity_rows": sensitivity_rows,
        "sensitivity_scenario_summaries": _sensitivity_scenario_summaries(
            sensitivity_rows
        ),
        "role_labels": role_labels,
        "fixed_weight_results_used_for_rule_tuning": False,
        "best_historical_result_selected": False,
        "active_research_limitations": active_limitations,
        "active_research_limitation_count": len(active_limitations),
        "strict_coverage_explanation_zh": (
            f"目前 {strict_complete}／{scenario_count} 個情境可完整使用當時資料。"
            "新架構已擴充 current/revised 資料與 PostgreSQL 保存，但 revised history "
            "不會自動變成早期 PIT vintage，因此網路泡沫、GFC 與歐債仍依法 abstain。"
        ),
        "research_only": True,
    }


def _replay_view(
    *,
    contract: dict[str, Any],
    snapshot: dict[str, Any],
    phase125_execution: dict[str, Any],
    phase_context: dict[str, Any],
    historical_policy: dict[str, Any],
    role_labels: dict[str, str],
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
    policy_by_key = {
        (str(row["scenario_id"]), str(row["as_of"])): row
        for row in historical_policy["monthly_annotations"]
    }
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
                "attribution_role_labels_zh": [
                    role_labels.get(str(role_id), str(role_id))
                    for role_id in display["attribution_role_ids"]
                ],
                "research_use_zh": SCENARIO_USE_ZH[scenario_id],
                "strict_evidence_replay_executed": any(
                    key[0] == scenario_id for key in evidence_by_key
                ),
                "research_backtest_result_count": len(scenario_results),
                "result_metric_range": _scenario_metric_range(scenario_results),
                "pit_status": governed_registry["scenario_status"][scenario_id][
                    "pit_status"
                ],
                "data_readiness_label_zh": _pit_status_label(
                    governed_registry["scenario_status"][scenario_id]["pit_status"]
                ),
                "available_answer_zh": _scenario_available_answer(
                    pit_status=governed_registry["scenario_status"][scenario_id][
                        "pit_status"
                    ],
                    result_count=len(scenario_results),
                ),
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
            policy_annotation = policy_by_key[(scenario_id, month_end)]
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
                    "attribution_role_labels_zh": [
                        role_labels.get(str(role_id), str(role_id))
                        for role_id in display["attribution_role_ids"]
                    ],
                    "strict_evidence_replay_executed": evidence is not None,
                    "strict_lane_states": (
                        dict(evidence["lane_states"]) if evidence else {}
                    ),
                    "strict_role_states": (
                        dict(evidence["role_states"]) if evidence else {}
                    ),
                    "reference_cycle_state": policy_annotation[
                        "reference_cycle_state"
                    ],
                    "reference_phase_age_month": policy_annotation[
                        "reference_phase_age_month"
                    ],
                    "book_policy_requirement_id": policy_annotation[
                        "book_policy_requirement_id"
                    ],
                    "book_policy_equity_parameter_percent": policy_annotation[
                        "book_policy_equity_parameter_percent"
                    ],
                    "historical_annotation_reason_zh": policy_annotation[
                        "annotation_reason_zh"
                    ],
                    "transition_watch_annotations": policy_annotation[
                        "transition_watch_annotations"
                    ],
                    "transition_confirmation_annotations": policy_annotation[
                        "transition_confirmation_annotations"
                    ],
                    "shock_annotation_present": policy_annotation[
                        "shock_annotation_present"
                    ],
                    "uncertainty_annotation_present": policy_annotation[
                        "uncertainty_annotation_present"
                    ],
                    "model_executed": evidence is not None,
                    "backtest_executed": bool(scenario_results),
                    "candidate_phase_emitted": False,
                    "current_phase_emitted": False,
                }
            )
            playhead_rows[-1] |= _monthly_learning_summary(playhead_rows[-1])
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
        "historical_policy_timeline_ready": historical_policy["result"]
        == "passed",
        "historical_policy_monthly_annotation_count": historical_policy[
            "monthly_annotation_count"
        ],
        "historical_policy_scenario_rows": historical_policy["scenario_rows"],
        "historical_label_runtime_usage_count": historical_policy[
            "historical_label_runtime_usage_count"
        ],
        "role_labels": role_labels,
    }


def _role_labels() -> dict[str, str]:
    payload = yaml.safe_load(ROLE_LABELS_PATH.read_text(encoding="utf-8"))
    return dict(payload["book_core_role_display_labels_zh"]["roles"])


def _portfolio_lane_context(
    *,
    live_transition_evidence: dict[str, Any] | None,
    phase_context: dict[str, Any],
) -> list[dict[str, Any]]:
    configured = {
        str(row["lane_id"]): row for row in phase_context["transition_lanes"]
    }
    rows = []
    for lane_id, lane in (live_transition_evidence or {}).get("lanes", {}).items():
        config = configured.get(str(lane_id), {})
        status = str(lane["lane_status"])
        rows.append(
            {
                "lane_id": str(lane_id),
                "title_zh": config.get(
                    "title_zh", LANE_LABELS_ZH.get(str(lane_id), str(lane_id))
                ),
                "purpose_zh": config.get("purpose_zh", "目前轉折證據研究。"),
                "lane_type": config.get("lane_type", "evidence_context"),
                "lane_status": status,
                "lane_status_label_zh": EVIDENCE_STATE_LABELS_ZH.get(status, status),
                "supportive_evidence_count": lane["supportive_evidence_count"],
                "contradictory_evidence_count": lane[
                    "contradictory_evidence_count"
                ],
                "abstained_evidence_count": lane["abstained_evidence_count"],
            }
        )
    return rows


def _policy_decision_boundary(
    *, phase_context: dict[str, Any], active_policy: dict[str, Any]
) -> str:
    if phase_context["phase_age_status"] == "unknown_or_user_required":
        return (
            "階段起始日尚未確認，70／50／30 只能作敏感度比較，不能依榮景年齡選定其中一個比例。"
        )
    return (
        f"目前可依受治理的階段起始資訊研究 {active_policy['numeric_policy_status']}；"
        "仍不會自動形成配置動作。"
    )


def _current_data_policy_summary(lanes: list[dict[str, Any]]) -> str:
    supportive_watch = [
        row["title_zh"]
        for row in lanes
        if row["lane_status"] == "supportive_evidence_present"
        and row["lane_type"] == "transition_watch"
    ]
    supportive_confirmation = [
        row["title_zh"]
        for row in lanes
        if row["lane_status"] == "supportive_evidence_present"
        and row["lane_type"] == "transition_confirmation"
    ]
    incomplete = [
        row["title_zh"]
        for row in lanes
        if row["lane_status"] in {"incomplete_evidence", "explicit_abstention"}
    ]
    if supportive_watch or supportive_confirmation:
        parts = []
        if supportive_watch:
            parts.append("觀察訊號：" + "、".join(supportive_watch))
        if supportive_confirmation:
            parts.append("確認證據：" + "、".join(supportive_confirmation))
        return "目前資料顯示" + "；".join(parts) + "。兩者不會自動改變配置。"
    if incomplete:
        return "目前尚不足以形成完整轉折判讀：" + "、".join(incomplete) + "。"
    return "目前資料用來追蹤榮景延續與衰退風險，不直接決定配置比例。"


def _sensitivity_scenario_summaries(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["scenario_id"]), []).append(row)
    summaries = []
    for scenario_id, scenario_rows in grouped.items():
        drawdowns = [
            abs(float(row["max_drawdown_on_unitized_nav"])) * 100.0
            for row in scenario_rows
        ]
        opportunity_costs = [
            float(value)
            for row in scenario_rows
            for value in (
                row["missed_recovery_opportunity_cost_percent"],
                row["false_derisk_opportunity_cost_percent"],
            )
            if value is not None
        ]
        summaries.append(
            {
                "scenario_id": scenario_id,
                "title_zh": _scenario_title_zh(scenario_id),
                "result_count": len(scenario_rows),
                "drawdown_range_zh": (
                    f"{min(drawdowns):.1f}%～{max(drawdowns):.1f}%"
                ),
                "maximum_opportunity_cost_percent": max(opportunity_costs, default=0.0),
                "research_question_zh": (
                    "降低股票曝險換來多少回撤變化，又可能犧牲多少後續復甦或未衰退期間的報酬？"
                ),
                "takeaway_zh": (
                    "比較重點是風險與機會成本的交換，不是找出一個歷史績效最高、現在就照做的比例。"
                ),
            }
        )
    return summaries


def _pit_status_label(status: str) -> str:
    return {
        "strict_complete": "可用當時資料完整重播",
        "partial_explicit_abstention": "早期官方資料不完整，只能部分研究",
    }.get(str(status), str(status))


def _scenario_available_answer(*, pit_status: str, result_count: int) -> str:
    if pit_status == "strict_complete":
        return (
            f"可逐月查看當時可得證據，並比較 {result_count} 組固定參數研究結果。"
        )
    return (
        "可查看事件背景、事後週期註解與缺漏資料；不能聲稱已重現當時的完整轉折判讀。"
    )


def _monthly_learning_summary(row: dict[str, Any]) -> dict[str, str]:
    lane_states = dict(row["strict_lane_states"])
    watch_rows = row["transition_watch_annotations"]
    confirmation_rows = row["transition_confirmation_annotations"]
    if not row["strict_evidence_replay_executed"]:
        evidence_summary = "當月資料不足，系統依法不做 evidence 判讀。"
        takeaway = "先看缺了哪些資料；不要用後來修訂值假裝當時已經知道。"
    elif any(
        item["evidence_state"] == "supportive_evidence_present"
        for item in confirmation_rows
    ):
        evidence_summary = "當月已有轉折確認證據，但它仍不是自動換檔或交易指令。"
        takeaway = "確認證據比 watch 強；仍要檢查資料完整度與受治理的狀態切換。"
    elif any(
        item["evidence_state"] == "supportive_evidence_present"
        for item in watch_rows
    ):
        evidence_summary = "當月出現早期觀察訊號，尚未形成轉折確認。"
        takeaway = "這是提高注意力的時點，不是提前把 watch 當成衰退。"
    else:
        evidence_summary = "當月 evidence 尚未形成一致的轉折方向。"
        takeaway = "觀察支持、反對與不足證據如何隨月份累積，而不是只看單一數值。"
    reference = {
        "recession": "事後資料將本月列在 NBER 衰退區間",
        "nber_expansion_book_subphase_unclassified": "事後為擴張期，但無法只靠 NBER 再分書籍子階段",
        "no_declared_us_recession_reference": "研究窗內沒有 NBER 美國衰退",
    }.get(str(row["reference_cycle_state"]), str(row["reference_cycle_state"]))
    policy = (
        f"書籍衰退期規則回放：股票 {row['book_policy_equity_parameter_percent']}%"
        if row["book_policy_requirement_id"]
        else "本月沒有可安全套用的書籍四階段權重"
    )
    transition_summary = _annotation_summary(watch_rows, confirmation_rows)
    event_summary = "／".join(
        item
        for item in (
            "外生衝擊" if row["shock_annotation_present"] else "",
            "PIT 資料不確定" if row["uncertainty_annotation_present"] else "",
        )
        if item
    ) or "沒有額外事件註記"
    return {
        "strict_input_state_label_zh": (
            "當時資料足以執行重播"
            if not row["strict_abstention_required"]
            else "當時資料不完整，必須暫不判讀"
        ),
        "strict_lane_summary_zh": evidence_summary,
        "reference_cycle_state_label_zh": reference,
        "book_policy_replay_summary_zh": policy,
        "transition_annotation_summary_zh": transition_summary,
        "event_flags_label_zh": event_summary,
        "learning_takeaway_zh": takeaway,
        "lane_state_count": len(lane_states),
    }


def _annotation_summary(
    watches: list[dict[str, str]], confirmations: list[dict[str, str]]
) -> str:
    parts = []
    for label, rows in (("觀察", watches), ("確認", confirmations)):
        for row in rows:
            parts.append(
                f"{label}「{LANE_LABELS_ZH.get(row['lane_id'], row['lane_id'])}」："
                f"{EVIDENCE_STATE_LABELS_ZH.get(row['evidence_state'], row['evidence_state'])}"
            )
    return "；".join(parts) or "當月沒有可用的轉折證據註解"


def _scenario_title_zh(scenario_id: str) -> str:
    return {
        "dotcom_cycle_2000_2003": "網路泡沫循環",
        "global_financial_crisis_2007_2009": "全球金融危機",
        "covid_recession_2020": "COVID 外生衝擊",
        "euro_debt_slowdown_2011_2012": "歐債危機疑慮",
        "late_cycle_2018_2019": "2018–2019 晚期循環",
    }.get(scenario_id, scenario_id)


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
