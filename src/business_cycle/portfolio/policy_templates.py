"""Load and validate portfolio policy template schemas and fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.policy_research_baseline import REQUIRED_TEMPLATE_IDS


class PortfolioPolicyTemplateError(ValueError):
    """Raised when portfolio policy template validation fails."""


@dataclass(frozen=True)
class PortfolioPolicyTemplateSchema:
    """Machine-readable portfolio policy template schema."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    template_object_schema: dict[str, Any]
    allowed_template_ids: list[str]
    allowed_statuses: list[str]
    allowed_parameter_contexts: list[str]
    prohibited_fields: list[str]
    prohibited_text_patterns: dict[str, list[str]]
    required_caveats_zh: list[str]
    template_specific_rules: dict[str, dict[str, Any]]
    recommended_next_phase: dict[str, Any]


@dataclass(frozen=True)
class PortfolioPolicyTemplateFixtures:
    """Machine-readable portfolio policy template fixtures."""

    version: int
    status: str
    schema_path: str
    objective_zh: str
    caveats_zh: list[str]
    valid_templates: list[dict[str, Any]]
    invalid_templates: list[dict[str, Any]]


@dataclass(frozen=True)
class PortfolioPolicyTemplateFixtureValidationSummary:
    """Summary returned by policy template fixture validation."""

    schema_version: int
    fixtures_version: int
    valid_template_count: int
    invalid_template_count: int
    valid_pass_count: int
    invalid_rejected_count: int
    unexpected_valid_failures: list[dict[str, str]]
    unexpected_invalid_passes: list[str]
    expected_error_mismatches: list[dict[str, str]]

    @property
    def passed(self) -> bool:
        """Return true when all fixture expectations were met."""

        return (
            self.valid_pass_count == self.valid_template_count
            and self.invalid_rejected_count == self.invalid_template_count
            and not self.unexpected_valid_failures
            and not self.unexpected_invalid_passes
            and not self.expected_error_mismatches
        )


def load_portfolio_policy_template_schema(path: str | Path) -> PortfolioPolicyTemplateSchema:
    """Load and validate portfolio policy template schema YAML."""

    payload = _load_root_mapping(path, "portfolio_policy_template_schema")
    schema = _schema_from_mapping(payload)
    validate_portfolio_policy_template_schema(schema)
    return schema


def validate_portfolio_policy_template_schema(schema: PortfolioPolicyTemplateSchema) -> None:
    """Validate parsed portfolio policy template schema."""

    if not isinstance(schema.version, int):
        raise PortfolioPolicyTemplateError("version must exist and be an integer")
    if not schema.status:
        raise PortfolioPolicyTemplateError("status must be non-empty")
    if not schema.template_object_schema:
        raise PortfolioPolicyTemplateError("template_object_schema must exist")
    if not schema.prohibited_fields:
        raise PortfolioPolicyTemplateError("prohibited_fields must exist")
    if not schema.prohibited_text_patterns:
        raise PortfolioPolicyTemplateError("prohibited_text_patterns must exist")
    if str(schema.recommended_next_phase.get("phase_id") or "") != "77":
        raise PortfolioPolicyTemplateError("recommended_next_phase.phase_id must be 77")
    for field in ("target_weight", "buy_signal", "sell_signal", "current_market_recommendation"):
        if field not in schema.prohibited_fields:
            raise PortfolioPolicyTemplateError(f"prohibited_fields must include {field}")
    for caveat in (
        "research-only，不是正式投資策略。",
        "backtest-only，不是目前配置建議。",
        "不構成投資建議。",
    ):
        if caveat not in schema.required_caveats_zh:
            raise PortfolioPolicyTemplateError(f"required_caveats_zh must include {caveat}")
    if set(schema.allowed_template_ids) != REQUIRED_TEMPLATE_IDS:
        raise PortfolioPolicyTemplateError("allowed_template_ids must contain the eight Phase75 templates")


def validate_portfolio_policy_template(
    template: dict[str, Any],
    schema: PortfolioPolicyTemplateSchema,
) -> None:
    """Validate one portfolio policy template object against schema."""

    if not isinstance(template, dict):
        raise PortfolioPolicyTemplateError("template must be a mapping")
    _validate_required_template_fields(template, schema)
    template_id = str(template["template_id"])
    if template_id not in schema.allowed_template_ids:
        raise PortfolioPolicyTemplateError(f"template_id must be allowed: {template_id}")
    if str(template["status"]) not in schema.allowed_statuses:
        raise PortfolioPolicyTemplateError(f"status must be allowed for {template_id}")
    _require_bool(template, "research_only", True)
    _require_bool(template, "backtest_only", True)
    _require_bool(template, "live_allocation_allowed", False)
    _require_bool(template, "trade_signal_allowed", False)
    _require_bool(template, "public_output_allowed", False)
    _validate_no_prohibited_fields(template, schema.prohibited_fields)
    _validate_no_prohibited_text(template, schema.prohibited_text_patterns)
    _validate_template_caveats(template)
    _validate_template_specific_rules(template, schema)
    _validate_backtest_only_parameters(template, schema)


def load_portfolio_policy_template_fixtures(path: str | Path) -> PortfolioPolicyTemplateFixtures:
    """Load portfolio policy template fixture YAML."""

    payload = _load_root_mapping(path, "portfolio_policy_template_fixtures")
    return _fixtures_from_mapping(payload)


def validate_portfolio_policy_template_fixtures(
    fixtures: PortfolioPolicyTemplateFixtures,
    schema: PortfolioPolicyTemplateSchema,
) -> PortfolioPolicyTemplateFixtureValidationSummary:
    """Validate all valid and invalid policy template fixtures."""

    unexpected_valid_failures: list[dict[str, str]] = []
    unexpected_invalid_passes: list[str] = []
    expected_error_mismatches: list[dict[str, str]] = []
    valid_pass_count = 0
    invalid_rejected_count = 0

    for fixture in fixtures.valid_templates:
        fixture_id = str(fixture.get("fixture_id") or "")
        try:
            validate_portfolio_policy_template(_fixture_template(fixture, fixture_id), schema)
        except PortfolioPolicyTemplateError as exc:
            unexpected_valid_failures.append({"fixture_id": fixture_id, "error": str(exc)})
        else:
            valid_pass_count += 1

    for fixture in fixtures.invalid_templates:
        fixture_id = str(fixture.get("fixture_id") or "")
        expected = str(fixture.get("expected_error_contains") or "")
        try:
            validate_portfolio_policy_template(_fixture_template(fixture, fixture_id), schema)
        except PortfolioPolicyTemplateError as exc:
            invalid_rejected_count += 1
            error = str(exc)
            if expected and expected not in error:
                expected_error_mismatches.append(
                    {"fixture_id": fixture_id, "expected": expected, "error": error}
                )
        else:
            unexpected_invalid_passes.append(fixture_id)

    return PortfolioPolicyTemplateFixtureValidationSummary(
        schema_version=schema.version,
        fixtures_version=fixtures.version,
        valid_template_count=len(fixtures.valid_templates),
        invalid_template_count=len(fixtures.invalid_templates),
        valid_pass_count=valid_pass_count,
        invalid_rejected_count=invalid_rejected_count,
        unexpected_valid_failures=unexpected_valid_failures,
        unexpected_invalid_passes=unexpected_invalid_passes,
        expected_error_mismatches=expected_error_mismatches,
    )


def _load_root_mapping(path: str | Path, root_key: str) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioPolicyTemplateError(f"{root_key} file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioPolicyTemplateError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PortfolioPolicyTemplateError(f"{root_key} YAML must be a mapping")
    root = payload.get(root_key)
    if not isinstance(root, dict):
        raise PortfolioPolicyTemplateError(f"{root_key} YAML must contain a mapping")
    return {str(key): raw for key, raw in root.items()}


def _schema_from_mapping(payload: dict[str, Any]) -> PortfolioPolicyTemplateSchema:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "template_object_schema",
        "allowed_template_ids",
        "allowed_statuses",
        "allowed_parameter_contexts",
        "prohibited_fields",
        "prohibited_text_patterns",
        "required_caveats_zh",
        "template_specific_rules",
        "recommended_next_phase",
    )
    _require_keys(payload, required, "portfolio_policy_template_schema")
    return PortfolioPolicyTemplateSchema(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        template_object_schema=_mapping(payload["template_object_schema"], "template_object_schema"),
        allowed_template_ids=_str_list(payload["allowed_template_ids"], "allowed_template_ids"),
        allowed_statuses=_str_list(payload["allowed_statuses"], "allowed_statuses"),
        allowed_parameter_contexts=_str_list(
            payload["allowed_parameter_contexts"],
            "allowed_parameter_contexts",
        ),
        prohibited_fields=_str_list(payload["prohibited_fields"], "prohibited_fields"),
        prohibited_text_patterns=_mapping_of_str_lists(
            payload["prohibited_text_patterns"],
            "prohibited_text_patterns",
        ),
        required_caveats_zh=_str_list(payload["required_caveats_zh"], "required_caveats_zh"),
        template_specific_rules=_mapping_of_mappings(
            payload["template_specific_rules"],
            "template_specific_rules",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _fixtures_from_mapping(payload: dict[str, Any]) -> PortfolioPolicyTemplateFixtures:
    required = (
        "version",
        "status",
        "schema_path",
        "objective_zh",
        "caveats_zh",
        "valid_templates",
        "invalid_templates",
    )
    _require_keys(payload, required, "portfolio_policy_template_fixtures")
    return PortfolioPolicyTemplateFixtures(
        version=int(payload["version"]),
        status=str(payload["status"]),
        schema_path=str(payload["schema_path"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        valid_templates=_list_of_mappings(payload["valid_templates"], "valid_templates"),
        invalid_templates=_list_of_mappings(payload["invalid_templates"], "invalid_templates"),
    )


def _validate_required_template_fields(
    template: dict[str, Any],
    schema: PortfolioPolicyTemplateSchema,
) -> None:
    object_schema = _mapping(schema.template_object_schema, "template_object_schema")
    required_fields = _str_list(
        object_schema.get("required_fields"),
        "template_object_schema.required_fields",
    )
    missing = [field for field in required_fields if field not in template]
    if missing:
        raise PortfolioPolicyTemplateError(f"template missing required field(s): {', '.join(missing)}")


def _require_bool(template: dict[str, Any], field: str, expected: bool) -> None:
    if template.get(field) is not expected:
        raise PortfolioPolicyTemplateError(f"{field} must be {str(expected).lower()}")


def _validate_no_prohibited_fields(value: Any, prohibited_fields: list[str], path: str = "") -> None:
    if isinstance(value, dict):
        for key, raw in value.items():
            key_text = str(key)
            current_path = f"{path}.{key_text}" if path else key_text
            if key_text in prohibited_fields:
                raise PortfolioPolicyTemplateError(f"prohibited field {key_text} found at {current_path}")
            _validate_no_prohibited_fields(raw, prohibited_fields, current_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_no_prohibited_fields(item, prohibited_fields, f"{path}[{index}]")


def _validate_no_prohibited_text(
    template: dict[str, Any],
    patterns_by_language: dict[str, list[str]],
) -> None:
    patterns = [pattern for values in patterns_by_language.values() for pattern in values]
    for path, text in _iter_text_fields_for_policy_safety(template):
        lowered = text.lower()
        for pattern in patterns:
            if pattern.lower() in lowered:
                raise PortfolioPolicyTemplateError(
                    f"prohibited text pattern {pattern} found at {path}"
                )


def _iter_text_fields_for_policy_safety(value: Any, path: str = "") -> list[tuple[str, str]]:
    if path in {"display_name_zh", "prohibited_interpretations_zh", "caveats_zh"}:
        return []
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        result: list[tuple[str, str]] = []
        for key, raw in value.items():
            key_text = str(key)
            current_path = f"{path}.{key_text}" if path else key_text
            if key_text in {"display_name_zh", "prohibited_interpretations_zh", "caveats_zh"}:
                continue
            result.extend(_iter_text_fields_for_policy_safety(raw, current_path))
        return result
    if isinstance(value, list):
        result = []
        for index, item in enumerate(value):
            result.extend(_iter_text_fields_for_policy_safety(item, f"{path}[{index}]"))
        return result
    return []


def _validate_template_caveats(template: dict[str, Any]) -> None:
    caveats = _str_list(template.get("caveats_zh"), "caveats_zh")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioPolicyTemplateError("caveats_zh must include 不構成投資建議")


def _validate_template_specific_rules(
    template: dict[str, Any],
    schema: PortfolioPolicyTemplateSchema,
) -> None:
    template_id = str(template["template_id"])
    rules = _mapping(
        schema.template_specific_rules.get(template_id),
        f"template_specific_rules.{template_id}",
    )
    required_interpretations = _str_list(
        rules.get("required_prohibited_interpretations"),
        f"template_specific_rules.{template_id}.required_prohibited_interpretations",
    )
    actual = set(_str_list(template["prohibited_interpretations_zh"], "prohibited_interpretations_zh"))
    missing = [item for item in required_interpretations if item not in actual]
    if missing:
        raise PortfolioPolicyTemplateError(
            f"{template_id}.prohibited_interpretations_zh missing required item: {missing[0]}"
        )
    if template_id == "boom_70_50_30_template":
        params = _mapping(
            template.get("book_aligned_parameters"),
            "boom_70_50_30_template.book_aligned_parameters",
        )
        weights = [float(value) for value in params.get("stock_weight_levels_for_backtest_only", [])]
        if weights != [0.70, 0.50, 0.30]:
            raise PortfolioPolicyTemplateError(
                "stock_weight_levels_for_backtest_only must equal [0.70, 0.50, 0.30]"
            )


def _validate_backtest_only_parameters(
    template: dict[str, Any],
    schema: PortfolioPolicyTemplateSchema,
) -> None:
    params = template.get("book_aligned_parameters")
    if params is None:
        return
    mapping = _mapping(params, "book_aligned_parameters")
    parameter_context = str(mapping.get("parameter_context") or "")
    if parameter_context and parameter_context not in schema.allowed_parameter_contexts:
        raise PortfolioPolicyTemplateError("book_aligned_parameters.parameter_context must be allowed")
    for key in mapping:
        if _looks_like_weight_parameter(key) and not key.endswith("_for_backtest_only"):
            if parameter_context != "backtest_only":
                raise PortfolioPolicyTemplateError(
                    f"book_aligned_parameters.{key} must be backtest-only"
                )


def _looks_like_weight_parameter(key: str) -> bool:
    return "weight" in key or "allocation" in key


def _fixture_template(fixture: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    template = fixture.get("template")
    if not isinstance(template, dict):
        raise PortfolioPolicyTemplateError(f"{fixture_id}.template must be a mapping")
    return {str(key): raw for key, raw in template.items()}


def _require_keys(payload: dict[str, Any], required: tuple[str, ...], field: str) -> None:
    missing = [key for key in required if key not in payload]
    if missing:
        raise PortfolioPolicyTemplateError(f"{field} missing required field(s): {', '.join(missing)}")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioPolicyTemplateError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise PortfolioPolicyTemplateError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PortfolioPolicyTemplateError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PortfolioPolicyTemplateError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PortfolioPolicyTemplateError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise PortfolioPolicyTemplateError(f"{field} must not contain empty items")
    return result
