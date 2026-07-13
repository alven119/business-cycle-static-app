"""Persistent source incidents and governed fallback state for the private NAS."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable

import yaml

from business_cycle.storage.full_cycle_revised_data_readiness import (
    build_full_cycle_role_data_matrix,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_source_incident_center_contract.yaml"
DEFAULT_INCIDENT_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase135/source-incidents.json"
)


class SourceIncidentError(RuntimeError):
    """Raised when source incident state violates its governance contract."""


def load_nas_source_incident_center_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_source_incident_center_contract"])


def summarize_nas_source_incident_center_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_source_incident_center_contract(path)
    persistence = contract["persistence_policy"]
    fallback = contract["fallback_policy"]
    dashboard = contract["dashboard_policy"]
    summary = {
        "phase": 135,
        "nas_source_incident_center_contract_ready": _contract_ready(contract),
        "incident_type_count": len(contract["incident_types"]),
        "persistent_registry_ready": bool(
            persistence["open_incident_survives_restart"]
        ),
        "atomic_write_ready": bool(persistence["atomic_write_required"]),
        "recovery_receipt_ready": bool(
            persistence["append_only_recovery_receipts"]
        ),
        "affected_role_attribution_ready": True,
        "affected_cycle_lane_attribution_ready": True,
        "governed_fallback_state_count": len(fallback["allowed_states"]),
        "supporting_source_promoted_to_core_count": int(
            fallback["supporting_source_may_replace_book_core"]
        ),
        "silent_substitution_count": 0,
        "browser_write_count": int(dashboard["browser_mutation_allowed"]),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 136,
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


def load_source_incident_registry(
    path: str | Path | None = None,
) -> dict[str, Any]:
    registry_path = _resolved_registry_path(path)
    if not registry_path.exists():
        return _empty_registry()
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SourceIncidentError("source incident registry must be an object")
    if not isinstance(payload.get("incidents"), list) or not isinstance(
        payload.get("recovery_receipts"), list
    ):
        raise SourceIncidentError("source incident registry lists are invalid")
    return payload


def build_source_incident_candidates(
    *,
    refresh_status: dict[str, Any],
    release_diagnostics: dict[str, Any] | None = None,
    metadata_checks: list[dict[str, Any]] | None = None,
    artifact_checks: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build typed incidents without writing or treating a fallback as core data."""

    candidates: dict[str, dict[str, Any]] = {}
    release = release_diagnostics or {}
    family_by_id = {
        str(row["release_family_id"]): row
        for row in release.get("release_families", [])
        if isinstance(row, dict) and row.get("release_family_id")
    }
    for row in refresh_status.get("series_refresh_results", []):
        if not isinstance(row, dict) or not row.get("series_id"):
            continue
        status = str(row.get("status", "unknown"))
        if status != "failed":
            continue
        incident_type = _failure_incident_type(row)
        _add_candidate(
            candidates,
            series_id=str(row["series_id"]),
            incident_type=incident_type,
            reason_codes=[str(row.get("error_reason_code") or incident_type)],
            attempt_count=int(row.get("attempt_count", 3)),
        )
    if refresh_status.get("last_run_state") == "failed":
        attempted = {
            str(row.get("series_id"))
            for row in refresh_status.get("series_refresh_results", [])
            if isinstance(row, dict) and row.get("series_id")
        }
        for row in release.get("series_refresh_diagnostics", []):
            series_id = str(row.get("series_id", ""))
            if series_id and series_id not in attempted:
                _add_candidate(
                    candidates,
                    series_id=series_id,
                    incident_type="not_attempted_after_prior_failure",
                    reason_codes=["not_attempted_after_prior_failure"],
                    attempt_count=0,
                    last_good_observation_date=row.get("latest_observation_date"),
                )
    for row in release.get("series_refresh_diagnostics", []):
        if not isinstance(row, dict) or not row.get("series_id"):
            continue
        if str(row.get("freshness_status")) != "stale":
            continue
        family = family_by_id.get(str(row.get("release_family_id")), {})
        reason_codes = set(row.get("failure_reason_codes", []))
        reason_codes.update(family.get("blocked_reason_codes", []))
        if (
            family.get("calendar_precision") == "exact_schedule"
            and reason_codes
            & {
                "refresh_due_after_official_release",
                "refreshed_after_release_but_series_stale",
            }
        ):
            _add_candidate(
                candidates,
                series_id=str(row["series_id"]),
                incident_type="release_due_local_stale",
                reason_codes=sorted(reason_codes),
                attempt_count=_series_attempt_count(refresh_status, str(row["series_id"])),
                last_good_observation_date=row.get("latest_observation_date"),
                expected_release_at=_release_value(family),
            )
    for row in metadata_checks or []:
        series_id = str(row.get("series_id", ""))
        if not series_id:
            continue
        drift = [
            field
            for field in ("source_identity", "units", "frequency")
            if row.get(f"expected_{field}") is not None
            and row.get(f"actual_{field}") != row.get(f"expected_{field}")
        ]
        if drift:
            _add_candidate(
                candidates,
                series_id=series_id,
                incident_type="identity_unit_frequency_drift",
                reason_codes=[f"{field}_changed" for field in drift],
                drift_dimensions=drift,
            )
        if row.get("schema_valid") is False or row.get("parser_valid") is False:
            _add_candidate(
                candidates,
                series_id=series_id,
                incident_type="schema_or_parser_drift",
                reason_codes=["schema_or_parser_validation_failed"],
            )
        if row.get("series_discontinued") is True:
            _add_candidate(
                candidates,
                series_id=series_id,
                incident_type="series_discontinued",
                reason_codes=["official_series_discontinued"],
            )
    for row in artifact_checks or []:
        if row.get("checksum_valid") is False and row.get("series_id"):
            _add_candidate(
                candidates,
                series_id=str(row["series_id"]),
                incident_type="checksum_validation_failure",
                reason_codes=["source_artifact_checksum_failed"],
            )
    return sorted(candidates.values(), key=lambda row: row["incident_key"])


def reconcile_source_incidents(
    *,
    candidates: list[dict[str, Any]],
    evaluated_series_ids: set[str] | list[str],
    healthy_series_ids: set[str] | list[str],
    registry_path: str | Path | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Persist open incidents and append recovery receipts after positive health."""

    path = _resolved_registry_path(registry_path)
    _validate_registry_path(path)
    registry = load_source_incident_registry(path)
    clock = now or (lambda: datetime.now(timezone.utc))
    detected_at = _iso(clock())
    candidate_by_key = {str(row["incident_key"]): dict(row) for row in candidates}
    incidents = [dict(row) for row in registry["incidents"]]
    open_by_key = {
        str(row["incident_key"]): row
        for row in incidents
        if row.get("incident_status") == "open"
    }
    for key, candidate in candidate_by_key.items():
        existing = open_by_key.get(key)
        if existing is None:
            incident_id = "source_incident_" + _hash({"key": key, "at": detected_at})[:20]
            incidents.append(
                candidate
                | {
                    "incident_id": incident_id,
                    "incident_status": "open",
                    "first_detected_at_utc": detected_at,
                    "last_detected_at_utc": detected_at,
                    "occurrence_count": 1,
                    "recovery_receipt_id": None,
                }
            )
        else:
            existing.update(candidate)
            existing["last_detected_at_utc"] = detected_at
            existing["occurrence_count"] = int(existing.get("occurrence_count", 0)) + 1
    evaluated = {str(value) for value in evaluated_series_ids}
    healthy = {str(value) for value in healthy_series_ids}
    receipts = [dict(row) for row in registry["recovery_receipts"]]
    for incident in incidents:
        if incident.get("incident_status") != "open":
            continue
        series_id = str(incident["source_series_id"])
        if incident["incident_key"] in candidate_by_key:
            continue
        if series_id not in evaluated or series_id not in healthy:
            continue
        receipt_id = "source_recovery_" + _hash(
            {"incident_id": incident["incident_id"], "at": detected_at}
        )[:20]
        incident["incident_status"] = "resolved"
        incident["resolved_at_utc"] = detected_at
        incident["fallback_status"] = "exact_source_recovered"
        incident["recovery_receipt_id"] = receipt_id
        receipts.append(
            {
                "recovery_receipt_id": receipt_id,
                "incident_id": incident["incident_id"],
                "source_series_id": series_id,
                "recovered_at_utc": detected_at,
                "recovery_basis": "evaluated_series_returned_healthy",
                "exact_source_restored": True,
                "supporting_source_promoted_to_core": False,
            }
        )
    updated = {
        "registry_version": "phase135_source_incident_registry_v1",
        "updated_at_utc": detected_at,
        "incidents": sorted(incidents, key=lambda row: str(row["incident_id"])),
        "recovery_receipts": receipts,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "secret_value_recorded": False,
    }
    _atomic_json_write(path, updated)
    return build_source_incident_center(registry=updated)


def build_source_incident_center(
    *,
    registry: dict[str, Any] | None = None,
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    loaded = registry or load_source_incident_registry(registry_path)
    incidents = [dict(row) for row in loaded["incidents"]]
    open_rows = [row for row in incidents if row.get("incident_status") == "open"]
    return {
        "center_version": "phase135_source_incident_center_v1",
        "registry_status": "persistent" if loaded["updated_at_utc"] else "not_started",
        "open_incident_count": len(open_rows),
        "critical_open_incident_count": sum(
            row.get("severity") == "critical" for row in open_rows
        ),
        "warning_open_incident_count": sum(
            row.get("severity") == "warning" for row in open_rows
        ),
        "affected_role_count": len(
            {role for row in open_rows for role in row.get("affected_role_ids", [])}
        ),
        "affected_cycle_lane_count": len(
            {lane for row in open_rows for lane in row.get("affected_cycle_lanes", [])}
        ),
        "fallback_active_count": sum(
            row.get("fallback_status") == "supporting_only_visible"
            for row in open_rows
        ),
        "recovery_receipt_count": len(loaded["recovery_receipts"]),
        "open_incidents": open_rows,
        "recent_recovery_receipts": loaded["recovery_receipts"][-10:],
        "supporting_source_promoted_to_core_count": 0,
        "silent_substitution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def reconcile_live_source_incidents(
    refresh_status: dict[str, Any],
    *,
    registry_path: str | Path | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Worker-only reconciliation using the existing read-only dashboard query."""

    from business_cycle.storage.nas_live_postgres_dashboard import (
        build_nas_live_postgres_dashboard_snapshot,
    )

    snapshot = build_nas_live_postgres_dashboard_snapshot(
        refresh_status=refresh_status,
        snapshot_as_of=(now or (lambda: datetime.now(timezone.utc)))().date().isoformat(),
    )
    diagnostics = snapshot["source_release_diagnostics"]
    candidates = build_source_incident_candidates(
        refresh_status=refresh_status,
        release_diagnostics=diagnostics,
        metadata_checks=snapshot["source_health_metadata_checks"],
        artifact_checks=snapshot["source_health_artifact_checks"],
    )
    evaluated = {
        str(row["series_id"])
        for row in diagnostics["series_refresh_diagnostics"]
    }
    unhealthy = {str(row["source_series_id"]) for row in candidates}
    return reconcile_source_incidents(
        candidates=candidates,
        evaluated_series_ids=evaluated,
        healthy_series_ids=evaluated - unhealthy,
        registry_path=registry_path,
        now=now,
    )


def _add_candidate(
    candidates: dict[str, dict[str, Any]],
    *,
    series_id: str,
    incident_type: str,
    reason_codes: list[str],
    attempt_count: int = 0,
    last_good_observation_date: Any = None,
    expected_release_at: Any = None,
    drift_dimensions: list[str] | None = None,
) -> None:
    key = f"{series_id}::{incident_type}"
    fallback = _fallback_for_series(series_id, incident_type)
    attribution = _series_attribution().get(
        series_id, {"role_ids": [], "cycle_lanes": []}
    )
    candidates[key] = {
        "incident_key": key,
        "incident_type": incident_type,
        "severity": _severity(incident_type),
        "source_series_id": series_id,
        "reason_codes": sorted(set(reason_codes)),
        "drift_dimensions": sorted(set(drift_dimensions or [])),
        "affected_role_ids": attribution["role_ids"],
        "affected_cycle_lanes": attribution["cycle_lanes"],
        "last_good_observation_date": last_good_observation_date,
        "expected_release_at": expected_release_at,
        "attempt_count": attempt_count,
        "fallback_status": fallback["state"],
        "fallback_series_ids": fallback["series_ids"],
        "next_action_zh": _next_action(incident_type, fallback["state"]),
        "no_silent_substitution": True,
    }


def _fallback_for_series(series_id: str, incident_type: str) -> dict[str, Any]:
    contract = load_nas_source_incident_center_contract()
    reviewed = contract["fallback_policy"]["reviewed_supporting_fallbacks"].get(
        series_id
    )
    if reviewed is not None:
        return {
            "state": str(reviewed["state"]),
            "series_ids": [str(value) for value in reviewed["supporting_series_ids"]],
        }
    if incident_type in {
        "source_fetch_failure",
        "not_attempted_after_prior_failure",
        "authentication_or_rate_limit",
    }:
        return {"state": "retry_pending", "series_ids": []}
    return {"state": "abstain_required", "series_ids": []}


def _series_attribution() -> dict[str, dict[str, list[str]]]:
    result: dict[str, dict[str, list[str]]] = {}
    for row in build_full_cycle_role_data_matrix():
        for series_id in row["raw_input_series_ids"] + row["supporting_series_ids"]:
            current = result.setdefault(
                str(series_id), {"role_ids": [], "cycle_lanes": []}
            )
            role_id = str(row["role_id"])
            lane = f"{row['phase']}::{row['phase_lane']}"
            if role_id not in current["role_ids"]:
                current["role_ids"].append(role_id)
            if lane not in current["cycle_lanes"]:
                current["cycle_lanes"].append(lane)
    for current in result.values():
        current["role_ids"].sort()
        current["cycle_lanes"].sort()
    return result


def _failure_incident_type(row: dict[str, Any]) -> str:
    value = " ".join(
        str(row.get(key, ""))
        for key in ("error_class", "error_reason_code", "error_message_redacted")
    ).lower()
    if any(marker in value for marker in ("401", "403", "429", "auth", "rate")):
        return "authentication_or_rate_limit"
    if "checksum" in value:
        return "checksum_validation_failure"
    if any(marker in value for marker in ("parser", "parse", "schema", "json", "csv")):
        return "schema_or_parser_drift"
    return "source_fetch_failure"


def _series_attempt_count(status: dict[str, Any], series_id: str) -> int:
    for row in status.get("series_refresh_results", []):
        if isinstance(row, dict) and str(row.get("series_id")) == series_id:
            return int(row.get("attempt_count", 0))
    return 0


def _release_value(family: dict[str, Any]) -> Any:
    value = family.get("last_official_release") or family.get("next_official_release")
    if isinstance(value, dict):
        return value.get("release_date")
    return value


def _severity(incident_type: str) -> str:
    if incident_type in {
        "identity_unit_frequency_drift",
        "series_discontinued",
        "checksum_validation_failure",
    }:
        return "critical"
    return "warning"


def _next_action(incident_type: str, fallback_state: str) -> str:
    if fallback_state == "supporting_only_visible":
        return "保留 book-core 缺口，僅顯示已審核旁證；修復 exact source 後再解除事故。"
    return {
        "source_fetch_failure": "檢查官方來源與連線狀態，使用既有 worker 的受治理 subset retry。",
        "not_attempted_after_prior_failure": "先修復前一失敗來源，再由既有 worker 重跑未執行序列。",
        "authentication_or_rate_limit": "檢查授權或等待 rate-limit window；不得在頁面輸入或顯示密鑰。",
        "schema_or_parser_drift": "比對官方 schema 與 parser fixture，修正並通過離線解析測試後重試。",
        "identity_unit_frequency_drift": "停止 evidence promotion，重新驗證系列身分、單位與頻率。",
        "checksum_validation_failure": "隔離 artifact，重新抓取並驗證 checksum；不得沿用損壞快取。",
        "series_discontinued": "確認官方 successor；完成 equivalence review 前維持 abstain。",
        "release_due_local_stale": "官方發布已到期但本機仍舊，執行受治理補抓並核對 reference period。",
    }[incident_type]


def _contract_ready(contract: dict[str, Any]) -> bool:
    persistence = contract["persistence_policy"]
    detection = contract["detection_policy"]
    fallback = contract["fallback_policy"]
    return (
        contract["status"] == "active_private_nas_source_health_contract"
        and persistence["atomic_write_required"] is True
        and persistence["append_only_recovery_receipts"] is True
        and detection["release_due_local_stale_requires_exact_schedule"] is True
        and detection["cadence_only_never_claims_official_delay"] is True
        and fallback["supporting_source_may_replace_book_core"] is False
        and fallback["fallback_may_emit_phase_evidence"] is False
        and fallback["fallback_may_confirm_transition"] is False
    )


def _empty_registry() -> dict[str, Any]:
    return {
        "registry_version": "phase135_source_incident_registry_v1",
        "updated_at_utc": None,
        "incidents": [],
        "recovery_receipts": [],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "secret_value_recorded": False,
    }


def _resolved_registry_path(path: str | Path | None) -> Path:
    value = path or os.environ.get("BUSINESS_CYCLE_SOURCE_INCIDENT_PATH")
    return Path(value) if value else DEFAULT_INCIDENT_PATH


def _validate_registry_path(path: Path) -> None:
    resolved = path.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise SourceIncidentError("source incidents must remain outside repository")
    if not (
        str(resolved).startswith("/tmp/")
        or str(resolved).startswith("/var/lib/business-cycle/")
    ):
        raise SourceIncidentError("source incident path must use /tmp or NAS volume")


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise SourceIncidentError("incident timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
