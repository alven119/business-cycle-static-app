"""Validate transition evidence badge renderer contract and safe display models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.transition_evidence_badges import (
    TransitionEvidenceBadgeSchema,
    TransitionEvidenceBadgeSchemaError,
    validate_transition_evidence_badge_object,
)


class TransitionEvidenceRendererContractError(ValueError):
    """Raised when renderer contract or safe display model is invalid."""


@dataclass(frozen=True)
class TransitionEvidenceBadgeRendererContract:
    """Machine-readable transition evidence badge renderer contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    input_contract: dict[str, Any]
    safe_display_model: dict[str, Any]
    level_display_mapping: dict[str, dict[str, dict[str, Any]]]
    required_global_display_caveats_zh: list[str]
    prohibited_text_patterns: dict[str, list[str]]
    dashboard_integration_preconditions: list[str]
    allowed_future_dashboard_sections: list[str]
    disallowed_future_dashboard_sections: list[str]
    recommended_next_phase: dict[str, Any]


def load_transition_evidence_badge_renderer_contract(
    path: str | Path,
) -> TransitionEvidenceBadgeRendererContract:
    """Load and validate transition evidence badge renderer contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise TransitionEvidenceRendererContractError(
            f"Transition evidence badge renderer contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TransitionEvidenceRendererContractError(
            f"Invalid YAML in transition evidence badge renderer contract file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise TransitionEvidenceRendererContractError(
            "Transition evidence badge renderer contract YAML must be a mapping"
        )
    raw = payload.get("transition_evidence_badge_renderer_contract")
    if not isinstance(raw, dict):
        raise TransitionEvidenceRendererContractError(
            "transition_evidence_badge_renderer_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping(raw)
    validate_transition_evidence_badge_renderer_contract(contract)
    return contract


def validate_transition_evidence_badge_renderer_contract(
    contract: TransitionEvidenceBadgeRendererContract,
) -> None:
    """Validate parsed transition evidence badge renderer contract."""

    if not isinstance(contract.version, int):
        raise TransitionEvidenceRendererContractError("version must exist and be an integer")
    if not contract.status:
        raise TransitionEvidenceRendererContractError("status must be non-empty")
    for field_name, value in (
        ("input_contract", contract.input_contract),
        ("safe_display_model", contract.safe_display_model),
        ("level_display_mapping", contract.level_display_mapping),
        ("prohibited_text_patterns", contract.prohibited_text_patterns),
        ("dashboard_integration_preconditions", contract.dashboard_integration_preconditions),
    ):
        if not value:
            raise TransitionEvidenceRendererContractError(f"{field_name} must be non-empty")

    _validate_forbidden_display_fields(contract.safe_display_model)
    _validate_required_caveats(contract.required_global_display_caveats_zh)
    _validate_prohibited_text_patterns(contract.prohibited_text_patterns)
    _validate_level_display_mapping(contract.level_display_mapping)

    if str(contract.recommended_next_phase.get("phase_id") or "") != "7G4":
        raise TransitionEvidenceRendererContractError("recommended_next_phase.phase_id must be 7G4")


def build_safe_badge_display_model(
    badge: dict[str, Any],
    schema: TransitionEvidenceBadgeSchema,
    contract: TransitionEvidenceBadgeRendererContract,
) -> dict[str, Any]:
    """Build a safe renderer display model for one validated transition evidence badge."""

    try:
        validate_transition_evidence_badge_object(badge, schema)
    except TransitionEvidenceBadgeSchemaError as exc:
        raise TransitionEvidenceRendererContractError(f"badge invalid: {exc}") from exc

    display_spec = contract.safe_display_model
    output_fields = set(_str_list(display_spec["required_fields"], "required_fields"))
    output_fields.update(_str_list(display_spec["optional_display_fields"], "optional_display_fields"))
    forbidden_fields = set(_str_list(display_spec["forbidden_display_fields"], "forbidden_display_fields"))

    display_model: dict[str, Any] = {
        field: badge[field]
        for field in output_fields
        if field in badge and field not in forbidden_fields
    }
    family_id = str(badge["family_id"])
    level = str(badge["level"])
    mapping = contract.level_display_mapping[family_id][level]
    caveat_parts = [*contract.required_global_display_caveats_zh, *_str_list(badge["caveats_zh"], "caveats_zh")]
    required_suffix = str(mapping.get("required_suffix_zh") or "")
    if required_suffix:
        caveat_parts.append(required_suffix)

    display_model.update(
        {
            "badge_css_class": f"evidence-badge evidence-badge--{family_id} evidence-badge--{level}",
            "badge_level_label_zh": str(mapping["label_zh"]),
            "badge_family_label_zh": str(badge["display_name_zh"]),
            "display_caveat_summary_zh": " ".join(dict.fromkeys(caveat_parts)),
        }
    )
    validate_safe_badge_display_model(display_model, contract)
    return display_model


def validate_safe_badge_display_model(
    display_model: dict[str, Any],
    contract: TransitionEvidenceBadgeRendererContract,
) -> None:
    """Validate a renderer-safe transition evidence badge display model."""

    forbidden_fields = set(
        _str_list(
            contract.safe_display_model["forbidden_display_fields"],
            "safe_display_model.forbidden_display_fields",
        )
    )
    present_forbidden = sorted(forbidden_fields & set(display_model))
    if present_forbidden:
        raise TransitionEvidenceRendererContractError(
            f"display model contains forbidden field(s): {', '.join(present_forbidden)}"
        )
    if display_model.get("diagnostics_only") is not True:
        raise TransitionEvidenceRendererContractError("display model diagnostics_only must be true")
    if str(display_model.get("formal_decision_impact")) != "none":
        raise TransitionEvidenceRendererContractError(
            "display model formal_decision_impact must be none"
        )

    caveat_summary = str(display_model.get("display_caveat_summary_zh") or "")
    for required in contract.required_global_display_caveats_zh:
        if required not in caveat_summary:
            raise TransitionEvidenceRendererContractError(
                f"display model caveat summary missing required caveat: {required}"
            )

    for field, value in display_model.items():
        if field in {"display_caveat_summary_zh", "caveats_zh", "badge_level_label_zh"}:
            continue
        for text in _iter_strings(value):
            _raise_if_prohibited_text(text, contract.prohibited_text_patterns, field)


def _contract_from_mapping(payload: dict[str, Any]) -> TransitionEvidenceBadgeRendererContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "input_contract",
        "safe_display_model",
        "level_display_mapping",
        "required_global_display_caveats_zh",
        "prohibited_text_patterns",
        "dashboard_integration_preconditions",
        "allowed_future_dashboard_sections",
        "disallowed_future_dashboard_sections",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise TransitionEvidenceRendererContractError(
            "transition_evidence_badge_renderer_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return TransitionEvidenceBadgeRendererContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        input_contract=_mapping(payload["input_contract"], "input_contract"),
        safe_display_model=_mapping(payload["safe_display_model"], "safe_display_model"),
        level_display_mapping=_nested_mapping(
            payload["level_display_mapping"],
            "level_display_mapping",
        ),
        required_global_display_caveats_zh=_str_list(
            payload["required_global_display_caveats_zh"],
            "required_global_display_caveats_zh",
        ),
        prohibited_text_patterns=_mapping_of_str_lists(
            payload["prohibited_text_patterns"],
            "prohibited_text_patterns",
        ),
        dashboard_integration_preconditions=_str_list(
            payload["dashboard_integration_preconditions"],
            "dashboard_integration_preconditions",
        ),
        allowed_future_dashboard_sections=_str_list(
            payload["allowed_future_dashboard_sections"],
            "allowed_future_dashboard_sections",
        ),
        disallowed_future_dashboard_sections=_str_list(
            payload["disallowed_future_dashboard_sections"],
            "disallowed_future_dashboard_sections",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_forbidden_display_fields(display_model: dict[str, Any]) -> None:
    forbidden = set(
        _str_list(
            display_model.get("forbidden_display_fields"),
            "safe_display_model.forbidden_display_fields",
        )
    )
    required = {
        "buy_signal",
        "sell_signal",
        "allocation",
        "target_weight",
        "current_phase_override",
        "decision_status_override",
    }
    missing = sorted(required - forbidden)
    if missing:
        raise TransitionEvidenceRendererContractError(
            f"safe_display_model.forbidden_display_fields missing required field(s): {', '.join(missing)}"
        )


def _validate_required_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise TransitionEvidenceRendererContractError(
            "required_global_display_caveats_zh must include 不構成投資建議"
        )


def _validate_prohibited_text_patterns(patterns: dict[str, list[str]]) -> None:
    zh = set(patterns.get("zh", []))
    en = set(patterns.get("en", []))
    for required in ("買進", "賣出", "加碼", "減碼"):
        if required not in zh:
            raise TransitionEvidenceRendererContractError(
                f"prohibited_text_patterns.zh must include {required}"
            )
    for required in ("buy signal", "sell signal"):
        if required not in en:
            raise TransitionEvidenceRendererContractError(
                f"prohibited_text_patterns.en must include {required}"
            )


def _validate_level_display_mapping(mapping: dict[str, dict[str, dict[str, Any]]]) -> None:
    for family_id, levels in mapping.items():
        for level, level_mapping in levels.items():
            if not str(level_mapping.get("label_zh") or ""):
                raise TransitionEvidenceRendererContractError(f"{family_id}.{level} missing label_zh")
            if not str(level_mapping.get("severity") or ""):
                raise TransitionEvidenceRendererContractError(f"{family_id}.{level} missing severity")


def _raise_if_prohibited_text(
    text: str,
    patterns: dict[str, list[str]],
    field: str,
) -> None:
    normalized = text.lower()
    allowed_negative_phrases = (
        "不是買賣訊號",
        "不是買進訊號",
        "不是賣出訊號",
        "不是減碼",
        "不是加碼",
        "not a buy signal",
        "not a sell signal",
    )
    for pattern in [*patterns.get("zh", []), *patterns.get("en", [])]:
        if pattern.lower() in normalized and not any(
            allowed.lower() in normalized for allowed in allowed_negative_phrases
        ):
            raise TransitionEvidenceRendererContractError(
                f"display model field {field} contains prohibited text pattern: {pattern}"
            )


def _iter_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_iter_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_iter_strings(item))
        return strings
    return []


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TransitionEvidenceRendererContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _nested_mapping(value: Any, field: str) -> dict[str, dict[str, dict[str, Any]]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for key, raw in mapping.items():
        child = _mapping(raw, f"{field}.{key}")
        result[key] = {}
        for child_key, child_raw in child.items():
            result[key][child_key] = _mapping(child_raw, f"{field}.{key}.{child_key}")
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TransitionEvidenceRendererContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise TransitionEvidenceRendererContractError(f"{field} must not contain empty items")
    return result
