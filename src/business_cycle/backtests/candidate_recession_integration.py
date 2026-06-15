"""Load and validate candidate recession integration design specs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class CandidateRecessionIntegrationDesignError(ValueError):
    """Raised when a candidate recession integration design is invalid."""


@dataclass(frozen=True)
class CandidateRecessionIntegrationDesign:
    """Machine-readable guardrails for future candidate recession integration."""

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


def load_candidate_recession_integration_design(
    path: str | Path,
) -> CandidateRecessionIntegrationDesign:
    """Load and validate candidate recession integration design YAML."""

    payload = _load_yaml_mapping(path)
    design = payload.get("candidate_recession_integration_design")
    if not isinstance(design, dict):
        raise CandidateRecessionIntegrationDesignError(
            "candidate_recession_integration_design YAML must contain a "
            "candidate_recession_integration_design mapping"
        )
    parsed = _design_from_mapping(design)
    validate_candidate_recession_integration_design(parsed)
    return parsed


def validate_candidate_recession_integration_design(
    design: CandidateRecessionIntegrationDesign,
) -> None:
    """Validate a parsed candidate recession integration design."""

    if not isinstance(design.version, int):
        raise CandidateRecessionIntegrationDesignError("version must exist and be an integer")
    if not design.status:
        raise CandidateRecessionIntegrationDesignError("status must be non-empty")
    if not design.evidence_summary:
        raise CandidateRecessionIntegrationDesignError("evidence_summary must exist")
    if not design.design_conclusion:
        raise CandidateRecessionIntegrationDesignError("design_conclusion must exist")
    if not design.proposed_future_integration_modes:
        raise CandidateRecessionIntegrationDesignError(
            "proposed_future_integration_modes must exist"
        )
    if not design.required_acceptance_before_live_integration:
        raise CandidateRecessionIntegrationDesignError(
            "required_acceptance_before_live_integration must exist"
        )
    if not design.recommended_next_phase:
        raise CandidateRecessionIntegrationDesignError("recommended_next_phase must exist")
    _validate_caveats(design.caveats_zh)
    _validate_design_conclusion(design.design_conclusion)
    _validate_modes(design.proposed_future_integration_modes)
    _validate_acceptance_targets(design.required_acceptance_before_live_integration)
    _validate_recommended_next_phase(design.recommended_next_phase)


def integration_mode_allowed(
    design: CandidateRecessionIntegrationDesign,
    mode_id: str,
) -> bool:
    """Return whether an integration mode is allowed now."""

    for mode in design.proposed_future_integration_modes:
        if mode.get("mode_id") == mode_id:
            return bool(mode.get("allowed_now", False))
    return False


def _design_from_mapping(payload: dict[str, Any]) -> CandidateRecessionIntegrationDesign:
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
        raise CandidateRecessionIntegrationDesignError(
            "candidate_recession_integration_design missing required field(s): "
            f"{', '.join(missing)}"
        )
    evidence_summary = payload["evidence_summary"]
    design_conclusion = payload["design_conclusion"]
    recommended_next_phase = payload["recommended_next_phase"]
    if not isinstance(evidence_summary, dict):
        raise CandidateRecessionIntegrationDesignError("evidence_summary must be a mapping")
    if not isinstance(design_conclusion, dict):
        raise CandidateRecessionIntegrationDesignError("design_conclusion must be a mapping")
    if not isinstance(recommended_next_phase, dict):
        raise CandidateRecessionIntegrationDesignError("recommended_next_phase must be a mapping")
    return CandidateRecessionIntegrationDesign(
        version=int(payload["version"]),
        status=str(payload["status"]),
        data_mode=str(payload["data_mode"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        evidence_summary=evidence_summary,
        design_conclusion={
            str(key): value
            for key, value in design_conclusion.items()
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
        recommended_next_phase=recommended_next_phase,
    )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("修訂後歷史資料" in caveat for caveat in caveats):
        raise CandidateRecessionIntegrationDesignError(
            "caveats_zh must include revised data caveat"
        )
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise CandidateRecessionIntegrationDesignError(
            "caveats_zh must include no-investment-advice caveat"
        )


def _validate_design_conclusion(design_conclusion: dict[str, dict[str, Any]]) -> None:
    required = (
        "hard_gate_candidate_status_confirmed_only",
        "soft_filter_with_watch_persistence",
        "diagnostic_layer_only",
    )
    missing = [key for key in required if key not in design_conclusion]
    if missing:
        raise CandidateRecessionIntegrationDesignError(
            f"design_conclusion missing required key(s): {', '.join(missing)}"
        )
    hard_gate = design_conclusion["hard_gate_candidate_status_confirmed_only"]
    if bool(hard_gate.get("allowed", True)):
        raise CandidateRecessionIntegrationDesignError("hard gate integration must not be allowed now")
    if not bool(design_conclusion["soft_filter_with_watch_persistence"].get("allowed", False)):
        raise CandidateRecessionIntegrationDesignError("soft filter integration must be allowed as a design path")
    if not bool(design_conclusion["diagnostic_layer_only"].get("allowed", False)):
        raise CandidateRecessionIntegrationDesignError("diagnostic-only integration must be allowed")


def _validate_modes(modes: list[dict[str, Any]]) -> None:
    _require_unique_ids(modes, "mode_id", "proposed_future_integration_modes")
    mode_by_id = {str(mode["mode_id"]): mode for mode in modes}
    hard_gate = mode_by_id.get("hard_confirmation_gate")
    if hard_gate is None:
        raise CandidateRecessionIntegrationDesignError(
            "proposed_future_integration_modes must include hard_confirmation_gate"
        )
    if bool(hard_gate.get("allowed_now", True)):
        raise CandidateRecessionIntegrationDesignError("hard_confirmation_gate allowed_now must be false")
    for mode_id in ("diagnostic_only", "soft_confirmation_filter"):
        if mode_id not in mode_by_id:
            raise CandidateRecessionIntegrationDesignError(
                f"proposed_future_integration_modes must include {mode_id}"
            )


def _validate_acceptance_targets(targets: list[dict[str, Any]]) -> None:
    _require_unique_ids(targets, "target_id", "required_acceptance_before_live_integration")
    for target in targets:
        if not isinstance(target.get("required"), bool):
            raise CandidateRecessionIntegrationDesignError(
                "required_acceptance_before_live_integration entries must include bool required"
            )


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if not str(next_phase.get("phase_id") or ""):
        raise CandidateRecessionIntegrationDesignError("recommended_next_phase must include phase_id")
    if not str(next_phase.get("title") or ""):
        raise CandidateRecessionIntegrationDesignError("recommended_next_phase must include title")
    if not str(next_phase.get("reason_zh") or ""):
        raise CandidateRecessionIntegrationDesignError("recommended_next_phase must include reason_zh")


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CandidateRecessionIntegrationDesignError(
            f"Candidate recession integration design file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateRecessionIntegrationDesignError(
            f"Invalid YAML in candidate recession integration design file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise CandidateRecessionIntegrationDesignError(
            "Candidate recession integration design YAML must be a mapping"
        )
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionIntegrationDesignError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise CandidateRecessionIntegrationDesignError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CandidateRecessionIntegrationDesignError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CandidateRecessionIntegrationDesignError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise CandidateRecessionIntegrationDesignError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise CandidateRecessionIntegrationDesignError(
                f"{field} contains duplicate {id_field}: {item_id}"
            )
        seen.add(item_id)
