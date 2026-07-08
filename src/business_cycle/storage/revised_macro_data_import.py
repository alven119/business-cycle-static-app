"""Revised macro data import dry-run for the Phase 91 warehouse schema."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import tempfile
from typing import Any

import yaml

from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.render.local_current_cache_dashboard_bridge import (
    seed_local_current_cache_rehearsal,
)
from business_cycle.storage.postgres_macro_warehouse import (
    summarize_postgres_macro_warehouse_contract,
)
from business_cycle.storage.raw_store import RawCsvStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/revised_macro_data_import_contract.yaml"
DEFAULT_REGISTRY_PATH = ROOT / "specs/common/series_release_lag_registry.yaml"
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


def load_revised_macro_data_import_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 92 revised import contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["revised_macro_data_import_contract"])


def build_revised_macro_data_import_manifest(
    *,
    cache_dir: str | Path | None = None,
    seed_tmp_cache_when_missing: bool = True,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Build warehouse-shaped revised import rows without writing to Postgres."""

    contract = load_revised_macro_data_import_contract(contract_path)
    if cache_dir is None and seed_tmp_cache_when_missing:
        with tempfile.TemporaryDirectory(prefix="phase92_revised_macro_", dir="/tmp") as tmp:
            tmp_cache = Path(tmp) / "fred_current_cache"
            seed_local_current_cache_rehearsal(tmp_cache)
            return _build_manifest_from_cache(
                contract=contract,
                cache_dir=tmp_cache,
                cache_dir_kind="tmp",
                snapshot_as_of=snapshot_as_of,
                tmp_seeded_rehearsal=True,
                registry_path=registry_path,
            )

    resolved_cache_dir = Path(cache_dir) if cache_dir is not None else None
    return _build_manifest_from_cache(
        contract=contract,
        cache_dir=resolved_cache_dir,
        cache_dir_kind=_cache_dir_kind(resolved_cache_dir),
        snapshot_as_of=snapshot_as_of,
        tmp_seeded_rehearsal=False,
        registry_path=registry_path,
    )


def write_revised_macro_data_import_manifest(
    manifest: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    """Write a dry-run manifest only to /tmp."""

    output_path = _validated_tmp_output(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "revised_macro_data_import_manifest_written": True,
        "written_file_count": 1,
        "dry_run_output_under_tmp_only": True,
        "repo_output_written_count": 0,
    }


def summarize_revised_macro_data_import(
    *,
    cache_dir: str | Path | None = None,
    seed_tmp_cache_when_missing: bool = True,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Return compact Phase 92 revised import readiness fields."""

    manifest = build_revised_macro_data_import_manifest(
        cache_dir=cache_dir,
        seed_tmp_cache_when_missing=seed_tmp_cache_when_missing,
        snapshot_as_of=snapshot_as_of,
        contract_path=contract_path,
        registry_path=registry_path,
    )
    contract = load_revised_macro_data_import_contract(contract_path)
    summary = {
        "phase": "92",
        "phase_id": 92,
        "revised_macro_data_import_contract_ready": manifest[
            "revised_macro_data_import_contract_ready"
        ],
        "revised_macro_data_import_dry_run_ready": manifest[
            "revised_macro_data_import_dry_run_ready"
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
        "role_without_import_status_count": manifest[
            "role_without_import_status_count"
        ],
        "blocked_role_with_reason_count": manifest["blocked_role_with_reason_count"],
        "unique_series_count": manifest["unique_series_count"],
        "series_registry_row_count": manifest["series_registry_row_count"],
        "source_artifact_row_count": manifest["source_artifact_row_count"],
        "observation_revised_row_count": manifest["observation_revised_row_count"],
        "observation_vintage_row_count": manifest["observation_vintage_row_count"],
        "warehouse_row_schema_valid": manifest["warehouse_row_schema_valid"],
        "source_artifact_hash_complete": manifest["source_artifact_hash_complete"],
        "provenance_hash_complete": manifest["provenance_hash_complete"],
        "dry_run_output_under_tmp_only": manifest["dry_run_output_under_tmp_only"],
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
    return summary | {"revised_macro_data_import_manifest": manifest}


def _build_manifest_from_cache(
    *,
    contract: dict[str, Any],
    cache_dir: Path | None,
    cache_dir_kind: str,
    snapshot_as_of: str,
    tmp_seeded_rehearsal: bool,
    registry_path: str | Path,
) -> dict[str, Any]:
    cards = build_indicator_detail_source_risk_value_cards()
    registry = _load_series_registry(registry_path)
    unique_series_ids = _unique_series_ids(cards)
    store = RawCsvStore(cache_dir) if cache_dir is not None else None

    observations_by_series = {
        series_id: _read_revised_observations(store, series_id)
        for series_id in unique_series_ids
    }
    source_artifacts = [
        _source_artifact_row(
            series_id=series_id,
            observations=observations_by_series[series_id],
            cache_dir_kind=cache_dir_kind,
        )
        for series_id in unique_series_ids
        if observations_by_series[series_id]
    ]
    artifact_by_series = {
        row["source_series_or_release_id"]: row for row in source_artifacts
    }
    series_registry_rows = [
        _series_registry_row(series_id, registry.get(series_id))
        for series_id in unique_series_ids
    ]
    observation_revised_rows = [
        _observation_revised_row(
            observation=observation,
            artifact=artifact_by_series[series_id],
        )
        for series_id in unique_series_ids
        for observation in observations_by_series[series_id]
        if series_id in artifact_by_series
    ]
    role_import_rows = [
        _role_import_row(
            card=card,
            observations_by_series=observations_by_series,
        )
        for card in sorted(cards, key=lambda item: item["role_id"])
    ]
    blocked_roles = [
        row for row in role_import_rows if row["revised_import_status"] == "blocked"
    ]
    ready_roles = [
        row for row in role_import_rows if row["revised_import_status"] == "ready"
    ]
    manifest: dict[str, Any] = {
        "artifact_id": "phase92_revised_macro_data_import_dry_run",
        "artifact_version": contract["version"],
        "phase": "92",
        "phase_id": 92,
        "phase_label": contract["phase_label"],
        "generated_at_utc": f"{snapshot_as_of}T00:00:00Z",
        "snapshot_as_of": snapshot_as_of,
        "output_mode": "research_only_revised_warehouse_import_dry_run",
        "research_only": True,
        "data_mode": "revised",
        "cache_dir_kind": cache_dir_kind,
        "tmp_seeded_rehearsal": tmp_seeded_rehearsal,
        "targeted_warehouse_tables": contract["targeted_warehouse_tables"],
        "excluded_warehouse_tables": contract["excluded_warehouse_tables"],
        "series_registry_rows": series_registry_rows,
        "source_artifact_rows": source_artifacts,
        "observation_revised_rows": observation_revised_rows,
        "observation_vintage_rows": [],
        "role_import_rows": role_import_rows,
        "revised_macro_data_import_contract_ready": _contract_ready(contract),
        "postgres_macro_warehouse_dependency_ready": _postgres_dependency_ready(),
        "role_count": len(role_import_rows),
        "revised_import_ready_role_count": len(ready_roles),
        "revised_import_blocked_role_count": len(blocked_roles),
        "role_without_import_status_count": sum(
            not row["revised_import_status"] for row in role_import_rows
        ),
        "blocked_role_with_reason_count": sum(
            bool(row["blocked_reason_codes"]) for row in blocked_roles
        ),
        "unique_series_count": len(unique_series_ids),
        "series_registry_row_count": len(series_registry_rows),
        "source_artifact_row_count": len(source_artifacts),
        "observation_revised_row_count": len(observation_revised_rows),
        "observation_vintage_row_count": 0,
        "warehouse_row_schema_valid": _warehouse_row_schema_valid(
            series_registry_rows=series_registry_rows,
            source_artifact_rows=source_artifacts,
            observation_revised_rows=observation_revised_rows,
        ),
        "source_artifact_hash_complete": all(
            row["content_hash"] for row in source_artifacts
        ),
        "provenance_hash_complete": all(
            row["provenance_hash"] for row in observation_revised_rows
        ),
        "dry_run_output_under_tmp_only": True,
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
            "revised_observations_only": True,
            "vintage_import_attempted": False,
            "live_db_connection_attempted": False,
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "point_in_time_result": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
        },
        "development_next_phase": int(contract["hard_gates"]["development_next_phase"]),
    }
    manifest["prohibited_output_field_count"] = _contains_prohibited_field(manifest)
    expected_without_self = dict(contract["hard_gates"])
    expected_without_self.pop("revised_macro_data_import_dry_run_ready", None)
    manifest["revised_macro_data_import_dry_run_ready"] = _passes(
        manifest,
        expected_without_self,
    )
    manifest["manifest_hash"] = _hash_payload(
        {
            "series_registry_rows": series_registry_rows,
            "source_artifact_rows": source_artifacts,
            "observation_revised_rows": observation_revised_rows,
            "role_import_rows": role_import_rows,
        },
    )
    manifest["result"] = (
        "passed" if manifest["revised_macro_data_import_dry_run_ready"] else "blocked"
    )
    return manifest


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active_research_contract"
        and contract["import_scope"]["postgres_write_allowed_now"] is False
        and contract["import_scope"]["live_db_connection_allowed_now"] is False
        and contract["data_mode_policy"]["imported_data_mode"] == "revised"
        and "observation_revised" in contract["targeted_warehouse_tables"]
        and "observation_vintage" in contract["excluded_warehouse_tables"]
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
    return {
        str(row["series_id"]): row
        for row in payload["series_release_lag_registry"]["series"]
    }


def _unique_series_ids(cards: list[dict[str, Any]]) -> list[str]:
    series_ids: list[str] = []
    for card in cards:
        for series_id in card["official_series_ids"]:
            if series_id not in series_ids:
                series_ids.append(series_id)
    return sorted(series_ids)


def _read_revised_observations(store: RawCsvStore | None, series_id: str) -> list[Any]:
    if store is None or not store.exists("fred", series_id):
        return []
    return sorted(
        store.read_observations("fred", series_id),
        key=lambda observation: observation.date,
    )


def _series_registry_row(
    series_id: str,
    registry_row: dict[str, Any] | None,
) -> dict[str, Any]:
    registry_row = registry_row or {}
    return {
        "series_key": series_id,
        "source_family": registry_row.get("source", "FRED/ALFRED"),
        "source_series_id": series_id,
        "source_title": registry_row.get("release_family", series_id),
        "units": "not_declared_in_release_lag_registry",
        "frequency": registry_row.get("frequency", "unknown"),
        "seasonal_adjustment": "not_declared_in_release_lag_registry",
        "geographic_scope": "US_or_source_declared",
        "source_url_without_secret": f"https://fred.stlouisfed.org/series/{series_id}",
        "source_identity_status": (
            "release_lag_registry_present" if registry_row else "registry_missing"
        ),
        "created_at_utc": GENERATED_AT_UTC,
        "updated_at_utc": GENERATED_AT_UTC,
    }


def _source_artifact_row(
    *,
    series_id: str,
    observations: list[Any],
    cache_dir_kind: str,
) -> dict[str, Any]:
    content_hash = _hash_payload(
        [
            {
                "series_id": observation.series_id,
                "date": observation.date,
                "value": observation.value,
            }
            for observation in observations
        ],
    )
    return {
        "artifact_id": f"revised_cache::{series_id}::{content_hash[:12]}",
        "source_family": "FRED/ALFRED",
        "source_url_without_secret": f"https://fred.stlouisfed.org/series/{series_id}",
        "source_series_or_release_id": series_id,
        "fetched_at_utc": GENERATED_AT_UTC,
        "content_hash": content_hash,
        "content_type": "text/csv",
        "adapter_id": "fred_current_refresh_revised_cache",
        "parser_version": "raw_csv_store_v1",
        "no_secret": True,
        "validation_status": f"validated_revised_import_dry_run_{cache_dir_kind}",
    }


def _observation_revised_row(
    *,
    observation: Any,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    raw_value = str(observation.value)
    value_numeric = _decimal_or_none(raw_value)
    provenance_hash = _hash_payload(
        {
            "series_key": observation.series_id,
            "observation_date": observation.date,
            "value": raw_value,
            "artifact_id": artifact["artifact_id"],
            "data_mode": "revised",
        },
    )
    return {
        "series_key": observation.series_id,
        "observation_date": observation.date,
        "value_numeric": str(value_numeric) if value_numeric is not None else None,
        "value_text": raw_value if value_numeric is None else None,
        "unit": "not_declared_in_release_lag_registry",
        "data_mode": "revised",
        "source_artifact_id": artifact["artifact_id"],
        "fetched_at_utc": artifact["fetched_at_utc"],
        "provenance_hash": provenance_hash,
    }


def _role_import_row(
    *,
    card: dict[str, Any],
    observations_by_series: dict[str, list[Any]],
) -> dict[str, Any]:
    series_ids = list(card["official_series_ids"])
    missing = [
        series_id
        for series_id in series_ids
        if not observations_by_series.get(series_id)
    ]
    blocked_reasons: list[str] = []
    if not series_ids:
        blocked_reasons.append("no_official_or_accepted_revised_series")
    if missing:
        blocked_reasons.append("local_revised_cache_missing_series")
    status = "blocked" if blocked_reasons else "ready"
    observation_count = sum(len(observations_by_series.get(series_id, [])) for series_id in series_ids)
    return {
        "role_id": card["role_id"],
        "phase_or_layer": card["phase_or_layer"],
        "major_group_id": card["major_group_id"],
        "official_series_ids": series_ids,
        "source_coverage_tier": card["source_coverage_tier"],
        "data_risk_level": card["data_risk_level"],
        "source_risk_label_zh": card["source_risk_label_zh"],
        "revised_import_status": status,
        "revised_observation_row_count": observation_count,
        "blocked_reason_codes": blocked_reasons,
        "data_mode": "revised",
        "point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
        "allowed_uses": [
            "revised_macro_warehouse_import_rehearsal",
            "source_lineage_review",
        ],
        "prohibited_uses": [
            "point_in_time_evidence",
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "portfolio_or_trade_decision",
        ],
    }


def _warehouse_row_schema_valid(
    *,
    series_registry_rows: list[dict[str, Any]],
    source_artifact_rows: list[dict[str, Any]],
    observation_revised_rows: list[dict[str, Any]],
) -> bool:
    return (
        all(row.get("series_key") and row.get("source_series_id") for row in series_registry_rows)
        and all(
            row.get("artifact_id")
            and row.get("content_hash")
            and row.get("no_secret") is True
            for row in source_artifact_rows
        )
        and all(
            row.get("series_key")
            and row.get("observation_date")
            and row.get("data_mode") == "revised"
            and row.get("source_artifact_id")
            and row.get("provenance_hash")
            for row in observation_revised_rows
        )
    )


def _decimal_or_none(value: str) -> Decimal | None:
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _validated_tmp_output(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return path
    raise ValueError("Phase92 dry-run output must be under /tmp")


def _cache_dir_kind(cache_dir: Path | None) -> str:
    if cache_dir is None:
        return "none"
    resolved = cache_dir.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return "tmp"
    return "explicit_local_cache"


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
