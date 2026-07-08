"""Vintage/PIT backfill availability accounting for Phase 93.

This module turns the Phase 92 revised import manifest into a no-write
backfill plan. It does not fetch ALFRED data, verify local vintage cache
coverage, connect to Postgres, or emit strict point-in-time results.
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
    DEFAULT_REGISTRY_PATH,
    build_revised_macro_data_import_manifest,
    summarize_revised_macro_data_import,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/vintage_pit_backfill_availability_contract.yaml"
)
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


def load_vintage_pit_backfill_availability_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 93 vintage/PIT backfill availability contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["vintage_pit_backfill_availability_contract"])


def build_vintage_pit_backfill_availability_manifest(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
) -> dict[str, Any]:
    """Build deterministic PIT backfill availability rows without side effects."""

    contract = load_vintage_pit_backfill_availability_contract(contract_path)
    revised_manifest = build_revised_macro_data_import_manifest(
        registry_path=registry_path,
        snapshot_as_of=snapshot_as_of,
    )
    series_registry = _load_series_registry(registry_path)
    backfill_rows = [
        _backfill_availability_row(
            row["series_key"],
            series_registry=series_registry,
        )
        for row in revised_manifest["series_registry_rows"]
    ]
    by_series = {row["series_key"]: row for row in backfill_rows}
    role_rows = [
        _role_backfill_row(row, by_series=by_series)
        for row in revised_manifest["role_import_rows"]
    ]
    ready_roles = [
        row for row in role_rows if row["pit_backfill_status"] == "planned"
    ]
    blocked_roles = [
        row for row in role_rows if row["pit_backfill_status"] == "blocked"
    ]
    covered_series = [
        row for row in backfill_rows if row["release_lag_registry_present"]
    ]
    pit_eligible = [row for row in covered_series if row["point_in_time_eligible"]]
    vintage_supported = [
        row for row in covered_series if row["vintage_query_supported"]
    ]
    derived_planned = [
        row for row in covered_series if row["backfill_request_type"] == "derived_plan"
    ]
    manifest: dict[str, Any] = {
        "artifact_id": "phase93_vintage_pit_backfill_availability_accounting",
        "artifact_version": contract["version"],
        "phase": "93",
        "phase_id": 93,
        "phase_label": contract["phase_label"],
        "generated_at_utc": f"{snapshot_as_of}T00:00:00Z",
        "snapshot_as_of": snapshot_as_of,
        "output_mode": "research_only_vintage_pit_backfill_accounting",
        "research_only": True,
        "phase92_manifest_hash": revised_manifest["manifest_hash"],
        "targeted_warehouse_tables": contract["targeted_warehouse_tables"],
        "excluded_outputs": contract["excluded_outputs"],
        "backfill_availability_rows": backfill_rows,
        "role_backfill_rows": role_rows,
        "planned_vintage_backfill_requests": [
            row for row in backfill_rows if row["backfill_status"] == "planned"
        ],
        "observation_vintage_rows": [],
        "vintage_pit_backfill_availability_contract_ready": _contract_ready(
            contract,
        ),
        "phase92_revised_import_dependency_ready": _phase92_dependency_ready(),
        "postgres_macro_warehouse_dependency_ready": _postgres_dependency_ready(),
        "role_count": revised_manifest["role_count"],
        "revised_import_ready_role_count": revised_manifest[
            "revised_import_ready_role_count"
        ],
        "revised_import_blocked_role_count": revised_manifest[
            "revised_import_blocked_role_count"
        ],
        "role_with_pit_backfill_plan_count": len(ready_roles),
        "role_blocked_from_pit_backfill_count": len(blocked_roles),
        "blocked_role_with_reason_count": sum(
            bool(row["blocked_reason_codes"]) for row in blocked_roles
        ),
        "unique_series_count": revised_manifest["unique_series_count"],
        "backfill_availability_row_count": len(backfill_rows),
        "series_registry_metadata_covered_count": len(covered_series),
        "series_missing_release_lag_registry_count": sum(
            not row["release_lag_registry_present"] for row in backfill_rows
        ),
        "pit_eligible_series_count": len(pit_eligible),
        "vintage_query_supported_series_count": len(vintage_supported),
        "derived_pit_plan_series_count": len(derived_planned),
        "planned_vintage_backfill_series_count": len(
            [row for row in backfill_rows if row["backfill_status"] == "planned"],
        ),
        "planned_vintage_request_row_count": sum(
            row["backfill_request_type"] == "direct_vintage_request"
            for row in backfill_rows
        ),
        "observation_vintage_row_count": 0,
        "strict_pit_result_emitted_count": 0,
        "local_vintage_cache_verification_attempt_count": 0,
        "local_vintage_cache_write_count": 0,
        "live_db_connection_attempt_count": 0,
        "postgres_write_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "point_in_time_claim_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "warehouse_shape": "postgres_macro_phase91",
            "phase92_revised_manifest_used": True,
            "revised_rows_remain_revised": True,
            "vintage_import_attempted": False,
            "strict_point_in_time_result": False,
            "local_vintage_cache_verification_attempted": False,
            "live_db_connection_attempted": False,
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
        },
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    manifest["prohibited_output_field_count"] = _contains_prohibited_field(manifest)
    manifest["backfill_accounting_hash"] = _hash_payload(
        {
            "phase92_manifest_hash": manifest["phase92_manifest_hash"],
            "backfill_availability_rows": backfill_rows,
            "role_backfill_rows": role_rows,
        },
    )
    expected_without_self = dict(contract["hard_gates"])
    expected_without_self.pop("vintage_pit_backfill_accounting_ready", None)
    manifest["vintage_pit_backfill_accounting_ready"] = _passes(
        manifest,
        expected_without_self,
    )
    manifest["result"] = (
        "passed" if manifest["vintage_pit_backfill_accounting_ready"] else "blocked"
    )
    return manifest


def write_vintage_pit_backfill_availability_manifest(
    manifest: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    """Write a Phase 93 dry-run manifest only under /tmp."""

    output_path = _validated_tmp_output(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "vintage_pit_backfill_availability_manifest_written": True,
        "written_file_count": 1,
        "dry_run_output_under_tmp_only": True,
        "repo_output_written_count": 0,
    }


def summarize_vintage_pit_backfill_availability(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Return compact Phase 93 vintage/PIT backfill readiness fields."""

    manifest = build_vintage_pit_backfill_availability_manifest(
        contract_path=contract_path,
        registry_path=registry_path,
    )
    contract = load_vintage_pit_backfill_availability_contract(contract_path)
    summary = {
        "phase": "93",
        "phase_id": 93,
        "vintage_pit_backfill_availability_contract_ready": manifest[
            "vintage_pit_backfill_availability_contract_ready"
        ],
        "vintage_pit_backfill_accounting_ready": manifest[
            "vintage_pit_backfill_accounting_ready"
        ],
        "phase92_revised_import_dependency_ready": manifest[
            "phase92_revised_import_dependency_ready"
        ],
        "postgres_macro_warehouse_dependency_ready": manifest[
            "postgres_macro_warehouse_dependency_ready"
        ],
        "role_count": manifest["role_count"],
        "revised_import_ready_role_count": manifest[
            "revised_import_ready_role_count"
        ],
        "revised_import_blocked_role_count": manifest[
            "revised_import_blocked_role_count"
        ],
        "role_with_pit_backfill_plan_count": manifest[
            "role_with_pit_backfill_plan_count"
        ],
        "role_blocked_from_pit_backfill_count": manifest[
            "role_blocked_from_pit_backfill_count"
        ],
        "blocked_role_with_reason_count": manifest[
            "blocked_role_with_reason_count"
        ],
        "unique_series_count": manifest["unique_series_count"],
        "backfill_availability_row_count": manifest[
            "backfill_availability_row_count"
        ],
        "series_registry_metadata_covered_count": manifest[
            "series_registry_metadata_covered_count"
        ],
        "series_missing_release_lag_registry_count": manifest[
            "series_missing_release_lag_registry_count"
        ],
        "pit_eligible_series_count": manifest["pit_eligible_series_count"],
        "vintage_query_supported_series_count": manifest[
            "vintage_query_supported_series_count"
        ],
        "derived_pit_plan_series_count": manifest["derived_pit_plan_series_count"],
        "planned_vintage_backfill_series_count": manifest[
            "planned_vintage_backfill_series_count"
        ],
        "planned_vintage_request_row_count": manifest[
            "planned_vintage_request_row_count"
        ],
        "observation_vintage_row_count": manifest["observation_vintage_row_count"],
        "strict_pit_result_emitted_count": manifest[
            "strict_pit_result_emitted_count"
        ],
        "local_vintage_cache_verification_attempt_count": manifest[
            "local_vintage_cache_verification_attempt_count"
        ],
        "local_vintage_cache_write_count": manifest[
            "local_vintage_cache_write_count"
        ],
        "live_db_connection_attempt_count": manifest[
            "live_db_connection_attempt_count"
        ],
        "postgres_write_attempt_count": manifest["postgres_write_attempt_count"],
        "live_fetch_attempt_count": manifest["live_fetch_attempt_count"],
        "repo_output_written_count": manifest["repo_output_written_count"],
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
    return summary | {"vintage_pit_backfill_availability_manifest": manifest}


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["scope"]
    data_mode = contract["data_mode_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["live_fetch_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["strict_pit_result_allowed_now"] is False
        and data_mode["vintage_rows_planned_not_written"] is True
        and data_mode["revised_data_may_not_be_labeled_point_in_time"] is True
        and "observation_vintage" in contract["targeted_warehouse_tables"]
    )


def _phase92_dependency_ready() -> bool:
    summary = summarize_revised_macro_data_import()
    return (
        summary["result"] == "passed"
        and summary["observation_revised_row_count"] > 0
        and summary["observation_vintage_row_count"] == 0
    )


def _postgres_dependency_ready() -> bool:
    summary = summarize_postgres_macro_warehouse_contract()
    return (
        summary["result"] == "passed"
        and summary["pit_ready_schema"] is True
        and summary["schema_requires_live_db"] is False
    )


def _load_series_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = payload["series_release_lag_registry"]["series"]
    registry = {str(row["series_id"]): row for row in rows}
    return registry | {
        str(row["series_id"]).removeprefix("derived:"): row
        for row in rows
        if str(row["series_id"]).startswith("derived:")
    }


def _backfill_availability_row(
    series_key: str,
    *,
    series_registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    registry_row = series_registry.get(series_key)
    if registry_row is None:
        return {
            "series_key": series_key,
            "release_lag_registry_present": False,
            "registry_series_id": None,
            "source_family": "unknown",
            "frequency": "unknown",
            "availability_mode": "unregistered",
            "point_in_time_eligible": False,
            "vintage_query_supported": False,
            "initial_release_query_supported": False,
            "input_series_ids": [],
            "latest_verified_vintage_date": "not_available",
            "scenario_coverage_start": "not_available",
            "scenario_coverage_end": "not_available",
            "temporal_status": "registry_missing",
            "backfill_status": "blocked",
            "backfill_request_type": "blocked_missing_registry",
            "planned_target_table": "observation_vintage",
            "actual_observation_vintage_rows_written": 0,
            "blocked_reason_codes": ["missing_release_lag_registry_metadata"],
            "live_fetch_attempted": False,
            "postgres_write_attempted": False,
            "strict_point_in_time_result": False,
        }

    is_derived = str(registry_row["series_id"]).startswith("derived:")
    point_in_time_eligible = bool(registry_row["point_in_time_eligible"])
    vintage_supported = bool(registry_row["vintage_query_supported"])
    backfill_status = (
        "planned" if point_in_time_eligible and (vintage_supported or is_derived) else "blocked"
    )
    request_type = (
        "derived_plan"
        if is_derived and backfill_status == "planned"
        else "direct_vintage_request"
        if vintage_supported and backfill_status == "planned"
        else "blocked_not_vintage_supported"
    )
    return {
        "series_key": series_key,
        "release_lag_registry_present": True,
        "registry_series_id": registry_row["series_id"],
        "source_family": registry_row["source"],
        "frequency": registry_row["frequency"],
        "availability_mode": registry_row["availability_mode"],
        "point_in_time_eligible": point_in_time_eligible,
        "vintage_query_supported": vintage_supported,
        "initial_release_query_supported": bool(
            registry_row["initial_release_query_supported"],
        ),
        "input_series_ids": list(registry_row.get("input_series_ids", [])),
        "latest_verified_vintage_date": registry_row["latest_verified_vintage_date"],
        "scenario_coverage_start": registry_row["scenario_coverage_start"],
        "scenario_coverage_end": registry_row["scenario_coverage_end"],
        "temporal_status": registry_row["temporal_status"],
        "backfill_status": backfill_status,
        "backfill_request_type": request_type,
        "planned_target_table": "observation_vintage",
        "actual_observation_vintage_rows_written": 0,
        "blocked_reason_codes": _series_blocked_reasons(
            is_derived=is_derived,
            point_in_time_eligible=point_in_time_eligible,
            vintage_supported=vintage_supported,
        ),
        "live_fetch_attempted": False,
        "postgres_write_attempted": False,
        "strict_point_in_time_result": False,
    }


def _series_blocked_reasons(
    *,
    is_derived: bool,
    point_in_time_eligible: bool,
    vintage_supported: bool,
) -> list[str]:
    reasons: list[str] = []
    if not point_in_time_eligible:
        reasons.append("not_point_in_time_eligible")
    if not vintage_supported and not is_derived:
        reasons.append("vintage_query_not_supported")
    return reasons


def _role_backfill_row(
    role_row: dict[str, Any],
    *,
    by_series: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    series_ids = list(role_row["official_series_ids"])
    series_rows = [by_series.get(series_id) for series_id in series_ids]
    blocked_reasons: list[str] = []
    if role_row["revised_import_status"] != "ready":
        blocked_reasons.extend(role_row["blocked_reason_codes"])
    missing_rows = [
        series_id
        for series_id, row in zip(series_ids, series_rows, strict=False)
        if row is None or not row["release_lag_registry_present"]
    ]
    blocked_series = [
        series_id
        for series_id, row in zip(series_ids, series_rows, strict=False)
        if row is not None and row["backfill_status"] != "planned"
    ]
    if missing_rows:
        blocked_reasons.append("series_release_lag_registry_missing")
    if blocked_series:
        blocked_reasons.append("series_pit_backfill_not_planned")
    status = "blocked" if blocked_reasons else "planned"
    return {
        "role_id": role_row["role_id"],
        "phase_or_layer": role_row["phase_or_layer"],
        "major_group_id": role_row["major_group_id"],
        "official_series_ids": series_ids,
        "pit_backfill_status": status,
        "backfill_request_series_ids": [
            row["series_key"]
            for row in series_rows
            if row is not None and row["backfill_status"] == "planned"
        ],
        "blocked_reason_codes": sorted(set(blocked_reasons)),
        "data_mode": "vintage_as_of_planned",
        "strict_point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "vintage_pit_backfill_planning",
            "strict_replay_readiness_accounting",
        ],
        "prohibited_uses": [
            "strict_point_in_time_evidence",
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "portfolio_or_trade_decision",
        ],
    }


def _validated_tmp_output(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return path
    raise ValueError("Phase93 dry-run output must be under /tmp")


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
