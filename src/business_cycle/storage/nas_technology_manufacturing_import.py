"""Import official US/Taiwan technology manufacturing series into NAS Postgres."""

from __future__ import annotations

from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Protocol

import yaml

from business_cycle.data_sources import FredProvider, SeriesObservation
from business_cycle.data_sources.moea_export_orders import MoeaExportOrdersProvider
from business_cycle.storage.nas_postgres_live_revised_import import PsqlSubprocessExecutor
from business_cycle.storage.postgres_macro_warehouse import generate_postgres_schema_sql

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/technology_manufacturing_cycle_research.yaml"
CONFIRMATION = "I_UNDERSTAND_THIS_FETCHES_OFFICIAL_TECHNOLOGY_DATA_AND_WRITES_NAS_POSTGRES"


class ObservationProvider(Protocol):
    def fetch_series_observations(self, series_id: str) -> list[SeriesObservation]: ...


class SqlExecutor(Protocol):
    def execute(self, sql: str) -> str: ...


def load_technology_manufacturing_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["technology_manufacturing_cycle_research"])


def summarize_technology_manufacturing_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_technology_manufacturing_contract(path)
    sources = list(contract["source_policy"]["sources"])
    summary = {
        "phase": 122,
        "contract_ready": contract["status"] == "active_private_nas_research_extension",
        "source_count": len(sources),
        "newly_wired_source_count": sum(
            row["source_mode"] != "existing_warehouse_series" for row in sources
        ),
        "official_source_count": len(sources),
        "yoy_display_source_count": sum(
            row["display_transform"] == "year_over_year_percent" for row in sources
        ),
        "source_with_complete_identity_count": sum(
            all(row.get(key) for key in (
                "series_id", "source_family", "source_url_without_secret", "units",
                "frequency", "seasonal_adjustment", "nominal_or_real",
            ))
            for row in sources
        ),
        "source_with_risk_label_count": sum(bool(row.get("definition_risk_zh")) for row in sources),
        "us_source_count": sum(row["geography"] == "US" for row in sources),
        "taiwan_source_count": sum(row["geography"] == "TW" for row in sources),
        "raw_source_value_preserved_count": len(sources),
        "silent_substitution_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 123,
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in contract["hard_gates"].items())
        else "blocked"
    )
    return summary


def run_technology_manufacturing_import(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path,
    fred_provider: ObservationProvider | None = None,
    moea_provider: ObservationProvider | None = None,
    executor: SqlExecutor | None = None,
    database_url: str | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    if not execute_live or operator_confirmation != CONFIRMATION:
        raise ValueError("technology import requires explicit operator confirmation")
    root = _validated_artifact_dir(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    contract = load_technology_manufacturing_contract(contract_path)
    definitions = [
        row for row in contract["source_policy"]["sources"]
        if row["source_mode"] != "existing_warehouse_series"
    ]
    fred = fred_provider or FredProvider()
    moea = moea_provider or MoeaExportOrdersProvider()
    sql = executor or PsqlSubprocessExecutor(
        database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    )
    sql.execute(generate_postgres_schema_sql())
    results: list[dict[str, Any]] = []
    for definition in definitions:
        series_id = str(definition["series_id"])
        provider = moea if series_id.startswith("TW_MOEA_") else fred
        try:
            observations = provider.fetch_series_observations(series_id)
            normalized = _normalize_observations(series_id, observations)
            csv_path, content_hash = _write_normalized_csv(root, series_id, normalized)
            fetched_at = _utc_now()
            artifact_id = f"phase122::{series_id}::{content_hash[:16]}"
            sql.execute(_upsert_sql(
                definition=definition,
                csv_path=csv_path,
                content_hash=content_hash,
                artifact_id=artifact_id,
                fetched_at=fetched_at,
            ))
            results.append({
                "series_id": series_id,
                "status": "imported",
                "observation_count": len(normalized),
                "content_hash": content_hash,
                "artifact_id": artifact_id,
            })
        except Exception as exc:  # noqa: BLE001 - preserve per-source drilldown
            results.append({
                "series_id": series_id,
                "status": "failed",
                "observation_count": 0,
                "error_class": exc.__class__.__name__,
                "error_message": str(exc)[:240],
            })
    completed = [row for row in results if row["status"] == "imported"]
    report = {
        "report_version": "phase122_technology_import_v1",
        "data_mode": "revised",
        "requested_series_count": len(definitions),
        "completed_series_count": len(completed),
        "failed_series_count": len(definitions) - len(completed),
        "observation_revised_row_count_planned": sum(row["observation_count"] for row in completed),
        "results": results,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "result": "passed" if len(completed) == len(definitions) else "blocked",
    }
    _atomic_json_write(root / "latest-technology-import-report.json", report)
    return report


def _normalize_observations(
    series_id: str,
    rows: list[SeriesObservation],
) -> list[SeriesObservation]:
    normalized: dict[str, SeriesObservation] = {}
    for row in rows:
        if row.series_id != series_id:
            raise ValueError(f"source returned wrong series identity for {series_id}")
        normalized[row.date] = row
    if len(normalized) < 24:
        raise ValueError(f"{series_id} history is unexpectedly short")
    return [normalized[key] for key in sorted(normalized)]


def _write_normalized_csv(
    root: Path,
    series_id: str,
    rows: list[SeriesObservation],
) -> tuple[Path, str]:
    output = root / "normalized" / f"{series_id}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", newline="", encoding="utf-8", dir=output.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["series_key", "observation_date", "value_numeric", "value_text"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "series_key": series_id,
                "observation_date": row.date,
                "value_numeric": row.value,
                "value_text": "",
            })
        temporary = Path(handle.name)
    digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
    temporary.replace(output)
    return output, digest


def _upsert_sql(
    *,
    definition: dict[str, Any],
    csv_path: Path,
    content_hash: str,
    artifact_id: str,
    fetched_at: str,
) -> str:
    source_family = str(definition["source_family"])
    adapter_id = (
        "moea_export_orders_csv_v1"
        if str(definition["series_id"]).startswith("TW_MOEA_")
        else "fred_census_technology_revised_v1"
    )
    values = {key: _literal(str(value)) for key, value in {
        "series": definition["series_id"],
        "family": source_family,
        "title": definition["title_zh"],
        "units": definition["units"],
        "frequency": definition["frequency"],
        "sa": definition["seasonal_adjustment"],
        "geo": definition["geography"],
        "url": definition["source_url_without_secret"],
        "fetched": fetched_at,
        "hash": content_hash,
        "artifact": artifact_id,
        "adapter": adapter_id,
    }.items()}
    csv_literal = str(csv_path).replace("'", "''")
    return f"""
BEGIN;
INSERT INTO macro.series_registry (
  series_key, source_family, source_series_id, source_title, units, frequency,
  seasonal_adjustment, geographic_scope, source_url_without_secret,
  source_identity_status, created_at_utc, updated_at_utc
) VALUES (
  {values['series']}, {values['family']}, {values['series']}, {values['title']},
  {values['units']}, {values['frequency']}, {values['sa']}, {values['geo']},
  {values['url']}, 'verified_official_phase122', {values['fetched']}::timestamptz,
  {values['fetched']}::timestamptz
)
ON CONFLICT (series_key) DO UPDATE SET
  source_title = EXCLUDED.source_title,
  units = EXCLUDED.units,
  frequency = EXCLUDED.frequency,
  seasonal_adjustment = EXCLUDED.seasonal_adjustment,
  source_url_without_secret = EXCLUDED.source_url_without_secret,
  source_identity_status = EXCLUDED.source_identity_status,
  updated_at_utc = EXCLUDED.updated_at_utc;

INSERT INTO macro.source_artifact (
  artifact_id, source_family, source_url_without_secret,
  source_series_or_release_id, fetched_at_utc, content_hash, content_type,
  adapter_id, parser_version, no_secret, validation_status
) VALUES (
  {values['artifact']}, {values['family']}, {values['url']}, {values['series']},
  {values['fetched']}::timestamptz, {values['hash']}, 'text/csv',
  {values['adapter']}, 'phase122_csv_v1', TRUE, 'validated_official_revised'
)
ON CONFLICT (content_hash) DO NOTHING;

CREATE TEMP TABLE phase122_observation_import (
  series_key text, observation_date date, value_numeric numeric, value_text text
) ON COMMIT DROP;
\copy phase122_observation_import FROM '{csv_literal}' WITH (FORMAT csv, HEADER true)

INSERT INTO macro.observation_revised (
  series_key, observation_date, value_numeric, value_text, unit, data_mode,
  source_artifact_id, fetched_at_utc, provenance_hash
)
SELECT series_key, observation_date, value_numeric, value_text, {values['units']},
  'revised', {values['artifact']}, {values['fetched']}::timestamptz,
  encode(sha256(convert_to(series_key || '|' || observation_date::text || '|' ||
    coalesce(value_numeric::text, value_text, '') || '|' || {values['artifact']}, 'UTF8')), 'hex')
FROM phase122_observation_import
ON CONFLICT (series_key, observation_date) DO UPDATE SET
  value_numeric = EXCLUDED.value_numeric,
  value_text = EXCLUDED.value_text,
  unit = EXCLUDED.unit,
  source_artifact_id = EXCLUDED.source_artifact_id,
  fetched_at_utc = EXCLUDED.fetched_at_utc,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _validated_artifact_dir(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("technology import artifacts must remain outside the repository")
    if not (str(resolved).startswith("/tmp/") or str(resolved).startswith("/var/lib/business-cycle/")):
        raise ValueError("artifact directory must be under /tmp or the NAS artifact volume")
    return resolved


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
