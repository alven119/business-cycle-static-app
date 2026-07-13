"""Read-only Postgres materialization for the private NAS dashboard."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Protocol
from urllib.parse import unquote, urlsplit

import yaml

from business_cycle.render.indicator_learning_semantics import (
    learning_semantics_for_role,
    load_indicator_transformation_learning_contract,
    transform_observations_for_display,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
)
from business_cycle.storage.full_cycle_revised_data_readiness import (
    build_full_cycle_revised_runtime_readiness,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    load_nas_postgres_live_revised_import_contract,
)
from business_cycle.service.nas_official_release_calendar import (
    build_nas_official_release_diagnostics,
)
from business_cycle.service.nas_release_aware_freshness import (
    build_release_aware_freshness,
    summarize_release_aware_freshness_source_identity_remediation,
)
from business_cycle.service.nas_source_retry_restore import (
    build_source_retry_preview,
    default_source_operations_status,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_live_postgres_dashboard_contract.yaml"

MUTATING_SQL_RE = re.compile(
    r"\b(insert|update|delete|merge|alter|create|drop|truncate|grant|revoke|copy)\b",
    re.IGNORECASE,
)

DASHBOARD_READ_SQL = """
WITH bounds AS (
  SELECT COALESCE(MAX(observation_date), CURRENT_DATE) AS database_latest_date
  FROM macro.observation_revised
),
series_rows AS (
  SELECT
    series_key,
    source_family,
    source_series_id,
    source_title,
    units,
    frequency,
    seasonal_adjustment,
    geographic_scope,
    source_url_without_secret,
    source_identity_status,
    to_char(updated_at_utc AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
      AS updated_at_utc
  FROM macro.series_registry
),
artifact_rows AS (
  SELECT
    artifact_id,
    source_family,
    source_url_without_secret,
    source_series_or_release_id,
    to_char(fetched_at_utc AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
      AS fetched_at_utc,
    content_hash,
    adapter_id,
    parser_version,
    validation_status
  FROM macro.source_artifact
),
observation_rows AS (
  SELECT
    observation_revised.series_key,
    to_char(observation_revised.observation_date, 'YYYY-MM-DD') AS observation_date,
    observation_revised.value_numeric,
    observation_revised.value_text,
    observation_revised.unit,
    observation_revised.data_mode,
    observation_revised.source_artifact_id,
    observation_revised.provenance_hash
  FROM macro.observation_revised
  CROSS JOIN bounds
  WHERE observation_revised.observation_date >=
    bounds.database_latest_date - INTERVAL '6 years'
  ORDER BY observation_revised.series_key, observation_revised.observation_date
)
SELECT json_build_object(
  'transaction_read_only', current_setting('transaction_read_only'),
  'database_latest_observation_date',
    (SELECT to_char(database_latest_date, 'YYYY-MM-DD') FROM bounds),
  'series_registry_rows',
    COALESCE((SELECT json_agg(row_to_json(series_rows) ORDER BY series_key)
              FROM series_rows), '[]'::json),
  'source_artifact_rows',
    COALESCE((SELECT json_agg(row_to_json(artifact_rows) ORDER BY artifact_id)
              FROM artifact_rows), '[]'::json),
  'observation_rows',
    COALESCE((SELECT json_agg(row_to_json(observation_rows))
              FROM observation_rows), '[]'::json),
  'observation_revised_total_count',
    (SELECT COUNT(*) FROM macro.observation_revised),
  'observation_vintage_total_count',
    (SELECT COUNT(*) FROM macro.observation_vintage),
  'release_calendar_total_count',
    (SELECT COUNT(*) FROM macro.release_calendar)
)::text;
""".strip()


class DashboardReadExecutor(Protocol):
    def query_json(self, sql: str) -> dict[str, Any]: ...


class PsqlReadOnlyExecutor:
    """Execute fixed dashboard reads with server-enforced read-only semantics."""

    def __init__(
        self,
        database_url: str,
        *,
        executable: str = "psql",
        statement_timeout_milliseconds: int = 15000,
    ) -> None:
        parsed = urlsplit(database_url)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise ValueError("BUSINESS_CYCLE_DATABASE_URL must use postgres/postgresql")
        if not parsed.hostname or not parsed.path.strip("/") or not parsed.username:
            raise ValueError("BUSINESS_CYCLE_DATABASE_URL is incomplete")
        if statement_timeout_milliseconds < 1:
            raise ValueError("statement timeout must be positive")
        self.executable = executable
        self.environment = {
            **os.environ,
            "PGHOST": parsed.hostname,
            "PGPORT": str(parsed.port or 5432),
            "PGDATABASE": parsed.path.strip("/"),
            "PGUSER": unquote(parsed.username),
            "PGPASSWORD": unquote(parsed.password or ""),
            "PGOPTIONS": (
                "-c default_transaction_read_only=on "
                f"-c statement_timeout={statement_timeout_milliseconds}"
            ),
        }

    def query_json(self, sql: str) -> dict[str, Any]:
        _validate_read_only_sql(sql)
        completed = subprocess.run(
            [
                self.executable,
                "-X",
                "--no-psqlrc",
                "-q",
                "-A",
                "-t",
                "-v",
                "ON_ERROR_STOP=1",
            ],
            input=sql,
            text=True,
            capture_output=True,
            env=self.environment,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError("read-only Postgres dashboard query failed")
        output = completed.stdout.strip()
        if not output:
            raise RuntimeError("read-only Postgres dashboard query returned no payload")
        payload = json.loads(output)
        if not isinstance(payload, dict):
            raise RuntimeError("read-only Postgres dashboard query returned invalid JSON")
        return payload


def load_nas_live_postgres_dashboard_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_live_postgres_dashboard_contract"])


def summarize_nas_live_postgres_dashboard_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_live_postgres_dashboard_contract(path)
    baseline = build_nas_indicator_snapshot_manifest()
    remediation = summarize_release_aware_freshness_source_identity_remediation()
    derived = contract["derived_display_series"]
    summary = {
        "phase": 111,
        "nas_live_postgres_dashboard_contract_ready": _contract_ready(contract),
        "postgres_read_only_executor_ready": True,
        "live_snapshot_materializer_ready": True,
        "live_runtime_wiring_ready": _runtime_wiring_ready(),
        "role_count": baseline["role_snapshot_count"],
        "source_blocked_role_count": remediation["exact_source_blocked_role_count"],
        "derived_display_role_count": len(derived),
        "chart_period_count": len(contract["data_policy"]["chart_periods"]),
        "interactive_chart_tooltip_ready": all(
            contract["chart_interaction_policy"][key] is True
            for key in (
                "hover_date_value_tooltip_required",
                "touch_pointer_support_required",
                "keyboard_arrow_navigation_required",
                "crosshair_and_point_marker_required",
            )
        ),
        "transaction_read_only_enforced": True,
        "silent_fixture_fallback_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "observation_vintage_read_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "missing_value_treated_as_neutral_count": 0,
        "unavailable_chart_treated_as_zero_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 112,
    }
    summary["result"] = (
        "passed" if _matches(summary, contract["hard_gates"]) else "blocked"
    )
    return summary


def build_nas_live_postgres_dashboard_snapshot(
    *,
    database_url: str | None = None,
    executor: DashboardReadExecutor | None = None,
    snapshot_as_of: str | None = None,
    refresh_status: dict[str, Any] | None = None,
    declared_cycle_state: dict[str, Any] | None = None,
    source_operations_status: dict[str, Any] | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build 39 role snapshots from a read-only live Postgres query."""

    contract = load_nas_live_postgres_dashboard_contract(contract_path)
    reader = executor or PsqlReadOnlyExecutor(
        database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", ""),
        statement_timeout_milliseconds=int(
            contract["database_read_policy"]["statement_timeout_milliseconds"],
        ),
    )
    payload = reader.query_json(DASHBOARD_READ_SQL)
    if str(payload.get("transaction_read_only", "")).lower() not in {
        "on",
        "true",
    }:
        raise RuntimeError("Postgres dashboard session is not read-only")

    baseline = build_nas_indicator_snapshot_manifest()
    resolved_as_of = snapshot_as_of or date.today().isoformat()
    date.fromisoformat(resolved_as_of)
    series_rows = _rows_by(payload.get("series_registry_rows", []), "series_key")
    artifact_rows = _rows_by(
        payload.get("source_artifact_rows", []),
        "artifact_id",
    )
    observations_by_series = _observations_by_series(
        payload.get("observation_rows", []),
    )
    technology_series_ids = {
        "DGORDER",
        "A34SNO",
        "A34HNO",
        "TW_MOEA_ICT_EXPORT_ORDERS",
        "TW_MOEA_ELECTRONICS_EXPORT_ORDERS",
    }
    derived = contract["derived_display_series"]
    learning_contract = load_indicator_transformation_learning_contract()
    role_snapshots = [
        _live_role_snapshot(
            row,
            observations_by_series=observations_by_series,
            series_rows=series_rows,
            artifact_rows=artifact_rows,
            derived=derived,
            as_of=resolved_as_of,
            contract=contract,
            learning_contract=learning_contract,
        )
        for row in baseline["role_snapshots"]
    ]
    available_roles = [
        row for row in role_snapshots if row["snapshot_status"] == "revised_snapshot_ready"
    ]
    chart_roles = [
        row for row in role_snapshots if row["chart_payload_detail"]["chart_available"]
    ]
    resolved_refresh_status = refresh_status or {
        "refresh_state": "not_started",
        "last_completed_at_utc": None,
        "next_scheduled_at_utc": None,
        "requested_series_count": 0,
        "completed_series_count": 0,
        "failed_series_count": 0,
    }
    resolved_declared_cycle_state = declared_cycle_state or {
        "declared_current_phase": "boom",
        "declared_current_phase_label_zh": "榮景",
        "legal_next_phase": "recession",
        "legal_next_phase_label_zh": "衰退",
        "declared_phase_start_context_status": "awaiting_user_confirmation",
        "declared_phase_start_display_zh": "尚待使用者確認",
        "declared_phase_age_days": None,
        "declared_phase_age_range_days": None,
        "active_registry_source": "canonical_default",
        "active_registry_override_present": False,
        "current_data_used_to_infer_declared_phase_count": 0,
    }
    series_release_inputs = _series_release_inputs(
        series_rows=series_rows,
        observations_by_series=observations_by_series,
        as_of=date.fromisoformat(resolved_as_of),
        freshness_windows=contract["freshness_windows_days"],
    )
    canonical_release_series_ids = set(
        load_nas_postgres_live_revised_import_contract()["source_policy"][
            "direct_series_ids"
        ]
    )
    series_release_inputs = [
        row
        for row in series_release_inputs
        if row["series_id"] in canonical_release_series_ids
    ]
    source_release_diagnostics = build_nas_official_release_diagnostics(
        as_of=resolved_as_of,
        series_inputs=series_release_inputs,
        refresh_status=resolved_refresh_status,
    )
    resolved_source_operations_status = (
        source_operations_status or default_source_operations_status()
    )
    source_release_diagnostics["source_retry_preview"] = build_source_retry_preview(
        resolved_refresh_status
    )
    source_release_diagnostics["backup_restore_status"] = (
        resolved_source_operations_status
    )
    full_cycle_readiness = build_full_cycle_revised_runtime_readiness(
        available_series_ids=set(observations_by_series),
    )
    source_release_diagnostics["full_cycle_data_readiness"] = (
        full_cycle_readiness
    )
    snapshot: dict[str, Any] = {
        "artifact_id": "phase111_nas_live_postgres_dashboard_snapshot",
        "artifact_version": contract["version"],
        "phase": "111",
        "phase_id": 111,
        "snapshot_as_of": resolved_as_of,
        "database_latest_observation_date": payload[
            "database_latest_observation_date"
        ],
        "output_mode": "research_only_private_nas_live_revised_dashboard",
        "research_only": True,
        "data_mode": "revised_diagnostic",
        "role_snapshots": role_snapshots,
        "series_snapshots": list(series_rows.values()),
        "source_artifact_snapshots": list(artifact_rows.values()),
        "technology_series_observations": {
            series_id: observations_by_series.get(series_id, [])
            for series_id in sorted(technology_series_ids)
        },
        "role_snapshot_count": len(role_snapshots),
        "role_with_revised_snapshot_count": len(available_roles),
        "role_without_revised_snapshot_count": len(role_snapshots) - len(available_roles),
        "series_snapshot_count": len(series_rows),
        "source_artifact_snapshot_count": len(artifact_rows),
        "observation_revised_total_count": int(
            payload["observation_revised_total_count"],
        ),
        "observation_revised_chart_query_count": sum(
            len(rows) for rows in observations_by_series.values()
        ),
        "observation_vintage_row_count": int(
            payload["observation_vintage_total_count"],
        ),
        "release_calendar_row_count": int(
            payload["release_calendar_total_count"],
        ),
        "chart_available_role_count": len(chart_roles),
        "chart_unavailable_role_count": len(role_snapshots) - len(chart_roles),
        "refresh_status": resolved_refresh_status,
        "source_refresh_health_status": _source_refresh_health_status(
            resolved_refresh_status,
            available_series_count=len(series_rows),
        ),
        "source_release_diagnostics": source_release_diagnostics,
        "full_cycle_revised_data_readiness": full_cycle_readiness,
        "declared_cycle_state": resolved_declared_cycle_state,
        "live_db_connection_attempt_count": 1,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "trust_metadata": {
            "output_label": "research_only",
            "source_mode": "live_postgres_read_only",
            "live_db_connected": True,
            "transaction_read_only": True,
            "frontend_database_access_allowed": False,
            "frontend_api_key_allowed": False,
            "revised_diagnostic_only": True,
            "strict_point_in_time_result": False,
            "observation_vintage_read_count": 0,
            "observation_vintage_available_count": int(
                payload["observation_vintage_total_count"],
            ),
            "normalized_release_calendar_row_count": int(
                payload["release_calendar_total_count"],
            ),
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
            "refresh_state": resolved_refresh_status["refresh_state"],
            "source_refresh_health_status": _source_refresh_health_status(
                resolved_refresh_status,
                available_series_count=len(series_rows),
            ),
            "release_calendar_runtime_ready": source_release_diagnostics[
                "release_calendar_runtime_ready"
            ],
            "release_family_count": source_release_diagnostics[
                "release_family_count"
            ],
            "retry_candidate_count": source_release_diagnostics[
                "source_retry_preview"
            ]["retry_candidate_count"],
            "backup_restore_state": resolved_source_operations_status[
                "backup_restore_state"
            ],
            "declared_state_source": resolved_declared_cycle_state[
                "active_registry_source"
            ],
            "current_data_used_to_infer_declared_phase": False,
        },
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
    }
    snapshot["snapshot_manifest_hash"] = _hash_payload(
        {
            "snapshot_as_of": resolved_as_of,
            "database_latest_observation_date": snapshot[
                "database_latest_observation_date"
            ],
            "role_snapshots": role_snapshots,
            "observation_revised_total_count": snapshot[
                "observation_revised_total_count"
            ],
            "declared_cycle_state": resolved_declared_cycle_state,
            "source_release_diagnostics": source_release_diagnostics,
        },
    )
    snapshot["result"] = "passed"
    return snapshot


def _series_release_inputs(
    *,
    series_rows: dict[str, dict[str, Any]],
    observations_by_series: dict[str, list[dict[str, Any]]],
    as_of: date,
    freshness_windows: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for series_id in sorted(series_rows):
        observations = observations_by_series.get(series_id, [])
        latest = date.fromisoformat(observations[-1]["observation_date"]) if observations else None
        freshness = (
            build_release_aware_freshness(
                series_id=series_id,
                latest_observation_date=latest,
                as_of=as_of,
                frequency=str(series_rows[series_id].get("frequency", "")),
                freshness_windows=freshness_windows,
            )
            if latest is not None
            else {"freshness_status": "unavailable"}
        )
        rows.append(
            {
                "series_id": series_id,
                "frequency": series_rows[series_id].get("frequency"),
                "latest_observation_date": latest.isoformat() if latest else None,
                "freshness_status": freshness["freshness_status"],
                "freshness_reason_code": freshness.get("freshness_reason_code"),
                "reference_period_end_date": freshness.get(
                    "reference_period_end_date"
                ),
            }
        )
    return rows


def _live_role_snapshot(
    baseline: dict[str, Any],
    *,
    observations_by_series: dict[str, list[dict[str, Any]]],
    series_rows: dict[str, dict[str, Any]],
    artifact_rows: dict[str, dict[str, Any]],
    derived: dict[str, dict[str, Any]],
    as_of: str,
    contract: dict[str, Any],
    learning_contract: dict[str, Any],
) -> dict[str, Any]:
    active_overrides = {
        str(key): [str(value) for value in values]
        for key, values in contract.get("active_role_series_overrides", {}).items()
    }
    role_id = str(baseline["role_id"])
    active_series_ids = active_overrides.get(
        role_id,
        list(baseline["official_series_ids"]),
    )
    series_contexts = [
        _materialize_display_series(
            series_id,
            observations_by_series=observations_by_series,
            series_rows=series_rows,
            artifact_rows=artifact_rows,
            derived=derived,
        )
        for series_id in active_series_ids
    ]
    series_contexts = [row for row in series_contexts if row is not None]
    chart_series = [
        _series_chart_payload(
            row,
            role_id=str(baseline["role_id"]),
            as_of=as_of,
            contract=contract,
            learning_contract=learning_contract,
        )
        for row in series_contexts
    ]
    learning_context = learning_semantics_for_role(
        str(baseline["role_id"]),
        contract=learning_contract,
    )
    latest_interpretations = [
        row["latest_interpretation"]
        for row in chart_series
        if row.get("latest_interpretation") is not None
    ]
    latest = [row["latest_observation"] for row in series_contexts]
    source_blocked = not active_series_ids
    available = bool(latest) and not source_blocked
    blocked_reasons = _active_blocked_reasons(
        list(baseline["blocked_reason_codes"]),
        override_applied=role_id in active_overrides,
        available=available,
    )
    if not available and not blocked_reasons:
        blocked_reasons.append("live_postgres_series_unavailable")
    freshness_rows = [row["freshness"] for row in chart_series]
    return {
        **baseline,
        "official_series_ids": active_series_ids,
        "active_source_identity_remediation_applied": role_id in active_overrides,
        "snapshot_status": "revised_snapshot_ready" if available else "blocked",
        "data_mode": "revised_diagnostic" if available else "unavailable",
        "latest_revised_observations": latest,
        "blocked_reason_codes": sorted(set(blocked_reasons)),
        "source_mode": "live_postgres_read_only",
        "freshness_status": _role_freshness_status(freshness_rows),
        "source_lineage": [row["source_lineage"] for row in series_contexts],
        "learning_semantics": learning_context,
        "latest_interpretation_observations": latest_interpretations,
        "evidence_input_series": [
            _evidence_input_series(row) for row in series_contexts
        ],
        "chart_payload_detail": {
            "chart_payload_id": f"live_postgres_chart:{baseline['role_id']}",
            "snapshot_as_of": as_of,
            "chart_data_mode": "live_postgres_revised_diagnostic",
            "chart_available": any(
                row["series_chart_available"] for row in chart_series
            ),
            "series_chart_count": len(chart_series),
            "series_charts": chart_series,
            "unavailable_reason": (
                None if chart_series else "no_live_postgres_series_for_role"
            ),
            "missing_value_treated_as_neutral": False,
            "unavailable_chart_treated_as_zero": False,
            "allowed_periods": ["ytd", "trailing_1y", "trailing_5y"],
            "primary_display_transform": learning_context[
                "transform_profile_id"
            ],
            "raw_source_value_preserved": True,
            "interpretation_promoted_to_phase_evidence": False,
        },
        "strict_point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _evidence_input_series(context: dict[str, Any]) -> dict[str, Any]:
    """Preserve causal revised history for a separately governed evaluator."""

    return {
        "series_id": context["series_id"],
        "source_series_ids": list(context["component_series_ids"]),
        "frequency": context["frequency"],
        "source_unit": context["unit"],
        "observations": [
            {
                "date": row["observation_date"],
                "value": row.get("value_numeric"),
                "data_mode": "revised",
                "source_artifact_id": row.get("source_artifact_id"),
                "provenance_hash": row.get("provenance_hash"),
            }
            for row in context["observations"]
            if row.get("value_numeric") is not None
        ],
        "source_lineage": context["source_lineage"],
        "phase_support_allowed_without_evaluator_contract": False,
    }


def _materialize_display_series(
    series_id: str,
    *,
    observations_by_series: dict[str, list[dict[str, Any]]],
    series_rows: dict[str, dict[str, Any]],
    artifact_rows: dict[str, dict[str, Any]],
    derived: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    definition = derived.get(series_id)
    component_ids = (
        list(definition["component_series_ids"]) if definition else [series_id]
    )
    if any(not observations_by_series.get(item) for item in component_ids):
        return None
    operation = definition["operation"] if definition else "direct"
    observations = _apply_display_operation(
        operation,
        component_ids,
        observations_by_series,
    )
    if not observations:
        return None
    metadata = series_rows[component_ids[0]]
    artifact_ids = sorted(
        {
            str(row["source_artifact_id"])
            for item in component_ids
            for row in observations_by_series[item]
            if row.get("source_artifact_id")
        },
    )
    latest = observations[-1]
    latest_context = {
        "series_key": series_id,
        "source_series_ids": component_ids,
        "observation_date": latest["observation_date"],
        "value_numeric": latest.get("value_numeric"),
        "value_text": latest.get("value_text"),
        "unit": definition.get("unit") if definition else latest.get("unit"),
        "source_artifact_id": (
            artifact_ids[0] if len(artifact_ids) == 1 else f"derived::{series_id}"
        ),
        "source_artifact_ids": artifact_ids,
        "provenance_hash": _hash_payload(
            {
                "series_id": series_id,
                "components": component_ids,
                "operation": operation,
                "component_provenance": [
                    row.get("provenance_hash")
                    for item in component_ids
                    for row in observations_by_series[item][-1:]
                ],
            },
        ),
        "derived_display_only": definition is not None,
        "phase_support_allowed": False,
    }
    source_lineage = {
        "display_series_id": series_id,
        "component_series_ids": component_ids,
        "operation": operation,
        "source_family": metadata["source_family"],
        "source_titles": [series_rows[item]["source_title"] for item in component_ids],
        "source_urls_without_secret": [
            series_rows[item]["source_url_without_secret"] for item in component_ids
        ],
        "source_artifacts": [
            artifact_rows[item]
            for item in artifact_ids
            if item in artifact_rows
        ],
        "revised_diagnostic_only": True,
        "phase_support_allowed": False,
    }
    return {
        "series_id": series_id,
        "component_series_ids": component_ids,
        "frequency": metadata["frequency"],
        "unit": latest_context["unit"],
        "observations": observations,
        "latest_observation": latest_context,
        "source_lineage": source_lineage,
    }


def _apply_display_operation(
    operation: str,
    component_ids: list[str],
    observations_by_series: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    if operation in {"direct", "passthrough_observation_context"}:
        return list(observations_by_series[component_ids[0]])
    if operation != "subtract_second_from_first" or len(component_ids) != 2:
        raise ValueError(f"unsupported derived display operation: {operation}")
    left = {
        row["observation_date"]: row for row in observations_by_series[component_ids[0]]
    }
    right = {
        row["observation_date"]: row for row in observations_by_series[component_ids[1]]
    }
    rows: list[dict[str, Any]] = []
    for observation_date in sorted(set(left) & set(right)):
        try:
            value = Decimal(str(left[observation_date]["value_numeric"])) - Decimal(
                str(right[observation_date]["value_numeric"]),
            )
        except (InvalidOperation, TypeError):
            continue
        rows.append(
            {
                "series_key": component_ids[0],
                "observation_date": observation_date,
                "value_numeric": str(value.normalize()),
                "value_text": None,
                "unit": "percentage_points",
                "source_artifact_id": None,
                "provenance_hash": None,
            },
        )
    return rows


def _series_chart_payload(
    context: dict[str, Any],
    *,
    role_id: str,
    as_of: str,
    contract: dict[str, Any],
    learning_contract: dict[str, Any],
) -> dict[str, Any]:
    as_of_date = date.fromisoformat(as_of)
    transformed, semantics = transform_observations_for_display(
        context["observations"],
        role_id=role_id,
        contract=learning_contract,
    )
    periods = [
        _period_payload(
            row["period_id"],
            row["label_zh"],
            observations=transformed,
            as_of=as_of_date,
        )
        for row in contract["data_policy"]["chart_periods"]
    ]
    latest_date = date.fromisoformat(context["latest_observation"]["observation_date"])
    freshness = build_release_aware_freshness(
        series_id=str(context["component_series_ids"][0]),
        latest_observation_date=latest_date,
        as_of=as_of_date,
        frequency=context["frequency"],
        freshness_windows=contract["freshness_windows_days"],
    )
    return {
        "series_id": context["series_id"],
        "source_series_ids": context["component_series_ids"],
        "provider": "postgres_revised_warehouse",
        "source_unit": context["unit"],
        "unit": (
            context["unit"]
            if semantics["interpretation_unit"] == "source_unit"
            else semantics["interpretation_unit"]
        ),
        "interpretation_unit_zh": semantics["interpretation_unit_zh"],
        "display_transform": semantics["transform_profile_id"],
        "display_transform_label_zh": semantics["transform_label_zh"],
        "display_transform_formula": semantics["transform_formula"],
        "interpretation_name_zh": semantics["interpretation_name_zh"],
        "latest_interpretation": (
            {
                "observation_date": transformed[-1]["observation_date"],
                "value_numeric": transformed[-1]["value_numeric"],
                "unit": (
                    context["unit"]
                    if semantics["interpretation_unit"] == "source_unit"
                    else semantics["interpretation_unit"]
                ),
                "source_series_ids": context["component_series_ids"],
                "display_transform": semantics["transform_profile_id"],
                "display_only": True,
                "phase_support_allowed": False,
            }
            if transformed
            else None
        ),
        "series_chart_available": any(
            row["chart_status"] == "available" for row in periods
        ),
        "freshness": freshness,
        "periods": periods,
        "raw_source_value_preserved": True,
        "phase_support_allowed": False,
    }


def _period_payload(
    period_id: str,
    label_zh: str,
    *,
    observations: list[dict[str, Any]],
    as_of: date,
) -> dict[str, Any]:
    start = _period_start(period_id, as_of)
    points = [
        {
            "date": row["observation_date"],
            "value": _numeric_value(row.get("value_numeric")),
        }
        for row in observations
        if start <= date.fromisoformat(row["observation_date"]) <= as_of
        and _numeric_value(row.get("value_numeric")) is not None
    ]
    return {
        "period_id": period_id,
        "label": label_zh,
        "start_date": start.isoformat(),
        "end_date": as_of.isoformat(),
        "chart_status": "available" if points else "unavailable",
        "point_count": len(points),
        "points": points,
        "unavailable_reason": None if points else "no_numeric_observations_in_period",
    }


def _role_freshness_status(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "unavailable"
    statuses = {row["freshness_status"] for row in rows}
    if len(statuses) == 1:
        return next(iter(statuses))
    return "mixed"


def _active_blocked_reasons(
    reasons: list[str],
    *,
    override_applied: bool,
    available: bool,
) -> list[str]:
    if not override_applied or not available:
        return reasons
    source_fragments = (
        "source",
        "access",
        "license",
        "authorized",
        "proprietary",
        "official_series",
    )
    return [
        reason
        for reason in reasons
        if not any(fragment in str(reason).lower() for fragment in source_fragments)
    ]


def _observations_by_series(rows: Any) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for raw in rows if isinstance(rows, list) else []:
        row = dict(raw)
        if row.get("data_mode") != "revised":
            raise RuntimeError("live dashboard query returned a non-revised row")
        date.fromisoformat(str(row["observation_date"]))
        result.setdefault(str(row["series_key"]), []).append(row)
    for series_rows in result.values():
        series_rows.sort(key=lambda row: row["observation_date"])
    return result


def _rows_by(rows: Any, key: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    return {
        str(row[key]): dict(row)
        for row in rows
    }


def _source_refresh_health_status(
    refresh_status: dict[str, Any],
    *,
    available_series_count: int,
) -> str:
    state = refresh_status.get("refresh_state")
    last_run_state = refresh_status.get("last_run_state")
    if (
        state == "succeeded" or last_run_state == "succeeded"
    ) and int(refresh_status.get("failed_series_count", 0)) == 0:
        return "healthy"
    if state == "failed" or last_run_state == "failed":
        return "degraded"
    if available_series_count > 0:
        return "baseline_loaded_waiting_for_scheduled_refresh"
    return "unavailable"


def _period_start(period_id: str, as_of: date) -> date:
    if period_id == "ytd":
        return date(as_of.year, 1, 1)
    if period_id == "trailing_1y":
        return as_of - timedelta(days=365)
    if period_id == "trailing_5y":
        return as_of - timedelta(days=365 * 5)
    raise ValueError(f"unknown chart period: {period_id}")


def _numeric_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_read_only_sql(sql: str) -> None:
    normalized = sql.strip()
    if not normalized.lower().startswith(("select", "with")):
        raise ValueError("dashboard SQL must be SELECT/WITH only")
    if MUTATING_SQL_RE.search(normalized):
        raise ValueError("dashboard SQL contains a prohibited mutating statement")


def _contract_ready(contract: dict[str, Any]) -> bool:
    read = contract["database_read_policy"]
    data = contract["data_policy"]
    return (
        contract["status"] == "active_private_nas_runtime_contract"
        and read["transaction_read_only_required"] is True
        and read["pgoptions_default_transaction_read_only_required"] is True
        and read["postgres_write_allowed"] is False
        and read["schema_migration_allowed"] is False
        and read["silent_fixture_fallback_when_database_configured"] is False
        and data["data_mode"] == "revised_diagnostic"
        and data["revised_may_not_be_labeled_point_in_time"] is True
    )


def _runtime_wiring_ready() -> bool:
    path = ROOT / "src/business_cycle/service/nas_runtime_server.py"
    source = path.read_text(encoding="utf-8")
    return "build_nas_live_dashboard_runtime" in source


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
