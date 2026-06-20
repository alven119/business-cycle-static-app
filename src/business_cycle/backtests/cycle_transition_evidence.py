"""Load and validate cycle transition evidence architecture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CycleTransitionEvidenceArchitectureError(ValueError):
    """Raised when cycle transition evidence architecture is invalid."""


@dataclass(frozen=True)
class CycleTransitionEvidenceArchitecture:
    """Machine-readable cycle transition evidence architecture."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    evidence_families: dict[str, dict[str, Any]]
    unified_evidence_outputs: dict[str, dict[str, Any]]
    dashboard_diagnostics_contract: dict[str, Any]
    future_transition_risk_contract: dict[str, Any]
    future_portfolio_policy_contract: dict[str, Any]
    required_acceptance_before_dashboard_integration: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


def load_cycle_transition_evidence_architecture(
    path: str | Path,
) -> CycleTransitionEvidenceArchitecture:
    """Load and validate cycle transition evidence architecture YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("cycle_transition_evidence_architecture")
    if not isinstance(raw, dict):
        raise CycleTransitionEvidenceArchitectureError(
            "cycle_transition_evidence_architecture YAML must contain a mapping"
        )
    architecture = _architecture_from_mapping(raw)
    validate_cycle_transition_evidence_architecture(architecture)
    return architecture


def validate_cycle_transition_evidence_architecture(
    architecture: CycleTransitionEvidenceArchitecture,
) -> None:
    """Validate parsed cycle transition evidence architecture."""

    if not isinstance(architecture.version, int):
        raise CycleTransitionEvidenceArchitectureError("version must exist and be an integer")
    if not architecture.status:
        raise CycleTransitionEvidenceArchitectureError("status must be non-empty")
    _validate_caveats(architecture.caveats_zh)
    _validate_evidence_families(architecture.evidence_families)
    _validate_unified_outputs(architecture.unified_evidence_outputs)
    _validate_dashboard_contract(architecture.dashboard_diagnostics_contract)
    _validate_future_contracts(
        architecture.future_transition_risk_contract,
        architecture.future_portfolio_policy_contract,
    )
    _validate_recommended_next_phase(architecture.recommended_next_phase)


def _architecture_from_mapping(payload: dict[str, Any]) -> CycleTransitionEvidenceArchitecture:
    required = (
        "version",
        "status",
        "data_mode",
        "objective_zh",
        "caveats_zh",
        "evidence_families",
        "unified_evidence_outputs",
        "dashboard_diagnostics_contract",
        "future_transition_risk_contract",
        "future_portfolio_policy_contract",
        "required_acceptance_before_dashboard_integration",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise CycleTransitionEvidenceArchitectureError(
            "cycle_transition_evidence_architecture missing required field(s): "
            f"{', '.join(missing)}"
        )
    return CycleTransitionEvidenceArchitecture(
        version=int(payload["version"]),
        status=str(payload["status"]),
        data_mode=str(payload["data_mode"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        evidence_families=_mapping_of_mappings(payload["evidence_families"], "evidence_families"),
        unified_evidence_outputs=_mapping_of_mappings(
            payload["unified_evidence_outputs"],
            "unified_evidence_outputs",
        ),
        dashboard_diagnostics_contract=_mapping(
            payload["dashboard_diagnostics_contract"],
            "dashboard_diagnostics_contract",
        ),
        future_transition_risk_contract=_mapping(
            payload["future_transition_risk_contract"],
            "future_transition_risk_contract",
        ),
        future_portfolio_policy_contract=_mapping(
            payload["future_portfolio_policy_contract"],
            "future_portfolio_policy_contract",
        ),
        required_acceptance_before_dashboard_integration=_list_of_mappings(
            payload["required_acceptance_before_dashboard_integration"],
            "required_acceptance_before_dashboard_integration",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_caveats(caveats: list[str]) -> None:
    for required in ["修訂後歷史資料", "watch 類訊號不是買賣訊號", "不構成投資建議"]:
        if not any(required in caveat for caveat in caveats):
            raise CycleTransitionEvidenceArchitectureError(f"caveats_zh must include {required}")


def _validate_evidence_families(families: dict[str, dict[str, Any]]) -> None:
    required_families = {"recession_confirmation", "boom_ending_watch", "recovery_watch"}
    missing = sorted(required_families - set(families))
    if missing:
        raise CycleTransitionEvidenceArchitectureError(
            f"evidence_families missing required family/families: {', '.join(missing)}"
        )
    for family_id in sorted(required_families):
        family = families[family_id]
        for field in ("allowed_uses", "prohibited_uses", "required_guardrails"):
            if field not in family:
                raise CycleTransitionEvidenceArchitectureError(f"{family_id} missing {field}")
        allowed = _mapping(family["allowed_uses"], f"{family_id}.allowed_uses")
        if bool(allowed.get("formal_phase_confirmation", True)):
            raise CycleTransitionEvidenceArchitectureError(
                f"{family_id}.allowed_uses.formal_phase_confirmation must be false"
            )
        if bool(allowed.get("direct_portfolio_action", True)):
            raise CycleTransitionEvidenceArchitectureError(
                f"{family_id}.allowed_uses.direct_portfolio_action must be false"
            )
        _non_empty_str_list(family["prohibited_uses"], f"{family_id}.prohibited_uses")
        _non_empty_str_list(family["required_guardrails"], f"{family_id}.required_guardrails")


def _validate_unified_outputs(outputs: dict[str, dict[str, Any]]) -> None:
    for required in (
        "evidence_badge",
        "transition_risk_research",
        "portfolio_policy_research",
        "formal_phase_change",
        "direct_trade_signal",
    ):
        if required not in outputs:
            raise CycleTransitionEvidenceArchitectureError(
                f"unified_evidence_outputs missing {required}"
            )
    if bool(outputs["formal_phase_change"].get("allowed_now", True)):
        raise CycleTransitionEvidenceArchitectureError(
            "unified_evidence_outputs.formal_phase_change.allowed_now must be false"
        )
    if bool(outputs["direct_trade_signal"].get("allowed_now", True)):
        raise CycleTransitionEvidenceArchitectureError(
            "unified_evidence_outputs.direct_trade_signal.allowed_now must be false"
        )


def _validate_dashboard_contract(contract: dict[str, Any]) -> None:
    if bool(contract.get("allowed_now", True)):
        raise CycleTransitionEvidenceArchitectureError("dashboard_diagnostics_contract.allowed_now must be false")
    caveats = _non_empty_str_list(
        contract.get("required_display_caveats_zh"),
        "dashboard_diagnostics_contract.required_display_caveats_zh",
    )
    if not any("watch 不是買賣訊號" in caveat for caveat in caveats):
        raise CycleTransitionEvidenceArchitectureError(
            "dashboard_diagnostics_contract required caveats must include watch not trade signal"
        )
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CycleTransitionEvidenceArchitectureError(
            "dashboard_diagnostics_contract required caveats must include no-investment-advice caveat"
        )


def _validate_future_contracts(
    transition_contract: dict[str, Any],
    portfolio_contract: dict[str, Any],
) -> None:
    if bool(transition_contract.get("allowed_now", True)):
        raise CycleTransitionEvidenceArchitectureError("future_transition_risk_contract.allowed_now must be false")
    if bool(portfolio_contract.get("allowed_now", True)):
        raise CycleTransitionEvidenceArchitectureError("future_portfolio_policy_contract.allowed_now must be false")


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if str(next_phase.get("phase_id") or "") != "7G1":
        raise CycleTransitionEvidenceArchitectureError("recommended_next_phase.phase_id must be 7G1")
    if not str(next_phase.get("title") or ""):
        raise CycleTransitionEvidenceArchitectureError("recommended_next_phase must include title")
    if not str(next_phase.get("reason_zh") or ""):
        raise CycleTransitionEvidenceArchitectureError("recommended_next_phase must include reason_zh")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CycleTransitionEvidenceArchitectureError(
            f"Cycle transition evidence architecture file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CycleTransitionEvidenceArchitectureError(
            f"Invalid YAML in cycle transition evidence architecture file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise CycleTransitionEvidenceArchitectureError(
            "Cycle transition evidence architecture YAML must be a mapping"
        )
    return payload


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CycleTransitionEvidenceArchitectureError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise CycleTransitionEvidenceArchitectureError(f"{field}.{key} must be a mapping")
        result[key] = raw
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CycleTransitionEvidenceArchitectureError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise CycleTransitionEvidenceArchitectureError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CycleTransitionEvidenceArchitectureError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CycleTransitionEvidenceArchitectureError(f"{field} entries must be non-empty")
    return items
