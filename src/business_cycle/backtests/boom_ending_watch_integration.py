"""Load and validate boom-ending watch integration guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BoomEndingWatchIntegrationGuardrailsError(ValueError):
    """Raised when boom-ending watch integration guardrails are invalid."""


@dataclass(frozen=True)
class BoomEndingWatchIntegrationGuardrails:
    """Machine-readable guardrails for future boom-ending watch integration."""

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


def load_boom_ending_watch_integration_guardrails(
    path: str | Path,
) -> BoomEndingWatchIntegrationGuardrails:
    """Load and validate boom-ending watch integration guardrails YAML."""

    payload = _load_yaml_mapping(path)
    raw = payload.get("boom_ending_watch_integration_guardrails")
    if not isinstance(raw, dict):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "boom_ending_watch_integration_guardrails YAML must contain a "
            "boom_ending_watch_integration_guardrails mapping"
        )
    guardrails = _guardrails_from_mapping(raw)
    validate_boom_ending_watch_integration_guardrails(guardrails)
    return guardrails


def validate_boom_ending_watch_integration_guardrails(
    guardrails: BoomEndingWatchIntegrationGuardrails,
) -> None:
    """Validate parsed boom-ending watch integration guardrails."""

    if not isinstance(guardrails.version, int):
        raise BoomEndingWatchIntegrationGuardrailsError("version must exist and be an integer")
    if not guardrails.status:
        raise BoomEndingWatchIntegrationGuardrailsError("status must be non-empty")
    if not guardrails.evidence_summary:
        raise BoomEndingWatchIntegrationGuardrailsError("evidence_summary must exist")
    if not guardrails.design_conclusion:
        raise BoomEndingWatchIntegrationGuardrailsError("design_conclusion must exist")
    if not guardrails.proposed_future_integration_modes:
        raise BoomEndingWatchIntegrationGuardrailsError("proposed_future_integration_modes must exist")
    if not guardrails.required_acceptance_before_live_integration:
        raise BoomEndingWatchIntegrationGuardrailsError(
            "required_acceptance_before_live_integration must exist"
        )
    if not guardrails.recommended_next_phase:
        raise BoomEndingWatchIntegrationGuardrailsError("recommended_next_phase must exist")
    _validate_caveats(guardrails.caveats_zh)
    _validate_design_conclusion(guardrails.design_conclusion)
    _validate_modes(guardrails.proposed_future_integration_modes)
    _validate_acceptance_targets(guardrails.required_acceptance_before_live_integration)
    _validate_recommended_next_phase(guardrails.recommended_next_phase)


def boom_ending_integration_mode_allowed(
    guardrails: BoomEndingWatchIntegrationGuardrails,
    mode_id: str,
) -> bool:
    """Return whether a boom-ending integration mode is allowed now."""

    for mode in guardrails.proposed_future_integration_modes:
        if mode.get("mode_id") == mode_id:
            return bool(mode.get("allowed_now", False))
    return False


def _guardrails_from_mapping(payload: dict[str, Any]) -> BoomEndingWatchIntegrationGuardrails:
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
        raise BoomEndingWatchIntegrationGuardrailsError(
            "boom_ending_watch_integration_guardrails missing required field(s): "
            f"{', '.join(missing)}"
        )
    if not isinstance(payload["evidence_summary"], dict):
        raise BoomEndingWatchIntegrationGuardrailsError("evidence_summary must be a mapping")
    if not isinstance(payload["design_conclusion"], dict):
        raise BoomEndingWatchIntegrationGuardrailsError("design_conclusion must be a mapping")
    if not isinstance(payload["recommended_next_phase"], dict):
        raise BoomEndingWatchIntegrationGuardrailsError("recommended_next_phase must be a mapping")
    return BoomEndingWatchIntegrationGuardrails(
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
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise BoomEndingWatchIntegrationGuardrailsError("caveats_zh must include revised data caveat")
    if not any("不等於 confirmed recession" in caveat for caveat in caveats):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "caveats_zh must state boom ending watch is not confirmed recession"
        )
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "caveats_zh must include no-investment-advice caveat"
        )


def _validate_design_conclusion(design_conclusion: dict[str, dict[str, Any]]) -> None:
    required = (
        "diagnostic_only",
        "transition_risk_boost",
        "direct_recession_confirmation",
        "direct_portfolio_action",
        "portfolio_policy_research_input",
    )
    missing = [key for key in required if key not in design_conclusion]
    if missing:
        raise BoomEndingWatchIntegrationGuardrailsError(
            f"design_conclusion missing required key(s): {', '.join(missing)}"
        )
    if not bool(design_conclusion["diagnostic_only"].get("allowed", False)):
        raise BoomEndingWatchIntegrationGuardrailsError("diagnostic_only must be allowed")
    if bool(design_conclusion["direct_recession_confirmation"].get("allowed", True)):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "direct_recession_confirmation must not be allowed"
        )
    if bool(design_conclusion["direct_portfolio_action"].get("allowed", True)):
        raise BoomEndingWatchIntegrationGuardrailsError("direct_portfolio_action must not be allowed")


def _validate_modes(modes: list[dict[str, Any]]) -> None:
    _require_unique_ids(modes, "mode_id", "proposed_future_integration_modes")
    by_id = {str(mode["mode_id"]): mode for mode in modes}
    for mode_id in (
        "diagnostic_badge_only",
        "transition_risk_boost",
        "portfolio_policy_input",
        "recession_confirmation_gate",
    ):
        if mode_id not in by_id:
            raise BoomEndingWatchIntegrationGuardrailsError(
                f"proposed_future_integration_modes must include {mode_id}"
            )
    if not bool(by_id["diagnostic_badge_only"].get("allowed_now", False)):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "diagnostic_badge_only allowed_now must be true"
        )
    if bool(by_id["recession_confirmation_gate"].get("allowed_now", True)):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "recession_confirmation_gate allowed_now must be false"
        )
    transition_impact = str(by_id["transition_risk_boost"].get("formal_decision_impact", "")).lower()
    if "phase change" in transition_impact and "no phase change" not in transition_impact:
        raise BoomEndingWatchIntegrationGuardrailsError(
            "transition_risk_boost must not change current phase"
        )


def _validate_acceptance_targets(targets: list[dict[str, Any]]) -> None:
    _require_unique_ids(targets, "target_id", "required_acceptance_before_live_integration")
    required_ids = {"watch_not_too_dense", "portfolio_backtest_required"}
    target_ids = {str(target["target_id"]) for target in targets}
    missing = sorted(required_ids - target_ids)
    if missing:
        raise BoomEndingWatchIntegrationGuardrailsError(
            "required_acceptance_before_live_integration missing required target(s): "
            f"{', '.join(missing)}"
        )
    for target in targets:
        if not isinstance(target.get("required"), bool):
            raise BoomEndingWatchIntegrationGuardrailsError(
                "required_acceptance_before_live_integration entries must include bool required"
            )


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if str(next_phase.get("phase_id") or "") != "7F3":
        raise BoomEndingWatchIntegrationGuardrailsError("recommended_next_phase.phase_id must be 7F3")
    if not str(next_phase.get("title") or ""):
        raise BoomEndingWatchIntegrationGuardrailsError("recommended_next_phase must include title")
    if not str(next_phase.get("reason_zh") or ""):
        raise BoomEndingWatchIntegrationGuardrailsError("recommended_next_phase must include reason_zh")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BoomEndingWatchIntegrationGuardrailsError(
            f"Boom ending watch integration guardrails file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BoomEndingWatchIntegrationGuardrailsError(
            f"Invalid YAML in boom ending watch integration guardrails file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise BoomEndingWatchIntegrationGuardrailsError(
            "Boom ending watch integration guardrails YAML must be a mapping"
        )
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BoomEndingWatchIntegrationGuardrailsError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BoomEndingWatchIntegrationGuardrailsError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BoomEndingWatchIntegrationGuardrailsError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise BoomEndingWatchIntegrationGuardrailsError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise BoomEndingWatchIntegrationGuardrailsError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise BoomEndingWatchIntegrationGuardrailsError(
                f"{field} contains duplicate {id_field}: {item_id}"
            )
        seen.add(item_id)
