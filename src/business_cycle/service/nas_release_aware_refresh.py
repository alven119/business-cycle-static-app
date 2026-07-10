"""Fixed-time and official-release-aware private NAS refresh scheduler."""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable
from zoneinfo import ZoneInfo

import yaml

from business_cycle.service.nas_official_release_calendar import (
    load_nas_official_release_calendar_contract,
)
from business_cycle.service.nas_scheduled_revised_refresh import (
    CONFIRMATION,
    run_scheduled_refresh_once,
)
from business_cycle.service.nas_source_retry_restore import (
    DEFAULT_OPERATIONS_ROOT,
    load_source_operations_status,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_release_aware_refresh_contract.yaml"
DEFAULT_ARTIFACT_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase116")
DEFAULT_STATUS_PATH = DEFAULT_ARTIFACT_ROOT / "schedule-status.json"
DEFAULT_REFRESH_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase112")


class ReleaseAwareRefreshError(RuntimeError):
    """Raised when scheduler inputs violate the governed contract."""


def load_nas_release_aware_refresh_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_release_aware_refresh_contract"])


def summarize_nas_release_aware_refresh_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_release_aware_refresh_contract(path)
    daily = contract["fixed_daily_schedule"]
    release = contract["release_aware_schedule"]
    retention = contract["backup_retention_policy"]
    completeness = contract["completeness_policy"]
    summary = {
        "phase": 116,
        "nas_release_aware_refresh_contract_ready": _contract_ready(contract),
        "fixed_daily_wall_clock_schedule_ready": True,
        "fixed_daily_time_zone": daily["time_zone"],
        "fixed_daily_local_time": daily["local_time"],
        "exact_schedule_release_followup_ready": release["exact_schedule_only"],
        "release_followup_delay_minutes": int(
            release["release_followup_delay_minutes"]
        ),
        "release_followup_availability_claim_count": 0,
        "cadence_or_reference_release_trigger_count": 0,
        "canonical_subset_enforced": release["canonical_subset_only"],
        "backup_retention_preview_ready": retention[
            "preview_token_required"
        ],
        "backup_retention_automatic_delete_count": int(
            retention["automatic_deletion_enabled"]
        ),
        "direct_revised_series_count": int(
            completeness["direct_revised_series_count"]
        ),
        "macro_history_all_modes_complete": completeness[
            "all_macro_history_complete"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 117,
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


def load_release_aware_schedule_status(
    path: str | Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return default_release_aware_schedule_status()
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReleaseAwareRefreshError("release-aware schedule status must be an object")
    return payload


def default_release_aware_schedule_status() -> dict[str, Any]:
    return {
        "status_version": "phase116_release_aware_schedule_v1",
        "scheduler_state": "not_started",
        "fixed_daily_time_zone": "Asia/Taipei",
        "fixed_daily_local_time": "03:30",
        "next_job_id": None,
        "next_trigger_kind": None,
        "next_scheduled_at_utc": None,
        "next_scheduled_at_local": None,
        "next_release_family_id": None,
        "next_series_ids": [],
        "next_series_count": 0,
        "last_job_id": None,
        "last_trigger_kind": None,
        "last_job_result": None,
        "last_completed_at_utc": None,
        "executed_job_ids": [],
        "exact_calendar_family_count": 9,
        "minimum_exact_calendar_horizon": None,
        "calendar_horizon_status": "not_evaluated",
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "secret_value_recorded": False,
    }


def build_release_aware_schedule_preview(
    *,
    now: datetime,
    executed_job_ids: list[str] | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    if now.tzinfo is None:
        raise ReleaseAwareRefreshError("schedule preview requires timezone-aware now")
    contract = load_nas_release_aware_refresh_contract(contract_path)
    executed = set(executed_job_ids or [])
    daily = contract["fixed_daily_schedule"]
    release = contract["release_aware_schedule"]
    canonical = _canonical_series_ids()
    daily_at = _next_daily_wall_clock(
        now=now,
        time_zone=str(daily["time_zone"]),
        local_time=str(daily["local_time"]),
    )
    candidates = [
        _schedule_job(
            trigger_kind="fixed_daily_full_refresh",
            scheduled_at=daily_at,
            series_ids=canonical,
            release_family_id=None,
            stable_basis={
                "trigger_kind": "fixed_daily_full_refresh",
                "local_date": daily_at.astimezone(
                    ZoneInfo(str(daily["time_zone"]))
                ).date().isoformat(),
            },
        )
    ]
    release_jobs, horizon = _release_jobs(
        now=now,
        delay_minutes=int(release["release_followup_delay_minutes"]),
        catchup_window_hours=int(release["catchup_window_hours"]),
    )
    candidates.extend(release_jobs)
    remaining = [row for row in candidates if row["job_id"] not in executed]
    if not remaining:
        raise ReleaseAwareRefreshError("no future refresh job is available")
    next_job = min(remaining, key=lambda row: (row["scheduled_at_utc"], row["job_id"]))
    seconds_until = max(
        0,
        int(
            (
                datetime.fromisoformat(
                    str(next_job["scheduled_at_utc"]).replace("Z", "+00:00")
                )
                - now.astimezone(timezone.utc)
            ).total_seconds()
        ),
    )
    return {
        "preview_version": "phase116_release_aware_preview_v1",
        "generated_at_utc": _iso(now),
        "fixed_daily_time_zone": daily["time_zone"],
        "fixed_daily_local_time": daily["local_time"],
        "next_job": next_job,
        "seconds_until_next_job": seconds_until,
        "exact_schedule_future_job_count": len(release_jobs),
        "exact_schedule_family_count": 9,
        "minimum_exact_calendar_horizon": horizon,
        "calendar_horizon_status": (
            "registered_exact_schedule_limited_horizon"
            if horizon is not None
            else "exact_schedule_unavailable"
        ),
        "cadence_or_reference_release_trigger_count": 0,
        "release_followup_availability_claim_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def serve_release_aware_schedule(
    *,
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    refresh_root: str | Path = DEFAULT_REFRESH_ROOT,
    operator_confirmation: str | None,
    sleep: Callable[[float], None],
    now: Callable[[], datetime],
    refresh_runner: Callable[..., dict[str, Any]] = run_scheduled_refresh_once,
    max_runs: int | None = None,
) -> int:
    if operator_confirmation != CONFIRMATION:
        raise ReleaseAwareRefreshError("release-aware refresh requires confirmation")
    root = Path(artifact_root)
    root.mkdir(parents=True, exist_ok=True)
    status_path = root / "schedule-status.json"
    run_count = 0
    while max_runs is None or run_count < max_runs:
        previous = load_release_aware_schedule_status(status_path)
        preview = build_release_aware_schedule_preview(
            now=now(),
            executed_job_ids=list(previous.get("executed_job_ids", [])),
        )
        job = preview["next_job"]
        scheduled = _status_with_next_job(previous, preview)
        _atomic_json_write(status_path, scheduled)
        sleep(float(preview["seconds_until_next_job"]))
        running = scheduled | {"scheduler_state": "running"}
        _atomic_json_write(status_path, running)
        result = refresh_runner(
            artifact_root=refresh_root,
            operator_confirmation=operator_confirmation,
            series_ids=list(job["series_ids"]),
        )
        executed = list(previous.get("executed_job_ids", [])) + [str(job["job_id"])]
        limit = int(
            load_nas_release_aware_refresh_contract()["release_aware_schedule"][
                "completed_job_ledger_limit"
            ]
        )
        completed_at = now()
        completed = scheduled | {
            "scheduler_state": "succeeded",
            "last_job_id": job["job_id"],
            "last_trigger_kind": job["trigger_kind"],
            "last_job_result": result.get("refresh_state", "unknown"),
            "last_completed_at_utc": _iso(completed_at),
            "executed_job_ids": executed[-limit:],
        }
        _atomic_json_write(status_path, completed)
        run_count += 1
    return 0


def build_backup_retention_preview(
    operations_root: str | Path = DEFAULT_OPERATIONS_ROOT,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_release_aware_refresh_contract(contract_path)
    policy = contract["backup_retention_policy"]
    root = Path(operations_root)
    run_root = root / "runs"
    latest = load_source_operations_status(root / "operations-status.json")
    rows: list[dict[str, str]] = []
    if run_root.is_dir():
        for path in sorted(run_root.iterdir(), reverse=True):
            if not path.is_dir() or path.is_symlink():
                continue
            status = _backup_run_status(path, latest)
            rows.append({"run_id": path.name, "state": status})
    succeeded = [row for row in rows if row["state"] == "succeeded"]
    failed = [row for row in rows if row["state"] == "failed"]
    unknown = [row for row in rows if row["state"] == "unknown"]
    candidates = (
        succeeded[int(policy["successful_run_keep_count"]):]
        + failed[int(policy["failed_run_keep_count"]):]
    )
    basis = {"runs": rows, "candidates": candidates, "policy": policy}
    return {
        "preview_version": "phase116_backup_retention_preview_v1",
        "successful_run_count": len(succeeded),
        "failed_run_count": len(failed),
        "unknown_run_count": len(unknown),
        "successful_run_keep_count": int(policy["successful_run_keep_count"]),
        "failed_run_keep_count": int(policy["failed_run_keep_count"]),
        "retention_candidate_count": len(candidates),
        "retention_candidate_run_ids": [row["run_id"] for row in candidates],
        "retention_preview_token": _hash_payload(basis),
        "automatic_deletion_enabled": False,
        "delete_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def refresh_scheduler_healthcheck(path: str | Path = DEFAULT_STATUS_PATH) -> bool:
    status = load_release_aware_schedule_status(path)
    return status["scheduler_state"] in {"not_started", "scheduled", "running", "succeeded"}


def _release_jobs(
    *,
    now: datetime,
    delay_minutes: int,
    catchup_window_hours: int,
) -> tuple[list[dict[str, Any]], str | None]:
    calendar = load_nas_official_release_calendar_contract()
    jobs: list[dict[str, Any]] = []
    exact_horizons: list[date] = []
    now_utc = now.astimezone(timezone.utc)
    for family in calendar["release_families"]:
        if family["calendar_precision"] != "exact_schedule":
            continue
        events = list(family.get("scheduled_releases", []))
        if events:
            exact_horizons.append(max(date.fromisoformat(row["release_date"]) for row in events))
        for event in events:
            released_at = datetime.combine(
                date.fromisoformat(str(event["release_date"])),
                time.fromisoformat(str(event["release_time"])),
                tzinfo=ZoneInfo(str(family["publication_time_zone"])),
            ).astimezone(timezone.utc)
            followup_at = released_at + timedelta(minutes=delay_minutes)
            if followup_at <= now_utc:
                if now_utc - followup_at > timedelta(hours=catchup_window_hours):
                    continue
                scheduled_at = now_utc
                trigger_kind = "official_release_catchup"
            else:
                scheduled_at = followup_at
                trigger_kind = "official_release_followup"
            jobs.append(
                _schedule_job(
                    trigger_kind=trigger_kind,
                    scheduled_at=scheduled_at,
                    series_ids=[str(value) for value in family["series_ids"]],
                    release_family_id=str(family["release_family_id"]),
                    stable_basis={
                        "trigger_kind": "official_release_followup",
                        "release_family_id": family["release_family_id"],
                        "release_date": event["release_date"],
                        "release_time": event["release_time"],
                    },
                )
            )
    horizon = min(exact_horizons).isoformat() if exact_horizons else None
    return jobs, horizon


def _next_daily_wall_clock(
    *,
    now: datetime,
    time_zone: str,
    local_time: str,
) -> datetime:
    zone = ZoneInfo(time_zone)
    local_now = now.astimezone(zone)
    target = datetime.combine(
        local_now.date(),
        time.fromisoformat(local_time),
        tzinfo=zone,
    )
    if target <= local_now:
        target += timedelta(days=1)
    return target.astimezone(timezone.utc)


def _schedule_job(
    *,
    trigger_kind: str,
    scheduled_at: datetime,
    series_ids: list[str],
    release_family_id: str | None,
    stable_basis: dict[str, Any],
) -> dict[str, Any]:
    canonical = _canonical_series_ids()
    requested = set(series_ids)
    ordered = [series_id for series_id in canonical if series_id in requested]
    if (
        not ordered
        or len(series_ids) != len(requested)
        or requested - set(canonical)
    ):
        raise ReleaseAwareRefreshError("scheduled series subset is outside canonical scope")
    local = scheduled_at.astimezone(ZoneInfo("Asia/Taipei"))
    return {
        "job_id": _hash_payload(stable_basis)[:24],
        "trigger_kind": trigger_kind,
        "scheduled_at_utc": _iso(scheduled_at),
        "scheduled_at_local": local.isoformat(),
        "release_family_id": release_family_id,
        "series_ids": ordered,
        "series_count": len(ordered),
        "research_only": True,
    }


def _status_with_next_job(
    previous: dict[str, Any],
    preview: dict[str, Any],
) -> dict[str, Any]:
    job = preview["next_job"]
    return previous | {
        "status_version": "phase116_release_aware_schedule_v1",
        "scheduler_state": "scheduled",
        "fixed_daily_time_zone": preview["fixed_daily_time_zone"],
        "fixed_daily_local_time": preview["fixed_daily_local_time"],
        "next_job_id": job["job_id"],
        "next_trigger_kind": job["trigger_kind"],
        "next_scheduled_at_utc": job["scheduled_at_utc"],
        "next_scheduled_at_local": job["scheduled_at_local"],
        "next_release_family_id": job["release_family_id"],
        "next_series_ids": job["series_ids"],
        "next_series_count": job["series_count"],
        "exact_calendar_family_count": preview["exact_schedule_family_count"],
        "minimum_exact_calendar_horizon": preview[
            "minimum_exact_calendar_horizon"
        ],
        "calendar_horizon_status": preview["calendar_horizon_status"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "secret_value_recorded": False,
    }


def _backup_run_status(path: Path, latest: dict[str, Any]) -> str:
    status_path = path / "drill-status.json"
    if status_path.is_file():
        payload = json.loads(status_path.read_text(encoding="utf-8"))
        state = str(payload.get("backup_restore_state", "unknown"))
        return state if state in {"succeeded", "failed"} else "unknown"
    if latest.get("run_id") == path.name:
        state = str(latest.get("backup_restore_state", "unknown"))
        return state if state in {"succeeded", "failed"} else "unknown"
    return "unknown"


def _canonical_series_ids() -> list[str]:
    contract = load_nas_postgres_live_revised_import_contract()
    return [str(value) for value in contract["source_policy"]["direct_series_ids"]]


def _contract_ready(contract: dict[str, Any]) -> bool:
    daily = contract["fixed_daily_schedule"]
    release = contract["release_aware_schedule"]
    retention = contract["backup_retention_policy"]
    return (
        contract["status"] == "active_private_nas_release_aware_scheduler"
        and daily["time_zone"] == "Asia/Taipei"
        and daily["local_time"] == "03:30"
        and release["exact_schedule_only"] is True
        and release["canonical_subset_only"] is True
        and release["release_followup_delay_is_official_availability_claim"] is False
        and retention["automatic_deletion_enabled"] is False
        and retention["unknown_run_preserved"] is True
    )


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args(argv)
    selected = sum([args.serve, args.preview, args.healthcheck])
    if selected != 1:
        raise ReleaseAwareRefreshError("select exactly one Phase116 scheduler mode")
    status_path = Path(args.artifact_root) / "schedule-status.json"
    if args.healthcheck:
        return 0 if refresh_scheduler_healthcheck(status_path) else 1
    if args.preview:
        previous = load_release_aware_schedule_status(status_path)
        preview = build_release_aware_schedule_preview(
            now=datetime.now(timezone.utc),
            executed_job_ids=list(previous.get("executed_job_ids", [])),
        )
        print(json.dumps(preview, sort_keys=True))
        return 0
    confirmation = os.environ.get("BUSINESS_CYCLE_REFRESH_OPERATOR_CONFIRMATION")
    return serve_release_aware_schedule(
        artifact_root=args.artifact_root,
        operator_confirmation=confirmation,
        sleep=lambda seconds: __import__("time").sleep(seconds),
        now=lambda: datetime.now(timezone.utc),
    )


if __name__ == "__main__":
    raise SystemExit(main())
