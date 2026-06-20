"""Load and validate recovery watch integration guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RecoveryWatchIntegrationGuardrailsError(ValueError):
    """Raised when recovery watch integration guardrails are invalid."""


@dataclass(frozen=True)
class RecoveryWatchIntegrationGuardrails:
    """Machine-readable guardrails for future recovery watch integration."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    evidence_summary: dict[str, Any]
    design_conclusion: dict[str, dict[str, Any]]
    proposed_future_integration_modes: list[dict[str, Any]]
    required_acceptance_before_live_integration: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


def load_recovery_watch_integration_guardrails(
    path: str | Path,
) -> RecoveryWatchIntegrationGuardrails:
    """Load and validate recovery watch integration guardrails YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("recovery_watch_integration_guardrails")
    if not isinstance(raw, dict):
        raise RecoveryWatchIntegrationGuardrailsError(
            "recovery_watch_integration_guardrails YAML must contain a mapping"
        )
    guardrails = _guardrails_from_mapping(raw)
    validate_recovery_watch_integration_guardrails(guardrails)
    return guardrails


def validate_recovery_watch_integration_guardrails(
    guardrails: RecoveryWatchIntegrationGuardrails,
) -> None:
    """Validate parsed recovery watch integration guardrails."""

    if not isinstance(guardrails.version, int):
        raise RecoveryWatchIntegrationGuardrailsError("version must exist and be an integer")
    if not guardrails.status:
        raise RecoveryWatchIntegrationGuardrailsError("status must be non-empty")
    if not guardrails.evidence_summary:
        raise RecoveryWatchIntegrationGuardrailsError("evidence_summary must exist")
    if not guardrails.design_conclusion:
        raise RecoveryWatchIntegrationGuardrailsError("design_conclusion must exist")
    if not guardrails.proposed_future_integration_modes:
        raise RecoveryWatchIntegrationGuardrailsError("proposed_future_integration_modes must exist")
    if not guardrails.required_acceptance_before_live_integration:
        raise RecoveryWatchIntegrationGuardrailsError(
            "required_acceptance_before_live_integration must exist"
        )
    if not guardrails.recommended_next_phase:
        raise RecoveryWatchIntegrationGuardrailsError("recommended_next_phase must exist")
    _validate_caveats(guardrails.caveats_zh)
    _validate_design_conclusion(guardrails.design_conclusion)
    _validate_modes(guardrails.proposed_future_integration_modes)
    _validate_acceptance_targets(guardrails.required_acceptance_before_live_integration)
    _validate_recommended_next_phase(guardrails.recommended_next_phase)


def recovery_watch_integration_mode_allowed(
    guardrails: RecoveryWatchIntegrationGuardrails,
    mode_id: str,
) -> bool:
    """Return whether a recovery watch integration mode is allowed now."""

    for mode in guardrails.proposed_future_integration_modes:
        if mode.get("mode_id") == mode_id:
            return bool(mode.get("allowed_now", False))
    return False


def _guardrails_from_mapping(payload: dict[str, Any]) -> RecoveryWatchIntegrationGuardrails:
    required = (
        "version",
        "status",
        "data_mode",
        "objective_zh",
        "caveats_zh",
        "evidence_summary",
        "design_conclusion",
        "proposed_future_integration_modes",
        "required_acceptance_before_live_integration",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise RecoveryWatchIntegrationGuardrailsError(
            "recovery_watch_integration_guardrails missing required field(s): "
            f"{', '.join(missing)}"
        )
    if not isinstance(payload["evidence_summary"], dict):
        raise RecoveryWatchIntegrationGuardrailsError("evidence_summary must be a mapping")
    if not isinstance(payload["design_conclusion"], dict):
        raise RecoveryWatchIntegrationGuardrailsError("design_conclusion must be a mapping")
    if not isinstance(payload["recommended_next_phase"], dict):
        raise RecoveryWatchIntegrationGuardrailsError("recommended_next_phase must be a mapping")
    return RecoveryWatchIntegrationGuardrails(
        version=int(payload["version"]),
        status=str(payload["status"]),
        data_mode=str(payload["data_mode"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        evidence_summary=payload["evidence_summary"],
        design_conclusion={
            str(key): value
            for key, value in payload["design_conclusion"].items()
            if isinstance(value, dict)
        },
        proposed_future_integration_modes=_list_of_mappings(
            payload["proposed_future_integration_modes"],
            "proposed_future_integration_modes",
        ),
        required_acceptance_before_live_integration=_list_of_mappings(
            payload["required_acceptance_before_live_integration"],
            "required_acceptance_before_live_integration",
        ),
        recommended_next_phase=payload["recommended_next_phase"],
    )


def _validate_caveats(caveats: list[str]) -> None:
    for required in [
        "修訂後歷史資料",
        "recovery watch 不等於正式復甦確認",
        "recovery watch 不是買進訊號",
        "不構成投資建議",
    ]:
        if not any(required in caveat for caveat in caveats):
            raise RecoveryWatchIntegrationGuardrailsError(f"caveats_zh must include {required}")


def _validate_design_conclusion(design_conclusion: dict[str, dict[str, Any]]) -> None:
    required = (
        "diagnostic_only",
        "recovery_evidence_display",
        "transition_risk_adjustment",
        "direct_recovery_confirmation",
        "direct_portfolio_action",
        "portfolio_policy_research_input",
    )
    missing = [key for key in required if key not in design_conclusion]
    if missing:
        raise RecoveryWatchIntegrationGuardrailsError(
            f"design_conclusion missing required key(s): {', '.join(missing)}"
        )
    if not bool(design_conclusion["diagnostic_only"].get("allowed", False)):
        raise RecoveryWatchIntegrationGuardrailsError("diagnostic_only must be allowed")
    if bool(design_conclusion["direct_recovery_confirmation"].get("allowed", True)):
        raise RecoveryWatchIntegrationGuardrailsError(
            "direct_recovery_confirmation must not be allowed"
        )
    if bool(design_conclusion["direct_portfolio_action"].get("allowed", True)):
        raise RecoveryWatchIntegrationGuardrailsError("direct_portfolio_action must not be allowed")
    if not bool(design_conclusion["portfolio_policy_research_input"].get("allowed", False)):
        raise RecoveryWatchIntegrationGuardrailsError("portfolio_policy_research_input must be allowed")


def _validate_modes(modes: list[dict[str, Any]]) -> None:
    _require_unique_ids(modes, "mode_id", "proposed_future_integration_modes")
    by_id = {str(mode["mode_id"]): mode for mode in modes}
    for mode_id in (
        "diagnostic_badge_only",
        "recovery_evidence_display",
        "transition_evidence_input",
        "portfolio_policy_input",
        "recovery_confirmation_trigger",
        "buy_signal",
    ):
        if mode_id not in by_id:
            raise RecoveryWatchIntegrationGuardrailsError(
                f"proposed_future_integration_modes must include {mode_id}"
            )
    if not bool(by_id["diagnostic_badge_only"].get("allowed_now", False)):
        raise RecoveryWatchIntegrationGuardrailsError(
            "diagnostic_badge_only allowed_now must be true"
        )
    for mode_id in ("recovery_confirmation_trigger", "buy_signal"):
        if bool(by_id[mode_id].get("allowed_now", True)):
            raise RecoveryWatchIntegrationGuardrailsError(f"{mode_id} allowed_now must be false")


def _validate_acceptance_targets(targets: list[dict[str, Any]]) -> None:
    _require_unique_ids(targets, "target_id", "required_acceptance_before_live_integration")
    required_ids = {
        "recovery_watch_not_formal_confirmation",
        "no_direct_buy_signal",
        "portfolio_backtest_required",
    }
    target_ids = {str(target["target_id"]) for target in targets}
    missing = sorted(required_ids - target_ids)
    if missing:
        raise RecoveryWatchIntegrationGuardrailsError(
            "required_acceptance_before_live_integration missing required target(s): "
            f"{', '.join(missing)}"
        )
    for target in targets:
        if not isinstance(target.get("required"), bool):
            raise RecoveryWatchIntegrationGuardrailsError(
                "required_acceptance_before_live_integration entries must include bool required"
            )


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if str(next_phase.get("phase_id") or "") != "7G":
        raise RecoveryWatchIntegrationGuardrailsError("recommended_next_phase.phase_id must be 7G")
    if not str(next_phase.get("title") or ""):
        raise RecoveryWatchIntegrationGuardrailsError("recommended_next_phase must include title")
    if not str(next_phase.get("reason_zh") or ""):
        raise RecoveryWatchIntegrationGuardrailsError("recommended_next_phase must include reason_zh")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise RecoveryWatchIntegrationGuardrailsError(
            f"Recovery watch integration guardrails file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RecoveryWatchIntegrationGuardrailsError(
            f"Invalid YAML in recovery watch integration guardrails file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RecoveryWatchIntegrationGuardrailsError(
            "Recovery watch integration guardrails YAML must be a mapping"
        )
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RecoveryWatchIntegrationGuardrailsError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise RecoveryWatchIntegrationGuardrailsError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise RecoveryWatchIntegrationGuardrailsError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise RecoveryWatchIntegrationGuardrailsError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise RecoveryWatchIntegrationGuardrailsError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise RecoveryWatchIntegrationGuardrailsError(
                f"{field} contains duplicate {id_field}: {item_id}"
            )
        seen.add(item_id)
