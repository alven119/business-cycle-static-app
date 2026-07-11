"""Postgres macro-warehouse schema contract helpers.

Phase 91 only preregisters a PIT-ready schema shape and deterministic DDL.
It intentionally does not connect to Postgres or add a runtime DB dependency.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/postgres_macro_warehouse_contract.yaml"
DATABASE_DEPENDENCY_MARKERS = ("psycopg", "sqlalchemy", "asyncpg")
IDENTIFIER_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
VINTAGE_REQUIRED_COLUMNS = {
    "realtime_start",
    "realtime_end",
    "vintage_as_of",
    "release_timestamp_utc",
    "source_artifact_id",
    "provenance_hash",
}
RELEASE_CALENDAR_REQUIRED_COLUMNS = {
    "release_event_id",
    "source_reference_period_label",
    "reference_period_precision",
    "release_semantics",
    "availability_precision",
}


def load_postgres_macro_warehouse_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 91 macro warehouse contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["postgres_macro_warehouse_contract"])


def table_contracts(
    contract: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return table contracts keyed by table name."""

    loaded = contract or load_postgres_macro_warehouse_contract()
    return dict(loaded["table_contracts"])


def generate_postgres_schema_sql(
    contract: dict[str, Any] | None = None,
) -> str:
    """Generate deterministic Postgres DDL without executing it."""

    loaded = contract or load_postgres_macro_warehouse_contract()
    schema_name = str(loaded["database"]["schema_name"])
    _validate_identifier(schema_name)

    lines = [
        "-- Generated from specs/common/postgres_macro_warehouse_contract.yaml",
        "-- Phase 91 contract DDL preview only; do not execute from tests.",
        f"CREATE SCHEMA IF NOT EXISTS {schema_name};",
        "",
    ]
    tables = table_contracts(loaded)
    for table_name in loaded["relationship_policy"]["migration_order"]:
        lines.extend(_create_table_sql(schema_name, table_name, tables[table_name]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def summarize_postgres_macro_warehouse_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize schema readiness gates for tests, CLIs, and closure checks."""

    contract = load_postgres_macro_warehouse_contract(path)
    tables = table_contracts(contract)
    required = list(contract["required_table_names"])
    missing = [table for table in required if table not in tables]
    table_without_pk = [
        table for table, spec in tables.items() if not spec.get("primary_key")
    ]
    vintage_missing = _vintage_required_column_missing_count(tables)
    release_calendar_missing = _release_calendar_required_column_missing_count(
        tables
    )
    ddl = generate_postgres_schema_sql(contract)
    database = contract["database"]
    design = contract["design_principles"]
    restrictions = contract["output_restrictions"]

    summary: dict[str, Any] = {
        "postgres_macro_warehouse_contract_ready": (
            contract["status"] == "active"
            and contract["database"]["engine"] == "postgres"
            and not missing
            and not table_without_pk
            and vintage_missing == 0
        ),
        "phase_id": contract["phase_id"],
        "phase_label": contract["phase_label"],
        "schema_name": database["schema_name"],
        "schema_table_count": len(tables),
        "required_table_count": len(required),
        "missing_required_table_count": len(missing),
        "table_with_primary_key_count": len(tables) - len(table_without_pk),
        "table_without_primary_key_count": len(table_without_pk),
        "pit_ready_schema": bool(design["pit_schema_required_from_start"]),
        "revised_vintage_separation_ready": _revised_vintage_separation_ready(tables),
        "vintage_required_column_missing_count": vintage_missing,
        "release_calendar_revision_events_supported": bool(
            design["release_calendar_revision_events_supported"]
        ),
        "release_calendar_required_column_missing_count": (
            release_calendar_missing
        ),
        "source_artifact_hash_required": _source_artifact_hash_required(tables),
        "schema_sql_generated": bool(ddl.strip()),
        "schema_requires_live_db": bool(database["live_connection_required_now"]),
        "live_db_connection_attempt_count": 0,
        "runtime_dependency_added_count": _runtime_dependency_added_count(),
        "frontend_database_access_allowed": bool(
            design["frontend_direct_db_access_allowed"],
        ),
        "frontend_api_key_allowed": bool(design["frontend_api_key_allowed"]),
        "candidate_phase_emitted": bool(restrictions["candidate_phase_emitted"]),
        "current_phase_emitted": bool(restrictions["current_phase_emitted"]),
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
        "schema_sql_preview": ddl,
    }
    expected = dict(contract["hard_gates"])
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _create_table_sql(
    schema_name: str,
    table_name: str,
    spec: dict[str, Any],
) -> list[str]:
    _validate_identifier(table_name)
    column_lines: list[str] = []
    for column in spec["columns"]:
        name = str(column["name"])
        _validate_identifier(name)
        nullable = "" if bool(column.get("nullable", True)) else " NOT NULL"
        column_lines.append(f"    {name} {column['sql_type']}{nullable}")

    pk = ", ".join(str(name) for name in spec["primary_key"])
    column_lines.append(f"    PRIMARY KEY ({pk})")
    for constraint in spec.get("constraints", []):
        column_lines.append(f"    {constraint}")

    rendered_columns = ",\n".join(column_lines)
    return [
        f"CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (",
        rendered_columns,
        ");",
    ]


def _validate_identifier(identifier: str) -> None:
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Unsafe SQL identifier in warehouse contract: {identifier}")


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _column_names(table: dict[str, Any]) -> set[str]:
    return {str(column["name"]) for column in table["columns"]}


def _revised_vintage_separation_ready(tables: dict[str, dict[str, Any]]) -> bool:
    revised = tables["observation_revised"]
    vintage = tables["observation_vintage"]
    revised_constraints = "\n".join(revised.get("constraints", []))
    vintage_constraints = "\n".join(vintage.get("constraints", []))
    return (
        "realtime_start" not in _column_names(revised)
        and "vintage_as_of" not in _column_names(revised)
        and "data_mode = 'revised'" in revised_constraints
        and "data_mode = 'vintage_as_of'" in vintage_constraints
    )


def _vintage_required_column_missing_count(tables: dict[str, dict[str, Any]]) -> int:
    vintage_columns = _column_names(tables["observation_vintage"])
    return len(VINTAGE_REQUIRED_COLUMNS - vintage_columns)


def _release_calendar_required_column_missing_count(
    tables: dict[str, dict[str, Any]],
) -> int:
    columns = _column_names(tables["release_calendar"])
    return len(RELEASE_CALENDAR_REQUIRED_COLUMNS - columns)


def _source_artifact_hash_required(tables: dict[str, dict[str, Any]]) -> bool:
    columns = {
        column["name"]: column
        for column in tables["source_artifact"]["columns"]
    }
    return (
        "content_hash" in columns
        and columns["content_hash"]["nullable"] is False
        and "UNIQUE (content_hash)" in tables["source_artifact"].get("constraints", [])
    )


def _runtime_dependency_added_count() -> int:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    return sum(marker in pyproject for marker in DATABASE_DEPENDENCY_MARKERS)
