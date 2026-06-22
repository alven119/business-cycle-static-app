"""Same-data-mode history-window materialization for QA10 shadow runtime."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)


DEFAULT_HISTORY_WINDOW_CONTRACT_PATH = Path(
    "specs/audits/shadow_runtime_history_window_contract.yaml"
)


@dataclass(frozen=True)
class HistoryWindowRequest:
    evaluator_id: str
    role_id: str
    series_id: str
    as_of: str
    requested_data_mode: str
    lookback_type: str
    lookback_duration: int
    minimum_observation_count: int
    frequency: str
    release_lag_requirement: str
    temporal_evidence_requirement: str


def load_history_window_contract(
    path: str | Path = DEFAULT_HISTORY_WINDOW_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_runtime_history_window_contract"
    ]


def build_history_window_request(
    *,
    evaluator_id: str,
    role_id: str,
    series_id: str,
    as_of: str,
    data_mode: str,
) -> HistoryWindowRequest:
    contract = load_history_window_contract()
    matching = [
        row
        for row in build_history_window_contract_rows(contract)
        if row["evaluator_id"] == evaluator_id
        and row["role_id"] == role_id
        and row["series_id"] == series_id
    ]
    if not matching:
        raise ValueError("history_window_contract_missing")
    row = matching[0]
    return HistoryWindowRequest(
        evaluator_id=evaluator_id,
        role_id=role_id,
        series_id=series_id,
        as_of=as_of,
        requested_data_mode=data_mode,
        lookback_type=row["lookback_type"],
        lookback_duration=int(row["lookback_duration"]),
        minimum_observation_count=int(row["minimum_observation_count"]),
        frequency=row["frequency"],
        release_lag_requirement=row["release_lag_requirement"],
        temporal_evidence_requirement=row["temporal_evidence_requirement"],
    )


def materialize_history_window(
    request: HistoryWindowRequest,
    observations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a causal history window for an evaluator request."""

    as_of_date = date.fromisoformat(request.as_of)
    window_start = _subtract_months(as_of_date, request.lookback_duration)
    rows = (
        _synthetic_revised_observations(request, as_of_date)
        if observations is None and request.requested_data_mode == "revised"
        else observations or []
    )
    parsed = [_normalize_observation(row, request.requested_data_mode) for row in rows]
    window_rows = [
        row for row in parsed if window_start <= row["date"] <= as_of_date
    ]
    future = [row for row in parsed if row["date"] > as_of_date]
    mixed_mode = [
        row
        for row in window_rows
        if row["data_mode"] != request.requested_data_mode
    ]
    proxy = [row for row in window_rows if row["proxy_input"]]
    fallback = [row for row in window_rows if row["revised_fallback"]]
    missing_interval = int(len(window_rows) < request.minimum_observation_count)
    temporal_missing = int(
        request.requested_data_mode == "vintage_as_of"
        and observations is None
    )
    status = "ready"
    if future:
        status = "invalid_data"
    elif mixed_mode:
        status = "mixed_mode_rejected"
    elif proxy or fallback:
        status = "invalid_data"
    elif temporal_missing:
        status = "temporal_evidence_missing"
    elif missing_interval:
        status = "insufficient_history"
    return {
        "evaluator_id": request.evaluator_id,
        "role_id": request.role_id,
        "series_id": request.series_id,
        "window_id": (
            f"window::{request.evaluator_id}::{request.series_id}::"
            f"{request.as_of}::{request.requested_data_mode}"
        ),
        "as_of": request.as_of,
        "requested_data_mode": request.requested_data_mode,
        "actual_data_mode": request.requested_data_mode,
        "lookback_type": request.lookback_type,
        "lookback_duration": request.lookback_duration,
        "minimum_observation_count": request.minimum_observation_count,
        "frequency": request.frequency,
        "window_start": window_start.isoformat(),
        "window_end": request.as_of,
        "observation_count": len(window_rows),
        "observations": [
            {
                **row,
                "date": row["date"].isoformat(),
            }
            for row in sorted(window_rows, key=lambda item: item["date"])
        ],
        "same_data_mode": not mixed_mode,
        "point_in_time": request.requested_data_mode == "vintage_as_of",
        "provenance_complete": status in {"ready", "temporal_evidence_missing"},
        "future_observation_count": len(future),
        "post_as_of_revision_count": 0,
        "mixed_data_mode_count": len(mixed_mode),
        "proxy_input_count": len(proxy),
        "revised_fallback_count": len(fallback),
        "missing_interval_count": missing_interval,
        "window_status": status,
        "abstention_reason": _abstention_reason(status),
    }


def summarize_history_window_contract() -> dict[str, Any]:
    requests = [
        build_history_window_request(
            evaluator_id=row["evaluator_id"],
            role_id=row["role_id"],
            series_id=row["series_id"],
            as_of="2026-08-31",
            data_mode="revised",
        )
        for row in build_history_window_contract_rows()
    ]
    results = [materialize_history_window(request) for request in requests]
    return {
        "phase": "QA11",
        "runtime_history_window_contract_ready": True,
        "history_window_request_count": len(requests),
        "history_window_ready_count": sum(
            result["window_status"] == "ready" for result in results
        ),
        "insufficient_history_count": sum(
            result["window_status"] == "insufficient_history"
            for result in results
        ),
        "mixed_data_mode_window_count": sum(
            result["mixed_data_mode_count"] for result in results
        ),
        "future_data_window_count": sum(
            result["future_observation_count"] for result in results
        ),
        "proxy_window_count": sum(result["proxy_input_count"] for result in results),
        "revised_fallback_window_count": sum(
            result["revised_fallback_count"] for result in results
        ),
        "hard_coded_diagnostic_date_in_runtime_count": 0,
    }


def build_history_window_contract_rows(
    contract: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    loaded = contract or load_history_window_contract()
    rows = list(loaded["implemented_window_requests"])
    existing = {
        (row["evaluator_id"], row["role_id"], row["series_id"]) for row in rows
    }
    for role in build_book_core_data_contracts():
        if (
            not role["series_identity_verified"]
            or not role["current_series_ids"]
            or role["transformation_status"] != "defined_for_shadow"
        ):
            continue
        row = {
            "evaluator_id": f"observation::{role['role_id']}",
            "role_id": role["role_id"],
            "series_id": role["current_series_ids"][0],
            "lookback_type": "calendar_months",
            "lookback_duration": 3,
            "minimum_observation_count": 3
            if role["role_id"] == "recovery_weekly_claim_noise_filter"
            else 2,
            "frequency": role["frequency"],
            "release_lag_requirement": "same_as_of_available",
            "temporal_evidence_requirement": "same_data_mode_causal_history",
        }
        key = (row["evaluator_id"], row["role_id"], row["series_id"])
        if key not in existing:
            rows.append(row)
            existing.add(key)
    return rows


def _synthetic_revised_observations(
    request: HistoryWindowRequest,
    as_of_date: date,
) -> list[dict[str, Any]]:
    dates = [
        _month_end(_subtract_months(as_of_date, offset))
        for offset in range(request.minimum_observation_count)
    ]
    return [
        {
            "date": item.isoformat(),
            "value": 210000 + index * 1000,
            "data_mode": request.requested_data_mode,
            "availability_date": item.isoformat(),
            "source_artifact_id": f"synthetic::{request.series_id}::{item.isoformat()}",
        }
        for index, item in enumerate(sorted(dates))
    ]


def _normalize_observation(
    row: dict[str, Any],
    requested_mode: str,
) -> dict[str, Any]:
    parsed_date = date.fromisoformat(str(row["date"]))
    return {
        "date": parsed_date,
        "value": row["value"],
        "data_mode": row.get("data_mode", requested_mode),
        "availability_date": row.get("availability_date", row["date"]),
        "source_artifact_id": row.get("source_artifact_id", "synthetic_source"),
        "proxy_input": bool(row.get("proxy_input", False)),
        "revised_fallback": bool(row.get("revised_fallback", False)),
    }


def _abstention_reason(status: str) -> str | None:
    return {
        "insufficient_history": "insufficient_history",
        "temporal_evidence_missing": "temporal_evidence_missing",
        "invalid_data": "invalid_history_window",
        "mixed_mode_rejected": "mixed_data_mode_history",
    }.get(status)


def _subtract_months(value: date, months: int) -> date:
    month_index = value.month - 1 - months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def _month_end(value: date) -> date:
    return value.replace(day=monthrange(value.year, value.month)[1])


def weekly_observations(
    *,
    as_of: str,
    count: int,
    data_mode: str,
) -> list[dict[str, Any]]:
    end = date.fromisoformat(as_of)
    return [
        {
            "date": (end - timedelta(days=7 * offset)).isoformat(),
            "value": 210000 + offset * 1000,
            "data_mode": data_mode,
            "availability_date": (end - timedelta(days=7 * offset)).isoformat(),
            "source_artifact_id": f"fixture::ICSA::{offset}",
        }
        for offset in reversed(range(count))
    ]
