"""Operator-gated transition-critical ALFRED/PIT and release-calendar import."""

from __future__ import annotations

import argparse
from calendar import monthrange
import csv
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import yaml

from business_cycle.data_sources.alfred_provider import (
    AlfredObservation,
    AlfredProvider,
)
from business_cycle.service.nas_official_release_calendar import (
    load_nas_official_release_calendar_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    PsqlSubprocessExecutor,
    _redact,
)
from business_cycle.storage.postgres_macro_warehouse import generate_postgres_schema_sql

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_transition_pit_backfill_contract.yaml"
)
DEFAULT_STATUS_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase117/latest-backfill-report.json"
)
CONFIRMATION = "I_UNDERSTAND_THIS_FETCHES_ALFRED_AND_WRITES_NAS_POSTGRES"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})(?:-.+)?$")
QUARTER_RE = re.compile(r"^(\d{4})-Q([1-4])(?:-.+)?$")


class TransitionVintageProvider(Protocol):
    def fetch_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
        realtime_start: str | None = None,
        realtime_end: str | None = None,
        output_type: int = 1,
    ) -> list[AlfredObservation]: ...


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> str: ...


@dataclass(frozen=True)
class PitSeriesImportResult:
    series_id: str
    status: str
    observation_count: int
    content_hash: str | None
    artifact_id: str | None
    error_class: str | None = None
    error_message_redacted: str | None = None


def load_nas_transition_pit_backfill_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_transition_pit_backfill_contract"])


def build_normalized_release_calendar_plan() -> dict[str, Any]:
    """Normalize only reference periods that the official contract identifies."""

    source = load_nas_official_release_calendar_contract()
    candidates: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    source_row_count = 0
    exact_families = [
        row
        for row in source["release_families"]
        if row["calendar_precision"] == "exact_schedule"
    ]
    for family in exact_families:
        for event in family["scheduled_releases"]:
            for series_id in family["series_ids"]:
                source_row_count += 1
                period = _reference_period(str(event["reference_period"]))
                if period is None:
                    blocked.append(
                        {
                            "series_key": series_id,
                            "release_family": family["release_family_id"],
                            "reference_period": event["reference_period"],
                            "release_date": event["release_date"],
                            "blocked_reason_code": (
                                "weekly_reference_period_date_unresolved"
                            ),
                        }
                    )
                    continue
                expected = _expected_release_at_utc(
                    release_date=str(event["release_date"]),
                    release_time=str(event["release_time"]),
                    time_zone=str(family["publication_time_zone"]),
                )
                semantics = _release_semantics(str(event["reference_period"]))
                candidates.append(
                    {
                        "series_key": str(series_id),
                        "release_family": str(family["release_family_id"]),
                        "reference_period_label": str(event["reference_period"]),
                        "reference_period_start": period[0],
                        "reference_period_end": period[1],
                        "expected_release_at_utc": expected,
                        "actual_release_at_utc": None,
                        "release_semantics": semantics,
                        "release_status": (
                            "expected_initial_release_registered"
                            if semantics == "initial_release"
                            else "expected_revision_only_registered"
                        ),
                        "official_calendar_url": str(
                            family["official_calendar_url"]
                        ),
                    }
                )

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in candidates:
        key = (
            row["series_key"],
            row["reference_period_start"],
            row["release_family"],
        )
        grouped.setdefault(key, []).append(row)
    normalized: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    for rows in grouped.values():
        ordered = sorted(rows, key=lambda row: row["expected_release_at_utc"])
        normalized.append(ordered[0])
        deferred.extend(
            row
            | {
                "blocked_reason_code": (
                    "phase91_release_calendar_primary_key_cannot_store_revision_event"
                )
            }
            for row in ordered[1:]
        )
    normalized.sort(
        key=lambda row: (
            row["series_key"],
            row["reference_period_start"],
            row["release_family"],
        )
    )
    blocked.sort(
        key=lambda row: (
            row["series_key"],
            row["release_date"],
            row["release_family"],
        )
    )
    deferred.sort(
        key=lambda row: (
            row["series_key"],
            row["expected_release_at_utc"],
            row["release_family"],
        )
    )
    return {
        "plan_version": "phase117_normalized_release_calendar_v1",
        "exact_schedule_family_count": len(exact_families),
        "source_release_event_series_row_count": source_row_count,
        "normalized_release_calendar_rows": normalized,
        "normalized_release_calendar_row_count": len(normalized),
        "blocked_release_calendar_rows": blocked,
        "unresolved_weekly_reference_row_count": len(blocked),
        "deferred_revision_event_rows": deferred,
        "deferred_revision_event_row_count": len(deferred),
        "observation_date_assumed_release_date_count": 0,
        "actual_release_time_claim_count": 0,
        "result": "passed" if normalized else "blocked",
    }


def summarize_nas_transition_pit_backfill_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_transition_pit_backfill_contract(path)
    scope = contract["transition_scope"]
    temporal = contract["temporal_policy"]
    plan = build_normalized_release_calendar_plan()
    series_ids = [str(value) for value in scope["transition_series_ids"]]
    role_map = dict(scope["role_input_map"])
    summary: dict[str, Any] = {
        "phase": 117,
        "nas_transition_pit_backfill_contract_ready": (
            contract["status"]
            == "active_operator_authorized_transition_pit_backfill"
            and series_ids == sorted(set(series_ids))
            and set(value for values in role_map.values() for value in values)
            == set(series_ids)
        ),
        "transition_series_count": len(series_ids),
        "transition_role_count": len(role_map),
        "alfred_output_type": int(scope["alfred_output_type"]),
        "conservative_release_timestamp_ready": (
            temporal["alfred_realtime_start_is_date_precision_availability"]
            and temporal["conservative_release_timestamp_rule"]
            == "realtime_start_end_of_day_utc"
            and temporal[
                "conservative_timestamp_is_not_official_release_time"
            ]
        ),
        "normalized_release_calendar_plan_ready": plan["result"] == "passed",
        "exact_schedule_family_count": plan["exact_schedule_family_count"],
        "source_release_event_series_row_count": plan[
            "source_release_event_series_row_count"
        ],
        "normalized_release_calendar_row_count": plan[
            "normalized_release_calendar_row_count"
        ],
        "unresolved_weekly_reference_row_count": plan[
            "unresolved_weekly_reference_row_count"
        ],
        "deferred_revision_event_row_count": plan[
            "deferred_revision_event_row_count"
        ],
        "observation_date_assumed_release_date_count": plan[
            "observation_date_assumed_release_date_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 118,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary | {"normalized_release_calendar_plan": plan}


def load_transition_pit_backfill_status(
    path: str | Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return {
            "report_version": "phase117_transition_pit_backfill_v1",
            "data_mode": "vintage_as_of",
            "transition_series_count": 13,
            "completed_series_count": 0,
            "failed_series_count": 0,
            "observation_vintage_row_count_planned": 0,
            "normalized_release_calendar_row_count_planned": 0,
            "full_all_series_pit_history_complete": False,
            "result": "not_started",
        }
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid Phase117 PIT backfill status")
    return payload


def import_alfred_pit_series(
    *,
    series_ids: list[str],
    artifact_root: Path,
    fetcher: TransitionVintageProvider,
    sql: SqlExecutor,
    observation_start: str,
    realtime_start: str,
    realtime_end: str,
    checkpoint_name: str,
    checkpoint_schema_version: str,
    resume: bool,
) -> list[PitSeriesImportResult]:
    """Reuse one checkpointed ALFRED interval importer across NAS phases."""

    checkpoint_path = artifact_root / checkpoint_name
    checkpoint = _load_checkpoint(checkpoint_path) if resume else {"completed": {}}
    results: list[PitSeriesImportResult] = []
    for series_id in series_ids:
        saved = checkpoint.get("completed", {}).get(series_id) if resume else None
        if saved:
            results.append(
                PitSeriesImportResult(
                    series_id=series_id,
                    status="resumed_existing",
                    observation_count=int(saved["observation_count"]),
                    content_hash=str(saved["content_hash"]),
                    artifact_id=str(saved["artifact_id"]),
                )
            )
            continue
        try:
            observations = fetcher.fetch_observations(
                series_id,
                observation_start=observation_start,
                realtime_start=realtime_start,
                realtime_end=realtime_end,
                output_type=1,
            )
            normalized = _normalize_vintage_observations(series_id, observations)
            if not normalized:
                raise ValueError(f"{series_id} returned no usable vintage intervals")
            csv_path, content_hash = _write_vintage_csv(
                artifact_root,
                series_id,
                normalized,
            )
            artifact_id = f"alfred_pit::{series_id}::{content_hash[:16]}"
            sql.execute(
                _vintage_upsert_sql(
                    series_id=series_id,
                    csv_path=csv_path,
                    content_hash=content_hash,
                    artifact_id=artifact_id,
                    fetched_at=_utc_now(),
                )
            )
            checkpoint.setdefault("completed", {})[series_id] = {
                "observation_count": len(normalized),
                "content_hash": content_hash,
                "artifact_id": artifact_id,
                "completed_at_utc": _utc_now(),
            }
            checkpoint["schema_version"] = checkpoint_schema_version
            _atomic_json_write(checkpoint_path, checkpoint)
            results.append(
                PitSeriesImportResult(
                    series_id=series_id,
                    status="imported",
                    observation_count=len(normalized),
                    content_hash=content_hash,
                    artifact_id=artifact_id,
                )
            )
        except Exception as exc:  # noqa: BLE001 - preserve all partial successes
            results.append(
                PitSeriesImportResult(
                    series_id=series_id,
                    status="failed",
                    observation_count=0,
                    content_hash=None,
                    artifact_id=None,
                    error_class=exc.__class__.__name__,
                    error_message_redacted=_redact(str(exc)),
                )
            )
    return results


def run_transition_pit_backfill(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path,
    provider: TransitionVintageProvider | None = None,
    executor: SqlExecutor | None = None,
    database_url: str | None = None,
    execution_date: date | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    """Import the governed transition subset and normalized release calendar."""

    if not execute_live or operator_confirmation != CONFIRMATION:
        raise ValueError("live PIT backfill requires explicit operator confirmation")
    contract = load_nas_transition_pit_backfill_contract()
    scope = contract["transition_scope"]
    artifact_root = _validated_artifact_dir(artifact_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)
    resolved_date = execution_date or date.today()
    realtime_end = resolved_date.isoformat()
    fetcher = provider or AlfredProvider()
    sql = executor or PsqlSubprocessExecutor(
        database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    )
    sql.execute(generate_postgres_schema_sql())

    release_plan = build_normalized_release_calendar_plan()
    release_artifact_path = artifact_root / "normalized-release-calendar.json"
    _atomic_json_write(release_artifact_path, release_plan)
    release_content_hash = hashlib.sha256(release_artifact_path.read_bytes()).hexdigest()
    release_artifact_id = f"official_release_calendar::{release_content_hash[:16]}"
    sql.execute(
        _release_calendar_upsert_sql(
            rows=release_plan["normalized_release_calendar_rows"],
            artifact_id=release_artifact_id,
            content_hash=release_content_hash,
            fetched_at=_utc_now(),
        )
    )

    results = import_alfred_pit_series(
        series_ids=list(scope["transition_series_ids"]),
        artifact_root=artifact_root,
        fetcher=fetcher,
        sql=sql,
        observation_start=str(scope["observation_start"]),
        realtime_start=str(scope["realtime_start"]),
        realtime_end=realtime_end,
        checkpoint_name="checkpoint.json",
        checkpoint_schema_version="phase117_transition_pit_backfill_v1",
        resume=resume,
    )

    rows = [row.__dict__ for row in results]
    completed = [
        row for row in rows if row["status"] in {"imported", "resumed_existing"}
    ]
    failed = [row for row in rows if row["status"] == "failed"]
    report: dict[str, Any] = {
        "report_version": "phase117_transition_pit_backfill_v1",
        "execution_date": realtime_end,
        "data_mode": "vintage_as_of",
        "transition_series_count": len(scope["transition_series_ids"]),
        "completed_series_count": len(completed),
        "failed_series_count": len(failed),
        "observation_vintage_row_count_planned": sum(
            int(row["observation_count"]) for row in completed
        ),
        "normalized_release_calendar_row_count_planned": release_plan[
            "normalized_release_calendar_row_count"
        ],
        "unresolved_weekly_reference_row_count": release_plan[
            "unresolved_weekly_reference_row_count"
        ],
        "deferred_revision_event_row_count": release_plan[
            "deferred_revision_event_row_count"
        ],
        "release_calendar_artifact_id": release_artifact_id,
        "release_calendar_content_hash": release_content_hash,
        "conservative_release_timestamp_rule": (
            "realtime_start_end_of_day_utc"
        ),
        "conservative_timestamp_is_official_release_time": False,
        "point_in_time_scope": "transition_critical_1998_to_execution_date",
        "full_all_series_pit_history_complete": False,
        "partial_success_preserved": True,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "results": rows,
        "result": (
            "passed"
            if len(completed) == len(scope["transition_series_ids"]) and not failed
            else "blocked"
        ),
    }
    _atomic_json_write(artifact_root / "latest-backfill-report.json", report)
    return report


def _normalize_vintage_observations(
    series_id: str,
    observations: list[AlfredObservation],
) -> list[AlfredObservation]:
    by_key: dict[tuple[str, str], AlfredObservation] = {}
    for row in observations:
        if row.series_id.upper() != series_id:
            raise ValueError(f"invalid ALFRED series identity for {series_id}")
        for value in (row.observation_date, row.realtime_start, row.realtime_end):
            if not DATE_RE.fullmatch(value):
                raise ValueError(f"invalid ALFRED date for {series_id}")
        if date.fromisoformat(row.realtime_start) > date.fromisoformat(row.realtime_end):
            raise ValueError(f"invalid ALFRED realtime interval for {series_id}")
        by_key[(row.observation_date, row.realtime_start)] = row
    return [by_key[key] for key in sorted(by_key)]


def _write_vintage_csv(
    root: Path,
    series_id: str,
    observations: list[AlfredObservation],
) -> tuple[Path, str]:
    output = root / "alfred" / f"{series_id}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "series_key",
        "observation_date",
        "realtime_start",
        "realtime_end",
        "vintage_as_of",
        "release_timestamp_utc",
        "value_numeric",
        "value_text",
    ]
    with tempfile.NamedTemporaryFile(
        "w", newline="", encoding="utf-8", dir=output.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in observations:
            numeric = _decimal_or_none(row.value)
            writer.writerow(
                {
                    "series_key": series_id,
                    "observation_date": row.observation_date,
                    "realtime_start": row.realtime_start,
                    "realtime_end": row.realtime_end,
                    "vintage_as_of": row.realtime_start,
                    "release_timestamp_utc": f"{row.realtime_start}T23:59:59Z",
                    "value_numeric": str(numeric) if numeric is not None else "",
                    "value_text": row.value if numeric is None else "",
                }
            )
        temporary = Path(handle.name)
    content_hash = hashlib.sha256(temporary.read_bytes()).hexdigest()
    temporary.replace(output)
    return output, content_hash


def _vintage_upsert_sql(
    *,
    series_id: str,
    csv_path: Path,
    content_hash: str,
    artifact_id: str,
    fetched_at: str,
) -> str:
    series = _literal(series_id)
    artifact = _literal(artifact_id)
    fetched = _literal(fetched_at)
    content = _literal(content_hash)
    source_url = _literal(f"https://fred.stlouisfed.org/series/{series_id}")
    csv_value = str(csv_path).replace("'", "''")
    return rf"""
BEGIN;
INSERT INTO macro.source_artifact (
  artifact_id, source_family, source_url_without_secret,
  source_series_or_release_id, fetched_at_utc, content_hash, content_type,
  adapter_id, parser_version, no_secret, validation_status
) VALUES (
  {artifact}, 'FRED/ALFRED', {source_url}, {series}, {fetched}::timestamptz,
  {content}, 'text/csv', 'alfred_realtime_intervals_v1',
  'phase117_vintage_csv_v1', TRUE, 'validated_transition_critical_pit'
)
ON CONFLICT (content_hash) DO NOTHING;

CREATE TEMP TABLE phase117_vintage_import (
  series_key text,
  observation_date date,
  realtime_start date,
  realtime_end date,
  vintage_as_of date,
  release_timestamp_utc timestamptz,
  value_numeric numeric,
  value_text text
) ON COMMIT DROP;
\copy phase117_vintage_import FROM '{csv_value}' WITH (FORMAT csv, HEADER true)

INSERT INTO macro.observation_vintage (
  series_key, observation_date, realtime_start, realtime_end, vintage_as_of,
  release_timestamp_utc, value_numeric, value_text, unit, data_mode,
  source_artifact_id, provenance_hash
)
SELECT
  series_key, observation_date, realtime_start, realtime_end, vintage_as_of,
  release_timestamp_utc, value_numeric, value_text,
  'source_native_unit', 'vintage_as_of', {artifact},
  encode(sha256(convert_to(
    series_key || '|' || observation_date::text || '|' ||
    realtime_start::text || '|' || realtime_end::text || '|' ||
    coalesce(value_numeric::text, value_text, '') || '|' || {artifact},
    'UTF8'
  )), 'hex')
FROM phase117_vintage_import
ON CONFLICT (series_key, observation_date, realtime_start) DO UPDATE SET
  realtime_end = EXCLUDED.realtime_end,
  vintage_as_of = EXCLUDED.vintage_as_of,
  release_timestamp_utc = EXCLUDED.release_timestamp_utc,
  value_numeric = EXCLUDED.value_numeric,
  value_text = EXCLUDED.value_text,
  source_artifact_id = EXCLUDED.source_artifact_id,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _release_calendar_upsert_sql(
    *,
    rows: list[dict[str, Any]],
    artifact_id: str,
    content_hash: str,
    fetched_at: str,
) -> str:
    values = []
    for row in rows:
        event_id = "phase117::" + _hash_payload(
            {
                "series_key": row["series_key"],
                "release_family": row["release_family"],
                "reference_period_label": row["reference_period_label"],
                "expected_release_at_utc": row["expected_release_at_utc"],
            }
        )[:24]
        expected = _literal(row["expected_release_at_utc"])
        provenance = _hash_payload(
            {
                "series_key": row["series_key"],
                "release_family": row["release_family"],
                "reference_period_start": row["reference_period_start"],
                "expected_release_at_utc": row["expected_release_at_utc"],
                "artifact_id": artifact_id,
            }
        )
        values.append(
            "(" + ", ".join(
                [
                    _literal(row["series_key"]),
                    _literal(event_id),
                    _literal(row["release_family"]),
                    _literal(row["reference_period_label"]),
                    _literal(
                        "quarter"
                        if "-Q" in row["reference_period_label"]
                        else "month"
                    ),
                    _literal(row["reference_period_start"]) + "::date",
                    _literal(row["reference_period_end"]) + "::date",
                    expected + "::timestamptz",
                    "NULL",
                    _literal(row["release_semantics"]),
                    "'exact_timestamp'",
                    _literal(row["release_status"]),
                    _literal(artifact_id),
                    _literal(provenance),
                ]
            ) + ")"
        )
    joined_values = ",\n".join(values)
    return f"""
BEGIN;
INSERT INTO macro.source_artifact (
  artifact_id, source_family, source_url_without_secret,
  source_series_or_release_id, fetched_at_utc, content_hash, content_type,
  adapter_id, parser_version, no_secret, validation_status
) VALUES (
  {_literal(artifact_id)}, 'US official release calendars',
  'repository://specs/common/nas_official_release_calendar_contract.yaml',
  'phase117_normalized_release_calendar', {_literal(fetched_at)}::timestamptz,
  {_literal(content_hash)}, 'application/json',
  'official_release_calendar_normalizer_v1', 'phase117_calendar_v1', TRUE,
  'validated_expected_release_calendar_no_actual_release_claim'
)
ON CONFLICT (content_hash) DO NOTHING;

INSERT INTO macro.release_calendar (
  series_key, release_event_id, release_family, source_reference_period_label,
  reference_period_precision, reference_period_start, reference_period_end,
  expected_release_at_utc, actual_release_at_utc, release_semantics,
  availability_precision, release_status, source_artifact_id, provenance_hash
) VALUES
{joined_values}
ON CONFLICT (series_key, release_event_id) DO UPDATE SET
  reference_period_end = EXCLUDED.reference_period_end,
  expected_release_at_utc = EXCLUDED.expected_release_at_utc,
  actual_release_at_utc = EXCLUDED.actual_release_at_utc,
  release_status = EXCLUDED.release_status,
  source_artifact_id = EXCLUDED.source_artifact_id,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _reference_period(value: str) -> tuple[str, str] | None:
    month_match = MONTH_RE.fullmatch(value)
    if month_match:
        year = int(month_match.group(1))
        month = int(month_match.group(2))
        if not 1 <= month <= 12:
            return None
        return (
            date(year, month, 1).isoformat(),
            date(year, month, monthrange(year, month)[1]).isoformat(),
        )
    quarter_match = QUARTER_RE.fullmatch(value)
    if quarter_match:
        year = int(quarter_match.group(1))
        quarter = int(quarter_match.group(2))
        start_month = 1 + ((quarter - 1) * 3)
        end_month = start_month + 2
        return (
            date(year, start_month, 1).isoformat(),
            date(year, end_month, monthrange(year, end_month)[1]).isoformat(),
        )
    return None


def _release_semantics(reference_period: str) -> str:
    lowered = reference_period.lower()
    if lowered.endswith("-second") or lowered.endswith("-third"):
        return "revision_release"
    return "initial_release"


def _expected_release_at_utc(
    *,
    release_date: str,
    release_time: str,
    time_zone: str,
) -> str:
    local = datetime.combine(
        date.fromisoformat(release_date),
        time.fromisoformat(release_time),
        tzinfo=ZoneInfo(time_zone),
    )
    return local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"completed": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("completed"), dict):
        raise ValueError("invalid Phase117 checkpoint")
    return payload


def _validated_artifact_dir(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("PIT backfill artifacts must remain outside the repository")
    if not (
        str(resolved).startswith("/tmp/")
        or str(resolved).startswith("/var/lib/business-cycle/")
    ):
        raise ValueError("artifact directory must be under /tmp or NAS artifact volume")
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


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument(
        "--artifact-dir",
        default="/var/lib/business-cycle/source-artifacts/phase117",
    )
    parser.add_argument("--no-resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.execute_live:
        print(json.dumps(summarize_nas_transition_pit_backfill_contract(), indent=2))
        return 0
    report = run_transition_pit_backfill(
        execute_live=True,
        operator_confirmation=os.environ.get(
            "BUSINESS_CYCLE_PIT_BACKFILL_OPERATOR_CONFIRMATION"
        ),
        artifact_dir=args.artifact_dir,
        resume=not args.no_resume,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
