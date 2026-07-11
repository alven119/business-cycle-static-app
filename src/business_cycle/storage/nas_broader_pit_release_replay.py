"""Phase 118 broader PIT import, revision-aware calendar, and input audit."""

from __future__ import annotations

import argparse
from calendar import monthrange
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Protocol
from zoneinfo import ZoneInfo

import yaml

from business_cycle.data_sources.alfred_provider import AlfredProvider
from business_cycle.service.nas_official_release_calendar import (
    load_nas_official_release_calendar_contract,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    PsqlReadOnlyExecutor,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    PsqlSubprocessExecutor,
)
from business_cycle.storage.nas_transition_pit_backfill import (
    SqlExecutor,
    TransitionVintageProvider,
    import_alfred_pit_series,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_broader_pit_release_replay_contract.yaml"
)
DEFAULT_STATUS_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase118/latest-broader-pit-report.json"
)
SCENARIO_PATH = ROOT / "specs/audits/historical_validation_scenario_manifest.yaml"
CONFIRMATION = "I_UNDERSTAND_THIS_MIGRATES_CALENDAR_AND_WRITES_BROADER_ALFRED_PIT"
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})(?:-.+)?$")
QUARTER_RE = re.compile(r"^(\d{4})-Q([1-4])(?:-.+)?$")


class AuditExecutor(Protocol):
    def query_json(self, sql: str) -> dict[str, Any]: ...


def load_nas_broader_pit_release_replay_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_broader_pit_release_replay_contract"])


def build_revision_aware_release_calendar_plan(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Normalize every exact official event, including revisions and DOL weeks."""

    contract = load_nas_broader_pit_release_replay_contract(contract_path)
    source = load_nas_official_release_calendar_contract()
    weekly_rules = contract["weekly_reference_period_policy"]["series_rules"]
    rows: list[dict[str, Any]] = []
    exact_families = [
        row
        for row in source["release_families"]
        if row["calendar_precision"] == "exact_schedule"
    ]
    for family in exact_families:
        for event in family["scheduled_releases"]:
            for series_id in family["series_ids"]:
                period = _reference_period(
                    label=str(event["reference_period"]),
                    release_date=str(event["release_date"]),
                    series_id=str(series_id),
                    weekly_rules=weekly_rules,
                )
                expected = _expected_release_at_utc(
                    release_date=str(event["release_date"]),
                    release_time=str(event["release_time"]),
                    time_zone=str(family["publication_time_zone"]),
                )
                semantics = _release_semantics(str(event["reference_period"]))
                event_basis = {
                    "series_key": str(series_id),
                    "release_family": str(family["release_family_id"]),
                    "source_reference_period_label": str(event["reference_period"]),
                    "expected_release_at_utc": expected,
                }
                rows.append(
                    {
                        **event_basis,
                        "release_event_id": "phase118::"
                        + _hash_payload(event_basis)[:24],
                        "reference_period_precision": period[2],
                        "reference_period_start": period[0],
                        "reference_period_end": period[1],
                        "actual_release_at_utc": None,
                        "release_semantics": semantics,
                        "availability_precision": "exact_expected_timestamp",
                        "release_status": (
                            "expected_initial_release_registered"
                            if semantics == "initial_release"
                            else "expected_revision_release_registered"
                        ),
                        "official_calendar_url": str(
                            family["official_calendar_url"]
                        ),
                        "observation_date_used_as_release_date": False,
                    }
                )
    rows.sort(
        key=lambda row: (
            row["series_key"],
            row["expected_release_at_utc"],
            row["release_event_id"],
        )
    )
    event_ids = [row["release_event_id"] for row in rows]
    return {
        "plan_version": "phase118_revision_aware_release_calendar_v1",
        "exact_schedule_family_count": len(exact_families),
        "source_release_event_series_row_count": len(rows),
        "normalized_release_event_rows": rows,
        "normalized_release_event_row_count": len(rows),
        "weekly_reference_event_row_count": sum(
            row["reference_period_precision"] == "official_week_ending_rule"
            for row in rows
        ),
        "revision_event_row_count": sum(
            row["release_semantics"] == "revision_release" for row in rows
        ),
        "deferred_release_event_row_count": 0,
        "duplicate_release_event_id_count": len(event_ids) - len(set(event_ids)),
        "observation_date_assumed_release_date_count": 0,
        "actual_release_time_claim_count": 0,
        "result": "passed"
        if rows and len(event_ids) == len(set(event_ids))
        else "blocked",
    }


def summarize_nas_broader_pit_release_replay_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_broader_pit_release_replay_contract(path)
    scope = contract["broader_pit_scope"]
    migration = contract["release_calendar_schema_migration"]
    audit = contract["strict_replay_input_audit"]
    plan = build_revision_aware_release_calendar_plan(contract_path=path)
    series_ids = [str(value) for value in scope["broader_series_ids"]]
    summary: dict[str, Any] = {
        "phase": 118,
        "nas_broader_pit_release_replay_contract_ready": (
            contract["status"]
            == "active_operator_authorized_broader_pit_and_calendar_migration"
            and series_ids == sorted(set(series_ids))
            and int(scope["alfred_output_type"]) == 1
        ),
        "broader_pit_series_count": len(series_ids),
        "expected_all_direct_series_count_after": int(
            scope["expected_all_direct_series_count_after"]
        ),
        "release_calendar_schema_migration_ready": (
            migration["guarded_replace_required"] is True
            and migration["expected_pre_migration_row_count"] == 59
            and migration["expected_pre_migration_actual_release_non_null_count"]
            == 0
            and migration["primary_key_after"]
            == ["series_key", "release_event_id"]
        ),
        "revision_aware_calendar_plan_ready": plan["result"] == "passed",
        "source_release_event_series_row_count": plan[
            "source_release_event_series_row_count"
        ],
        "normalized_release_event_row_count": plan[
            "normalized_release_event_row_count"
        ],
        "weekly_reference_event_row_count": plan[
            "weekly_reference_event_row_count"
        ],
        "revision_event_row_count": plan["revision_event_row_count"],
        "deferred_release_event_row_count": plan[
            "deferred_release_event_row_count"
        ],
        "observation_date_assumed_release_date_count": plan[
            "observation_date_assumed_release_date_count"
        ],
        "strict_replay_scenario_count": int(audit["scenario_count"]),
        "model_execution_count": 0,
        "backtest_execution_count": 0,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 119,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary | {"revision_aware_release_calendar_plan": plan}


def build_release_calendar_schema_migration_sql(
    *,
    expected_pre_migration_row_count: int = 59,
) -> str:
    """Build an idempotent migration with a guarded replacement of Phase 117 rows."""

    if expected_pre_migration_row_count < 0:
        raise ValueError("expected pre-migration row count must be non-negative")
    return f"""
BEGIN;
ALTER TABLE macro.release_calendar
  ADD COLUMN IF NOT EXISTS release_event_id text,
  ADD COLUMN IF NOT EXISTS source_reference_period_label text,
  ADD COLUMN IF NOT EXISTS reference_period_precision text,
  ADD COLUMN IF NOT EXISTS release_semantics text,
  ADD COLUMN IF NOT EXISTS availability_precision text;

DO $$
DECLARE
  total_count bigint;
  null_event_count bigint;
  actual_release_count bigint;
BEGIN
  SELECT count(*), count(*) FILTER (WHERE release_event_id IS NULL),
         count(actual_release_at_utc)
    INTO total_count, null_event_count, actual_release_count
    FROM macro.release_calendar;
  IF null_event_count > 0 THEN
    IF total_count <> {expected_pre_migration_row_count}
       OR actual_release_count <> 0 THEN
      RAISE EXCEPTION 'Phase118 calendar guard rejected unexpected live rows';
    END IF;
    DELETE FROM macro.release_calendar;
  END IF;
END $$;

ALTER TABLE macro.release_calendar
  ALTER COLUMN release_event_id SET NOT NULL,
  ALTER COLUMN source_reference_period_label SET NOT NULL,
  ALTER COLUMN reference_period_precision SET NOT NULL,
  ALTER COLUMN release_semantics SET NOT NULL,
  ALTER COLUMN availability_precision SET NOT NULL;

ALTER TABLE macro.release_calendar
  DROP CONSTRAINT IF EXISTS release_calendar_pkey;
ALTER TABLE macro.release_calendar
  ADD CONSTRAINT release_calendar_pkey PRIMARY KEY (series_key, release_event_id);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'release_calendar_event_identity_key'
      AND conrelid = 'macro.release_calendar'::regclass
  ) THEN
    ALTER TABLE macro.release_calendar ADD CONSTRAINT
      release_calendar_event_identity_key UNIQUE (
        series_key, release_family, source_reference_period_label,
        expected_release_at_utc
      );
  END IF;
END $$;
COMMIT;
""".lstrip()


def run_nas_broader_pit_release_replay(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path,
    provider: TransitionVintageProvider | None = None,
    executor: SqlExecutor | None = None,
    audit_executor: AuditExecutor | None = None,
    database_url: str | None = None,
    execution_date: date | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    """Migrate/import/audit without executing model, labels, metrics, or backtests."""

    if not execute_live or operator_confirmation != CONFIRMATION:
        raise ValueError("Phase118 live execution requires explicit confirmation")
    contract = load_nas_broader_pit_release_replay_contract()
    scope = contract["broader_pit_scope"]
    migration = contract["release_calendar_schema_migration"]
    artifact_root = _validated_artifact_dir(artifact_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)
    resolved_date = execution_date or date.today()
    resolved_url = database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    sql = executor or PsqlSubprocessExecutor(resolved_url)
    reader = audit_executor or PsqlReadOnlyExecutor(resolved_url)
    fetcher = provider or AlfredProvider()

    sql.execute(
        build_release_calendar_schema_migration_sql(
            expected_pre_migration_row_count=int(
                migration["expected_pre_migration_row_count"]
            )
        )
    )
    calendar_plan = build_revision_aware_release_calendar_plan()
    calendar_path = artifact_root / "revision-aware-release-calendar.json"
    _atomic_json_write(calendar_path, calendar_plan)
    calendar_hash = hashlib.sha256(calendar_path.read_bytes()).hexdigest()
    calendar_artifact_id = f"official_release_events::{calendar_hash[:16]}"
    sql.execute(
        _release_event_upsert_sql(
            rows=calendar_plan["normalized_release_event_rows"],
            artifact_id=calendar_artifact_id,
            content_hash=calendar_hash,
            fetched_at=_utc_now(),
        )
    )

    results = import_alfred_pit_series(
        series_ids=list(scope["broader_series_ids"]),
        artifact_root=artifact_root,
        fetcher=fetcher,
        sql=sql,
        observation_start=str(scope["observation_start"]),
        realtime_start=str(scope["realtime_start"]),
        realtime_end=str(scope["realtime_end"]),
        checkpoint_name="broader-pit-checkpoint.json",
        checkpoint_schema_version="phase118_broader_pit_backfill_v1",
        resume=resume,
    )
    result_rows = [row.__dict__ for row in results]
    completed = [
        row
        for row in result_rows
        if row["status"] in {"imported", "resumed_existing"}
    ]
    failed = [row for row in result_rows if row["status"] == "failed"]
    audit = build_strict_replay_input_audit(executor=reader)
    report: dict[str, Any] = {
        "report_version": "phase118_broader_pit_release_replay_v1",
        "execution_date": resolved_date.isoformat(),
        "data_mode": "vintage_as_of",
        "broader_pit_series_count": len(scope["broader_series_ids"]),
        "completed_series_count": len(completed),
        "failed_series_count": len(failed),
        "broader_observation_vintage_row_count_planned": sum(
            int(row["observation_count"]) for row in completed
        ),
        "normalized_release_event_row_count_planned": calendar_plan[
            "normalized_release_event_row_count"
        ],
        "weekly_reference_event_row_count": calendar_plan[
            "weekly_reference_event_row_count"
        ],
        "revision_event_row_count": calendar_plan["revision_event_row_count"],
        "deferred_release_event_row_count": 0,
        "calendar_schema_migrated": True,
        "calendar_artifact_id": calendar_artifact_id,
        "calendar_content_hash": calendar_hash,
        "strict_replay_input_audit": audit,
        "model_execution_count": 0,
        "backtest_execution_count": 0,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "partial_success_preserved": True,
        "results": result_rows,
        "result": (
            "passed"
            if len(completed) == len(scope["broader_series_ids"])
            and not failed
            and audit["result"] == "passed"
            else "blocked"
        ),
    }
    _atomic_json_write(artifact_root / "latest-broader-pit-report.json", report)
    return report


def build_strict_replay_input_audit(
    *,
    executor: AuditExecutor,
    scenario_path: str | Path = SCENARIO_PATH,
) -> dict[str, Any]:
    """Audit PIT input presence only; never invoke evidence or decision runtime."""

    scenarios = _scenario_rows(scenario_path)
    required = _all_direct_series_ids()
    payload = executor.query_json(_strict_replay_input_sql(scenarios, required))
    if str(payload.get("transaction_read_only", "")).lower() not in {"on", "true"}:
        raise RuntimeError("strict replay input audit session is not read-only")
    rows = payload.get("scenario_rows", [])
    if not isinstance(rows, list) or len(rows) != len(scenarios):
        raise RuntimeError("strict replay input audit returned invalid scenario rows")
    normalized_rows = []
    for row in rows:
        available = sorted(str(value) for value in row.get("available_series_ids", []))
        missing = sorted(set(required) - set(available))
        normalized_rows.append(
            {
                "scenario_id": str(row["scenario_id"]),
                "as_of": str(row["as_of"]),
                "required_series_count": len(required),
                "available_series_count": len(available),
                "missing_series_count": len(missing),
                "available_series_ids": available,
                "missing_series_ids": missing,
                "input_readiness_status": (
                    "all_direct_series_present"
                    if not missing
                    else "partial_official_pit_history"
                ),
            }
        )
    return {
        "audit_version": "phase118_strict_replay_input_audit_v1",
        "data_mode": "vintage_as_of",
        "database_vintage_series_count": int(
            payload["database_vintage_series_count"]
        ),
        "scenario_count": len(normalized_rows),
        "required_direct_series_count": len(required),
        "scenario_with_all_required_series_count": sum(
            not row["missing_series_ids"] for row in normalized_rows
        ),
        "scenario_with_partial_input_count": sum(
            bool(row["missing_series_ids"]) for row in normalized_rows
        ),
        "scenario_rows": normalized_rows,
        "model_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "accuracy_metric_count": 0,
        "performance_metric_count": 0,
        "result": "passed",
    }


def load_broader_pit_status(path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return {
            "report_version": "phase118_broader_pit_release_replay_v1",
            "broader_pit_series_count": 13,
            "completed_series_count": 0,
            "failed_series_count": 0,
            "normalized_release_event_row_count_planned": 0,
            "result": "not_started",
        }
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid Phase118 broader PIT status")
    return payload


def _release_event_upsert_sql(
    *,
    rows: list[dict[str, Any]],
    artifact_id: str,
    content_hash: str,
    fetched_at: str,
) -> str:
    values = []
    for row in rows:
        provenance = _hash_payload(
            {
                "release_event_id": row["release_event_id"],
                "expected_release_at_utc": row["expected_release_at_utc"],
                "artifact_id": artifact_id,
            }
        )
        values.append(
            "(" + ", ".join(
                [
                    _literal(row["series_key"]),
                    _literal(row["release_event_id"]),
                    _literal(row["release_family"]),
                    _literal(row["source_reference_period_label"]),
                    _literal(row["reference_period_precision"]),
                    _literal(row["reference_period_start"]) + "::date",
                    _literal(row["reference_period_end"]) + "::date",
                    _literal(row["expected_release_at_utc"]) + "::timestamptz",
                    "NULL",
                    _literal(row["release_semantics"]),
                    _literal(row["availability_precision"]),
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
  'phase118_revision_aware_release_calendar',
  {_literal(fetched_at)}::timestamptz, {_literal(content_hash)},
  'application/json', 'official_release_calendar_normalizer_v2',
  'phase118_revision_event_calendar_v1', TRUE,
  'validated_expected_events_no_actual_release_claim'
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
  reference_period_start = EXCLUDED.reference_period_start,
  reference_period_end = EXCLUDED.reference_period_end,
  expected_release_at_utc = EXCLUDED.expected_release_at_utc,
  actual_release_at_utc = EXCLUDED.actual_release_at_utc,
  release_semantics = EXCLUDED.release_semantics,
  availability_precision = EXCLUDED.availability_precision,
  release_status = EXCLUDED.release_status,
  source_artifact_id = EXCLUDED.source_artifact_id,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _strict_replay_input_sql(
    scenarios: list[dict[str, str]],
    required_series: list[str],
) -> str:
    scenario_values = ",\n".join(
        f"({_literal(row['scenario_id'])}, {_literal(row['as_of'])}::date)"
        for row in scenarios
    )
    series_values = ",\n".join(
        f"({_literal(series_id)})" for series_id in required_series
    )
    return f"""
WITH scenarios(scenario_id, as_of) AS (
  VALUES
{scenario_values}
),
required(series_key) AS (
  VALUES
{series_values}
),
availability AS (
  SELECT s.scenario_id, s.as_of, r.series_key,
         EXISTS (
           SELECT 1
           FROM macro.observation_vintage v
           WHERE v.series_key = r.series_key
             AND v.observation_date <= s.as_of
             AND v.realtime_start <= s.as_of
             AND v.realtime_end >= s.as_of
         ) AS available
  FROM scenarios s CROSS JOIN required r
),
scenario_rows AS (
  SELECT scenario_id, as_of,
         array_agg(series_key ORDER BY series_key)
           FILTER (WHERE available) AS available_series_ids
  FROM availability
  GROUP BY scenario_id, as_of
)
SELECT json_build_object(
  'transaction_read_only', current_setting('transaction_read_only'),
  'database_vintage_series_count',
    (SELECT count(DISTINCT series_key) FROM macro.observation_vintage),
  'scenario_rows',
    (SELECT json_agg(json_build_object(
       'scenario_id', scenario_id,
       'as_of', to_char(as_of, 'YYYY-MM-DD'),
       'available_series_ids', coalesce(available_series_ids, ARRAY[]::text[])
     ) ORDER BY as_of) FROM scenario_rows)
)::text;
""".strip()


def _scenario_rows(path: str | Path) -> list[dict[str, str]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "historical_validation_scenario_manifest"
    ]
    return [
        {
            "scenario_id": str(row["scenario_id"]),
            "as_of": str(row["validation_window_start"]),
        }
        for row in payload["scenario_rows"]
    ]


def _all_direct_series_ids() -> list[str]:
    payload = yaml.safe_load(
        (ROOT / "specs/common/nas_postgres_live_revised_import_contract.yaml").read_text(
            encoding="utf-8"
        )
    )
    return list(
        payload["nas_postgres_live_revised_import_contract"]["source_policy"]
        ["direct_series_ids"]
    )


def _reference_period(
    *,
    label: str,
    release_date: str,
    series_id: str,
    weekly_rules: dict[str, Any],
) -> tuple[str, str, str]:
    if label == "weekly":
        rule = weekly_rules.get(series_id)
        if not isinstance(rule, dict):
            raise ValueError(f"missing governed weekly rule for {series_id}")
        end = date.fromisoformat(release_date) - timedelta(
            days=int(rule["reference_period_end_days_before_release"])
        )
        return (
            (end - timedelta(days=6)).isoformat(),
            end.isoformat(),
            str(rule["reference_period_precision"]),
        )
    month_match = MONTH_RE.fullmatch(label)
    if month_match:
        year = int(month_match.group(1))
        month = int(month_match.group(2))
        if not 1 <= month <= 12:
            raise ValueError(f"invalid monthly reference period: {label}")
        return (
            date(year, month, 1).isoformat(),
            date(year, month, monthrange(year, month)[1]).isoformat(),
            "month",
        )
    quarter_match = QUARTER_RE.fullmatch(label)
    if quarter_match:
        year = int(quarter_match.group(1))
        quarter = int(quarter_match.group(2))
        start_month = 1 + (quarter - 1) * 3
        end_month = start_month + 2
        return (
            date(year, start_month, 1).isoformat(),
            date(year, end_month, monthrange(year, end_month)[1]).isoformat(),
            "quarter",
        )
    raise ValueError(f"unsupported reference period: {label}")


def _release_semantics(label: str) -> str:
    lowered = label.lower()
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


def _validated_artifact_dir(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("Phase118 artifacts must remain outside the repository")
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


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument(
        "--artifact-dir",
        default="/var/lib/business-cycle/source-artifacts/phase118",
    )
    parser.add_argument("--no-resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.execute_live:
        print(
            json.dumps(
                summarize_nas_broader_pit_release_replay_contract(),
                indent=2,
            )
        )
        return 0
    report = run_nas_broader_pit_release_replay(
        execute_live=True,
        operator_confirmation=os.environ.get(
            "BUSINESS_CYCLE_PHASE118_OPERATOR_CONFIRMATION"
        ),
        artifact_dir=args.artifact_dir,
        resume=not args.no_resume,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
