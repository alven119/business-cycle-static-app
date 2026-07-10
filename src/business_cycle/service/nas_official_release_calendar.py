"""Official release-calendar and refresh-failure diagnostics for the private NAS."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_official_release_calendar_contract.yaml"


def load_nas_official_release_calendar_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_official_release_calendar_contract"])


def summarize_nas_official_release_calendar_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_official_release_calendar_contract(path)
    families = list(contract["release_families"])
    direct_series = _direct_series_ids()
    mapped = [str(series_id) for row in families for series_id in row["series_ids"]]
    summary = {
        "phase": 114,
        "nas_official_release_calendar_contract_ready": _contract_ready(contract),
        "direct_series_count": len(direct_series),
        "release_family_count": len(families),
        "exact_schedule_family_count": _precision_count(families, "exact_schedule"),
        "cadence_only_family_count": _precision_count(families, "cadence_only"),
        "reference_only_family_count": _precision_count(families, "reference_only"),
        "series_without_release_family_count": len(set(direct_series) - set(mapped)),
        "duplicate_series_mapping_count": len(mapped) - len(set(mapped)),
        "observation_date_assumed_release_date_count": 0,
        "official_delay_claim_without_exact_schedule_count": 0,
        "refresh_failure_reason_count": len(contract["failure_reason_taxonomy"]),
        "private_source_operations_route_count": 2,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 115,
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


def build_nas_official_release_diagnostics(
    *,
    as_of: str,
    series_inputs: list[dict[str, Any]],
    refresh_status: dict[str, Any],
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build per-family diagnostics without inferring release dates from observations."""

    contract = load_nas_official_release_calendar_contract(path)
    as_of_date = date.fromisoformat(as_of)
    inputs = {str(row["series_id"]): dict(row) for row in series_inputs}
    expected = set(_direct_series_ids())
    if set(inputs) != expected:
        missing = sorted(expected - set(inputs))
        unexpected = sorted(set(inputs) - expected)
        raise ValueError(
            f"release diagnostic series coverage mismatch: missing={missing}, "
            f"unexpected={unexpected}"
        )
    refresh_results = _refresh_results_by_series(refresh_status)
    family_rows = [
        _family_diagnostic(
            family=dict(family),
            as_of=as_of_date,
            inputs=inputs,
            refresh_status=refresh_status,
            refresh_results=refresh_results,
            grace_days=int(contract["operations_policy"]["release_refresh_grace_days"]),
        )
        for family in contract["release_families"]
    ]
    series_rows = [
        _series_diagnostic(
            series_id=series_id,
            family=family,
            source_input=inputs[series_id],
            refresh_status=refresh_status,
            refresh_result=refresh_results.get(series_id),
        )
        for family in contract["release_families"]
        for series_id in family["series_ids"]
    ]
    failed = [row for row in series_rows if row["failure_reason_codes"]]
    due = [
        row
        for row in family_rows
        if row["release_monitor_status"]
        in {"release_due_refresh_pending", "release_delayed_or_refresh_missing"}
    ]
    diagnostics: dict[str, Any] = {
        "artifact_id": "phase114_nas_official_release_calendar_diagnostics",
        "artifact_version": contract["version"],
        "phase": 114,
        "as_of": as_of,
        "data_mode": "revised_diagnostic",
        "research_only": True,
        "release_families": family_rows,
        "series_refresh_diagnostics": series_rows,
        "release_family_count": len(family_rows),
        "series_diagnostic_count": len(series_rows),
        "exact_schedule_family_count": sum(
            row["calendar_precision"] == "exact_schedule" for row in family_rows
        ),
        "family_due_or_missing_refresh_count": len(due),
        "series_with_failure_reason_count": len(failed),
        "official_source_delay_confirmed_count": 0,
        "observation_date_assumed_release_date_count": 0,
        "refresh_failure_separated_from_source_delay": True,
        "label_used_by_runtime_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "private_source_operations_dashboard",
            "release_due_review",
            "refresh_failure_triage",
        ],
        "prohibited_uses": contract["prohibited_outputs"],
    }
    diagnostics["release_calendar_runtime_ready"] = (
        len(family_rows) == 12
        and len(series_rows) == 26
        and diagnostics["observation_date_assumed_release_date_count"] == 0
        and diagnostics["official_source_delay_confirmed_count"] == 0
    )
    diagnostics["result"] = (
        "passed" if diagnostics["release_calendar_runtime_ready"] else "blocked"
    )
    return diagnostics


def _family_diagnostic(
    *,
    family: dict[str, Any],
    as_of: date,
    inputs: dict[str, dict[str, Any]],
    refresh_status: dict[str, Any],
    refresh_results: dict[str, dict[str, Any]],
    grace_days: int,
) -> dict[str, Any]:
    events = sorted(
        (dict(row) for row in family.get("scheduled_releases", [])),
        key=lambda row: row["release_date"],
    )
    last_event = next(
        (row for row in reversed(events) if date.fromisoformat(row["release_date"]) <= as_of),
        None,
    )
    next_event = next(
        (row for row in events if date.fromisoformat(row["release_date"]) > as_of),
        None,
    )
    series_ids = [str(value) for value in family["series_ids"]]
    failed = [
        series_id
        for series_id in series_ids
        if refresh_results.get(series_id, {}).get("status") == "failed"
    ]
    missing_after_failure = [
        series_id
        for series_id in series_ids
        if series_id not in refresh_results
        and refresh_status.get("last_run_state") == "failed"
    ]
    stale = [
        series_id
        for series_id in series_ids
        if inputs[series_id].get("freshness_status") == "stale"
    ]
    status, reasons = _release_monitor_status(
        precision=str(family["calendar_precision"]),
        as_of=as_of,
        last_event=last_event,
        last_completed=_optional_datetime_date(refresh_status.get("last_completed_at_utc")),
        failed=failed,
        missing_after_failure=missing_after_failure,
        stale=stale,
        grace_days=grace_days,
    )
    return {
        "release_family_id": family["release_family_id"],
        "title_zh": family["title_zh"],
        "agency_zh": family["agency_zh"],
        "series_ids": series_ids,
        "calendar_precision": family["calendar_precision"],
        "official_calendar_url": family["official_calendar_url"],
        "publication_time_zone": family["publication_time_zone"],
        "last_official_release": last_event,
        "next_official_release": next_event,
        "release_monitor_status": status,
        "release_monitor_status_zh": _status_zh(status),
        "blocked_reason_codes": reasons,
        "failed_series_ids": failed,
        "not_attempted_series_ids": missing_after_failure,
        "stale_series_ids": stale,
        "official_source_delay_confirmed": False,
        "operator_next_action_zh": _operator_action_zh(status),
        "cadence_rule": family.get("cadence_rule"),
    }


def _release_monitor_status(
    *,
    precision: str,
    as_of: date,
    last_event: dict[str, Any] | None,
    last_completed: date | None,
    failed: list[str],
    missing_after_failure: list[str],
    stale: list[str],
    grace_days: int,
) -> tuple[str, list[str]]:
    if failed:
        return "refresh_failed", ["source_fetch_failed"]
    if missing_after_failure:
        return "refresh_blocked_by_prior_failure", ["not_attempted_after_prior_failure"]
    if precision != "exact_schedule":
        reasons = ["calendar_precision_insufficient_for_delay_claim"]
        if stale:
            return "calendar_precision_limited_and_stale", reasons
        return (
            "cadence_only_monitoring"
            if precision == "cadence_only"
            else "official_calendar_reference_only",
            reasons,
        )
    if last_event is None:
        return "waiting_for_registered_release", []
    release_date = date.fromisoformat(str(last_event["release_date"]))
    if last_completed is None or last_completed < release_date:
        if (as_of - release_date).days > grace_days:
            return (
                "release_delayed_or_refresh_missing",
                ["refresh_due_after_official_release"],
            )
        return "release_due_refresh_pending", ["refresh_due_after_official_release"]
    if stale:
        return (
            "refreshed_after_release_but_series_stale",
            ["refreshed_after_release_but_series_stale"],
        )
    return "refreshed_after_release", []


def _series_diagnostic(
    *,
    series_id: str,
    family: dict[str, Any],
    source_input: dict[str, Any],
    refresh_status: dict[str, Any],
    refresh_result: dict[str, Any] | None,
) -> dict[str, Any]:
    reason_codes: list[str] = []
    state = "no_per_series_refresh_result"
    error_class = None
    if refresh_result is not None:
        state = str(refresh_result.get("status", "unknown"))
        error_class = refresh_result.get("error_class")
        if state == "failed":
            reason_codes.append("source_fetch_failed")
    elif refresh_status.get("last_run_state") == "failed":
        state = "not_attempted_after_prior_failure"
        reason_codes.append("not_attempted_after_prior_failure")
    return {
        "series_id": series_id,
        "release_family_id": family["release_family_id"],
        "calendar_precision": family["calendar_precision"],
        "latest_observation_date": source_input.get("latest_observation_date"),
        "freshness_status": source_input.get("freshness_status", "unavailable"),
        "last_refresh_result": state,
        "error_class": error_class,
        "failure_reason_codes": reason_codes,
        "source_delay_claimed": False,
    }


def _refresh_results_by_series(
    refresh_status: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    rows = refresh_status.get("series_refresh_results", [])
    if not isinstance(rows, list):
        return {}
    return {
        str(row["series_id"]): dict(row)
        for row in rows
        if isinstance(row, dict) and row.get("series_id")
    }


def _optional_datetime_date(value: Any) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def _contract_ready(contract: dict[str, Any]) -> bool:
    semantics = contract["semantics"]
    operations = contract["operations_policy"]
    return (
        contract["status"] == "active_private_nas_operations_contract"
        and semantics["exact_schedule_may_determine_due_state"] is True
        and semantics["cadence_only_may_not_claim_official_delay"] is True
        and semantics["reference_only_may_not_claim_official_delay"] is True
        and semantics["observation_date_may_not_equal_release_date"] is True
        and semantics["refresh_failure_must_be_separate_from_source_delay"] is True
        and operations["authentication_required"] is True
        and operations["frontend_database_access_allowed"] is False
        and operations["manual_retry_button_enabled"] is False
    )


def _direct_series_ids() -> list[str]:
    contract = load_nas_postgres_live_revised_import_contract()
    return [str(value) for value in contract["source_policy"]["direct_series_ids"]]


def _precision_count(rows: list[dict[str, Any]], precision: str) -> int:
    return sum(row["calendar_precision"] == precision for row in rows)


def _status_zh(status: str) -> str:
    return {
        "refresh_failed": "最近更新在此來源失敗",
        "refresh_blocked_by_prior_failure": "前一來源失敗，尚未輪到此來源",
        "calendar_precision_limited_and_stale": "資料過期；官方日曆精度不足以判定延遲",
        "cadence_only_monitoring": "僅依官方更新頻率監看，不宣稱精確發布日",
        "official_calendar_reference_only": "官方頁面未提供可安全自動化的未來日期",
        "waiting_for_registered_release": "等待已登錄的第一個官方發布日",
        "release_delayed_or_refresh_missing": "官方日期已過，但尚無其後成功更新",
        "release_due_refresh_pending": "官方資料剛發布，等待排程更新",
        "refreshed_after_release_but_series_stale": "已更新，但序列仍超過新鮮度期限",
        "refreshed_after_release": "官方發布後已有成功更新",
    }.get(status, status)


def _operator_action_zh(status: str) -> str:
    return {
        "refresh_failed": "查看失敗序列與錯誤類別；修復來源後由既有排程重試。",
        "refresh_blocked_by_prior_failure": "先處理前一個失敗來源，再重跑受治理 refresh。",
        "calendar_precision_limited_and_stale": "檢查官方頁面與 FRED 入庫狀態，不要直接判定官方延遲。",
        "cadence_only_monitoring": "維持每日 refresh；精確假日與入庫時間只作人工查核。",
        "official_calendar_reference_only": "人工查看官方更新頁；未取得精確日期前維持 abstain。",
        "waiting_for_registered_release": "等待官方日曆事件。",
        "release_delayed_or_refresh_missing": "先執行一次受治理 refresh，再區分來源延遲或本地更新缺漏。",
        "release_due_refresh_pending": "等待下一次每日排程；必要時由 operator 手動執行既有 worker。",
        "refreshed_after_release_but_series_stale": "檢查 FRED 是否已入庫以及序列是否停止更新。",
        "refreshed_after_release": "無需處理。",
    }.get(status, "人工檢查來源狀態。")
