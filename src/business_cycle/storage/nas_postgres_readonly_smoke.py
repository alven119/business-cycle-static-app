"""Fixture-backed NAS Postgres read-only smoke for Phase 99.

The smoke validates read-only query shape and row schemas without connecting to
Postgres. A future phase can implement the same driver protocol with a real
read-only NAS database connection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import yaml

from business_cycle.audits.phase98_nas_service_lifecycle_closure import (
    summarize_phase98_nas_service_lifecycle_closure,
)
from business_cycle.storage.postgres_macro_warehouse import (
    summarize_postgres_macro_warehouse_contract,
)
from business_cycle.storage.revised_macro_data_import import (
    build_revised_macro_data_import_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_postgres_readonly_smoke_contract.yaml"
DATABASE_DEPENDENCY_MARKERS = ("psycopg", "sqlalchemy", "asyncpg")


class ReadOnlyQueryDriver(Protocol):
    """Small protocol for future Postgres read-only driver implementations."""

    def fetch(self, *, query_id: str, sql: str) -> list[dict[str, Any]]:
        """Fetch rows for a governed read-only query."""


class FixtureReadOnlyDriver:
    """Fixture driver backed by Phase92 warehouse-shaped rows."""

    def __init__(self) -> None:
        manifest = build_revised_macro_data_import_manifest()
        self.rows_by_table = {
            "series_registry": manifest["series_registry_rows"],
            "source_artifact": manifest["source_artifact_rows"],
            "observation_revised": manifest["observation_revised_rows"],
            "dashboard_snapshot": [_dashboard_snapshot_fixture(manifest)],
        }

    def fetch(self, *, query_id: str, sql: str) -> list[dict[str, Any]]:
        """Return deterministic fixture rows for the query table."""

        _ = query_id
        table = _table_from_sql(sql)
        return list(self.rows_by_table[table])[: _limit_from_sql(sql)]


def load_nas_postgres_readonly_smoke_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase99 read-only smoke contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_postgres_readonly_smoke_contract"])


def build_nas_postgres_readonly_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    driver: ReadOnlyQueryDriver | None = None,
) -> dict[str, Any]:
    """Build a fixture-backed read-only smoke summary."""

    contract = load_nas_postgres_readonly_smoke_contract(contract_path)
    driver = driver or FixtureReadOnlyDriver()
    query_results = [
        _execute_readonly_query(contract=contract, driver=driver, query=query)
        for query in contract["query_contracts"]
    ]
    forbidden_results = [
        _reject_forbidden_sql(contract, f"{prefix} test")
        for prefix in contract["readonly_policy"]["prohibited_statement_prefixes"]
    ]
    missing_required_columns = sum(
        result["missing_required_column_count"] for result in query_results
    )
    summary: dict[str, Any] = {
        "phase": "99",
        "phase_id": 99,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase99_nas_postgres_readonly_smoke",
        "artifact_version": contract["version"],
        "output_mode": "research_only_fixture_backed_postgres_readonly_smoke",
        "research_only": True,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_postgres_readonly_smoke_contract_ready": _contract_ready(contract),
        "postgres_macro_warehouse_dependency_ready": _postgres_dependency_ready(),
        "phase92_revised_import_dependency_ready": _phase92_dependency_ready(),
        "phase98_lifecycle_dependency_ready": _phase98_dependency_ready(),
        "fixture_driver_ready": isinstance(driver, FixtureReadOnlyDriver),
        "readonly_query_contract_count": len(contract["query_contracts"]),
        "readonly_query_pass_count": sum(
            result["query_passed"] is True for result in query_results
        ),
        "readonly_result_set_count": len(query_results),
        "readonly_result_row_count": sum(
            result["row_count"] for result in query_results
        ),
        "readonly_required_column_missing_count": missing_required_columns,
        "forbidden_sql_rejected_count": sum(
            result["rejected"] is True for result in forbidden_results
        ),
        "forbidden_sql_accepted_count": sum(
            result["rejected"] is False for result in forbidden_results
        ),
        "query_results": query_results,
        "forbidden_sql_results": forbidden_results,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "runtime_dependency_added_count": _runtime_dependency_added_count(),
        "network_bind_attempt_count": 0,
        "live_server_start_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "fixture_mislabeled_as_live_count": 0,
        "point_in_time_claim_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
        "trust_metadata": _trust_metadata(contract),
    }
    summary["nas_postgres_readonly_smoke_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed" if summary["nas_postgres_readonly_smoke_ready"] else "blocked"
    )
    return summary


def summarize_nas_postgres_readonly_smoke(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase99 read-only smoke fields."""

    smoke = build_nas_postgres_readonly_smoke(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_postgres_readonly_smoke_contract_ready",
        "nas_postgres_readonly_smoke_ready",
        "postgres_macro_warehouse_dependency_ready",
        "phase92_revised_import_dependency_ready",
        "phase98_lifecycle_dependency_ready",
        "fixture_driver_ready",
        "readonly_query_contract_count",
        "readonly_query_pass_count",
        "readonly_result_set_count",
        "readonly_result_row_count",
        "readonly_required_column_missing_count",
        "forbidden_sql_rejected_count",
        "forbidden_sql_accepted_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "runtime_dependency_added_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "fixture_mislabeled_as_live_count",
        "point_in_time_claim_count",
        "revised_mislabeled_as_pit_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "development_next_phase",
        "result",
    )
    return {key: smoke[key] for key in keys} | {
        "nas_postgres_readonly_smoke": smoke,
    }


def _execute_readonly_query(
    *,
    contract: dict[str, Any],
    driver: ReadOnlyQueryDriver,
    query: dict[str, Any],
) -> dict[str, Any]:
    rejected = _reject_forbidden_sql(contract, query["sql"])
    if rejected["rejected"]:
        return {
            "query_id": query["query_id"],
            "query_passed": False,
            "row_count": 0,
            "missing_required_column_count": len(query["required_columns"]),
            "rejection_reason": rejected["reason"],
        }
    rows = driver.fetch(query_id=query["query_id"], sql=query["sql"])
    missing = _missing_required_column_count(rows, query["required_columns"])
    return {
        "query_id": query["query_id"],
        "table": query["table"],
        "query_passed": bool(rows) and missing == 0,
        "row_count": len(rows),
        "missing_required_column_count": missing,
        "data_mode": _data_mode_from_rows(rows),
        "fixture_backed": True,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
    }


def _reject_forbidden_sql(contract: dict[str, Any], sql: str) -> dict[str, Any]:
    normalized = sql.strip().upper()
    allowed = contract["readonly_policy"]["allowed_statement_prefix"]
    if not normalized.startswith(f"{allowed} "):
        return {"rejected": True, "reason": "non_select_statement"}
    forbidden = tuple(contract["readonly_policy"]["prohibited_statement_prefixes"])
    if normalized.startswith(forbidden):
        return {"rejected": True, "reason": "forbidden_statement"}
    return {"rejected": False, "reason": None}


def _table_from_sql(sql: str) -> str:
    marker = " FROM macro."
    after_from = sql.split(marker, 1)[1]
    return after_from.split(" ", 1)[0]


def _limit_from_sql(sql: str) -> int:
    marker = " LIMIT "
    if marker not in sql:
        return 5
    return int(sql.rsplit(marker, 1)[1])


def _missing_required_column_count(
    rows: list[dict[str, Any]],
    required_columns: list[str],
) -> int:
    if not rows:
        return len(required_columns)
    row_keys = set(rows[0])
    return len(set(required_columns) - row_keys)


def _data_mode_from_rows(rows: list[dict[str, Any]]) -> str:
    modes = {row.get("data_mode") for row in rows if row.get("data_mode")}
    return modes.pop() if len(modes) == 1 else "mixed_or_not_applicable"


def _dashboard_snapshot_fixture(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_snapshot_id": f"dashboard_snapshot::{manifest['snapshot_as_of']}",
        "as_of": manifest["snapshot_as_of"],
        "data_mode": "revised",
        "declared_current_phase": "boom",
        "declared_phase_start_date": None,
        "phase_age_status": "unknown_or_user_required",
        "legal_next_phase": "recession",
        "research_only": True,
        "generated_at_utc": manifest["generated_at_utc"],
        "source_evidence_hash": manifest["manifest_hash"],
        "provenance_hash": manifest["manifest_hash"],
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["smoke_scope"]
    policy = contract["readonly_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["fixture_backed_rehearsal_only"] is True
        and scope["live_db_connection_allowed_now"] is False
        and scope["read_only_query_shape_allowed"] is True
        and scope["postgres_write_allowed_now"] is False
        and scope["schema_migration_allowed_now"] is False
        and scope["runtime_dependency_added_now"] is False
        and policy["allowed_statement_prefix"] == "SELECT"
        and len(policy["required_query_ids"]) == len(contract["query_contracts"])
    )


def _postgres_dependency_ready() -> bool:
    summary = summarize_postgres_macro_warehouse_contract()
    return (
        summary["result"] == "passed"
        and summary["postgres_macro_warehouse_contract_ready"] is True
        and summary["pit_ready_schema"] is True
    )


def _phase92_dependency_ready() -> bool:
    manifest = build_revised_macro_data_import_manifest()
    return (
        manifest["result"] == "passed"
        and manifest["revised_macro_data_import_dry_run_ready"] is True
        and manifest["observation_revised_row_count"] >= 112
    )


def _phase98_dependency_ready() -> bool:
    summary = summarize_phase98_nas_service_lifecycle_closure()
    return (
        summary["result"] == "passed"
        and summary["nas_service_lifecycle_ready"] is True
        and summary["readiness_probe_pass_count"] == 5
    )


def _runtime_dependency_added_count() -> int:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    return sum(marker in pyproject for marker in DATABASE_DEPENDENCY_MARKERS)


def _trust_metadata(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "service_target": contract["smoke_scope"]["target_runtime"],
        "nas_migration_surface": "postgres_readonly_fixture_smoke",
        "fixture_backed_rehearsal_only": True,
        "live_db_connection_attempted": False,
        "postgres_read_attempted": False,
        "postgres_write_attempted": False,
        "schema_migration_attempted": False,
        "runtime_dependency_added_now": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected = dict(expected)
    expected.pop("nas_postgres_readonly_smoke_ready", None)
    return expected
