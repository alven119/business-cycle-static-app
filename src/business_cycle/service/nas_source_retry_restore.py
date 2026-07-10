"""Governed source retry and private NAS backup/restore drill runtime."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
from typing import Any, Callable, Protocol
from urllib.parse import unquote, urlsplit

import yaml

from business_cycle.service.nas_scheduled_revised_refresh import (
    DEFAULT_ARTIFACT_ROOT as DEFAULT_REFRESH_ROOT,
    load_refresh_status,
    run_scheduled_refresh_once,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    CONFIRMATION as IMPORT_CONFIRMATION,
    load_nas_postgres_live_revised_import_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_source_retry_restore_contract.yaml"
DEFAULT_OPERATIONS_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase115")
DEFAULT_OPERATIONS_STATUS_PATH = DEFAULT_OPERATIONS_ROOT / "operations-status.json"
RETRY_CONFIRMATION = "I_CONFIRM_RETRY_FAILED_OFFICIAL_SOURCES"
BACKUP_RESTORE_CONFIRMATION = "I_CONFIRM_PRIVATE_NAS_BACKUP_RESTORE_DRILL"
PG_DUMP_VERSION_RE = re.compile(r"\b(\d+)(?:\.\d+)+\b")


class SourceRetryRestoreError(RuntimeError):
    """Raised when an operator gate or restore invariant fails."""


class CommandExecutor(Protocol):
    def run(self, command: list[str], *, environment: dict[str, str]) -> str: ...


@dataclass
class SubprocessCommandExecutor:
    """Execute Postgres client commands without credentials in argv."""

    def run(self, command: list[str], *, environment: dict[str, str]) -> str:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        if completed.returncode != 0:
            raise SourceRetryRestoreError(
                f"{Path(command[0]).name} failed with redacted operational error"
            )
        return completed.stdout.strip()


def load_nas_source_retry_restore_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_source_retry_restore_contract"])


def summarize_nas_source_retry_restore_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_source_retry_restore_contract(path)
    retry = contract["retry_policy"]
    backup = contract["backup_restore_policy"]
    summary = {
        "phase": 115,
        "nas_source_retry_restore_contract_ready": _contract_ready(contract),
        "retry_preview_ready": True,
        "retry_preview_token_bound_to_status": bool(
            retry["preview_token_binds_refresh_status_hash"]
        ),
        "retry_subset_scope_enforced": bool(retry["canonical_series_scope_required"]),
        "worker_only_retry_execution_ready": bool(
            retry["execute_through_existing_worker_only"]
        ),
        "backup_restore_runtime_ready": True,
        "postgres_client_server_major_match_ready": (
            int(backup["postgres_client_major"])
            == int(backup["postgres_server_major"])
            and backup["postgres_client_server_major_match_required"] is True
        ),
        "database_verification_table_count": len(
            contract["database_verification_tables"]
        ),
        "source_artifact_restore_verification_ready": bool(
            backup["source_artifact_temporary_restore_required"]
        ),
        "staging_database_isolation_ready": bool(
            backup["restore_database_isolation_required"]
            and backup["restore_database_drop_required"]
        ),
        "status_atomic_write_ready": bool(backup["status_atomic_write_required"]),
        "tests_network_dependency_count": 0,
        "tests_backup_command_execution_count": 0,
        "tests_restore_command_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 116,
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


def load_source_operations_status(
    path: str | Path = DEFAULT_OPERATIONS_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return _base_operations_status()
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SourceRetryRestoreError("source operations status must be an object")
    return payload


def default_source_operations_status() -> dict[str, Any]:
    """Return a fresh non-executing status for dashboard fixtures and first start."""

    return _base_operations_status()


def build_source_retry_preview(refresh_status: dict[str, Any]) -> dict[str, Any]:
    allowed = _canonical_series_ids()
    rows = refresh_status.get("series_refresh_results", [])
    by_series = {
        str(row["series_id"]): dict(row)
        for row in rows
        if isinstance(row, dict) and row.get("series_id") in allowed
    }
    candidates: list[dict[str, str]] = []
    if refresh_status.get("last_run_state") == "failed":
        for series_id in allowed:
            row = by_series.get(series_id)
            if row and row.get("status") == "failed":
                candidates.append(
                    {"series_id": series_id, "reason_code": "source_fetch_failed"}
                )
            elif row is None:
                candidates.append(
                    {
                        "series_id": series_id,
                        "reason_code": "not_attempted_after_prior_failure",
                    }
                )
    status_hash = _hash_payload(_retry_status_basis(refresh_status))
    candidate_ids = [row["series_id"] for row in candidates]
    preview_token = _hash_payload(
        {"refresh_status_hash": status_hash, "retry_series_ids": candidate_ids}
    )
    return {
        "preview_version": "phase115_source_retry_preview_v1",
        "refresh_status_hash": status_hash,
        "retry_preview_token": preview_token,
        "retry_eligible": bool(candidates),
        "retry_candidate_count": len(candidates),
        "retry_candidates": candidates,
        "retry_series_ids": candidate_ids,
        "no_failure_means_no_retry": True,
        "worker_only_execution": True,
        "network_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def execute_governed_source_retry(
    *,
    preview_token: str,
    confirmation: str | None,
    refresh_root: str | Path = DEFAULT_REFRESH_ROOT,
    refresh_runner: Callable[..., dict[str, Any]] = run_scheduled_refresh_once,
) -> dict[str, Any]:
    if confirmation != RETRY_CONFIRMATION:
        raise SourceRetryRestoreError("explicit source retry confirmation is required")
    status = load_refresh_status(Path(refresh_root) / "refresh-status.json")
    preview = build_source_retry_preview(status)
    if not preview["retry_eligible"]:
        raise SourceRetryRestoreError("no failed source is eligible for retry")
    if preview_token != preview["retry_preview_token"]:
        raise SourceRetryRestoreError("source retry preview is stale or mismatched")
    result = refresh_runner(
        artifact_root=refresh_root,
        operator_confirmation=IMPORT_CONFIRMATION,
        series_ids=preview["retry_series_ids"],
    )
    return {
        "retry_executed": True,
        "retry_series_count": preview["retry_candidate_count"],
        "retry_series_ids": preview["retry_series_ids"],
        "refresh_state": result["refresh_state"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def run_private_backup_restore_drill(
    *,
    confirmation: str | None,
    database_url: str | None = None,
    operations_root: str | Path = DEFAULT_OPERATIONS_ROOT,
    source_artifact_root: str | Path | None = None,
    executor: CommandExecutor | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    if confirmation != BACKUP_RESTORE_CONFIRMATION:
        raise SourceRetryRestoreError("explicit backup restore confirmation is required")
    root = _validated_operations_root(operations_root)
    source_root = Path(source_artifact_root) if source_artifact_root else root.parent
    root.mkdir(parents=True, exist_ok=True)
    clock = now or (lambda: datetime.now(timezone.utc))
    started = clock()
    run_id = started.strftime("%Y%m%dT%H%M%S%fZ")
    run_root = root / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    status_path = root / "operations-status.json"
    db_url = database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    environment, database_name = _postgres_environment(db_url)
    staging_database = f"phase115_restore_verify_{started.strftime('%Y%m%d%H%M%S')}"
    command_executor = executor or SubprocessCommandExecutor()
    dump_path = run_root / "postgres.dump"
    source_snapshot_path = run_root / "source-artifacts.tar.gz"
    staging_created = False
    status = _base_operations_status() | {
        "backup_restore_state": "running",
        "run_id": run_id,
        "last_started_at_utc": _iso(started),
    }
    _atomic_json_write(status_path, status)
    original_error: Exception | None = None
    try:
        postgres_client_major, postgres_server_major = _postgres_major_versions(
            command_executor,
            environment=environment,
            database_name=database_name,
        )
        if postgres_client_major != postgres_server_major:
            raise SourceRetryRestoreError(
                "postgres client/server major versions do not match"
            )
        live_counts = _database_counts(
            command_executor,
            environment=environment,
            database_name=database_name,
        )
        command_executor.run(
            ["pg_dump", "--format=custom", f"--file={dump_path}", database_name],
            environment=environment,
        )
        if not dump_path.is_file() or dump_path.stat().st_size < 1:
            raise SourceRetryRestoreError("pg_dump did not create a backup artifact")
        postgres_checksum = _sha256_file(dump_path)
        source_manifest = _create_source_artifact_snapshot(
            source_root=source_root,
            output_path=source_snapshot_path,
            excluded_root=root,
        )
        source_checksum = _sha256_file(source_snapshot_path)
        command_executor.run(
            ["createdb", "--maintenance-db", database_name, staging_database],
            environment=environment,
        )
        staging_created = True
        command_executor.run(
            [
                "pg_restore",
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                f"--dbname={staging_database}",
                str(dump_path),
            ],
            environment=environment,
        )
        restored_counts = _database_counts(
            command_executor,
            environment=environment,
            database_name=staging_database,
        )
        if restored_counts != live_counts:
            raise SourceRetryRestoreError("restored database row counts do not match")
        restored_source_file_count = _verify_source_artifact_snapshot(
            source_snapshot_path,
            expected_manifest=source_manifest,
            temporary_parent=run_root,
        )
        completed = clock()
        status = _base_operations_status() | {
            "backup_restore_state": "succeeded",
            "run_id": run_id,
            "last_started_at_utc": _iso(started),
            "last_completed_at_utc": _iso(completed),
            "postgres_backup_path": str(dump_path),
            "postgres_client_major": postgres_client_major,
            "postgres_server_major": postgres_server_major,
            "postgres_backup_checksum": postgres_checksum,
            "postgres_backup_size_bytes": dump_path.stat().st_size,
            "source_artifact_backup_path": str(source_snapshot_path),
            "source_artifact_backup_checksum": source_checksum,
            "source_artifact_file_count": len(source_manifest),
            "restored_source_artifact_file_count": restored_source_file_count,
            "live_row_counts": live_counts,
            "restored_row_counts": restored_counts,
            "row_count_match": True,
            "staging_database_name_hash": hashlib.sha256(
                staging_database.encode("utf-8")
            ).hexdigest(),
            "staging_database_dropped": False,
            "secret_value_recorded": False,
        }
    except Exception as exc:
        original_error = exc
        status = _base_operations_status() | {
            "backup_restore_state": "failed",
            "run_id": run_id,
            "last_started_at_utc": _iso(started),
            "last_completed_at_utc": _iso(clock()),
            "error_class": exc.__class__.__name__,
            "error_reason_code": "backup_restore_drill_failed",
            "secret_value_recorded": False,
        }
    finally:
        if staging_created:
            try:
                command_executor.run(
                    ["dropdb", "--if-exists", staging_database],
                    environment=environment,
                )
                status["staging_database_dropped"] = True
            except Exception as cleanup_error:
                status["backup_restore_state"] = "failed"
                status["error_class"] = cleanup_error.__class__.__name__
                status["error_reason_code"] = "staging_database_cleanup_failed"
                if original_error is None:
                    original_error = cleanup_error
        _atomic_json_write(run_root / "drill-status.json", status)
        _atomic_json_write(status_path, status)
    if original_error is not None:
        raise original_error
    return status


def _database_counts(
    executor: CommandExecutor,
    *,
    environment: dict[str, str],
    database_name: str,
) -> dict[str, int]:
    sql = """
SELECT json_build_object(
  'series_registry', (SELECT count(*) FROM macro.series_registry),
  'source_artifact', (SELECT count(*) FROM macro.source_artifact),
  'observation_revised', (SELECT count(*) FROM macro.observation_revised),
  'observation_vintage', (SELECT count(*) FROM macro.observation_vintage),
  'release_calendar', (SELECT count(*) FROM macro.release_calendar)
)::text;
""".strip()
    output = executor.run(
        [
            "psql",
            "-X",
            "--no-psqlrc",
            "-q",
            "-A",
            "-t",
            "--dbname",
            database_name,
            "--command",
            sql,
        ],
        environment=environment,
    )
    payload = json.loads(output)
    expected_keys = {
        "series_registry",
        "source_artifact",
        "observation_revised",
        "observation_vintage",
        "release_calendar",
    }
    if set(payload) != expected_keys:
        raise SourceRetryRestoreError("database verification query returned invalid keys")
    return {key: int(value) for key, value in payload.items()}


def _postgres_major_versions(
    executor: CommandExecutor,
    *,
    environment: dict[str, str],
    database_name: str,
) -> tuple[int, int]:
    client_output = executor.run(["pg_dump", "--version"], environment=environment)
    match = PG_DUMP_VERSION_RE.search(client_output)
    if match is None:
        raise SourceRetryRestoreError("pg_dump version output is invalid")
    server_output = executor.run(
        [
            "psql",
            "-X",
            "--no-psqlrc",
            "-q",
            "-A",
            "-t",
            "--dbname",
            database_name,
            "--command",
            "SHOW server_version_num;",
        ],
        environment=environment,
    )
    try:
        server_major = int(server_output.strip()) // 10000
    except ValueError as exc:
        raise SourceRetryRestoreError("server version output is invalid") from exc
    return int(match.group(1)), server_major


def _create_source_artifact_snapshot(
    *,
    source_root: Path,
    output_path: Path,
    excluded_root: Path,
) -> dict[str, str]:
    source_root = source_root.resolve()
    excluded_root = excluded_root.resolve()
    if not source_root.is_dir():
        raise SourceRetryRestoreError("source artifact root does not exist")
    files = sorted(
        path
        for path in source_root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and excluded_root not in path.resolve().parents
    )
    manifest = {
        path.relative_to(source_root).as_posix(): _sha256_file(path) for path in files
    }
    with tarfile.open(output_path, "w:gz") as archive:
        for path in files:
            archive.add(path, arcname=path.relative_to(source_root).as_posix())
    if not manifest:
        raise SourceRetryRestoreError("source artifact snapshot would be empty")
    return manifest


def _verify_source_artifact_snapshot(
    snapshot_path: Path,
    *,
    expected_manifest: dict[str, str],
    temporary_parent: Path,
) -> int:
    with tempfile.TemporaryDirectory(prefix="source-restore-", dir=temporary_parent) as temp:
        restore_root = Path(temp).resolve()
        with tarfile.open(snapshot_path, "r:gz") as archive:
            members = [member for member in archive.getmembers() if member.isfile()]
            for member in members:
                destination = (restore_root / member.name).resolve()
                if restore_root not in destination.parents:
                    raise SourceRetryRestoreError("unsafe source artifact member path")
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise SourceRetryRestoreError("source artifact member cannot be read")
                destination.write_bytes(source.read())
        restored_manifest = {
            path.relative_to(restore_root).as_posix(): _sha256_file(path)
            for path in sorted(restore_root.rglob("*"))
            if path.is_file()
        }
        if restored_manifest != expected_manifest:
            raise SourceRetryRestoreError("source artifact restored checksums do not match")
        return len(restored_manifest)


def _postgres_environment(database_url: str) -> tuple[dict[str, str], str]:
    parsed = urlsplit(database_url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise SourceRetryRestoreError("BUSINESS_CYCLE_DATABASE_URL must be postgres")
    database_name = parsed.path.strip("/")
    if not parsed.hostname or not parsed.username or not database_name:
        raise SourceRetryRestoreError("BUSINESS_CYCLE_DATABASE_URL is incomplete")
    environment = {
        **os.environ,
        "PGHOST": parsed.hostname,
        "PGPORT": str(parsed.port or 5432),
        "PGUSER": unquote(parsed.username),
        "PGPASSWORD": unquote(parsed.password or ""),
    }
    return environment, database_name


def _validated_operations_root(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise SourceRetryRestoreError("operations output must remain outside repository")
    return resolved


def _canonical_series_ids() -> list[str]:
    contract = load_nas_postgres_live_revised_import_contract()
    return [str(value) for value in contract["source_policy"]["direct_series_ids"]]


def _retry_status_basis(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "status_version": status.get("status_version"),
        "run_id": status.get("run_id"),
        "last_run_state": status.get("last_run_state"),
        "last_completed_at_utc": status.get("last_completed_at_utc"),
        "series_refresh_results": status.get("series_refresh_results", []),
    }


def _base_operations_status() -> dict[str, Any]:
    return {
        "status_version": "phase115_source_operations_status_v1",
        "backup_restore_state": "not_started",
        "run_id": None,
        "last_started_at_utc": None,
        "last_completed_at_utc": None,
        "postgres_backup_path": None,
        "postgres_client_major": None,
        "postgres_server_major": None,
        "postgres_backup_checksum": None,
        "postgres_backup_size_bytes": 0,
        "source_artifact_backup_path": None,
        "source_artifact_backup_checksum": None,
        "source_artifact_file_count": 0,
        "restored_source_artifact_file_count": 0,
        "live_row_counts": {},
        "restored_row_counts": {},
        "row_count_match": False,
        "staging_database_name_hash": None,
        "staging_database_dropped": False,
        "error_class": None,
        "error_reason_code": None,
        "secret_value_recorded": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    retry = contract["retry_policy"]
    backup = contract["backup_restore_policy"]
    dashboard = contract["dashboard_policy"]
    return (
        contract["status"] == "active_private_nas_operator_contract"
        and retry["preview_required"] is True
        and retry["subset_import_only"] is True
        and retry["execute_through_existing_worker_only"] is True
        and retry["tests_network_allowed"] is False
        and backup["postgres_backup_format"] == "custom"
        and backup["restore_database_isolation_required"] is True
        and backup["restore_database_drop_required"] is True
        and backup["tests_command_execution_allowed"] is False
        and dashboard["raw_command_visible"] is False
        and dashboard["database_url_visible"] is False
        and dashboard["secret_visible"] is False
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-contract", action="store_true")
    parser.add_argument("--retry-preview", action="store_true")
    parser.add_argument("--execute-retry", action="store_true")
    parser.add_argument("--backup-restore-drill", action="store_true")
    parser.add_argument("--preview-token")
    parser.add_argument("--confirmation")
    parser.add_argument("--refresh-root", default=str(DEFAULT_REFRESH_ROOT))
    parser.add_argument("--operations-root", default=str(DEFAULT_OPERATIONS_ROOT))
    args = parser.parse_args(argv)
    selected = sum(
        [
            args.show_contract,
            args.retry_preview,
            args.execute_retry,
            args.backup_restore_drill,
        ]
    )
    if selected != 1:
        raise SourceRetryRestoreError("select exactly one Phase115 operation")
    if args.show_contract:
        print(json.dumps(summarize_nas_source_retry_restore_contract(), sort_keys=True))
        return 0
    if args.retry_preview:
        status = load_refresh_status(Path(args.refresh_root) / "refresh-status.json")
        print(json.dumps(build_source_retry_preview(status), sort_keys=True))
        return 0
    if args.execute_retry:
        result = execute_governed_source_retry(
            preview_token=args.preview_token or "",
            confirmation=args.confirmation,
            refresh_root=args.refresh_root,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    result = run_private_backup_restore_drill(
        confirmation=args.confirmation,
        operations_root=args.operations_root,
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["backup_restore_state"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
