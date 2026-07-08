"""NAS service indicator snapshot materialization for Phase 94.

The snapshot joins Phase 92 revised warehouse-shaped rows with Phase 93
vintage/PIT availability accounting. It is a server-side view-model rehearsal:
no live database connection, no Postgres write, no live source fetch, and no
strict point-in-time evidence emission.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
from typing import Any

import yaml

from business_cycle.storage.postgres_macro_warehouse import (
    summarize_postgres_macro_warehouse_contract,
)
from business_cycle.storage.revised_macro_data_import import (
    build_revised_macro_data_import_manifest,
    summarize_revised_macro_data_import,
)
from business_cycle.storage.vintage_pit_backfill_availability import (
    build_vintage_pit_backfill_availability_manifest,
    summarize_vintage_pit_backfill_availability,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_indicator_snapshot_contract.yaml"
TMP_ROOT = Path("/tmp")
SNAPSHOT_AS_OF = "2026-07-03"
GENERATED_AT_UTC = f"{SNAPSHOT_AS_OF}T00:00:00Z"

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


def load_nas_indicator_snapshot_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 94 NAS indicator snapshot contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_indicator_snapshot_contract"])


def build_nas_indicator_snapshot_manifest(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
) -> dict[str, Any]:
    """Build a deterministic NAS service indicator snapshot manifest."""

    contract = load_nas_indicator_snapshot_contract(contract_path)
    revised_manifest = build_revised_macro_data_import_manifest(
        snapshot_as_of=snapshot_as_of,
    )
    pit_manifest = build_vintage_pit_backfill_availability_manifest(
        snapshot_as_of=snapshot_as_of,
    )
    observations_by_series = _latest_observations_by_series(
        revised_manifest["observation_revised_rows"],
    )
    source_artifact_by_series = {
        row["source_series_or_release_id"]: row
        for row in revised_manifest["source_artifact_rows"]
    }
    pit_by_series = {
        row["series_key"]: row for row in pit_manifest["backfill_availability_rows"]
    }
    pit_by_role = {row["role_id"]: row for row in pit_manifest["role_backfill_rows"]}

    series_snapshots = [
        _series_snapshot_row(
            row,
            observation=observations_by_series.get(row["series_key"]),
            source_artifact=source_artifact_by_series.get(row["series_key"]),
            pit_row=pit_by_series.get(row["series_key"]),
        )
        for row in revised_manifest["series_registry_rows"]
    ]
    role_snapshots = [
        _role_snapshot_row(
            row,
            observations_by_series=observations_by_series,
            pit_row=pit_by_role[row["role_id"]],
        )
        for row in revised_manifest["role_import_rows"]
    ]
    source_artifact_snapshots = [
        _source_artifact_snapshot_row(row)
        for row in revised_manifest["source_artifact_rows"]
    ]
    service_view_model = _service_view_model(
        contract=contract,
        role_snapshots=role_snapshots,
        series_snapshots=series_snapshots,
        source_artifact_snapshots=source_artifact_snapshots,
        snapshot_as_of=snapshot_as_of,
    )
    manifest: dict[str, Any] = {
        "artifact_id": "phase94_nas_indicator_snapshot_materialization",
        "artifact_version": contract["version"],
        "phase": "94",
        "phase_id": 94,
        "phase_label": contract["phase_label"],
        "generated_at_utc": f"{snapshot_as_of}T00:00:00Z",
        "snapshot_as_of": snapshot_as_of,
        "output_mode": "research_only_nas_service_indicator_snapshot",
        "research_only": True,
        "target_runtime": contract["service_scope"]["target_runtime"],
        "phase92_manifest_hash": revised_manifest["manifest_hash"],
        "phase93_backfill_accounting_hash": pit_manifest["backfill_accounting_hash"],
        "role_snapshots": role_snapshots,
        "series_snapshots": series_snapshots,
        "source_artifact_snapshots": source_artifact_snapshots,
        "service_view_model": service_view_model,
        "nas_indicator_snapshot_contract_ready": _contract_ready(contract),
        "phase92_revised_import_dependency_ready": _phase92_dependency_ready(),
        "phase93_pit_availability_dependency_ready": _phase93_dependency_ready(),
        "postgres_macro_warehouse_dependency_ready": _postgres_dependency_ready(),
        "role_snapshot_count": len(role_snapshots),
        "role_with_revised_snapshot_count": sum(
            row["snapshot_status"] == "revised_snapshot_ready"
            for row in role_snapshots
        ),
        "role_without_revised_snapshot_count": sum(
            row["snapshot_status"] == "blocked" for row in role_snapshots
        ),
        "role_with_pit_backfill_plan_count": sum(
            row["pit_backfill_status"] == "planned" for row in role_snapshots
        ),
        "role_with_pit_backfill_blocker_count": sum(
            row["pit_backfill_status"] == "blocked" for row in role_snapshots
        ),
        "series_snapshot_count": len(series_snapshots),
        "source_artifact_snapshot_count": len(source_artifact_snapshots),
        "observation_revised_source_row_count": len(
            revised_manifest["observation_revised_rows"],
        ),
        "latest_revised_observation_context_count": sum(
            len(row["latest_revised_observations"]) for row in role_snapshots
        ),
        "snapshot_row_schema_valid": _snapshot_schema_valid(
            role_snapshots=role_snapshots,
            series_snapshots=series_snapshots,
            source_artifact_snapshots=source_artifact_snapshots,
        ),
        "service_view_model_ready": _service_view_model_ready(service_view_model),
        "server_side_view_model_count": 1,
        "api_endpoint_contract_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "observation_vintage_row_count": 0,
        "strict_pit_result_emitted_count": 0,
        "point_in_time_claim_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "trust_metadata": service_view_model["trust_metadata"],
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    manifest["prohibited_output_field_count"] = _contains_prohibited_field(manifest)
    manifest["snapshot_manifest_hash"] = _hash_payload(
        {
            "phase92_manifest_hash": manifest["phase92_manifest_hash"],
            "phase93_backfill_accounting_hash": manifest[
                "phase93_backfill_accounting_hash"
            ],
            "role_snapshots": role_snapshots,
            "series_snapshots": series_snapshots,
        },
    )
    expected_without_self = dict(contract["hard_gates"])
    expected_without_self.pop("nas_indicator_snapshot_materialization_ready", None)
    manifest["nas_indicator_snapshot_materialization_ready"] = _passes(
        manifest,
        expected_without_self,
    )
    manifest["result"] = (
        "passed"
        if manifest["nas_indicator_snapshot_materialization_ready"]
        else "blocked"
    )
    return manifest


def write_nas_indicator_snapshot_manifest(
    manifest: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    """Write a Phase 94 dry-run manifest only under /tmp."""

    output_path = _validated_tmp_output(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "nas_indicator_snapshot_manifest_written": True,
        "written_file_count": 1,
        "dry_run_output_under_tmp_only": True,
        "repo_output_written_count": 0,
        "public_output_count": 0,
    }


def summarize_nas_indicator_snapshot(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase 94 NAS indicator snapshot readiness fields."""

    manifest = build_nas_indicator_snapshot_manifest(contract_path=contract_path)
    contract = load_nas_indicator_snapshot_contract(contract_path)
    summary = {
        "phase": "94",
        "phase_id": 94,
        "nas_indicator_snapshot_contract_ready": manifest[
            "nas_indicator_snapshot_contract_ready"
        ],
        "nas_indicator_snapshot_materialization_ready": manifest[
            "nas_indicator_snapshot_materialization_ready"
        ],
        "phase92_revised_import_dependency_ready": manifest[
            "phase92_revised_import_dependency_ready"
        ],
        "phase93_pit_availability_dependency_ready": manifest[
            "phase93_pit_availability_dependency_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": manifest[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "role_snapshot_count": manifest["role_snapshot_count"],
        "role_with_revised_snapshot_count": manifest[
            "role_with_revised_snapshot_count"
        ],
        "role_without_revised_snapshot_count": manifest[
            "role_without_revised_snapshot_count"
        ],
        "role_with_pit_backfill_plan_count": manifest[
            "role_with_pit_backfill_plan_count"
        ],
        "role_with_pit_backfill_blocker_count": manifest[
            "role_with_pit_backfill_blocker_count"
        ],
        "series_snapshot_count": manifest["series_snapshot_count"],
        "source_artifact_snapshot_count": manifest["source_artifact_snapshot_count"],
        "observation_revised_source_row_count": manifest[
            "observation_revised_source_row_count"
        ],
        "latest_revised_observation_context_count": manifest[
            "latest_revised_observation_context_count"
        ],
        "snapshot_row_schema_valid": manifest["snapshot_row_schema_valid"],
        "service_view_model_ready": manifest["service_view_model_ready"],
        "server_side_view_model_count": manifest["server_side_view_model_count"],
        "api_endpoint_contract_count": manifest["api_endpoint_contract_count"],
        "live_db_connection_attempt_count": manifest[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": manifest["postgres_write_attempt_count"],
        "live_fetch_attempt_count": manifest["live_fetch_attempt_count"],
        "repo_output_written_count": manifest["repo_output_written_count"],
        "public_output_count": manifest["public_output_count"],
        "observation_vintage_row_count": manifest["observation_vintage_row_count"],
        "strict_pit_result_emitted_count": manifest[
            "strict_pit_result_emitted_count"
        ],
        "point_in_time_claim_count": manifest["point_in_time_claim_count"],
        "revised_mislabeled_as_pit_count": manifest[
            "revised_mislabeled_as_pit_count"
        ],
        "candidate_phase_emitted": manifest["candidate_phase_emitted"],
        "current_phase_emitted": manifest["current_phase_emitted"],
        "production_behavior_change_count": manifest[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": manifest["semantic_drift_count"],
        "development_next_phase": manifest["development_next_phase"],
    }
    summary["result"] = "passed" if _passes(summary, contract["hard_gates"]) else "blocked"
    return summary | {"nas_indicator_snapshot_manifest": manifest}


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    policy = contract["snapshot_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["server_side_view_model_allowed"] is True
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["frontend_database_access_allowed"] is False
        and scope["frontend_api_key_allowed"] is False
        and policy["use_phase92_revised_rows"] is True
        and policy["use_phase93_pit_availability_accounting"] is True
        and policy["strict_point_in_time_result_allowed_now"] is False
    )


def _phase92_dependency_ready() -> bool:
    summary = summarize_revised_macro_data_import()
    return (
        summary["result"] == "passed"
        and summary["observation_revised_row_count"] == 112
        and summary["observation_vintage_row_count"] == 0
    )


def _phase93_dependency_ready() -> bool:
    summary = summarize_vintage_pit_backfill_availability()
    return (
        summary["result"] == "passed"
        and summary["role_with_pit_backfill_plan_count"] == 34
        and summary["strict_pit_result_emitted_count"] == 0
    )


def _postgres_dependency_ready() -> bool:
    summary = summarize_postgres_macro_warehouse_contract()
    return (
        summary["result"] == "passed"
        and summary["pit_ready_schema"] is True
        and summary["schema_requires_live_db"] is False
    )


def _latest_observations_by_series(
    observation_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in observation_rows:
        series_key = row["series_key"]
        if (
            series_key not in latest
            or row["observation_date"] > latest[series_key]["observation_date"]
        ):
            latest[series_key] = row
    return latest


def _series_snapshot_row(
    series_row: dict[str, Any],
    *,
    observation: dict[str, Any] | None,
    source_artifact: dict[str, Any] | None,
    pit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    pit_row = pit_row or {}
    return {
        "series_key": series_row["series_key"],
        "source_family": series_row["source_family"],
        "source_series_id": series_row["source_series_id"],
        "frequency": series_row["frequency"],
        "source_url_without_secret": series_row["source_url_without_secret"],
        "latest_revised_observation": _observation_context(observation),
        "source_artifact_id": source_artifact["artifact_id"] if source_artifact else None,
        "source_artifact_hash": source_artifact["content_hash"] if source_artifact else None,
        "pit_backfill_status": pit_row.get("backfill_status", "blocked"),
        "pit_backfill_request_type": pit_row.get("backfill_request_type", "blocked"),
        "pit_backfill_blocked_reason_codes": pit_row.get("blocked_reason_codes", []),
        "data_mode": "revised_diagnostic",
        "strict_point_in_time_result": False,
    }


def _source_artifact_snapshot_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": row["artifact_id"],
        "source_family": row["source_family"],
        "source_series_or_release_id": row["source_series_or_release_id"],
        "fetched_at_utc": row["fetched_at_utc"],
        "content_hash": row["content_hash"],
        "adapter_id": row["adapter_id"],
        "parser_version": row["parser_version"],
        "no_secret": row["no_secret"],
        "validation_status": row["validation_status"],
    }


def _role_snapshot_row(
    role_row: dict[str, Any],
    *,
    observations_by_series: dict[str, dict[str, Any]],
    pit_row: dict[str, Any],
) -> dict[str, Any]:
    latest_context = [
        _observation_context(observations_by_series.get(series_id))
        | {"series_key": series_id}
        for series_id in role_row["official_series_ids"]
        if observations_by_series.get(series_id)
    ]
    snapshot_status = (
        "revised_snapshot_ready"
        if role_row["revised_import_status"] == "ready"
        else "blocked"
    )
    return {
        "role_id": role_row["role_id"],
        "phase_or_layer": role_row["phase_or_layer"],
        "major_group_id": role_row["major_group_id"],
        "official_series_ids": role_row["official_series_ids"],
        "snapshot_status": snapshot_status,
        "data_mode": "revised_diagnostic" if latest_context else "unavailable",
        "latest_revised_observations": latest_context,
        "pit_backfill_status": pit_row["pit_backfill_status"],
        "pit_backfill_ready_for_future_import": (
            pit_row["pit_backfill_status"] == "planned"
        ),
        "blocked_reason_codes": sorted(
            set(role_row["blocked_reason_codes"] + pit_row["blocked_reason_codes"]),
        ),
        "strict_point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "nas_service_indicator_snapshot_rehearsal",
            "dashboard_data_api_view_model",
            "source_lineage_explanation",
        ],
        "prohibited_uses": [
            "strict_point_in_time_evidence",
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "portfolio_or_trade_decision",
        ],
    }


def _observation_context(row: dict[str, Any] | None) -> dict[str, Any]:
    if row is None:
        return {
            "observation_date": None,
            "value_numeric": None,
            "value_text": None,
            "source_artifact_id": None,
            "provenance_hash": None,
        }
    return {
        "observation_date": row["observation_date"],
        "value_numeric": row["value_numeric"],
        "value_text": row["value_text"],
        "source_artifact_id": row["source_artifact_id"],
        "provenance_hash": row["provenance_hash"],
    }


def _service_view_model(
    *,
    contract: dict[str, Any],
    role_snapshots: list[dict[str, Any]],
    series_snapshots: list[dict[str, Any]],
    source_artifact_snapshots: list[dict[str, Any]],
    snapshot_as_of: str,
) -> dict[str, Any]:
    return {
        "view_model_version": contract["version"],
        "service_target": contract["service_scope"]["target_runtime"],
        "as_of": snapshot_as_of,
        "output_mode": "research_only_nas_service_indicator_snapshot",
        "readiness_label": "revised_diagnostic_snapshot_with_pit_availability_accounting",
        "role_snapshot_count": len(role_snapshots),
        "series_snapshot_count": len(series_snapshots),
        "source_artifact_snapshot_count": len(source_artifact_snapshots),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "nas_migration_surface": "server_side_view_model_rehearsal",
            "frontend_database_access_allowed": False,
            "frontend_api_key_allowed": False,
            "revised_diagnostic_only": True,
            "pit_availability_accounting_included": True,
            "strict_point_in_time_result": False,
            "live_db_connection_attempted": False,
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
        },
    }


def _snapshot_schema_valid(
    *,
    role_snapshots: list[dict[str, Any]],
    series_snapshots: list[dict[str, Any]],
    source_artifact_snapshots: list[dict[str, Any]],
) -> bool:
    return (
        all(
            row.get("role_id")
            and row.get("snapshot_status") in {"revised_snapshot_ready", "blocked"}
            and row.get("pit_backfill_status") in {"planned", "blocked"}
            and row.get("strict_point_in_time_result") is False
            for row in role_snapshots
        )
        and all(
            row.get("series_key")
            and row.get("source_series_id")
            and row.get("latest_revised_observation") is not None
            for row in series_snapshots
        )
        and all(
            row.get("artifact_id")
            and row.get("content_hash")
            and row.get("no_secret") is True
            for row in source_artifact_snapshots
        )
    )


def _service_view_model_ready(view_model: dict[str, Any]) -> bool:
    trust = view_model["trust_metadata"]
    return (
        view_model["service_target"] == "private_nas_dynamic_service"
        and trust["frontend_database_access_allowed"] is False
        and trust["frontend_api_key_allowed"] is False
        and trust["revised_diagnostic_only"] is True
        and trust["pit_availability_accounting_included"] is True
        and trust["strict_point_in_time_result"] is False
    )


def _validated_tmp_output(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return path
    raise ValueError("Phase94 dry-run output must be under /tmp")


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
