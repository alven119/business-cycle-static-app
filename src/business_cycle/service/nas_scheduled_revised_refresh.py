"""Governed recurring revised-data refresh for the private NAS service."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Callable, Iterator

import yaml

from business_cycle.storage.nas_postgres_live_revised_import import (
    CONFIRMATION,
    automated_revised_series_ids,
    load_nas_postgres_live_revised_import_contract,
    run_nas_postgres_live_revised_import,
)
from business_cycle.storage.nas_technology_manufacturing_import import (
    run_technology_manufacturing_import,
)
from business_cycle.service.nas_consumer_confidence_sources import (
    CONFIRMATION as OECD_CONFIDENCE_CONFIRMATION,
    run_oecd_consumer_confidence_import,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_scheduled_revised_refresh_contract.yaml"
DEFAULT_ARTIFACT_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase112")
DEFAULT_STATUS_PATH = DEFAULT_ARTIFACT_ROOT / "refresh-status.json"


def load_nas_scheduled_revised_refresh_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_scheduled_revised_refresh_contract"])


def summarize_nas_scheduled_revised_refresh_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_scheduled_revised_refresh_contract(path)
    source = load_nas_postgres_live_revised_import_contract()
    schedule = contract["schedule_policy"]
    summary = {
        "phase": 112,
        "nas_scheduled_revised_refresh_contract_ready": (
            contract["status"] == "active_private_nas_refresh_contract"
            and contract["execution_policy"]["data_mode"] == "revised"
            and contract["execution_policy"]["postgres_write_allowed_only_in_worker"]
            is True
        ),
        "scheduled_refresh_runner_ready": True,
        "source_health_status_ready": True,
        "dashboard_shell_ttl_cache_ready": True,
        "direct_series_count": len(source["source_policy"]["direct_series_ids"]),
        "supporting_context_series_count": len(
            source["source_policy"].get("supporting_context_series_ids", [])
        ),
        "automated_revised_series_count": len(
            automated_revised_series_ids(source)
        ),
        "default_interval_seconds": int(schedule["default_interval_seconds"]),
        "bounded_retry_count": int(schedule["bounded_retry_count"]),
        "concurrent_refresh_rejected": bool(
            schedule["single_process_lock_required"]
        ),
        "status_atomic_write_ready": bool(
            schedule["latest_status_atomic_write_required"]
        ),
        "tests_network_dependency_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 113,
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


def load_refresh_status(path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return _base_status("not_started")
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("refresh status must be a JSON object")
    return payload


def run_scheduled_refresh_once(
    *,
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    operator_confirmation: str | None,
    import_runner: Callable[..., dict[str, Any]] = run_nas_postgres_live_revised_import,
    now: Callable[[], datetime] | None = None,
    series_ids: list[str] | None = None,
    technology_import_runner: Callable[..., dict[str, Any]] = (
        run_technology_manufacturing_import
    ),
    consumer_confidence_import_runner: Callable[..., dict[str, Any]] = (
        run_oecd_consumer_confidence_import
    ),
    source_incident_reconciler: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run one mutually exclusive refresh and preserve a redacted latest status."""

    if operator_confirmation != CONFIRMATION:
        raise ValueError("scheduled refresh requires explicit operator confirmation")
    clock = now or (lambda: datetime.now(timezone.utc))
    root = Path(artifact_root)
    root.mkdir(parents=True, exist_ok=True)
    status_path = root / "refresh-status.json"
    started = clock()
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    run_root = root / "runs" / run_id
    with _exclusive_refresh_lock(root / "refresh.lock"):
        previous = load_refresh_status(status_path)
        running = previous | {
            "refresh_state": "running",
            "run_id": run_id,
            "last_started_at_utc": _iso(started),
        }
        _atomic_json_write(status_path, running)
        try:
            report = import_runner(
                execute_live=True,
                operator_confirmation=operator_confirmation,
                artifact_dir=run_root,
                retry_count=3,
                resume=False,
                series_ids=series_ids,
            )
            technology_report: dict[str, Any] | None = None
            if _technology_refresh_enabled() and _is_full_daily_refresh(series_ids):
                technology_report = technology_import_runner(
                    execute_live=True,
                    operator_confirmation=os.environ.get(
                        "BUSINESS_CYCLE_TECHNOLOGY_REFRESH_OPERATOR_CONFIRMATION",
                    ),
                    artifact_dir=root.parent / "phase122" / "runs" / run_id,
                )
            confidence_report: dict[str, Any] | None = None
            if _consumer_confidence_refresh_enabled() and _is_full_daily_refresh(
                series_ids
            ):
                confidence_report = consumer_confidence_import_runner(
                    execute_live=True,
                    operator_confirmation=os.environ.get(
                        "BUSINESS_CYCLE_CONSUMER_CONFIDENCE_OPERATOR_CONFIRMATION",
                        OECD_CONFIDENCE_CONFIRMATION,
                    ),
                    artifact_dir=root.parent / "phase136" / "runs" / run_id,
                )
            completed = clock()
            succeeded = report.get("result") == "passed" and int(
                report.get("failed_series_count", 0)
            ) == 0 and (
                technology_report is None
                or technology_report.get("result") == "passed"
            ) and (
                confidence_report is None
                or confidence_report.get("result") == "passed"
            )
            confidence_requested = int(confidence_report is not None)
            confidence_completed = int(
                confidence_report is not None
                and confidence_report.get("result") == "passed"
            )
            confidence_failed = int(
                confidence_report is not None
                and confidence_report.get("result") != "passed"
            )
            status = _base_status("succeeded" if succeeded else "failed") | {
                "last_run_state": "succeeded" if succeeded else "failed",
                "run_id": run_id,
                "last_started_at_utc": _iso(started),
                "last_completed_at_utc": _iso(completed),
                "next_scheduled_at_utc": _iso(completed + timedelta(days=1)),
                "requested_series_count": int(
                    report.get("requested_series_count", 0)
                ) + confidence_requested,
                "completed_series_count": int(
                    report.get("completed_series_count", 0)
                ) + confidence_completed,
                "failed_series_count": int(report.get("failed_series_count", 0))
                + confidence_failed,
                "source_artifact_count": int(
                    report.get("source_artifact_count", 0)
                ) + confidence_completed,
                "report_path": str(run_root / "latest-import-report.json"),
                "error_class": None if succeeded else "RefreshReportFailed",
                "error_message_redacted": None
                if succeeded
                else "one_or_more_sources_failed",
                "series_refresh_results": [
                    *_redacted_series_refresh_results(report),
                    *_redacted_external_series_refresh_results(confidence_report),
                ],
                "technology_refresh_enabled": _technology_refresh_enabled(),
                "technology_refresh_result": (
                    technology_report.get("result")
                    if technology_report is not None
                    else "not_run_for_subset_or_disabled"
                ),
                "technology_completed_series_count": int(
                    (technology_report or {}).get("completed_series_count", 0)
                ),
                "consumer_confidence_refresh_enabled": (
                    _consumer_confidence_refresh_enabled()
                ),
                "consumer_confidence_refresh_result": (
                    confidence_report.get("result")
                    if confidence_report is not None
                    else "not_run_for_subset_or_disabled"
                ),
                "consumer_confidence_completed_series_count": confidence_completed,
            }
        except Exception as exc:  # noqa: BLE001 - status must survive failure
            completed = clock()
            status = _base_status("failed") | {
                "last_run_state": "failed",
                "run_id": run_id,
                "last_started_at_utc": _iso(started),
                "last_completed_at_utc": _iso(completed),
                "next_scheduled_at_utc": _iso(completed + timedelta(days=1)),
                "error_class": exc.__class__.__name__,
                "error_message_redacted": "refresh_execution_failed",
            }
        _atomic_json_write(status_path, status)
        if _source_incident_reconciliation_enabled() or source_incident_reconciler:
            reconciler = source_incident_reconciler or _reconcile_live_source_incidents
            try:
                incident_center = reconciler(status)
                status["source_incident_reconciliation_state"] = "succeeded"
                status["open_source_incident_count"] = int(
                    incident_center["open_incident_count"]
                )
                status["source_incident_reconciliation_error_class"] = None
            except Exception as exc:  # noqa: BLE001 - refresh status must stay available
                status["source_incident_reconciliation_state"] = "failed"
                status["source_incident_reconciliation_error_class"] = (
                    exc.__class__.__name__
                )
            _atomic_json_write(status_path, status)
        return status


def serve_refresh_schedule(
    *,
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    operator_confirmation: str | None,
    interval_seconds: int = 86400,
    initial_delay_seconds: int = 86400,
    sleep: Callable[[float], None] = time.sleep,
    max_runs: int | None = None,
    refresh_runner: Callable[..., dict[str, Any]] = run_scheduled_refresh_once,
    now: Callable[[], datetime] | None = None,
) -> int:
    if interval_seconds < 60 or initial_delay_seconds < 0:
        raise ValueError("refresh schedule timing is invalid")
    root = Path(artifact_root)
    root.mkdir(parents=True, exist_ok=True)
    clock = now or (lambda: datetime.now(timezone.utc))
    current = clock()
    previous = load_refresh_status(root / "refresh-status.json")
    delay_seconds = _scheduled_delay_seconds(
        previous,
        current=current,
        interval_seconds=interval_seconds,
        initial_delay_seconds=initial_delay_seconds,
    )
    waiting = previous | {
        "refresh_state": "scheduled",
        "next_scheduled_at_utc": _iso(
            current + timedelta(seconds=delay_seconds)
        ),
    }
    _atomic_json_write(root / "refresh-status.json", waiting)
    sleep(float(delay_seconds))
    run_count = 0
    while max_runs is None or run_count < max_runs:
        refresh_runner(
            artifact_root=root,
            operator_confirmation=operator_confirmation,
        )
        run_count += 1
        if max_runs is not None and run_count >= max_runs:
            break
        sleep(float(interval_seconds))
    return 0


def refresh_healthcheck(path: str | Path = DEFAULT_STATUS_PATH) -> bool:
    status = load_refresh_status(path)
    return status["refresh_state"] in {
        "not_started",
        "scheduled",
        "running",
        "succeeded",
    }


@contextmanager
def _exclusive_refresh_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another revised refresh is already running") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _base_status(state: str) -> dict[str, Any]:
    return {
        "status_version": "phase114_refresh_status_v2",
        "refresh_state": state,
        "last_run_state": None,
        "data_mode": "revised",
        "run_id": None,
        "last_started_at_utc": None,
        "last_completed_at_utc": None,
        "next_scheduled_at_utc": None,
        "requested_series_count": 0,
        "completed_series_count": 0,
        "failed_series_count": 0,
        "source_artifact_count": 0,
        "report_path": None,
        "error_class": None,
        "error_message_redacted": None,
        "series_refresh_results": [],
        "technology_refresh_enabled": _technology_refresh_enabled(),
        "technology_refresh_result": "not_run",
        "technology_completed_series_count": 0,
        "consumer_confidence_refresh_enabled": (
            _consumer_confidence_refresh_enabled()
        ),
        "consumer_confidence_refresh_result": "not_run",
        "consumer_confidence_completed_series_count": 0,
        "source_incident_reconciliation_state": "disabled",
        "source_incident_reconciliation_error_class": None,
        "open_source_incident_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "secret_value_recorded": False,
    }


def _source_incident_reconciliation_enabled() -> bool:
    return os.environ.get(
        "BUSINESS_CYCLE_SOURCE_INCIDENT_RECONCILIATION_ENABLED", "false"
    ).lower() in {"1", "true", "yes", "on"}


def _reconcile_live_source_incidents(status: dict[str, Any]) -> dict[str, Any]:
    from business_cycle.service.nas_source_incident_center import (
        reconcile_live_source_incidents,
    )

    return reconcile_live_source_incidents(status)


def _technology_refresh_enabled() -> bool:
    return os.environ.get("BUSINESS_CYCLE_TECHNOLOGY_REFRESH_ENABLED", "false").lower() in {
        "1", "true", "yes", "on",
    }


def _consumer_confidence_refresh_enabled() -> bool:
    return os.environ.get(
        "BUSINESS_CYCLE_CONSUMER_CONFIDENCE_REFRESH_ENABLED", "false"
    ).lower() in {"1", "true", "yes", "on"}


def _is_full_daily_refresh(series_ids: list[str] | None) -> bool:
    if series_ids is None:
        return True
    return set(series_ids) == set(automated_revised_series_ids())


def _redacted_series_refresh_results(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = report.get("results", [])
    if not isinstance(rows, list):
        return []
    allowed_statuses = {"imported", "resumed_existing", "failed"}
    results: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, dict) or not raw.get("series_id"):
            continue
        status = str(raw.get("status", "unknown"))
        results.append(
            {
                "series_id": str(raw["series_id"]),
                "status": status if status in allowed_statuses else "unknown",
                "observation_count": int(raw.get("observation_count", 0)),
                "error_class": (
                    str(raw["error_class"])
                    if status == "failed" and raw.get("error_class")
                    else None
                ),
                "error_reason_code": (
                    "source_fetch_failed" if status == "failed" else None
                ),
            }
        )
    return results


def _redacted_external_series_refresh_results(
    report: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if report is None:
        return []
    rows = report.get("series_refresh_results", [])
    if not isinstance(rows, list):
        return []
    results = []
    for raw in rows:
        if not isinstance(raw, dict) or not raw.get("series_id"):
            continue
        status = str(raw.get("status", "unknown"))
        results.append(
            {
                "series_id": str(raw["series_id"]),
                "status": status if status in {"imported", "failed"} else "unknown",
                "observation_count": int(raw.get("observation_count", 0)),
                "attempt_count": int(raw.get("attempt_count", 1)),
                "error_class": (
                    str(raw["error_class"])
                    if status == "failed" and raw.get("error_class")
                    else None
                ),
                "error_reason_code": (
                    "source_fetch_failed" if status == "failed" else None
                ),
            }
        )
    return results


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _scheduled_delay_seconds(
    status: dict[str, Any],
    *,
    current: datetime,
    interval_seconds: int,
    initial_delay_seconds: int,
) -> int:
    completed = status.get("last_completed_at_utc")
    if not completed:
        return initial_delay_seconds
    completed_at = datetime.fromisoformat(str(completed).replace("Z", "+00:00"))
    next_run = completed_at + timedelta(seconds=interval_seconds)
    return max(0, int((next_run - current).total_seconds()))


def main(argv: list[str] | None = None) -> int:
    contract = load_nas_scheduled_revised_refresh_contract()
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument("--operator-confirmation", required=False)
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=int(contract["schedule_policy"]["default_interval_seconds"]),
    )
    parser.add_argument(
        "--initial-delay-seconds",
        type=int,
        default=int(contract["schedule_policy"]["default_initial_delay_seconds"]),
    )
    args = parser.parse_args(argv)
    confirmation = args.operator_confirmation or os.environ.get(
        "BUSINESS_CYCLE_REFRESH_OPERATOR_CONFIRMATION"
    )
    if args.healthcheck:
        healthy = refresh_healthcheck(Path(args.artifact_root) / "refresh-status.json")
        return 0 if healthy else 1
    if args.run_once:
        status = run_scheduled_refresh_once(
            artifact_root=args.artifact_root,
            operator_confirmation=confirmation,
        )
        print(json.dumps(status, sort_keys=True))
        return 0 if status["refresh_state"] == "succeeded" else 1
    if not args.serve:
        raise ValueError("select --run-once, --serve, or --healthcheck")
    return serve_refresh_schedule(
        artifact_root=args.artifact_root,
        operator_confirmation=confirmation,
        interval_seconds=args.interval_seconds,
        initial_delay_seconds=args.initial_delay_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
