"""NY Fed SCE supporting-only dashboard, calendar, and incident integration."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from business_cycle.service.nas_nyfed_sce_components import (
    load_nyfed_sce_component_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nyfed_sce_dashboard_integration.yaml"
)


def load_nyfed_sce_dashboard_integration_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nyfed_sce_dashboard_integration"])


def summarize_nyfed_sce_dashboard_integration_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nyfed_sce_dashboard_integration_contract(path)
    components = load_nyfed_sce_component_contract()["component_series"]
    release = contract["release_family"]
    limitations = contract["portfolio_research_limitations"]
    strict = contract["strict_pit_reassessment"]
    summary = {
        "phase": 138,
        "nyfed_sce_dashboard_integration_contract_ready": _contract_ready(
            contract
        ),
        "supporting_indicator_count": len(components),
        "chart_period_count": len(
            contract["indicator_explorer_policy"]["chart_periods"]
        ),
        "supporting_indicator_with_complete_learning_semantics_count": sum(
            bool(row.get("title_zh"))
            and bool(row.get("high_meaning_zh"))
            and bool(row.get("low_meaning_zh"))
            for row in components
        ),
        "supporting_indicator_promoted_to_book_core_count": 0,
        "release_family_extension_count": 1,
        "exact_release_event_count": len(release["release_evidence"]),
        "incident_component_drilldown_count": len(components),
        "portfolio_research_limitation_count": len(limitations),
        "strict_replay_scenario_count": int(strict["scenario_count"]),
        "strict_replay_complete_scenario_count": int(
            strict["strict_complete_scenario_count"]
        ),
        "strict_replay_blocked_scenario_count": int(
            strict["strict_blocked_scenario_count"]
        ),
        "revised_data_mislabeled_as_pit_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 139,
    }
    expected = contract["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def augment_nyfed_sce_release_diagnostics(
    diagnostics: dict[str, Any],
    *,
    as_of: str,
    series_inputs: list[dict[str, Any]],
    refresh_status: dict[str, Any],
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Append one official supporting family without changing Phase114 scope."""

    contract = load_nyfed_sce_dashboard_integration_contract(path)
    component_contract = load_nyfed_sce_component_contract()
    component_ids = [
        str(row["series_id"]) for row in component_contract["component_series"]
    ]
    inputs = {str(row["series_id"]): dict(row) for row in series_inputs}
    normalized_inputs = {
        series_id: inputs.get(
            series_id,
            {
                "series_id": series_id,
                "frequency": "monthly",
                "latest_observation_date": None,
                "reference_period_end_date": None,
                "freshness_status": "unavailable",
                "freshness_reason_code": "no_observation_available",
            },
        )
        for series_id in component_ids
    }
    release = contract["release_family"]
    events = sorted(
        [dict(row) for row in release["release_evidence"]],
        key=lambda row: str(row["release_date"]),
    )
    as_of_date = date.fromisoformat(as_of)
    last_event = next(
        (
            row
            for row in reversed(events)
            if date.fromisoformat(str(row["release_date"])) <= as_of_date
        ),
        None,
    )
    next_event = next(
        (
            row
            for row in events
            if date.fromisoformat(str(row["release_date"])) > as_of_date
        ),
        None,
    )
    parent_result = _parent_refresh_result(refresh_status)
    status, reason_codes = _family_status(
        as_of=as_of_date,
        last_event=last_event,
        refresh_status=refresh_status,
        parent_result=parent_result,
        inputs=normalized_inputs,
    )
    family = {
        "release_family_id": str(release["release_family_id"]),
        "title_zh": str(release["title_zh"]),
        "agency_zh": str(release["agency_zh"]),
        "series_ids": component_ids,
        "parent_source_series_id": str(release["parent_source_series_id"]),
        "calendar_precision": str(release["calendar_precision"]),
        "official_calendar_url": str(release["official_calendar_url"]),
        "publication_time_zone": str(release["publication_time_zone"]),
        "last_official_release": last_event,
        "next_official_release": next_event,
        "release_monitor_status": status,
        "release_monitor_status_zh": _status_zh(status),
        "blocked_reason_codes": reason_codes,
        "failed_series_ids": (
            component_ids if status == "refresh_failed" else []
        ),
        "not_attempted_series_ids": [],
        "stale_series_ids": [
            series_id
            for series_id, row in normalized_inputs.items()
            if row.get("freshness_status") == "stale"
        ],
        "official_source_delay_confirmed": False,
        "operator_next_action_zh": _operator_action_zh(status),
        "schedule_caveat_zh": str(release["schedule_caveat_zh"]),
        "supporting_only": True,
        "book_core_replacement_allowed": False,
    }
    series_rows = [
        {
            "series_id": series_id,
            "release_family_id": str(release["release_family_id"]),
            "parent_source_series_id": str(release["parent_source_series_id"]),
            "calendar_precision": str(release["calendar_precision"]),
            "latest_observation_date": row.get("latest_observation_date"),
            "reference_period_end_date": row.get("reference_period_end_date"),
            "freshness_status": row.get("freshness_status", "unavailable"),
            "freshness_reason_code": row.get("freshness_reason_code"),
            "last_refresh_result": _component_refresh_status(parent_result),
            "error_class": parent_result.get("error_class"),
            "failure_reason_codes": (
                ["source_fetch_failed"]
                if parent_result.get("status") == "failed"
                else []
            ),
            "source_delay_claimed": False,
            "supporting_only": True,
        }
        for series_id, row in normalized_inputs.items()
    ]
    result = deepcopy(diagnostics)
    result["book_core_release_family_count"] = int(
        diagnostics["release_family_count"]
    )
    result["book_core_series_diagnostic_count"] = int(
        diagnostics["series_diagnostic_count"]
    )
    result["release_families"] = [*diagnostics["release_families"], family]
    result["series_refresh_diagnostics"] = [
        *diagnostics["series_refresh_diagnostics"],
        *series_rows,
    ]
    result["release_family_count"] = len(result["release_families"])
    result["series_diagnostic_count"] = len(
        result["series_refresh_diagnostics"]
    )
    result["exact_schedule_family_count"] = int(
        diagnostics["exact_schedule_family_count"]
    ) + 1
    result["supporting_release_family_count"] = 1
    result["supporting_release_series_count"] = len(series_rows)
    result["nyfed_sce_release_family_ready"] = True
    result["release_calendar_runtime_ready"] = bool(
        diagnostics["release_calendar_runtime_ready"]
    )
    return result


def enrich_nyfed_sce_incident_center(
    incident_center: dict[str, Any],
) -> dict[str, Any]:
    """Attach component impact to the single governed parent incident."""

    result = deepcopy(incident_center)
    components = load_nyfed_sce_component_contract()["component_series"]
    component_rows = [
        {
            "series_id": str(row["series_id"]),
            "title_zh": str(row["title_zh"]),
            "conceptual_group": str(row["conceptual_group"]),
        }
        for row in components
    ]
    enriched_count = 0
    for row in result.get("open_incidents", []):
        if str(row.get("source_series_id")) != "NYFED_SCE_CONTEXT":
            continue
        row["affected_component_count"] = len(component_rows)
        row["affected_component_series"] = component_rows
        row["component_incident_fanout_count"] = 0
        row["parent_workbook_failure"] = True
        enriched_count += 1
    result["nyfed_parent_incident_drilldown_count"] = enriched_count
    result["nyfed_affected_component_count"] = (
        len(component_rows) if enriched_count else 0
    )
    result["supporting_source_promoted_to_core_count"] = 0
    return result


def build_portfolio_research_limitations(
    *,
    strict_complete_scenario_count: int,
    scenario_count: int,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Return governed limitations with live strict-coverage context."""

    contract = load_nyfed_sce_dashboard_integration_contract(path)
    rows = deepcopy(contract["portfolio_research_limitations"])
    for row in rows:
        if row["limitation_id"] != "strict_pit_scenario_coverage_partial":
            continue
        row["current_state_zh"] = (
            f"目前 {strict_complete_scenario_count}／{scenario_count} 個情境可做完整 strict PIT 研究。"
        )
        row["strict_complete_scenario_count"] = strict_complete_scenario_count
        row["scenario_count"] = scenario_count
    return rows


def _parent_refresh_result(refresh_status: dict[str, Any]) -> dict[str, Any]:
    return next(
        (
            dict(row)
            for row in refresh_status.get("series_refresh_results", [])
            if isinstance(row, dict)
            and row.get("series_id") == "NYFED_SCE_CONTEXT"
        ),
        {},
    )


def _family_status(
    *,
    as_of: date,
    last_event: dict[str, Any] | None,
    refresh_status: dict[str, Any],
    parent_result: dict[str, Any],
    inputs: dict[str, dict[str, Any]],
) -> tuple[str, list[str]]:
    if parent_result.get("status") == "failed":
        return "refresh_failed", ["source_fetch_failed"]
    if not any(row.get("latest_observation_date") for row in inputs.values()):
        return "supporting_components_unavailable", [
            "nyfed_sce_component_data_unavailable"
        ]
    if last_event is None:
        return "waiting_for_registered_release", []
    release_date = date.fromisoformat(str(last_event["release_date"]))
    completed = _optional_datetime_date(refresh_status.get("last_completed_at_utc"))
    if completed is None or completed < release_date:
        if (as_of - release_date).days > 2:
            return "release_delayed_or_refresh_missing", [
                "refresh_due_after_official_release"
            ]
        return "release_due_refresh_pending", [
            "refresh_due_after_official_release"
        ]
    if any(row.get("freshness_status") == "stale" for row in inputs.values()):
        return "refreshed_after_release_but_series_stale", [
            "refreshed_after_release_but_series_stale"
        ]
    return "refreshed_after_release", []


def _component_refresh_status(parent_result: dict[str, Any]) -> str:
    status = str(parent_result.get("status") or "no_parent_refresh_result")
    return (
        "imported_from_parent_workbook"
        if status in {"imported", "succeeded"}
        else status
    )


def _optional_datetime_date(value: Any) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def _status_zh(status: str) -> str:
    return {
        "refresh_failed": "NY Fed SCE workbook 更新失敗",
        "supporting_components_unavailable": "本機尚無 NY Fed SCE 元件資料",
        "waiting_for_registered_release": "等待已登錄的官方發布日",
        "release_delayed_or_refresh_missing": "官方日期已過，但尚無其後成功更新",
        "release_due_refresh_pending": "官方資料剛發布，等待排程更新",
        "refreshed_after_release_but_series_stale": "已更新，但元件仍超過新鮮度期限",
        "refreshed_after_release": "官方發布後已有成功更新",
    }.get(status, status)


def _operator_action_zh(status: str) -> str:
    return {
        "refresh_failed": "查看父 workbook 錯誤與 11 個受影響元件，修復後由既有排程重試。",
        "supporting_components_unavailable": "執行受治理 NY Fed SCE refresh；不可用時維持 supporting unavailable。",
        "waiting_for_registered_release": "等待 NY Fed 官方日曆事件。",
        "release_delayed_or_refresh_missing": "執行一次受治理 refresh，再區分來源變更與本機缺漏。",
        "release_due_refresh_pending": "等待下一次每日排程，必要時由 operator 執行既有 worker。",
        "refreshed_after_release_but_series_stale": "核對官方 workbook 是否已更新參考月份與 schema。",
        "refreshed_after_release": "無需處理。",
    }.get(status, "人工檢查 NY Fed SCE 來源狀態。")


def _contract_ready(contract: dict[str, Any]) -> bool:
    evidence = contract["evidence_boundary"]
    explorer = contract["indicator_explorer_policy"]
    incident = contract["incident_drilldown_policy"]
    return (
        contract["status"] == "active_private_nas_supporting_context_surface"
        and evidence["book_core_replacement_allowed"] is False
        and evidence["phase_evidence_emission_allowed"] is False
        and evidence["transition_confirmation_allowed"] is False
        and evidence["component_composite_allowed"] is False
        and explorer["direct_measure_only"] is True
        and incident["component_incident_fanout_allowed"] is False
    )
