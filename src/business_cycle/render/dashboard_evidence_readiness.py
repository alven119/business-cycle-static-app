"""Load and validate dashboard evidence integration readiness checklist."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class DashboardEvidenceReadinessError(ValueError):
    """Raised when dashboard evidence integration readiness is invalid."""


@dataclass(frozen=True)
class DashboardEvidenceIntegrationReadiness:
    """Machine-readable dashboard evidence integration readiness checklist."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    artifact_readiness: dict[str, dict[str, Any]]
    validator_readiness: dict[str, dict[str, Any]]
    dashboard_integration_blockers: list[dict[str, Any]]
    allowed_future_work: list[dict[str, Any]]
    required_before_dashboard_wiring: list[dict[str, Any]]
    phase_7g_closure: dict[str, Any]


def load_dashboard_evidence_integration_readiness(
    path: str | Path,
) -> DashboardEvidenceIntegrationReadiness:
    """Load and validate dashboard evidence integration readiness YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise DashboardEvidenceReadinessError(
            f"Dashboard evidence integration readiness file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise DashboardEvidenceReadinessError(
            f"Invalid YAML in dashboard evidence integration readiness file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise DashboardEvidenceReadinessError(
            "Dashboard evidence integration readiness YAML must be a mapping"
        )
    raw = payload.get("dashboard_evidence_integration_readiness")
    if not isinstance(raw, dict):
        raise DashboardEvidenceReadinessError(
            "dashboard_evidence_integration_readiness YAML must contain a mapping"
        )
    readiness = _readiness_from_mapping(raw)
    validate_dashboard_evidence_integration_readiness(readiness)
    return readiness


def validate_dashboard_evidence_integration_readiness(
    readiness: DashboardEvidenceIntegrationReadiness,
) -> None:
    """Validate parsed dashboard evidence integration readiness checklist."""

    if not isinstance(readiness.version, int):
        raise DashboardEvidenceReadinessError("version must exist and be an integer")
    if not readiness.status:
        raise DashboardEvidenceReadinessError("status must be non-empty")
    if not readiness.artifact_readiness:
        raise DashboardEvidenceReadinessError("artifact_readiness must exist")
    if not readiness.validator_readiness:
        raise DashboardEvidenceReadinessError("validator_readiness must exist")
    if not readiness.dashboard_integration_blockers:
        raise DashboardEvidenceReadinessError("dashboard_integration_blockers must exist")
    if not readiness.required_before_dashboard_wiring:
        raise DashboardEvidenceReadinessError("required_before_dashboard_wiring must exist")
    _validate_caveats(readiness.caveats_zh)
    _validate_artifacts(readiness.artifact_readiness)
    _validate_validators(readiness.validator_readiness)
    _validate_blockers(readiness.dashboard_integration_blockers)
    _validate_required_before_wiring(readiness.required_before_dashboard_wiring)
    _validate_phase_closure(readiness.phase_7g_closure)


def summarize_dashboard_evidence_integration_readiness(
    readiness: DashboardEvidenceIntegrationReadiness,
) -> dict[str, Any]:
    """Return a concise machine-readable dashboard evidence readiness summary."""

    active_blockers = [
        blocker
        for blocker in readiness.dashboard_integration_blockers
        if blocker.get("active") is True
    ]
    next_phase = readiness.phase_7g_closure["recommended_next_phase"]
    return {
        "version": readiness.version,
        "status": readiness.status,
        "artifact_count": len(readiness.artifact_readiness),
        "validator_count": len(readiness.validator_readiness),
        "active_blocker_count": len(active_blockers),
        "required_before_dashboard_wiring_count": len(readiness.required_before_dashboard_wiring),
        "phase_7g_closure_status": readiness.phase_7g_closure["status"],
        "dashboard_wiring_allowed_now": False,
        "public_output_allowed_now": False,
        "formal_decision_impact_allowed": False,
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def _readiness_from_mapping(payload: dict[str, Any]) -> DashboardEvidenceIntegrationReadiness:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "artifact_readiness",
        "validator_readiness",
        "dashboard_integration_blockers",
        "allowed_future_work",
        "required_before_dashboard_wiring",
        "phase_7g_closure",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise DashboardEvidenceReadinessError(
            "dashboard_evidence_integration_readiness missing required field(s): "
            f"{', '.join(missing)}"
        )
    return DashboardEvidenceIntegrationReadiness(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        artifact_readiness=_mapping_of_mappings(
            payload["artifact_readiness"],
            "artifact_readiness",
        ),
        validator_readiness=_mapping_of_mappings(
            payload["validator_readiness"],
            "validator_readiness",
        ),
        dashboard_integration_blockers=_list_of_mappings(
            payload["dashboard_integration_blockers"],
            "dashboard_integration_blockers",
        ),
        allowed_future_work=_list_of_mappings(payload["allowed_future_work"], "allowed_future_work"),
        required_before_dashboard_wiring=_list_of_mappings(
            payload["required_before_dashboard_wiring"],
            "required_before_dashboard_wiring",
        ),
        phase_7g_closure=_mapping(payload["phase_7g_closure"], "phase_7g_closure"),
    )


def _validate_caveats(caveats: list[str]) -> None:
    for required in (
        "evidence badge 僅供 diagnostics display",
        "evidence badge 不會改變 current_phase_id",
        "evidence badge 不會改變 decision_status",
        "watch 類訊號不是買賣訊號",
        "不構成投資建議",
    ):
        if not any(required in caveat for caveat in caveats):
            raise DashboardEvidenceReadinessError(f"caveats_zh must include {required}")


def _validate_artifacts(artifacts: dict[str, dict[str, Any]]) -> None:
    required = {
        "cycle_transition_evidence_architecture",
        "transition_evidence_badge_schema",
        "transition_evidence_badge_fixtures",
        "transition_evidence_badge_renderer_contract",
        "transition_evidence_badge_display_fixtures",
    }
    missing = sorted(required - set(artifacts))
    if missing:
        raise DashboardEvidenceReadinessError(
            f"artifact_readiness missing required artifact(s): {', '.join(missing)}"
        )
    for artifact_id in sorted(required):
        artifact = artifacts[artifact_id]
        if artifact.get("required") is not True:
            raise DashboardEvidenceReadinessError(f"{artifact_id}.required must be true")
        if str(artifact.get("expected_status") or "") != "draft":
            raise DashboardEvidenceReadinessError(f"{artifact_id}.expected_status must be draft")
        path = str(artifact.get("path") or "")
        if not path:
            raise DashboardEvidenceReadinessError(f"{artifact_id}.path must be non-empty")
        if not Path(path).exists():
            raise DashboardEvidenceReadinessError(f"{artifact_id}.path does not exist: {path}")


def _validate_validators(validators: dict[str, dict[str, Any]]) -> None:
    required = {
        "badge_schema_summary",
        "badge_fixture_validation",
        "renderer_contract_summary",
        "display_fixture_validation",
    }
    missing = sorted(required - set(validators))
    if missing:
        raise DashboardEvidenceReadinessError(
            f"validator_readiness missing required validator(s): {', '.join(missing)}"
        )
    for validator_id in sorted(required):
        validator = validators[validator_id]
        if validator.get("required") is not True:
            raise DashboardEvidenceReadinessError(f"{validator_id}.required must be true")
        if not str(validator.get("command") or ""):
            raise DashboardEvidenceReadinessError(f"{validator_id}.command must be non-empty")
    for validator_id in ("badge_fixture_validation", "display_fixture_validation"):
        if str(validators[validator_id].get("required_result") or "") != "passed":
            raise DashboardEvidenceReadinessError(f"{validator_id}.required_result must be passed")


def _validate_blockers(blockers: list[dict[str, Any]]) -> None:
    active_by_id = {
        str(blocker.get("blocker_id")): blocker
        for blocker in blockers
        if blocker.get("active") is True
    }
    for blocker_id in (
        "dashboard_renderer_not_wired",
        "generated_site_validation_not_updated",
        "no_phase_decision_impact_allowed",
    ):
        if blocker_id not in active_by_id:
            raise DashboardEvidenceReadinessError(f"{blocker_id} blocker must be active")


def _validate_required_before_wiring(targets: list[dict[str, Any]]) -> None:
    target_ids = {str(target.get("target_id")) for target in targets}
    for target_id in (
        "generated_site_validation_updated",
        "html_text_safety_tests_added",
        "no_formal_decision_impact",
    ):
        if target_id not in target_ids:
            raise DashboardEvidenceReadinessError(
                f"required_before_dashboard_wiring must include {target_id}"
            )


def _validate_phase_closure(closure: dict[str, Any]) -> None:
    if str(closure.get("status") or "") != "ready_to_close_after_validation":
        raise DashboardEvidenceReadinessError(
            "phase_7g_closure.status must be ready_to_close_after_validation"
        )
    next_phase = _mapping(closure.get("recommended_next_phase"), "phase_7g_closure.recommended_next_phase")
    if str(next_phase.get("phase_id") or "") != "8A":
        raise DashboardEvidenceReadinessError("recommended_next_phase.phase_id must be 8A")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DashboardEvidenceReadinessError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise DashboardEvidenceReadinessError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise DashboardEvidenceReadinessError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise DashboardEvidenceReadinessError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise DashboardEvidenceReadinessError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise DashboardEvidenceReadinessError(f"{field} must not contain empty items")
    return result
