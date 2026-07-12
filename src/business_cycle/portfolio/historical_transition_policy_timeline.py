"""Historical event annotations and fixed-weight policy sensitivity research."""

from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
)
from business_cycle.validation.historical_pit_transition_events import (
    build_historical_pit_transition_event_registry,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/historical_transition_policy_timeline.yaml"
)


def load_historical_transition_policy_timeline_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["historical_transition_policy_timeline"])


def build_historical_transition_policy_timeline(
    phase125_artifact: dict[str, Any],
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build research annotations without feeding historical labels to runtime."""

    contract = load_historical_transition_policy_timeline_contract(contract_path)
    manifest = load_historical_validation_scenario_manifest()
    evidence_rows = list(phase125_artifact.get("evidence_replay_rows", []))
    event_registry = build_historical_pit_transition_event_registry(
        evidence_rows=evidence_rows
    )
    evidence_by_key = {
        (str(row["scenario_id"]), str(row["as_of"])): row
        for row in evidence_rows
    }
    events_by_scenario: dict[str, list[dict[str, Any]]] = {}
    for event in event_registry["event_rows"]:
        events_by_scenario.setdefault(str(event["scenario_id"]), []).append(event)

    annotations: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    chronology = contract["reference_chronology"]["scenario_turning_points"]
    for scenario in manifest["scenario_rows"]:
        scenario_id = str(scenario["scenario_id"])
        months = _month_ends(
            str(scenario["validation_window_start"]),
            str(scenario["validation_window_end"]),
        )
        pit_status = str(event_registry["scenario_status"][scenario_id]["pit_status"])
        scenario_annotations = []
        for as_of in months:
            evidence = evidence_by_key.get((scenario_id, as_of), {})
            active_events = [
                dict(event)
                for event in events_by_scenario.get(scenario_id, [])
                if str(event["event_start"]) <= as_of <= str(event["event_end"])
            ]
            reference = _reference_annotation(
                as_of=as_of,
                chronology=dict(chronology[scenario_id]),
                annotation_policy=contract["annotation_policy"],
            )
            row = {
                "scenario_id": scenario_id,
                "as_of": as_of,
                "data_mode": "vintage_as_of",
                **reference,
                "transition_watch_annotations": _lane_annotations(
                    evidence, suffix="_watch"
                ),
                "transition_confirmation_annotations": _lane_annotations(
                    evidence, suffix="_confirmation"
                ),
                "event_annotations": active_events,
                "shock_annotation_present": any(
                    event["event_type"] == "shock" for event in active_events
                ),
                "uncertainty_annotation_present": any(
                    event["event_type"] == "uncertainty_window"
                    for event in active_events
                ),
                "pit_status": pit_status,
                "strict_evidence_replay_executed": bool(evidence),
                "historical_label_runtime_input": False,
                "book_policy_state_caused_transition": False,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
            annotations.append(row)
            scenario_annotations.append(row)
        scenario_rows.append(
            {
                "scenario_id": scenario_id,
                "monthly_annotation_count": len(scenario_annotations),
                "pit_status": pit_status,
                "annotation_status": (
                    "governed_annotation_ready"
                    if pit_status == "strict_complete"
                    else "governed_annotation_with_explicit_pit_blocker"
                ),
                "nber_recession_annotation_month_count": sum(
                    row["reference_cycle_state"] == "recession"
                    for row in scenario_annotations
                ),
                "book_policy_annotation_month_count": sum(
                    row["book_policy_requirement_id"] is not None
                    for row in scenario_annotations
                ),
            }
        )

    sensitivity = _fixed_weight_sensitivity(
        list(phase125_artifact.get("research_backtest_results", [])),
        contract=contract,
    )
    summary: dict[str, Any] = {
        "artifact_id": "phase133_historical_transition_policy_timeline_v1",
        "phase": 133,
        "phase_id": 133,
        "research_only": True,
        "historical_transition_policy_timeline_ready": True,
        "scenario_count": len(scenario_rows),
        "monthly_annotation_count": len(annotations),
        "scenario_with_annotation_or_blocker_count": len(scenario_rows),
        "strict_complete_scenario_count": sum(
            row["pit_status"] == "strict_complete" for row in scenario_rows
        ),
        "explicit_pit_blocked_scenario_count": sum(
            row["pit_status"] != "strict_complete" for row in scenario_rows
        ),
        "nber_recession_annotation_month_count": sum(
            row["reference_cycle_state"] == "recession" for row in annotations
        ),
        "book_policy_annotation_month_count": sum(
            row["book_policy_requirement_id"] is not None for row in annotations
        ),
        "fixed_weight_sensitivity_result_count": len(sensitivity),
        "cash_flow_metric_provenance_complete_count": sum(
            bool(row["metric_provenance"]) for row in sensitivity
        ),
        "recovery_cost_result_count": sum(
            row["missed_recovery_opportunity_cost_percent"] is not None
            for row in sensitivity
        ),
        "false_derisk_cost_result_count": sum(
            row["false_derisk_opportunity_cost_percent"] is not None
            for row in sensitivity
        ),
        "book_policy_state_transition_cause_count": 0,
        "fixed_weight_result_rule_tuning_count": 0,
        "best_historical_result_selected_count": 0,
        "historical_label_runtime_usage_count": 0,
        "personalized_instruction_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "semantic_drift_count": 0,
        "scenario_rows": scenario_rows,
        "monthly_annotations": annotations,
        "fixed_weight_sensitivity_rows": sensitivity,
        "source_reference": dict(contract["reference_chronology"]),
        "trust_metadata": {
            "historical_labels_are_annotations_only": True,
            "nber_expansion_not_mapped_to_book_subphase": True,
            "strict_revised_fallback_allowed": False,
            "cash_flow_kernel_source": "phase125_cash_flow_research_backtest",
            "fixed_weight_results_used_for_rule_tuning": False,
            "best_historical_result_selected": False,
        },
        "allowed_uses": [
            "historical_event_annotation",
            "book_policy_rule_replay_research",
            "fixed_weight_sensitivity_comparison",
        ],
        "prohibited_uses": [
            "runtime_phase_input",
            "transition_rule_tuning",
            "current_allocation_instruction",
            "historical_best_weight_selection",
            "trade_action",
        ],
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary


def _reference_annotation(
    *, as_of: str, chronology: dict[str, Any], annotation_policy: dict[str, Any]
) -> dict[str, Any]:
    if chronology.get("no_declared_us_recession_in_window"):
        return {
            "reference_cycle_state": annotation_policy["no_recession_label"],
            "reference_phase_age_month": None,
            "book_policy_requirement_id": None,
            "book_policy_equity_parameter_percent": None,
            "annotation_reason_zh": "此研究窗沒有 NBER 宣告的美國衰退；不推論書籍四階段子階段。",
        }
    peak = _month_end(str(chronology["peak_month"]))
    trough = _month_end(str(chronology["trough_month"]))
    recession_start = _next_month_end(peak)
    if recession_start <= as_of <= trough:
        return {
            "reference_cycle_state": "recession",
            "reference_phase_age_month": _month_distance(recession_start, as_of) + 1,
            "book_policy_requirement_id": annotation_policy[
                "book_recession_policy_requirement_id"
            ],
            "book_policy_equity_parameter_percent": annotation_policy[
                "book_recession_equity_parameter_percent"
            ],
            "annotation_reason_zh": "NBER peak 後至 trough 的事後衰退註解；僅供歷史研究。",
        }
    return {
        "reference_cycle_state": annotation_policy["unknown_book_subphase_label"],
        "reference_phase_age_month": None,
        "book_policy_requirement_id": None,
        "book_policy_equity_parameter_percent": None,
        "annotation_reason_zh": "NBER expansion 無法單獨判定復甦、成長或榮景，故不硬套書籍權重。",
    }


def _lane_annotations(evidence: dict[str, Any], *, suffix: str) -> list[dict[str, str]]:
    return [
        {"lane_id": str(lane_id), "evidence_state": str(state)}
        for lane_id, state in sorted(dict(evidence.get("lane_states", {})).items())
        if str(lane_id).endswith(suffix)
    ]


def _fixed_weight_sensitivity(
    results: list[dict[str, Any]], *, contract: dict[str, Any]
) -> list[dict[str, Any]]:
    policy = contract["sensitivity_policy"]
    included = set(policy["included_parameter_ids"])
    order = {value: index for index, value in enumerate(policy["parameter_order"])}
    selected = [row for row in results if str(row["parameter_id"]) in included]
    selected.sort(key=lambda row: (str(row["scenario_id"]), order[str(row["parameter_id"])]))
    baselines = {
        str(row["scenario_id"]): row
        for row in selected
        if row["parameter_id"] == "passive_equity_100"
    }
    chronology = contract["reference_chronology"]["scenario_turning_points"]
    rows = []
    for source in selected:
        scenario_id = str(source["scenario_id"])
        baseline = baselines[scenario_id]
        turning = dict(chronology[scenario_id])
        has_recession = not turning.get("no_declared_us_recession_in_window", False)
        rows.append(
            {
                "result_id": source["result_id"],
                "scenario_id": scenario_id,
                "parameter_id": source["parameter_id"],
                "equity_parameter_percent": source["equity_parameter_percent"],
                "defensive_asset": source["defensive_asset"],
                "defensive_parameter_percent": source["defensive_parameter_percent"],
                "annualized_time_weighted_return": source["metrics"][
                    "annualized_time_weighted_return"
                ],
                "money_weighted_return_xirr": source["metrics"][
                    "money_weighted_return_xirr"
                ],
                "max_drawdown_on_unitized_nav": source["metrics"][
                    "max_drawdown_on_unitized_nav"
                ],
                "drawdown_recovery_months": _drawdown_recovery_months(
                    list(source["monthly_rows"])
                ),
                "turnover": source["metrics"]["turnover"],
                "transaction_cost_total": source["metrics"][
                    "transaction_cost_total"
                ],
                "missed_recovery_opportunity_cost_percent": (
                    _missed_recovery_cost(source, baseline, turning)
                    if has_recession
                    else None
                ),
                "false_derisk_opportunity_cost_percent": (
                    _relative_return_gap(source, baseline)
                    if not has_recession
                    else None
                ),
                "metric_provenance": {
                    "source_result_id": source["result_id"],
                    "source_scope": source["result_scope"],
                    "source_data_mode": source["data_mode"],
                    "unitized_nav_row_count": len(source["monthly_rows"]),
                    "cash_flow_kernel": "phase125_cash_flow_research_backtest",
                },
                "result_used_for_rule_tuning": False,
                "selected_as_best_historical_result": False,
                "current_allocation_instruction_allowed": False,
            }
        )
    return rows


def _drawdown_recovery_months(rows: list[dict[str, Any]]) -> int | None:
    if not rows:
        return None
    peak = float(rows[0]["unitized_nav"])
    trough_index = 0
    trough_ratio = 1.0
    peak_before_trough = peak
    for index, row in enumerate(rows):
        value = float(row["unitized_nav"])
        if value > peak:
            peak = value
        ratio = value / peak
        if ratio < trough_ratio:
            trough_ratio = ratio
            trough_index = index
            peak_before_trough = peak
    if trough_ratio == 1.0:
        return 0
    for index in range(trough_index + 1, len(rows)):
        if float(rows[index]["unitized_nav"]) >= peak_before_trough:
            return index - trough_index
    return None


def _missed_recovery_cost(
    source: dict[str, Any], baseline: dict[str, Any], turning: dict[str, Any]
) -> float | None:
    trough = _month_end(str(turning["trough_month"]))
    source_return = _nav_return_after(source, trough)
    baseline_return = _nav_return_after(baseline, trough)
    if source_return is None or baseline_return is None:
        return None
    return round(max(0.0, baseline_return - source_return) * 100.0, 4)


def _nav_return_after(result: dict[str, Any], anchor: str) -> float | None:
    rows = [row for row in result["monthly_rows"] if str(row["as_of"]) >= anchor]
    if len(rows) < 2:
        return None
    return float(rows[-1]["unitized_nav"]) / float(rows[0]["unitized_nav"]) - 1.0


def _relative_return_gap(source: dict[str, Any], baseline: dict[str, Any]) -> float:
    gap = float(baseline["metrics"]["time_weighted_return"]) - float(
        source["metrics"]["time_weighted_return"]
    )
    return round(max(0.0, gap) * 100.0, 4)


def _month_ends(start: str, end: str) -> list[str]:
    cursor = date.fromisoformat(start).replace(day=1)
    end_date = date.fromisoformat(end)
    rows = []
    while cursor <= end_date:
        month_end = cursor.replace(day=calendar.monthrange(cursor.year, cursor.month)[1])
        if month_end >= date.fromisoformat(start) and month_end <= end_date:
            rows.append(month_end.isoformat())
        cursor = (
            cursor.replace(year=cursor.year + 1, month=1)
            if cursor.month == 12
            else cursor.replace(month=cursor.month + 1)
        )
    return rows


def _month_end(label: str) -> str:
    year, month = (int(value) for value in label.split("-"))
    return date(year, month, calendar.monthrange(year, month)[1]).isoformat()


def _next_month_end(label: str) -> str:
    current = date.fromisoformat(label)
    year, month = (current.year + 1, 1) if current.month == 12 else (current.year, current.month + 1)
    return date(year, month, calendar.monthrange(year, month)[1]).isoformat()


def _month_distance(start: str, end: str) -> int:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    return (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
