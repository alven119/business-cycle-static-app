"""DS925+ Postgres revised macro import and backup rehearsal.

Phase 104 prepares the NAS-side import handoff without connecting to Postgres,
executing pg_dump, importing a compose bundle, or writing repository outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import ipaddress
import json

import yaml

from business_cycle.service.nas_ds925_connectivity_smoke import (
    summarize_nas_ds925_connectivity_smoke,
)
from business_cycle.storage.postgres_macro_warehouse import (
    summarize_postgres_macro_warehouse_contract,
)
from business_cycle.storage.revised_macro_data_import import (
    build_revised_macro_data_import_manifest,
    summarize_revised_macro_data_import,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_postgres_revised_import_rehearsal_contract.yaml"
)
TMP_ROOT = Path("/tmp")

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}
SECRET_MARKERS = ("PASSWORD", "SECRET", "API_KEY", "TOKEN")


def load_nas_postgres_revised_import_rehearsal_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase104 NAS revised import rehearsal contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_postgres_revised_import_rehearsal_contract"])


def build_nas_postgres_revised_import_rehearsal(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    cache_dir: str | Path | None = None,
    seed_tmp_cache_when_missing: bool = True,
    snapshot_as_of: str = "2026-07-03",
) -> dict[str, Any]:
    """Build a DS925+ import/backup rehearsal artifact without live writes."""

    contract = load_nas_postgres_revised_import_rehearsal_contract(contract_path)
    revised_manifest = build_revised_macro_data_import_manifest(
        cache_dir=cache_dir,
        seed_tmp_cache_when_missing=seed_tmp_cache_when_missing,
        snapshot_as_of=snapshot_as_of,
    )
    table_plan = _table_import_plan(contract, revised_manifest)
    backup_plan = _backup_plan(contract)
    verification_plan = _verification_plan(contract)
    upsert_sql = _deterministic_upsert_sql_preview(table_plan)
    payload_for_scan = {
        "table_import_plan": table_plan,
        "backup_plan": backup_plan,
        "verification_plan": verification_plan,
        "upsert_sql_preview": upsert_sql,
    }

    summary: dict[str, Any] = {
        "phase": "104",
        "phase_id": 104,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase104_nas_postgres_revised_import_rehearsal",
        "artifact_version": contract["version"],
        "output_mode": "research_only_nas_postgres_import_rehearsal",
        "research_only": True,
        "data_mode": "revised",
        "nas_private_ip": str(contract["target_endpoint"]["nas_private_ip"]),
        "nas_private_ip_private_lan": _is_private_lan_ip(
            str(contract["target_endpoint"]["nas_private_ip"]),
        ),
        "nas_private_ip_source": contract["target_endpoint"]["ip_source"],
        "postgres_service_name": contract["target_endpoint"]["postgres_service_name"],
        "postgres_schema_name": contract["target_endpoint"]["postgres_schema_name"],
        "nas_postgres_revised_import_rehearsal_contract_ready": _contract_ready(
            contract,
        ),
        "phase91_postgres_schema_dependency_ready": _phase91_dependency_ready(),
        "phase92_revised_import_dependency_ready": _phase92_dependency_ready(),
        "phase103_connectivity_dependency_ready": _phase103_dependency_ready(),
        "planned_import_table_count": len(table_plan),
        "planned_import_row_count": sum(row["planned_row_count"] for row in table_plan),
        "planned_series_registry_row_count": _row_count(
            table_plan,
            "series_registry",
        ),
        "planned_source_artifact_row_count": _row_count(table_plan, "source_artifact"),
        "planned_observation_revised_row_count": _row_count(
            table_plan,
            "observation_revised",
        ),
        "observation_vintage_row_count": revised_manifest[
            "observation_vintage_row_count"
        ],
        "import_plan_ready": _import_plan_ready(table_plan, contract),
        "deterministic_upsert_sql_preview_ready": bool(upsert_sql.strip()),
        "backup_rehearsal_plan_ready": _backup_plan_ready(backup_plan),
        "backup_step_count": len(backup_plan["steps"]),
        "restore_verification_plan_ready": _verification_plan_ready(
            verification_plan,
        ),
        "verification_query_count": len(verification_plan),
        "table_import_plan": table_plan,
        "backup_rehearsal_plan": backup_plan,
        "restore_verification_plan": verification_plan,
        "deterministic_upsert_sql_preview": upsert_sql,
        "source_revised_manifest_hash": revised_manifest["manifest_hash"],
        "rehearsal_hash": _hash_payload(payload_for_scan),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "trust_metadata": _trust_metadata(contract, revised_manifest),
        "generated_output_under_tmp_only": True,
        "live_db_connection_attempt_count": 0,
        "postgres_read_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "backup_command_execution_count": 0,
        "restore_command_execution_count": 0,
        "docker_compose_execution_count": 0,
        "container_manager_import_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "tests_network_dependency_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "point_in_time_claim_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "secret_value_literal_count": _secret_value_literal_count(payload_for_scan),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(
        payload_for_scan,
    )
    summary["nas_postgres_revised_import_rehearsal_ready"] = _passes(
        summary,
        _without_self(contract["hard_gates"]),
    )
    summary["result"] = (
        "passed"
        if summary["nas_postgres_revised_import_rehearsal_ready"]
        else "blocked"
    )
    return summary


def summarize_nas_postgres_revised_import_rehearsal(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase104 rehearsal readiness fields."""

    rehearsal = build_nas_postgres_revised_import_rehearsal(
        contract_path=contract_path,
    )
    keys = (
        "phase",
        "phase_id",
        "nas_postgres_revised_import_rehearsal_contract_ready",
        "nas_postgres_revised_import_rehearsal_ready",
        "phase91_postgres_schema_dependency_ready",
        "phase92_revised_import_dependency_ready",
        "phase103_connectivity_dependency_ready",
        "nas_private_ip",
        "nas_private_ip_private_lan",
        "planned_import_table_count",
        "planned_import_row_count",
        "planned_series_registry_row_count",
        "planned_source_artifact_row_count",
        "planned_observation_revised_row_count",
        "observation_vintage_row_count",
        "import_plan_ready",
        "deterministic_upsert_sql_preview_ready",
        "backup_rehearsal_plan_ready",
        "backup_step_count",
        "restore_verification_plan_ready",
        "verification_query_count",
        "generated_output_under_tmp_only",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "schema_migration_attempt_count",
        "backup_command_execution_count",
        "restore_command_execution_count",
        "docker_compose_execution_count",
        "container_manager_import_attempt_count",
        "live_fetch_attempt_count",
        "tests_network_dependency_count",
        "repo_output_written_count",
        "public_output_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "point_in_time_claim_count",
        "revised_mislabeled_as_pit_count",
        "secret_value_literal_count",
        "prohibited_output_field_count",
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
    return {key: rehearsal[key] for key in keys} | {
        "nas_postgres_revised_import_rehearsal": rehearsal,
    }


def write_nas_postgres_revised_import_rehearsal_report(
    output_dir: str | Path,
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Write import rehearsal artifacts under an explicit temporary directory."""

    output_path = Path(output_dir)
    if not _is_under_tmp(output_path):
        raise ValueError("Phase104 NAS import rehearsal output must be under /tmp")
    output_path.mkdir(parents=True, exist_ok=True)
    rehearsal = build_nas_postgres_revised_import_rehearsal(
        contract_path=contract_path,
    )
    files = {
        "ds925-revised-import-plan.json": rehearsal["table_import_plan"],
        "ds925-revised-import-backup-plan.json": rehearsal["backup_rehearsal_plan"],
        "ds925-revised-import-verification-plan.json": rehearsal[
            "restore_verification_plan"
        ],
        "ds925-revised-import-upsert-preview.sql": rehearsal[
            "deterministic_upsert_sql_preview"
        ],
        "ds925-revised-import-rehearsal-summary.json": {
            key: value
            for key, value in rehearsal.items()
            if key
            not in {
                "table_import_plan",
                "backup_rehearsal_plan",
                "restore_verification_plan",
                "deterministic_upsert_sql_preview",
                "trust_metadata",
            }
        },
        "ds925-revised-import-trust-metadata.json": rehearsal["trust_metadata"],
    }
    written = []
    for filename, payload in files.items():
        path = output_path / filename
        if filename.endswith(".sql"):
            path.write_text(str(payload), encoding="utf-8")
        else:
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        written.append(str(path))
    return {
        "nas_postgres_revised_import_rehearsal_ready": rehearsal[
            "nas_postgres_revised_import_rehearsal_ready"
        ],
        "rehearsal_output_path_count": len(written),
        "rehearsal_output_under_tmp_only": all(
            _is_under_tmp(Path(path)) for path in written
        ),
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "written_paths": written,
        "result": "passed",
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["rehearsal_scope"]
    return (
        contract["status"] == "active_research_contract"
        and scope["default_mode"] == "no_live_db_rehearsal"
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["repo_output_allowed_now"] is False
        and contract["target_endpoint"]["private_lan_only"] is True
        and contract["planned_import_tables"]
        == ["series_registry", "source_artifact", "observation_revised"]
    )


def _phase91_dependency_ready() -> bool:
    summary = summarize_postgres_macro_warehouse_contract()
    return (
        summary["result"] == "passed"
        and summary["postgres_macro_warehouse_contract_ready"] is True
        and summary["pit_ready_schema"] is True
    )


def _phase92_dependency_ready() -> bool:
    summary = summarize_revised_macro_data_import()
    return (
        summary["result"] == "passed"
        and summary["revised_macro_data_import_dry_run_ready"] is True
        and summary["postgres_write_attempt_count"] == 0
    )


def _phase103_dependency_ready() -> bool:
    summary = summarize_nas_ds925_connectivity_smoke()
    return (
        summary["result"] == "passed"
        and summary["nas_private_ip"] == "192.168.1.116"
        and summary["nas_private_ip_private_lan"] is True
    )


def _table_import_plan(
    contract: dict[str, Any],
    revised_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    row_sources = {
        "series_registry": revised_manifest["series_registry_rows"],
        "source_artifact": revised_manifest["source_artifact_rows"],
        "observation_revised": revised_manifest["observation_revised_rows"],
    }
    return [
        {
            "table_name": table,
            "schema_name": contract["target_endpoint"]["postgres_schema_name"],
            "planned_row_count": len(row_sources[table]),
            "source_manifest_id": revised_manifest["artifact_id"],
            "source_manifest_hash": revised_manifest["manifest_hash"],
            "data_mode": "revised",
            "execution_allowed_now": False,
            "write_allowed_now": False,
            "backup_required_before_import": True,
            "provenance_required": True,
        }
        for table in contract["planned_import_tables"]
    ]


def _backup_plan(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "backup_kind": contract["backup_rehearsal"]["backup_kind"],
        "backup_before_import_required": True,
        "backup_output_policy": contract["backup_rehearsal"]["backup_output_policy"],
        "restore_verification_kind": contract["backup_rehearsal"][
            "restore_verification_kind"
        ],
        "execution_allowed_now": False,
        "steps": [
            "confirm_private_lan_or_tailnet_access",
            "confirm_container_manager_postgres_service_health",
            "run_operator_selected_pg_dump_outside_repo",
            "record_backup_checksum_outside_repo",
            "perform_future_restore_verification_in_tmp_or_staging_db",
            "only_then_allow_future_operator_approved_import",
        ],
    }


def _verification_plan(contract: dict[str, Any]) -> list[dict[str, Any]]:
    schema = contract["target_endpoint"]["postgres_schema_name"]
    return [
        {
            "query_id": "series_registry_row_count",
            "sql_preview": f"SELECT count(*) FROM {schema}.series_registry;",
            "expected_row_count": 28,
            "execution_allowed_now": False,
        },
        {
            "query_id": "source_artifact_row_count",
            "sql_preview": f"SELECT count(*) FROM {schema}.source_artifact;",
            "expected_row_count": 28,
            "execution_allowed_now": False,
        },
        {
            "query_id": "observation_revised_row_count",
            "sql_preview": f"SELECT count(*) FROM {schema}.observation_revised;",
            "expected_row_count": 112,
            "execution_allowed_now": False,
        },
        {
            "query_id": "vintage_rows_remain_zero_for_phase104",
            "sql_preview": f"SELECT count(*) FROM {schema}.observation_vintage;",
            "expected_row_count": 0,
            "execution_allowed_now": False,
        },
    ]


def _deterministic_upsert_sql_preview(table_plan: list[dict[str, Any]]) -> str:
    lines = [
        "-- Phase104 DS925+ revised macro import rehearsal only.",
        "-- Do not execute from tests. Future operator approval is required.",
    ]
    for row in table_plan:
        lines.append(
            "-- "
            f"{row['schema_name']}.{row['table_name']}: "
            f"{row['planned_row_count']} planned revised rows",
        )
    return "\n".join(lines) + "\n"


def _import_plan_ready(
    table_plan: list[dict[str, Any]],
    contract: dict[str, Any],
) -> bool:
    expected = contract["planned_import_tables"]
    return (
        [row["table_name"] for row in table_plan] == expected
        and all(row["planned_row_count"] > 0 for row in table_plan)
        and all(row["write_allowed_now"] is False for row in table_plan)
    )


def _backup_plan_ready(plan: dict[str, Any]) -> bool:
    return (
        plan["backup_before_import_required"] is True
        and plan["execution_allowed_now"] is False
        and len(plan["steps"]) == 6
    )


def _verification_plan_ready(plan: list[dict[str, Any]]) -> bool:
    return (
        len(plan) == 4
        and all(row["execution_allowed_now"] is False for row in plan)
        and all(row["expected_row_count"] >= 0 for row in plan)
    )


def _row_count(table_plan: list[dict[str, Any]], table_name: str) -> int:
    return next(
        row["planned_row_count"]
        for row in table_plan
        if row["table_name"] == table_name
    )


def _is_private_lan_ip(value: str) -> bool:
    return ipaddress.ip_address(value).is_private


def _trust_metadata(
    contract: dict[str, Any],
    revised_manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "output_label": "research_only_private_nas_rehearsal",
        "target_endpoint": contract["target_endpoint"]["nas_private_ip"],
        "postgres_service_name": contract["target_endpoint"]["postgres_service_name"],
        "source_manifest_hash": revised_manifest["manifest_hash"],
        "data_mode": "revised",
        "point_in_time_result": False,
        "live_db_connection_attempted": False,
        "postgres_write_attempted": False,
        "schema_migration_attempted": False,
        "backup_command_executed": False,
        "restore_command_executed": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _without_self(expected: dict[str, Any]) -> dict[str, Any]:
    expected_without_self = dict(expected)
    expected_without_self.pop("nas_postgres_revised_import_rehearsal_ready", None)
    return expected_without_self


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _secret_value_literal_count(value: Any) -> int:
    rendered = json.dumps(value, sort_keys=True).upper()
    return sum(marker in rendered for marker in SECRET_MARKERS)


def _is_under_tmp(path: Path) -> bool:
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    return resolved == tmp_resolved or tmp_resolved in resolved.parents
