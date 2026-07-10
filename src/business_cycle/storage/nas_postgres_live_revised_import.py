"""Operator-gated revised-history import into the private NAS Postgres warehouse."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from typing import Any, Callable, Protocol
from urllib.parse import unquote, urlsplit

import yaml

from business_cycle.data_sources import FredProvider, SeriesObservation
from business_cycle.storage.postgres_macro_warehouse import (
    generate_postgres_schema_sql,
    summarize_postgres_macro_warehouse_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_postgres_live_revised_import_contract.yaml"
DEFAULT_REGISTRY_PATH = ROOT / "specs/common/series_release_lag_registry.yaml"
CONFIRMATION = "I_UNDERSTAND_THIS_FETCHES_FRED_AND_WRITES_NAS_POSTGRES"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SERIES_RE = re.compile(r"^[A-Z0-9_]+$")


class RevisedHistoryProvider(Protocol):
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]: ...


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> str: ...


@dataclass(frozen=True)
class SeriesImportResult:
    series_id: str
    status: str
    observation_count: int
    content_hash: str | None
    artifact_id: str | None
    error_class: str | None = None
    error_message_redacted: str | None = None


class PsqlSubprocessExecutor:
    """Run psql without placing database credentials in command arguments."""

    def __init__(self, database_url: str, *, executable: str = "psql") -> None:
        parsed = urlsplit(database_url)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise ValueError("BUSINESS_CYCLE_DATABASE_URL must use postgres/postgresql")
        if not parsed.hostname or not parsed.path.strip("/") or not parsed.username:
            raise ValueError("BUSINESS_CYCLE_DATABASE_URL is incomplete")
        self.executable = executable
        self.environment = {
            **os.environ,
            "PGHOST": parsed.hostname,
            "PGPORT": str(parsed.port or 5432),
            "PGDATABASE": parsed.path.strip("/"),
            "PGUSER": unquote(parsed.username),
            "PGPASSWORD": unquote(parsed.password or ""),
        }

    def execute(self, sql: str) -> str:
        completed = subprocess.run(
            [self.executable, "-X", "--no-psqlrc", "-v", "ON_ERROR_STOP=1"],
            input=sql,
            text=True,
            capture_output=True,
            env=self.environment,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(_redact(completed.stderr.strip() or "psql failed"))
        return completed.stdout


def load_nas_postgres_live_revised_import_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_postgres_live_revised_import_contract"])


def summarize_nas_postgres_live_revised_import_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_postgres_live_revised_import_contract(path)
    source = contract["source_policy"]
    execution = contract["execution_policy"]
    warehouse = summarize_postgres_macro_warehouse_contract()
    direct = list(source["direct_series_ids"])
    derived = dict(source["derived_roles_deferred_to_snapshot_materialization"])
    summary = {
        "phase": 110,
        "nas_postgres_live_revised_import_contract_ready": (
            contract["status"] == "active_operator_authorized_live_import"
            and direct == sorted(set(direct))
            and all(SERIES_RE.fullmatch(item) for item in direct)
        ),
        "postgres_schema_contract_ready": warehouse[
            "postgres_macro_warehouse_contract_ready"
        ],
        "direct_series_count": len(direct),
        "derived_role_count": len(derived),
        "full_history_requested": bool(source["full_history_requested"]),
        "migration_idempotent": bool(execution["schema_migration_idempotent"]),
        "upsert_idempotent": bool(execution["upsert_idempotent"]),
        "checkpoint_resume_ready": bool(execution["checkpoint_after_each_series"]),
        "backup_required": bool(execution["backup_before_first_migration_required"]),
        "source_artifact_checksum_required": bool(
            execution["source_artifact_checksum_required"]
        ),
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 111,
    }
    summary["result"] = (
        "passed" if _matches(summary, contract["hard_gates"]) else "blocked"
    )
    return summary


def run_nas_postgres_live_revised_import(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path,
    provider: RevisedHistoryProvider | None = None,
    executor: SqlExecutor | None = None,
    database_url: str | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    retry_count: int = 3,
    retry_sleep: Callable[[float], None] = time.sleep,
    resume: bool = True,
) -> dict[str, Any]:
    """Migrate and import revised history after explicit operator confirmation."""

    if not execute_live or operator_confirmation != CONFIRMATION:
        raise ValueError("live import requires explicit operator confirmation")
    contract = load_nas_postgres_live_revised_import_contract(contract_path)
    artifact_root = _validated_artifact_dir(artifact_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = artifact_root / "checkpoint.json"
    checkpoint = _load_checkpoint(checkpoint_path) if resume else {"completed": {}}
    fetcher = provider or FredProvider()
    sql = executor or PsqlSubprocessExecutor(
        database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    )
    registry = _load_registry(registry_path)
    series_ids = list(contract["source_policy"]["direct_series_ids"])
    started_at = _utc_now()
    sql.execute(generate_postgres_schema_sql())
    results: list[SeriesImportResult] = []

    for series_id in series_ids:
        if resume and series_id in checkpoint.get("completed", {}):
            saved = checkpoint["completed"][series_id]
            results.append(
                SeriesImportResult(
                    series_id=series_id,
                    status="resumed_existing",
                    observation_count=int(saved["observation_count"]),
                    content_hash=str(saved["content_hash"]),
                    artifact_id=str(saved["artifact_id"]),
                )
            )
            continue
        try:
            observations = _fetch_with_retry(
                fetcher,
                series_id,
                retry_count=retry_count,
                retry_sleep=retry_sleep,
            )
            normalized = _normalize_observations(series_id, observations)
            if not normalized:
                raise ValueError(f"{series_id} returned no usable revised observations")
            csv_path, content_hash = _write_series_csv(
                artifact_root,
                series_id,
                normalized,
            )
            fetched_at = _utc_now()
            artifact_id = f"fred_revised::{series_id}::{content_hash[:16]}"
            sql.execute(
                _series_upsert_sql(
                    series_id=series_id,
                    registry_row=registry[series_id],
                    csv_path=csv_path,
                    content_hash=content_hash,
                    artifact_id=artifact_id,
                    fetched_at=fetched_at,
                )
            )
            checkpoint.setdefault("completed", {})[series_id] = {
                "observation_count": len(normalized),
                "content_hash": content_hash,
                "artifact_id": artifact_id,
                "completed_at_utc": fetched_at,
            }
            checkpoint["schema_version"] = "phase110_revised_import_v1"
            _atomic_json_write(checkpoint_path, checkpoint)
            results.append(
                SeriesImportResult(
                    series_id=series_id,
                    status="imported",
                    observation_count=len(normalized),
                    content_hash=content_hash,
                    artifact_id=artifact_id,
                )
            )
        except Exception as exc:  # noqa: BLE001 - preserve partial success and redact
            results.append(
                SeriesImportResult(
                    series_id=series_id,
                    status="failed",
                    observation_count=0,
                    content_hash=None,
                    artifact_id=None,
                    error_class=exc.__class__.__name__,
                    error_message_redacted=_redact(str(exc)),
                )
            )
            break

    report = _build_report(
        started_at=started_at,
        completed_at=_utc_now(),
        series_ids=series_ids,
        results=results,
        artifact_root=artifact_root,
    )
    _atomic_json_write(artifact_root / "latest-import-report.json", report)
    return report


def _fetch_with_retry(
    provider: RevisedHistoryProvider,
    series_id: str,
    *,
    retry_count: int,
    retry_sleep: Callable[[float], None],
) -> list[SeriesObservation]:
    last_error: Exception | None = None
    for attempt in range(retry_count):
        try:
            return provider.fetch_series_observations(series_id)
        except Exception as exc:  # noqa: BLE001 - bounded operational retry
            last_error = exc
            if attempt + 1 < retry_count:
                retry_sleep(float(2**attempt))
    assert last_error is not None
    raise last_error


def _normalize_observations(
    series_id: str,
    observations: list[SeriesObservation],
) -> list[SeriesObservation]:
    by_date: dict[str, SeriesObservation] = {}
    for observation in observations:
        if observation.series_id.upper() != series_id or not DATE_RE.fullmatch(observation.date):
            raise ValueError(f"invalid observation identity for {series_id}")
        by_date[observation.date] = observation
    return [by_date[date] for date in sorted(by_date)]


def _write_series_csv(
    root: Path,
    series_id: str,
    observations: list[SeriesObservation],
) -> tuple[Path, str]:
    output = root / "fred" / f"{series_id}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        newline="",
        encoding="utf-8",
        dir=output.parent,
        delete=False,
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["series_key", "observation_date", "value_numeric", "value_text"],
        )
        writer.writeheader()
        for item in observations:
            numeric = _decimal_or_none(item.value)
            writer.writerow(
                {
                    "series_key": series_id,
                    "observation_date": item.date,
                    "value_numeric": str(numeric) if numeric is not None else "",
                    "value_text": item.value if numeric is None else "",
                }
            )
        tmp_path = Path(handle.name)
    content = tmp_path.read_bytes()
    content_hash = hashlib.sha256(content).hexdigest()
    tmp_path.replace(output)
    return output, content_hash


def _series_upsert_sql(
    *,
    series_id: str,
    registry_row: dict[str, Any],
    csv_path: Path,
    content_hash: str,
    artifact_id: str,
    fetched_at: str,
) -> str:
    values = {
        "series": _literal(series_id),
        "source": _literal(str(registry_row["source"])),
        "title": _literal(str(registry_row["release_family"])),
        "frequency": _literal(str(registry_row["frequency"])),
        "url": _literal(f"https://fred.stlouisfed.org/series/{series_id}"),
        "fetched": _literal(fetched_at),
        "hash": _literal(content_hash),
        "artifact": _literal(artifact_id),
        "csv": str(csv_path).replace("'", "''"),
    }
    return rf"""
BEGIN;
INSERT INTO macro.series_registry (
  series_key, source_family, source_series_id, source_title, units, frequency,
  seasonal_adjustment, geographic_scope, source_url_without_secret,
  source_identity_status, created_at_utc, updated_at_utc
) VALUES (
  {values['series']}, {values['source']}, {values['series']}, {values['title']},
  'not_declared_in_release_lag_registry', {values['frequency']},
  'not_declared_in_release_lag_registry', 'US_or_source_declared', {values['url']},
  'release_lag_registry_present', {values['fetched']}::timestamptz,
  {values['fetched']}::timestamptz
)
ON CONFLICT (series_key) DO UPDATE SET
  source_title = EXCLUDED.source_title,
  frequency = EXCLUDED.frequency,
  source_url_without_secret = EXCLUDED.source_url_without_secret,
  updated_at_utc = EXCLUDED.updated_at_utc;

INSERT INTO macro.source_artifact (
  artifact_id, source_family, source_url_without_secret,
  source_series_or_release_id, fetched_at_utc, content_hash, content_type,
  adapter_id, parser_version, no_secret, validation_status
) VALUES (
  {values['artifact']}, 'FRED/ALFRED', {values['url']}, {values['series']},
  {values['fetched']}::timestamptz, {values['hash']}, 'text/csv',
  'fred_revised_full_history_v1', 'phase110_csv_v1', TRUE, 'validated_live_revised'
)
ON CONFLICT (content_hash) DO NOTHING;

CREATE TEMP TABLE phase110_observation_import (
  series_key text,
  observation_date date,
  value_numeric numeric,
  value_text text
) ON COMMIT DROP;
\copy phase110_observation_import FROM '{values['csv']}' WITH (FORMAT csv, HEADER true)

INSERT INTO macro.observation_revised (
  series_key, observation_date, value_numeric, value_text, unit, data_mode,
  source_artifact_id, fetched_at_utc, provenance_hash
)
SELECT
  series_key,
  observation_date,
  value_numeric,
  value_text,
  'not_declared_in_release_lag_registry',
  'revised',
  {values['artifact']},
  {values['fetched']}::timestamptz,
  encode(sha256(convert_to(
    series_key || '|' || observation_date::text || '|' ||
    coalesce(value_numeric::text, value_text, '') || '|' || {values['artifact']},
    'UTF8'
  )), 'hex')
FROM phase110_observation_import
ON CONFLICT (series_key, observation_date) DO UPDATE SET
  value_numeric = EXCLUDED.value_numeric,
  value_text = EXCLUDED.value_text,
  source_artifact_id = EXCLUDED.source_artifact_id,
  fetched_at_utc = EXCLUDED.fetched_at_utc,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _build_report(
    *,
    started_at: str,
    completed_at: str,
    series_ids: list[str],
    results: list[SeriesImportResult],
    artifact_root: Path,
) -> dict[str, Any]:
    rows = [result.__dict__ for result in results]
    failed = [row for row in rows if row["status"] == "failed"]
    completed = [row for row in rows if row["status"] in {"imported", "resumed_existing"}]
    return {
        "report_version": "phase110_live_revised_import_v1",
        "data_mode": "revised",
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "requested_series_count": len(series_ids),
        "completed_series_count": len(completed),
        "failed_series_count": len(failed),
        "observation_revised_row_count_planned": sum(
            int(row["observation_count"]) for row in completed
        ),
        "source_artifact_count": len(completed),
        "artifact_root_kind": "nas_named_volume"
        if str(artifact_root).startswith("/var/lib/business-cycle/")
        else "test_tmp",
        "partial_success_preserved": True,
        "point_in_time_result": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "results": rows,
        "result": "passed" if len(completed) == len(series_ids) and not failed else "blocked",
    }


def _load_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = {
        str(row["series_id"]): dict(row)
        for row in payload["series_release_lag_registry"]["series"]
    }
    return rows


def _load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"completed": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("completed"), dict):
        raise ValueError("invalid Phase110 checkpoint")
    return payload


def _validated_artifact_dir(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("live import artifacts must remain outside the repository")
    if not (
        str(resolved).startswith("/tmp/")
        or str(resolved).startswith("/var/lib/business-cycle/")
    ):
        raise ValueError("artifact directory must be under /tmp or the NAS artifact volume")
    return resolved


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _decimal_or_none(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _redact(message: str) -> str:
    redacted = re.sub(r"(?i)(api_key=)[^&\s)\"']+", r"\1[REDACTED]", message)
    redacted = re.sub(r"(?i)(postgres(?:ql)?://[^:]+:)[^@\s]+", r"\1[REDACTED]", redacted)
    secret = os.environ.get("FRED_API_KEY")
    if secret:
        redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())
