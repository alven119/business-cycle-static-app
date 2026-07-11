"""Private NAS v1.0 operational acceptance and artifact retention."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_v1_operational_acceptance_contract.yaml"
DEFAULT_RUNBOOK_PATH = ROOT / "docs/nas_v1_operator_runbook.md"
DEFAULT_PHASE125_ROOT = Path("/var/lib/business-cycle/source-artifacts/phase125")
DEFAULT_STATUS_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase126/operational-acceptance.json"
)
CONFIRMATION = "I_CONFIRM_PRIVATE_NAS_V1_OPERATIONAL_ACCEPTANCE"
FORBIDDEN_KEYS = {
    "password",
    "token",
    "database_url",
    "fred_api_key",
    "tailnet_ip",
    "tailnet_dns_name",
}


class NasV1OperationalAcceptanceError(RuntimeError):
    """Raised when operational acceptance evidence is incomplete or unsafe."""


def load_nas_v1_operational_acceptance_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_v1_operational_acceptance_contract"])


def persist_strict_replay_artifact(
    output_path: str | Path,
    artifact: dict[str, Any],
    *,
    retention_root: str | Path | None = None,
) -> dict[str, Any]:
    """Write latest and an immutable checksummed snapshot on the NAS volume."""

    output = Path(output_path)
    persisted = dict(artifact)
    resolved_retention_root = (
        Path(retention_root) if retention_root is not None else DEFAULT_PHASE125_ROOT
    )
    retention_enabled = retention_root is not None or output.resolve().as_posix().startswith(
        DEFAULT_PHASE125_ROOT.as_posix() + "/"
    )
    if retention_enabled:
        generated = str(persisted["generated_at_utc"])
        safe_time = generated.replace(":", "").replace("-", "").replace(".", "")
        safe_time = safe_time.replace("+", "").replace("Z", "Z")
        snapshot_id = f"{safe_time}-{str(persisted['artifact_hash'])[:16]}"
        persisted["retention_snapshot_id"] = snapshot_id
        persisted["retention_policy"] = "immutable_snapshot_no_automatic_delete"
        snapshot = resolved_retention_root / "runs" / f"{snapshot_id}.json"
        if snapshot.exists():
            existing = json.loads(snapshot.read_text(encoding="utf-8"))
            if existing != persisted:
                raise NasV1OperationalAcceptanceError(
                    "immutable strict replay snapshot already exists with different content"
                )
        else:
            _atomic_json_write(snapshot, persisted)
            _atomic_text_write(
                snapshot.with_suffix(".json.sha256"),
                f"{_sha256_file(snapshot)}  {snapshot.name}\n",
            )
    _atomic_json_write(output, persisted)
    return persisted


def build_strict_replay_retention_preview(
    phase125_root: str | Path = DEFAULT_PHASE125_ROOT,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_v1_operational_acceptance_contract(contract_path)
    policy = contract["artifact_retention_policy"]
    run_root = Path(phase125_root) / str(policy["immutable_run_directory"])
    rows: list[dict[str, Any]] = []
    if run_root.is_dir():
        for snapshot in sorted(run_root.glob("*.json"), reverse=True):
            checksum_path = snapshot.with_suffix(".json.sha256")
            payload = _load_json(snapshot)
            checksum_valid = False
            if checksum_path.is_file():
                recorded = checksum_path.read_text(encoding="utf-8").split()[0]
                checksum_valid = recorded == _sha256_file(snapshot)
            state = str(payload.get("result", "unknown"))
            rows.append(
                {
                    "snapshot_id": snapshot.stem,
                    "state": state if state in {"passed", "blocked"} else "unknown",
                    "artifact_hash": payload.get("artifact_hash"),
                    "checksum_valid": checksum_valid,
                }
            )
    succeeded = [row for row in rows if row["state"] == "passed"]
    failed = [row for row in rows if row["state"] == "blocked"]
    unknown = [row for row in rows if row["state"] == "unknown"]
    candidates = (
        succeeded[int(policy["successful_snapshot_keep_count"]) :]
        + failed[int(policy["failed_snapshot_keep_count"]) :]
    )
    return {
        "preview_version": "phase126_strict_replay_retention_v1",
        "immutable_snapshot_count": len(rows),
        "successful_snapshot_count": len(succeeded),
        "failed_snapshot_count": len(failed),
        "unknown_snapshot_count": len(unknown),
        "checksum_valid_snapshot_count": sum(row["checksum_valid"] for row in rows),
        "all_snapshot_checksums_valid": bool(rows)
        and all(row["checksum_valid"] for row in rows),
        "successful_snapshot_keep_count": int(policy["successful_snapshot_keep_count"]),
        "failed_snapshot_keep_count": int(policy["failed_snapshot_keep_count"]),
        "retention_candidate_count": len(candidates),
        "retention_candidate_snapshot_ids": [row["snapshot_id"] for row in candidates],
        "automatic_delete_enabled": False,
        "delete_execution_count": 0,
        "unknown_snapshot_preserved": True,
    }


def build_nas_v1_operational_acceptance(
    *,
    rerun_report: dict[str, Any],
    retention_preview: dict[str, Any],
    backup_restore_status: dict[str, Any],
    rollback_report: dict[str, Any],
    mobile_report: dict[str, Any],
    release_schedule_status: dict[str, Any],
    runbook_path: str | Path = DEFAULT_RUNBOOK_PATH,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_v1_operational_acceptance_contract(contract_path)
    runbook = Path(runbook_path).read_text(encoding="utf-8")
    required_sections = contract["runbook_policy"]["required_sections"]
    runbook_sections = sum(f"## {section}" in runbook for section in required_sections)
    rerun_ready = (
        int(rerun_report.get("execution_count", 0))
        >= int(contract["rerun_policy"]["minimum_execution_count"])
        and rerun_report.get("baseline_artifact_hash")
        == rerun_report.get("rerun_artifact_hash")
        and rerun_report.get("rerun_result") == "passed"
    )
    backup_ready = (
        backup_restore_status.get("backup_restore_state") == "succeeded"
        and backup_restore_status.get("row_count_match") is True
        and backup_restore_status.get("staging_database_dropped") is True
        and _sha256_like(backup_restore_status.get("postgres_backup_checksum"))
        and _sha256_like(backup_restore_status.get("source_artifact_backup_checksum"))
    )
    rollback_ready = (
        rollback_report.get("rollback_executed") is True
        and rollback_report.get("previous_image_health_passed") is True
        and rollback_report.get("forward_image_health_passed") is True
        and rollback_report.get("database_row_count_before")
        == rollback_report.get("database_row_count_after")
        and rollback_report.get("phase125_artifact_hash_before")
        == rollback_report.get("phase125_artifact_hash_after")
        and rollback_report.get("final_image")
        == contract["rollback_policy"]["accepted_image"]
    )
    mobile_ready = (
        mobile_report.get("prior_private_https_acceptance_preserved") is True
        and mobile_report.get("login_route_verified") is True
        and mobile_report.get("dashboard_route_verified") is True
        and mobile_report.get("mobile_viewport_present") is True
        and mobile_report.get("traditional_chinese_navigation_present") is True
        and mobile_report.get("secure_cookie_enabled") is True
        and mobile_report.get("tailscale_funnel_configured") is False
        and mobile_report.get("public_exposure_enabled") is False
    )
    artifact: dict[str, Any] = {
        "artifact_id": "phase126_private_nas_v1_operational_acceptance_v1",
        "artifact_version": contract["version"],
        "phase": 126,
        "generated_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "nas_v1_operational_acceptance_contract_ready": _contract_ready(contract),
        "strict_replay_rerun_verified": rerun_ready,
        "strict_replay_rerun_hash_match": rerun_report.get("baseline_artifact_hash")
        == rerun_report.get("rerun_artifact_hash"),
        "strict_replay_rerun_execution_count": int(
            rerun_report.get("execution_count", 0)
        ),
        "immutable_artifact_retention_ready": int(
            retention_preview.get("immutable_snapshot_count", 0)
        )
        >= 2,
        "retained_snapshot_count": int(
            retention_preview.get("immutable_snapshot_count", 0)
        ),
        "retained_snapshot_checksum_valid": retention_preview.get(
            "all_snapshot_checksums_valid"
        )
        is True,
        "retention_delete_execution_count": int(
            retention_preview.get("delete_execution_count", 0)
        ),
        "backup_restore_drill_passed": backup_ready,
        "backup_restore_row_count_match": backup_restore_status.get(
            "row_count_match"
        )
        is True,
        "backup_restore_staging_database_dropped": backup_restore_status.get(
            "staging_database_dropped"
        )
        is True,
        "backup_restore_verified_table_count": len(
            backup_restore_status.get("live_row_counts", {})
        ),
        "rollback_drill_passed": rollback_ready,
        "rollback_database_continuity_valid": rollback_report.get(
            "database_row_count_before"
        )
        == rollback_report.get("database_row_count_after"),
        "rollback_artifact_continuity_valid": rollback_report.get(
            "phase125_artifact_hash_before"
        )
        == rollback_report.get("phase125_artifact_hash_after"),
        "final_accepted_image_restored": rollback_report.get("final_image")
        == contract["rollback_policy"]["accepted_image"],
        "mobile_private_https_acceptance_preserved": mobile_report.get(
            "prior_private_https_acceptance_preserved"
        )
        is True,
        "mobile_current_routes_verified": mobile_ready,
        "tailscale_funnel_configured": bool(
            mobile_report.get("tailscale_funnel_configured", True)
        ),
        "public_exposure_enabled": bool(
            mobile_report.get("public_exposure_enabled", True)
        ),
        "operator_runbook_ready": runbook_sections == len(required_sections),
        "operator_runbook_section_count": runbook_sections,
        "operator_runbook_hash": hashlib.sha256(runbook.encode()).hexdigest(),
        "source_scheduler_healthy": release_schedule_status.get("scheduler_state")
        in {"scheduled", "running", "succeeded"},
        "nas_v1_operational_acceptance_passed": False,
        "acceptance_status": "blocked",
        "formal_production_validated": False,
        "economic_validation_status": "not_started",
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "secret_value_recorded": False,
        "prohibited_field_count": 0,
        "allowed_uses": [
            "private_nas_v1_operations",
            "operator_health_and_rollback_review",
            "research_service_acceptance",
        ],
        "prohibited_uses": [
            "economic_validation_claim",
            "book_alignment_claim",
            "investment_instruction",
            "public_service_exposure",
        ],
    }
    artifact["prohibited_field_count"] = _recursive_key_count(
        artifact, FORBIDDEN_KEYS
    )
    provisional = dict(artifact)
    provisional["nas_v1_operational_acceptance_passed"] = True
    provisional["acceptance_status"] = contract["acceptance_status"]
    passed = _matches(provisional, contract["hard_gates"])
    artifact["nas_v1_operational_acceptance_passed"] = passed
    artifact["acceptance_status"] = (
        contract["acceptance_status"] if passed else "blocked_operational_evidence"
    )
    artifact["result"] = "passed" if passed else "blocked"
    artifact["artifact_hash"] = _hash_payload(
        {key: artifact[key] for key in sorted(artifact) if key != "generated_at_utc"}
    )
    return artifact


def run_nas_v1_operational_acceptance(
    *,
    confirmation: str | None,
    rerun_report_path: str | Path,
    rollback_report_path: str | Path,
    mobile_report_path: str | Path,
    backup_restore_status_path: str | Path,
    release_schedule_status_path: str | Path,
    phase125_root: str | Path,
    output: str | Path,
) -> dict[str, Any]:
    if confirmation != CONFIRMATION:
        raise NasV1OperationalAcceptanceError(
            "explicit NAS v1 operational acceptance confirmation is required"
        )
    artifact = build_nas_v1_operational_acceptance(
        rerun_report=_load_json(rerun_report_path),
        retention_preview=build_strict_replay_retention_preview(phase125_root),
        backup_restore_status=_load_json(backup_restore_status_path),
        rollback_report=_load_json(rollback_report_path),
        mobile_report=_load_json(mobile_report_path),
        release_schedule_status=_load_json(release_schedule_status_path),
    )
    output_path = _validated_output_path(output)
    _atomic_json_write(output_path, artifact)
    return artifact


def load_nas_v1_operational_acceptance_status(
    path: str | Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.is_file():
        return {
            "result": "not_started",
            "acceptance_status": "not_started",
            "nas_v1_operational_acceptance_passed": False,
            "retained_snapshot_count": 0,
        }
    return _load_json(status_path)


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active_private_nas_v1_research_acceptance"
        and contract["rerun_policy"]["deterministic_artifact_hash_required"] is True
        and contract["artifact_retention_policy"]["automatic_delete_enabled"]
        is False
        and contract["rollback_policy"]["database_continuity_required"] is True
        and contract["mobile_acceptance_policy"]["tailscale_funnel_allowed"] is False
        and contract["output_policy"]["secret_output_allowed"] is False
    )


def _validated_output_path(path: str | Path) -> Path:
    output = Path(path)
    resolved = output.resolve().as_posix()
    if not output.is_absolute() or not (
        resolved.startswith("/tmp/")
        or resolved.startswith(
            "/var/lib/business-cycle/source-artifacts/phase126/"
        )
    ):
        raise NasV1OperationalAcceptanceError(
            "Phase 126 output must be under /tmp or phase126 artifacts"
        )
    return output


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise NasV1OperationalAcceptanceError("operational evidence must be an object")
    return payload


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_like(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(str(key).lower() in prohibited for key in value) + sum(
            _recursive_key_count(item, prohibited) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept", action="store_true")
    parser.add_argument("--confirmation")
    parser.add_argument("--rerun-report", required=True)
    parser.add_argument("--rollback-report", required=True)
    parser.add_argument("--mobile-report", required=True)
    parser.add_argument("--backup-restore-status", required=True)
    parser.add_argument("--release-schedule-status", required=True)
    parser.add_argument("--phase125-root", default=str(DEFAULT_PHASE125_ROOT))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if not args.accept:
        raise NasV1OperationalAcceptanceError("Phase 126 requires --accept")
    artifact = run_nas_v1_operational_acceptance(
        confirmation=args.confirmation,
        rerun_report_path=args.rerun_report,
        rollback_report_path=args.rollback_report,
        mobile_report_path=args.mobile_report,
        backup_restore_status_path=args.backup_restore_status,
        release_schedule_status_path=args.release_schedule_status,
        phase125_root=args.phase125_root,
        output=args.output,
    )
    for key in (
        "result",
        "acceptance_status",
        "strict_replay_rerun_verified",
        "retained_snapshot_count",
        "backup_restore_drill_passed",
        "rollback_drill_passed",
        "mobile_current_routes_verified",
        "nas_v1_operational_acceptance_passed",
    ):
        print(f"{key}={str(artifact[key]).lower()}")
    return 0 if artifact["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
