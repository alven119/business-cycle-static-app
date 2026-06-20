"""Load and validate transition evidence badge schema and badge objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class TransitionEvidenceBadgeSchemaError(ValueError):
    """Raised when transition evidence badge schema or badge object is invalid."""


@dataclass(frozen=True)
class TransitionEvidenceBadgeSchema:
    """Machine-readable transition evidence badge schema."""

    version: int
    status: str
    data_mode: str
    objective_zh: str
    caveats_zh: list[str]
    badge_families: dict[str, dict[str, Any]]
    badge_object_schema: dict[str, Any]
    allowed_dashboard_contract: dict[str, Any]
    prohibited_fields: list[str]
    validation_rules: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


@dataclass(frozen=True)
class TransitionEvidenceBadgeFixtures:
    """Machine-readable transition evidence badge validation fixtures."""

    version: int
    status: str
    schema_path: str
    objective_zh: str
    caveats_zh: list[str]
    valid_badges: list[dict[str, Any]]
    invalid_badges: list[dict[str, Any]]


@dataclass(frozen=True)
class TransitionEvidenceBadgeFixtureValidationSummary:
    """Summary of transition evidence badge fixture validation."""

    valid_fixture_count: int
    invalid_fixture_count: int
    valid_pass_count: int
    invalid_rejected_count: int
    unexpected_valid_failures: list[dict[str, str]]
    unexpected_invalid_passes: list[str]
    expected_error_mismatches: list[dict[str, str]]

    @property
    def passed(self) -> bool:
        """Return whether all fixture validation gates passed."""

        return (
            self.valid_pass_count == self.valid_fixture_count
            and self.invalid_rejected_count == self.invalid_fixture_count
            and not self.unexpected_valid_failures
            and not self.unexpected_invalid_passes
            and not self.expected_error_mismatches
        )


def load_transition_evidence_badge_schema(path: str | Path) -> TransitionEvidenceBadgeSchema:
    """Load and validate transition evidence badge schema YAML."""

    payload = _load_yaml_mapping(path, "Transition evidence badge schema")
    raw = payload.get("transition_evidence_badge_schema")
    if not isinstance(raw, dict):
        raise TransitionEvidenceBadgeSchemaError(
            "transition_evidence_badge_schema YAML must contain a mapping"
        )
    schema = _schema_from_mapping(raw)
    validate_transition_evidence_badge_schema(schema)
    return schema


def load_transition_evidence_badge_fixtures(path: str | Path) -> TransitionEvidenceBadgeFixtures:
    """Load transition evidence badge validation fixtures YAML."""

    payload = _load_yaml_mapping(path, "Transition evidence badge fixtures")
    raw = payload.get("transition_evidence_badge_fixtures")
    if not isinstance(raw, dict):
        raise TransitionEvidenceBadgeSchemaError(
            "transition_evidence_badge_fixtures YAML must contain a mapping"
        )
    return _fixtures_from_mapping(raw)


def validate_transition_evidence_badge_schema(schema: TransitionEvidenceBadgeSchema) -> None:
    """Validate parsed transition evidence badge schema."""

    if not isinstance(schema.version, int):
        raise TransitionEvidenceBadgeSchemaError("version must exist and be an integer")
    if not schema.status:
        raise TransitionEvidenceBadgeSchemaError("status must be non-empty")
    _validate_caveats(schema.caveats_zh)
    _validate_badge_families(schema.badge_families)
    _validate_badge_object_schema(schema.badge_object_schema)
    _validate_dashboard_contract(schema.allowed_dashboard_contract)
    _validate_prohibited_fields(schema.prohibited_fields)
    _validate_recommended_next_phase(schema.recommended_next_phase)


def validate_transition_evidence_badge_list(
    badges: list[dict[str, Any]],
    schema: TransitionEvidenceBadgeSchema,
) -> None:
    """Validate a list of transition evidence badge objects."""

    if not isinstance(badges, list):
        raise TransitionEvidenceBadgeSchemaError("badges must be a list")
    for index, badge in enumerate(badges):
        try:
            validate_transition_evidence_badge_object(badge, schema)
        except TransitionEvidenceBadgeSchemaError as exc:
            raise TransitionEvidenceBadgeSchemaError(f"badges[{index}] invalid: {exc}") from exc


def validate_transition_evidence_badge_fixtures(
    fixtures: TransitionEvidenceBadgeFixtures,
    schema: TransitionEvidenceBadgeSchema,
) -> TransitionEvidenceBadgeFixtureValidationSummary:
    """Validate valid and invalid transition evidence badge fixtures."""

    unexpected_valid_failures: list[dict[str, str]] = []
    unexpected_invalid_passes: list[str] = []
    expected_error_mismatches: list[dict[str, str]] = []
    valid_pass_count = 0
    invalid_rejected_count = 0

    for fixture in fixtures.valid_badges:
        fixture_id = str(fixture["fixture_id"])
        try:
            validate_transition_evidence_badge_object(_mapping(fixture["badge"], "badge"), schema)
        except TransitionEvidenceBadgeSchemaError as exc:
            unexpected_valid_failures.append({"fixture_id": fixture_id, "error": str(exc)})
        else:
            valid_pass_count += 1

    for fixture in fixtures.invalid_badges:
        fixture_id = str(fixture["fixture_id"])
        expected_error = str(fixture.get("expected_error_contains") or "")
        try:
            validate_transition_evidence_badge_object(_mapping(fixture["badge"], "badge"), schema)
        except TransitionEvidenceBadgeSchemaError as exc:
            error = str(exc)
            if expected_error and expected_error not in error:
                expected_error_mismatches.append(
                    {
                        "fixture_id": fixture_id,
                        "expected_error_contains": expected_error,
                        "actual_error": error,
                    }
                )
            else:
                invalid_rejected_count += 1
        else:
            unexpected_invalid_passes.append(fixture_id)

    return TransitionEvidenceBadgeFixtureValidationSummary(
        valid_fixture_count=len(fixtures.valid_badges),
        invalid_fixture_count=len(fixtures.invalid_badges),
        valid_pass_count=valid_pass_count,
        invalid_rejected_count=invalid_rejected_count,
        unexpected_valid_failures=unexpected_valid_failures,
        unexpected_invalid_passes=unexpected_invalid_passes,
        expected_error_mismatches=expected_error_mismatches,
    )


def validate_transition_evidence_badge_object(
    badge: dict[str, Any],
    schema: TransitionEvidenceBadgeSchema,
) -> None:
    """Validate one transition evidence badge object against the schema."""

    required_fields = _non_empty_str_list(
        schema.badge_object_schema.get("required_fields"),
        "badge_object_schema.required_fields",
    )
    missing = [field for field in required_fields if field not in badge]
    if missing:
        raise TransitionEvidenceBadgeSchemaError(
            f"badge missing required field(s): {', '.join(missing)}"
        )

    family_id = str(badge["family_id"])
    family = schema.badge_families.get(family_id)
    if family is None:
        raise TransitionEvidenceBadgeSchemaError(f"badge family_id is not allowed: {family_id}")

    level = str(badge["level"])
    allowed_levels = _non_empty_str_list(
        family.get("allowed_badge_levels"),
        f"{family_id}.allowed_badge_levels",
    )
    if level not in allowed_levels:
        raise TransitionEvidenceBadgeSchemaError(
            f"badge level {level} is not allowed for family {family_id}"
        )

    if badge.get("diagnostics_only") is not True:
        raise TransitionEvidenceBadgeSchemaError("badge diagnostics_only must be true")
    if str(badge.get("formal_decision_impact")) != "none":
        raise TransitionEvidenceBadgeSchemaError("badge formal_decision_impact must be none")

    prohibited = sorted(set(schema.prohibited_fields) & set(badge))
    if prohibited:
        raise TransitionEvidenceBadgeSchemaError(
            f"badge contains prohibited field(s): {', '.join(prohibited)}"
        )

    caveats = _non_empty_str_list(badge.get("caveats_zh"), "badge.caveats_zh")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise TransitionEvidenceBadgeSchemaError(
            "badge caveats_zh must include 不構成投資建議 no-investment-advice caveat"
        )

    confidence = badge.get("confidence")
    if not isinstance(confidence, int | float):
        raise TransitionEvidenceBadgeSchemaError("badge confidence must be numeric")
    confidence_range = schema.badge_object_schema.get("constraints", {}).get("confidence_range")
    if isinstance(confidence_range, list) and len(confidence_range) == 2:
        min_confidence = float(confidence_range[0])
        max_confidence = float(confidence_range[1])
    else:
        min_confidence = 0.0
        max_confidence = 1.0
    if not min_confidence <= float(confidence) <= max_confidence:
        raise TransitionEvidenceBadgeSchemaError(
            f"badge confidence must be between {min_confidence} and {max_confidence}"
        )


def _fixtures_from_mapping(payload: dict[str, Any]) -> TransitionEvidenceBadgeFixtures:
    required = (
        "version",
        "status",
        "schema_path",
        "objective_zh",
        "caveats_zh",
        "valid_badges",
        "invalid_badges",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise TransitionEvidenceBadgeSchemaError(
            "transition_evidence_badge_fixtures missing required field(s): "
            f"{', '.join(missing)}"
        )
    caveats = _non_empty_str_list(payload["caveats_zh"], "caveats_zh")
    for required_caveat in (
        "evidence badge 不會改變 current_phase_id",
        "evidence badge 不會改變 decision_status",
        "watch 類訊號不是買賣訊號",
        "不構成投資建議",
    ):
        if not any(required_caveat in caveat for caveat in caveats):
            raise TransitionEvidenceBadgeSchemaError(
                f"transition_evidence_badge_fixtures.caveats_zh must include {required_caveat}"
            )
    valid_badges = _list_of_mappings(payload["valid_badges"], "valid_badges")
    invalid_badges = _list_of_mappings(payload["invalid_badges"], "invalid_badges")
    for field, fixtures in (("valid_badges", valid_badges), ("invalid_badges", invalid_badges)):
        for index, fixture in enumerate(fixtures):
            if "fixture_id" not in fixture:
                raise TransitionEvidenceBadgeSchemaError(f"{field}[{index}] missing fixture_id")
            if "badge" not in fixture:
                raise TransitionEvidenceBadgeSchemaError(f"{field}[{index}] missing badge")
            _mapping(fixture["badge"], f"{field}[{index}].badge")
    return TransitionEvidenceBadgeFixtures(
        version=int(payload["version"]),
        status=str(payload["status"]),
        schema_path=str(payload["schema_path"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=caveats,
        valid_badges=valid_badges,
        invalid_badges=invalid_badges,
    )


def _schema_from_mapping(payload: dict[str, Any]) -> TransitionEvidenceBadgeSchema:
    required = (
        "version",
        "status",
        "data_mode",
        "objective_zh",
        "caveats_zh",
        "badge_families",
        "badge_object_schema",
        "allowed_dashboard_contract",
        "prohibited_fields",
        "validation_rules",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise TransitionEvidenceBadgeSchemaError(
            "transition_evidence_badge_schema missing required field(s): "
            f"{', '.join(missing)}"
        )
    return TransitionEvidenceBadgeSchema(
        version=int(payload["version"]),
        status=str(payload["status"]),
        data_mode=str(payload["data_mode"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_non_empty_str_list(payload["caveats_zh"], "caveats_zh"),
        badge_families=_mapping_of_mappings(payload["badge_families"], "badge_families"),
        badge_object_schema=_mapping(payload["badge_object_schema"], "badge_object_schema"),
        allowed_dashboard_contract=_mapping(
            payload["allowed_dashboard_contract"],
            "allowed_dashboard_contract",
        ),
        prohibited_fields=_non_empty_str_list(payload["prohibited_fields"], "prohibited_fields"),
        validation_rules=_list_of_mappings(payload["validation_rules"], "validation_rules"),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _validate_caveats(caveats: list[str]) -> None:
    for required in ("修訂後歷史資料", "watch 類訊號不是買賣訊號", "不構成投資建議"):
        if not any(required in caveat for caveat in caveats):
            raise TransitionEvidenceBadgeSchemaError(f"caveats_zh must include {required}")


def _validate_badge_families(families: dict[str, dict[str, Any]]) -> None:
    required_families = {"recession_confirmation", "boom_ending_watch", "recovery_watch"}
    missing = sorted(required_families - set(families))
    if missing:
        raise TransitionEvidenceBadgeSchemaError(
            f"badge_families missing required family/families: {', '.join(missing)}"
        )
    for family_id in sorted(required_families):
        family = families[family_id]
        if family.get("allowed_display") is not True:
            raise TransitionEvidenceBadgeSchemaError(f"{family_id}.allowed_display must be true")
        if str(family.get("formal_decision_impact")) != "none":
            raise TransitionEvidenceBadgeSchemaError(
                f"{family_id}.formal_decision_impact must be none"
            )
        _non_empty_str_list(family.get("allowed_badge_levels"), f"{family_id}.allowed_badge_levels")
        caveats = _non_empty_str_list(
            family.get("required_caveats_zh"),
            f"{family_id}.required_caveats_zh",
        )
        if not any("不構成投資建議" in caveat for caveat in caveats):
            raise TransitionEvidenceBadgeSchemaError(
                f"{family_id}.required_caveats_zh must include no-investment-advice caveat"
            )


def _validate_badge_object_schema(object_schema: dict[str, Any]) -> None:
    required_fields = set(
        _non_empty_str_list(
            object_schema.get("required_fields"),
            "badge_object_schema.required_fields",
        )
    )
    for field in ("diagnostics_only", "formal_decision_impact", "caveats_zh"):
        if field not in required_fields:
            raise TransitionEvidenceBadgeSchemaError(
                f"badge_object_schema.required_fields must include {field}"
            )
    constraints = _mapping(object_schema.get("constraints"), "badge_object_schema.constraints")
    if constraints.get("diagnostics_only_must_be_true") is not True:
        raise TransitionEvidenceBadgeSchemaError(
            "badge_object_schema.constraints.diagnostics_only_must_be_true must be true"
        )
    if constraints.get("formal_decision_impact_must_be_none") is not True:
        raise TransitionEvidenceBadgeSchemaError(
            "badge_object_schema.constraints.formal_decision_impact_must_be_none must be true"
        )


def _validate_dashboard_contract(contract: dict[str, Any]) -> None:
    if contract.get("allowed_now") is not False:
        raise TransitionEvidenceBadgeSchemaError("allowed_dashboard_contract.allowed_now must be false")
    display_text = _non_empty_str_list(
        contract.get("required_display_text_zh"),
        "allowed_dashboard_contract.required_display_text_zh",
    )
    if not any("watch 不是買賣訊號" in text for text in display_text):
        raise TransitionEvidenceBadgeSchemaError(
            "allowed_dashboard_contract.required_display_text_zh must include watch not trade signal"
        )
    if not any("不構成投資建議" in text for text in display_text):
        raise TransitionEvidenceBadgeSchemaError(
            "allowed_dashboard_contract.required_display_text_zh must include no-investment-advice"
        )


def _validate_prohibited_fields(fields: list[str]) -> None:
    required = {
        "action",
        "buy_signal",
        "sell_signal",
        "allocation",
        "target_weight",
        "confirmed_phase_override",
        "current_phase_override",
    }
    missing = sorted(required - set(fields))
    if missing:
        raise TransitionEvidenceBadgeSchemaError(
            f"prohibited_fields missing required field(s): {', '.join(missing)}"
        )


def _validate_recommended_next_phase(next_phase: dict[str, Any]) -> None:
    if str(next_phase.get("phase_id") or "") != "7G2":
        raise TransitionEvidenceBadgeSchemaError("recommended_next_phase.phase_id must be 7G2")
    if not str(next_phase.get("title") or ""):
        raise TransitionEvidenceBadgeSchemaError("recommended_next_phase must include title")
    if not str(next_phase.get("reason_zh") or ""):
        raise TransitionEvidenceBadgeSchemaError("recommended_next_phase must include reason_zh")


def _load_yaml_mapping(path: str | Path, description: str) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise TransitionEvidenceBadgeSchemaError(
            f"{description} file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TransitionEvidenceBadgeSchemaError(
            f"Invalid YAML in {description.lower()} file {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise TransitionEvidenceBadgeSchemaError(f"{description} YAML must be a mapping")
    return payload


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TransitionEvidenceBadgeSchemaError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise TransitionEvidenceBadgeSchemaError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise TransitionEvidenceBadgeSchemaError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise TransitionEvidenceBadgeSchemaError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TransitionEvidenceBadgeSchemaError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise TransitionEvidenceBadgeSchemaError(f"{field} must not contain empty items")
    return result
