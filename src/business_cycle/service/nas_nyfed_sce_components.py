"""Official NY Fed SCE component import for private NAS explanatory context."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any, Callable
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

import requests
import yaml

from business_cycle.data_sources import SeriesObservation
from business_cycle.storage.nas_postgres_live_revised_import import (
    PsqlSubprocessExecutor,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nyfed_sce_component_adapter.yaml"
DEFAULT_ARTIFACT_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase137")
CONFIRMATION = "I_UNDERSTAND_THIS_FETCHES_NYFED_SCE_AND_WRITES_NAS_POSTGRES"
PARENT_SERIES_ID = "NYFED_SCE_CONTEXT"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CELL_RE = re.compile(r"^([A-Z]+)(\d+)$")


class NyfedSceSourceError(RuntimeError):
    """Raised when an official SCE workbook violates its pinned schema."""


def load_nyfed_sce_component_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nyfed_sce_component_adapter"])


def summarize_nyfed_sce_component_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nyfed_sce_component_contract(path)
    components = list(contract["component_series"])
    source = contract["source"]
    policy = contract["runtime_policy"]
    ids = [str(row["series_id"]) for row in components]
    direct_count = sum(bool(row.get("value_column")) for row in components)
    summary = {
        "phase": 137,
        "nyfed_sce_component_adapter_contract_ready": (
            contract["status"] == "active_private_nas_supporting_only_adapter"
            and len(ids) == len(set(ids))
            and policy["book_core_replacement_allowed"] is False
            and policy["component_composite_score_allowed"] is False
        ),
        "component_series_count": len(components),
        "conceptual_group_count": len(contract["conceptual_groups"]),
        "direct_measure_count": direct_count,
        "derived_measure_count": len(components) - direct_count,
        "arbitrary_composite_score_count": 0,
        "attribution_contract_ready": bool(source["attribution"] and source["license_url"]),
        "official_release_calendar_contract_ready": bool(
            source["release_calendar_url"]
        ),
        "book_core_replacement_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
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


def parse_nyfed_sce_workbook(
    content: bytes,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, list[SeriesObservation]]:
    """Parse only pinned direct component columns from the official XLSX."""

    contract = load_nyfed_sce_component_contract(contract_path)
    try:
        with ZipFile(BytesIO(content)) as archive:
            shared_strings = _shared_strings(archive)
            sheet_paths = _sheet_paths(archive)
            cache: dict[str, dict[str, str]] = {}
            parsed: dict[str, list[SeriesObservation]] = {}
            for component in contract["component_series"]:
                sheet_name = str(component["sheet_name"])
                if sheet_name not in sheet_paths:
                    raise NyfedSceSourceError(f"missing SCE sheet: {sheet_name}")
                cells = cache.setdefault(
                    sheet_name,
                    _worksheet_cells(
                        archive,
                        sheet_paths[sheet_name],
                        shared_strings,
                    ),
                )
                _validate_component_header(component, cells)
                parsed[str(component["series_id"])] = _component_observations(
                    component,
                    cells,
                    first_data_row=int(contract["workbook_contract"]["first_data_row"]),
                )
    except BadZipFile as exc:
        raise NyfedSceSourceError("NY Fed SCE download is not a valid XLSX") from exc
    if len(parsed) != len(contract["component_series"]):
        raise NyfedSceSourceError("NY Fed SCE component coverage is incomplete")
    return parsed


def run_nyfed_sce_component_import(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path = DEFAULT_ARTIFACT_ROOT,
    database_url: str | None = None,
    executor: Any | None = None,
    fetcher: Callable[..., Any] = requests.get,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Fetch, validate and persist direct SCE components as revised context."""

    if not execute_live or operator_confirmation != CONFIRMATION:
        raise NyfedSceSourceError("NY Fed SCE import requires explicit confirmation")
    contract = load_nyfed_sce_component_contract(contract_path)
    root = _validated_artifact_root(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    started_at = _utc_now()
    try:
        response = fetcher(
            str(contract["source"]["workbook_url"]),
            timeout=60.0,
            headers={"User-Agent": "business-cycle-private-nas/phase137"},
        )
        response.raise_for_status()
        raw = bytes(response.content)
        parsed = parse_nyfed_sce_workbook(raw, contract_path=contract_path)
        _, csv_path, content_hash = _write_artifacts(root, raw, parsed, contract)
        fetched_at = _utc_now()
        artifact_id = f"nyfed_sce::{content_hash[:20]}"
        sql = executor or PsqlSubprocessExecutor(
            database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
        )
        sql.execute(
            _nyfed_sce_upsert_sql(
                csv_path=csv_path,
                content_hash=content_hash,
                artifact_id=artifact_id,
                fetched_at=fetched_at,
                contract=contract,
            )
        )
        observation_count = sum(len(rows) for rows in parsed.values())
        row = {
            "series_id": PARENT_SERIES_ID,
            "status": "imported",
            "observation_count": observation_count,
            "component_series_count": len(parsed),
            "attempt_count": 1,
            "artifact_id": artifact_id,
            "error_class": None,
            "error_message_redacted": None,
        }
        result = "passed"
    except Exception as exc:  # noqa: BLE001 - worker emits typed source failure
        row = {
            "series_id": PARENT_SERIES_ID,
            "status": "failed",
            "observation_count": 0,
            "component_series_count": 0,
            "attempt_count": 1,
            "artifact_id": None,
            "error_class": exc.__class__.__name__,
            "error_message_redacted": "nyfed_sce_component_import_failed",
        }
        result = "blocked"
    report = {
        "report_version": "phase137_nyfed_sce_component_import_v1",
        "data_mode": "revised_supporting_only",
        "started_at_utc": started_at,
        "completed_at_utc": _utc_now(),
        "requested_series_count": 1,
        "completed_series_count": int(result == "passed"),
        "failed_series_count": int(result != "passed"),
        "source_artifact_count": int(result == "passed"),
        "component_series_count": int(row["component_series_count"]),
        "observation_count": int(row["observation_count"]),
        "series_refresh_results": [row],
        "book_core_replacement_count": 0,
        "arbitrary_composite_score_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "result": result,
    }
    _atomic_json_write(root / "latest-nyfed-sce-report.json", report)
    return report


def _shared_strings(archive: ZipFile) -> list[str]:
    path = "xl/sharedStrings.xml"
    if path not in archive.namelist():
        return []
    root = ET.fromstring(archive.read(path))
    return ["".join(node.itertext()) for node in root.findall(f"{{{MAIN_NS}}}si")]


def _sheet_paths(archive: ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        str(node.attrib["Id"]): str(node.attrib["Target"])
        for node in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    paths: dict[str, str] = {}
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        relation_id = sheet.attrib[f"{{{REL_NS}}}id"]
        target = targets[relation_id].lstrip("/")
        if not target.startswith("xl/"):
            target = str(PurePosixPath("xl") / target)
        paths[str(sheet.attrib["name"])] = target
    return paths


def _worksheet_cells(
    archive: ZipFile,
    path: str,
    shared_strings: list[str],
) -> dict[str, str]:
    root = ET.fromstring(archive.read(path))
    cells: dict[str, str] = {}
    for cell in root.findall(f".//{{{MAIN_NS}}}c"):
        reference = str(cell.attrib.get("r", ""))
        if not CELL_RE.fullmatch(reference):
            continue
        cell_type = str(cell.attrib.get("t", ""))
        if cell_type == "inlineStr":
            value = "".join(cell.itertext())
        else:
            value_node = cell.find(f"{{{MAIN_NS}}}v")
            if value_node is None or value_node.text is None:
                continue
            value = value_node.text
            if cell_type == "s":
                try:
                    value = shared_strings[int(value)]
                except (IndexError, ValueError) as exc:
                    raise NyfedSceSourceError("invalid XLSX shared string index") from exc
        cells[reference] = value.strip()
    return cells


def _validate_component_header(
    component: dict[str, Any],
    cells: dict[str, str],
) -> None:
    column = str(component["value_column"])
    actual = cells.get(f"{column}4")
    if actual != str(component["expected_header"]):
        raise NyfedSceSourceError(
            f"NY Fed SCE header changed for {component['series_id']}"
        )
    scope_row = component.get("scope_row")
    if scope_row is not None:
        scope_column = str(component.get("scope_column", column))
        scope = cells.get(f"{scope_column}{int(scope_row)}")
        if scope != str(component["expected_scope"]):
            raise NyfedSceSourceError(
                f"NY Fed SCE scope changed for {component['series_id']}"
            )


def _component_observations(
    component: dict[str, Any],
    cells: dict[str, str],
    *,
    first_data_row: int,
) -> list[SeriesObservation]:
    by_date: dict[str, SeriesObservation] = {}
    row_numbers = sorted(
        {
            int(match.group(2))
            for reference in cells
            if (match := CELL_RE.fullmatch(reference))
            and match.group(1) == "A"
            and int(match.group(2)) >= first_data_row
        }
    )
    for row_number in row_numbers:
        period = cells.get(f"A{row_number}", "")
        value = cells.get(f"{component['value_column']}{row_number}", "")
        if not re.fullmatch(r"\d{6}", period):
            continue
        if _decimal(value) is None:
            continue
        month = int(period[4:6])
        if month < 1 or month > 12:
            raise NyfedSceSourceError("NY Fed SCE monthly period is invalid")
        observation_date = f"{period[:4]}-{period[4:]}-01"
        observation = SeriesObservation(
            series_id=str(component["series_id"]),
            date=observation_date,
            value=value,
        )
        if observation_date in by_date:
            raise NyfedSceSourceError("duplicate NY Fed SCE monthly observation")
        by_date[observation_date] = observation
    if not by_date:
        raise NyfedSceSourceError(
            f"no NY Fed SCE observations for {component['series_id']}"
        )
    return [by_date[key] for key in sorted(by_date)]


def _write_artifacts(
    root: Path,
    raw: bytes,
    parsed: dict[str, list[SeriesObservation]],
    contract: dict[str, Any],
) -> tuple[Path, Path, str]:
    output_dir = root / "nyfed-sce"
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "frbny-sce-data.xlsx"
    _atomic_bytes_write(raw_path, raw)
    content_hash = hashlib.sha256(raw).hexdigest()
    csv_path = output_dir / "nyfed-sce-components.csv"
    units = {
        str(row["series_id"]): str(row["units"])
        for row in contract["component_series"]
    }
    with tempfile.NamedTemporaryFile(
        "w", newline="", encoding="utf-8", dir=output_dir, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "series_key",
                "observation_date",
                "value_numeric",
                "value_text",
                "unit",
            ],
        )
        writer.writeheader()
        for series_id in sorted(parsed):
            for row in parsed[series_id]:
                writer.writerow(
                    {
                        "series_key": series_id,
                        "observation_date": row.date,
                        "value_numeric": row.value,
                        "value_text": "",
                        "unit": units[series_id],
                    }
                )
        temporary = Path(handle.name)
    temporary.replace(csv_path)
    return raw_path, csv_path, content_hash


def _nyfed_sce_upsert_sql(
    *,
    csv_path: Path,
    content_hash: str,
    artifact_id: str,
    fetched_at: str,
    contract: dict[str, Any],
) -> str:
    source = contract["source"]
    registry_values = []
    for component in contract["component_series"]:
        registry_values.append(
            "(" + ", ".join(
                [
                    _literal(str(component["series_id"])),
                    "'Federal Reserve Bank of New York'",
                    _literal(
                        f"SCE:{component['sheet_name']}:{component['value_column']}"
                    ),
                    _literal(str(component["title_zh"])),
                    _literal(str(component["units"])),
                    "'monthly'",
                    "'not_applicable_survey_statistic'",
                    "'United States households'",
                    _literal(str(source["workbook_url"])),
                    "'verified_direct_supporting_only'",
                    f"{_literal(fetched_at)}::timestamptz",
                    f"{_literal(fetched_at)}::timestamptz",
                ]
            ) + ")"
        )
    csv_literal = str(csv_path).replace("'", "''")
    registry_sql = ",\n".join(registry_values)
    return rf"""
BEGIN;
INSERT INTO macro.series_registry (
  series_key, source_family, source_series_id, source_title, units, frequency,
  seasonal_adjustment, geographic_scope, source_url_without_secret,
  source_identity_status, created_at_utc, updated_at_utc
) VALUES
{registry_sql}
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
  {_literal(artifact_id)}, 'Federal Reserve Bank of New York',
  {_literal(str(source['workbook_url']))}, 'SCE_CHART_DATA_WORKBOOK',
  {_literal(fetched_at)}::timestamptz, {_literal(content_hash)},
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'nyfed_sce_component_workbook_v1', 'phase137_stdlib_xlsx_v1', TRUE,
  'validated_revised_supporting_only'
)
ON CONFLICT (content_hash) DO NOTHING;

CREATE TEMP TABLE phase137_nyfed_sce_import (
  series_key text,
  observation_date date,
  value_numeric numeric,
  value_text text,
  unit text
) ON COMMIT DROP;
\copy phase137_nyfed_sce_import FROM '{csv_literal}' WITH (FORMAT csv, HEADER true)

INSERT INTO macro.observation_revised (
  series_key, observation_date, value_numeric, value_text, unit, data_mode,
  source_artifact_id, fetched_at_utc, provenance_hash
)
SELECT
  series_key, observation_date, value_numeric, value_text, unit, 'revised',
  {_literal(artifact_id)}, {_literal(fetched_at)}::timestamptz,
  encode(sha256(convert_to(
    series_key || '|' || observation_date::text || '|' ||
    coalesce(value_numeric::text, value_text, '') || '|' || {_literal(artifact_id)},
    'UTF8'
  )), 'hex')
FROM phase137_nyfed_sce_import
ON CONFLICT (series_key, observation_date) DO UPDATE SET
  value_numeric = EXCLUDED.value_numeric,
  value_text = EXCLUDED.value_text,
  unit = EXCLUDED.unit,
  source_artifact_id = EXCLUDED.source_artifact_id,
  fetched_at_utc = EXCLUDED.fetched_at_utc,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _validated_artifact_root(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise NyfedSceSourceError("source artifacts must remain outside repository")
    if not (
        str(resolved).startswith("/tmp/")
        or str(resolved).startswith("/var/lib/business-cycle/")
    ):
        raise NyfedSceSourceError("artifact root must use /tmp or NAS volume")
    return resolved


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _atomic_bytes_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args(argv)
    if not args.run_live:
        summary = summarize_nyfed_sce_component_contract()
        print(json.dumps(summary, sort_keys=True))
        return 0 if summary["result"] == "passed" else 1
    report = run_nyfed_sce_component_import(
        execute_live=True,
        operator_confirmation=os.environ.get(
            "BUSINESS_CYCLE_NYFED_SCE_OPERATOR_CONFIRMATION"
        ),
        artifact_dir=args.artifact_root,
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
