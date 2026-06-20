"""Load and validate portfolio backtest input contracts and scenario mappings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PortfolioBacktestContractError(ValueError):
    """Raised when portfolio backtest input contract validation fails."""


@dataclass(frozen=True)
class PortfolioBacktestInputContract:
    """Machine-readable portfolio backtest input contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    input_sources: dict[str, dict[str, Any]]
    allowed_policy_templates: list[str]
    allowed_scenarios: list[str]
    data_contract: dict[str, Any]
    rebalance_contract: dict[str, Any]
    cost_assumptions: dict[str, Any]
    risk_metric_contract: dict[str, Any]
    output_contract: dict[str, Any]
    required_acceptance_before_running_backtest: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


@dataclass(frozen=True)
class PortfolioBacktestScenarioMapping:
    """Machine-readable portfolio backtest scenario mapping."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    scenarios: dict[str, dict[str, Any]]
    mapping_validation_rules: list[dict[str, Any]]


@dataclass(frozen=True)
class PortfolioBacktestInputFixtures:
    """Machine-readable portfolio backtest input fixtures."""

    version: int
    status: str
    contract_path: str
    scenario_mapping_path: str
    objective_zh: str
    caveats_zh: list[str]
    valid_inputs: list[dict[str, Any]]
    invalid_inputs: list[dict[str, Any]]


@dataclass(frozen=True)
class PortfolioBacktestInputFixtureValidationSummary:
    """Summary returned by backtest input fixture validation."""

    contract_version: int
    mapping_version: int
    fixtures_version: int
    valid_input_count: int
    invalid_input_count: int
    valid_pass_count: int
    invalid_rejected_count: int
    unexpected_valid_failures: list[dict[str, str]]
    unexpected_invalid_passes: list[str]
    expected_error_mismatches: list[dict[str, str]]

    @property
    def passed(self) -> bool:
        """Return true when all fixture expectations were met."""

        return (
            self.valid_pass_count == self.valid_input_count
            and self.invalid_rejected_count == self.invalid_input_count
            and not self.unexpected_valid_failures
            and not self.unexpected_invalid_passes
            and not self.expected_error_mismatches
        )


def load_portfolio_backtest_input_contract(path: str | Path) -> PortfolioBacktestInputContract:
    """Load and validate portfolio backtest input contract YAML."""

    payload = _load_root_mapping(path, "portfolio_backtest_input_contract")
    contract = _contract_from_mapping(payload)
    validate_portfolio_backtest_input_contract(contract)
    return contract


def validate_portfolio_backtest_input_contract(contract: PortfolioBacktestInputContract) -> None:
    """Validate parsed portfolio backtest input contract."""

    if not isinstance(contract.version, int):
        raise PortfolioBacktestContractError("version must exist and be an integer")
    if not contract.status:
        raise PortfolioBacktestContractError("status must be non-empty")
    if not contract.input_sources:
        raise PortfolioBacktestContractError("input_sources must exist")
    if not contract.allowed_policy_templates:
        raise PortfolioBacktestContractError("allowed_policy_templates must exist")
    if not contract.allowed_scenarios:
        raise PortfolioBacktestContractError("allowed_scenarios must exist")
    for field_name, value in (
        ("data_contract", contract.data_contract),
        ("rebalance_contract", contract.rebalance_contract),
        ("cost_assumptions", contract.cost_assumptions),
        ("risk_metric_contract", contract.risk_metric_contract),
        ("output_contract", contract.output_contract),
    ):
        if not value:
            raise PortfolioBacktestContractError(f"{field_name} must exist")
    if str(contract.recommended_next_phase.get("phase_id") or "") != "8D":
        raise PortfolioBacktestContractError("recommended_next_phase.phase_id must be 8D")
    _validate_prohibited_inputs(contract.data_contract)
    _validate_risk_metrics(contract.risk_metric_contract)
    _validate_output_contract(contract.output_contract)
    _validate_contract_caveats(contract.caveats_zh)


def load_portfolio_backtest_scenario_mapping(path: str | Path) -> PortfolioBacktestScenarioMapping:
    """Load portfolio backtest scenario mapping YAML."""

    payload = _load_root_mapping(path, "portfolio_backtest_scenario_mapping")
    return _mapping_from_mapping(payload)


def validate_portfolio_backtest_scenario_mapping(
    mapping: PortfolioBacktestScenarioMapping,
    contract: PortfolioBacktestInputContract,
) -> None:
    """Validate scenario mapping against the input contract."""

    if not isinstance(mapping.version, int):
        raise PortfolioBacktestContractError("scenario mapping version must exist and be an integer")
    if not mapping.status:
        raise PortfolioBacktestContractError("scenario mapping status must be non-empty")
    if not mapping.scenarios:
        raise PortfolioBacktestContractError("scenario mapping scenarios must exist")
    missing = sorted(set(contract.allowed_scenarios) - set(mapping.scenarios))
    if missing:
        raise PortfolioBacktestContractError(
            f"scenario mapping missing allowed scenario(s): {', '.join(missing)}"
        )
    prohibited = _prohibited_mapping_fields(contract)
    allowed_templates = set(contract.allowed_policy_templates)
    known_families = {"recession_confirmation", "boom_ending_watch", "recovery_watch"}
    for scenario_id in contract.allowed_scenarios:
        scenario = _mapping(mapping.scenarios.get(scenario_id), f"scenarios.{scenario_id}")
        if "enabled_for_backtest" not in scenario:
            raise PortfolioBacktestContractError(f"{scenario_id}.enabled_for_backtest must exist")
        templates = _str_list(scenario.get("primary_research_purpose"), f"{scenario_id}.primary_research_purpose")
        unknown_templates = sorted(set(templates) - allowed_templates)
        if unknown_templates:
            raise PortfolioBacktestContractError(
                f"{scenario_id}.primary_research_purpose contains unknown template(s): "
                f"{', '.join(unknown_templates)}"
            )
        families = _str_list(
            scenario.get("required_evidence_families"),
            f"{scenario_id}.required_evidence_families",
        )
        unknown_families = sorted(set(families) - known_families)
        if unknown_families:
            raise PortfolioBacktestContractError(
                f"{scenario_id}.required_evidence_families contains unknown family(s): "
                f"{', '.join(unknown_families)}"
            )
        _str_list(scenario.get("caveats_zh"), f"{scenario_id}.caveats_zh")
    _validate_no_prohibited_fields(mapping.scenarios, prohibited)
    _validate_mapping_caveats(mapping.caveats_zh)


def summarize_portfolio_backtest_input_contract(
    contract: PortfolioBacktestInputContract,
    mapping: PortfolioBacktestScenarioMapping,
) -> dict[str, Any]:
    """Return a concise machine-readable contract and mapping summary."""

    validate_portfolio_backtest_input_contract(contract)
    validate_portfolio_backtest_scenario_mapping(mapping, contract)
    prohibited_outputs = _str_list(
        contract.output_contract.get("prohibited_outputs"),
        "output_contract.prohibited_outputs",
    )
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "allowed_policy_template_count": len(contract.allowed_policy_templates),
        "allowed_scenario_count": len(contract.allowed_scenarios),
        "mapped_scenario_count": len(mapping.scenarios),
        "required_metric_count": len(
            _str_list(
                contract.risk_metric_contract.get("required_metrics"),
                "risk_metric_contract.required_metrics",
            )
        ),
        "prohibited_output_count": len(prohibited_outputs),
        "live_allocation_output_allowed": "live_allocation" not in prohibited_outputs,
        "trade_signal_output_allowed": not {"buy_signal", "sell_signal"}.issubset(
            set(prohibited_outputs)
        ),
        "public_dashboard_output_allowed": "public_dashboard_output" not in prohibited_outputs,
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def load_portfolio_backtest_input_fixtures(path: str | Path) -> PortfolioBacktestInputFixtures:
    """Load portfolio backtest input fixtures YAML."""

    payload = _load_root_mapping(path, "portfolio_backtest_input_fixtures")
    return _fixtures_from_mapping(payload)


def validate_portfolio_backtest_input(
    backtest_input: dict[str, Any],
    contract: PortfolioBacktestInputContract,
    mapping: PortfolioBacktestScenarioMapping,
) -> None:
    """Validate one portfolio backtest input object against contract and mapping."""

    if not isinstance(backtest_input, dict):
        raise PortfolioBacktestContractError("backtest input must be a mapping")
    required = (
        "backtest_input_id",
        "scenario_id",
        "policy_template_id",
        "research_only",
        "backtest_only",
        "rebalance_frequency",
        "transaction_cost_bps",
        "slippage_bps",
        "minimum_holding_period_months",
        "cooldown_months",
        "parameter_context",
        "caveats_zh",
    )
    _require_keys(backtest_input, required, "portfolio_backtest_input")
    if backtest_input.get("research_only") is not True:
        raise PortfolioBacktestContractError("research_only must be true")
    if backtest_input.get("backtest_only") is not True:
        raise PortfolioBacktestContractError("backtest_only must be true")
    if str(backtest_input["parameter_context"]) != "backtest_only":
        raise PortfolioBacktestContractError("parameter_context must be backtest_only")

    scenario_id = str(backtest_input["scenario_id"])
    if scenario_id not in contract.allowed_scenarios or scenario_id not in mapping.scenarios:
        raise PortfolioBacktestContractError(f"scenario_id must be known: {scenario_id}")

    template_id = str(backtest_input["policy_template_id"])
    if template_id not in contract.allowed_policy_templates:
        raise PortfolioBacktestContractError(f"policy_template_id must be known: {template_id}")

    allowed_frequencies = set(
        _str_list(
            contract.rebalance_contract.get("allowed_frequencies"),
            "rebalance_contract.allowed_frequencies",
        )
    )
    if str(backtest_input["rebalance_frequency"]) not in allowed_frequencies:
        raise PortfolioBacktestContractError(
            f"rebalance_frequency must be one of {', '.join(sorted(allowed_frequencies))}"
        )

    _validate_optional_required_metrics(backtest_input, contract)
    _validate_optional_required_inputs(backtest_input, contract)
    _validate_no_prohibited_fields(backtest_input, _prohibited_mapping_fields(contract))
    _validate_no_prohibited_text(backtest_input)
    _validate_backtest_input_caveats(backtest_input)
    _validate_optional_false_flags(backtest_input)


def validate_portfolio_backtest_input_fixtures(
    fixtures: PortfolioBacktestInputFixtures,
    contract: PortfolioBacktestInputContract,
    mapping: PortfolioBacktestScenarioMapping,
) -> PortfolioBacktestInputFixtureValidationSummary:
    """Validate all valid and invalid portfolio backtest input fixtures."""

    unexpected_valid_failures: list[dict[str, str]] = []
    unexpected_invalid_passes: list[str] = []
    expected_error_mismatches: list[dict[str, str]] = []
    valid_pass_count = 0
    invalid_rejected_count = 0

    for fixture in fixtures.valid_inputs:
        fixture_id = str(fixture.get("fixture_id") or "")
        try:
            validate_portfolio_backtest_input(_fixture_input(fixture, fixture_id), contract, mapping)
        except PortfolioBacktestContractError as exc:
            unexpected_valid_failures.append({"fixture_id": fixture_id, "error": str(exc)})
        else:
            valid_pass_count += 1

    for fixture in fixtures.invalid_inputs:
        fixture_id = str(fixture.get("fixture_id") or "")
        expected = str(fixture.get("expected_error_contains") or "")
        try:
            validate_portfolio_backtest_input(_fixture_input(fixture, fixture_id), contract, mapping)
        except PortfolioBacktestContractError as exc:
            invalid_rejected_count += 1
            error = str(exc)
            if expected and expected not in error:
                expected_error_mismatches.append(
                    {"fixture_id": fixture_id, "expected": expected, "error": error}
                )
        else:
            unexpected_invalid_passes.append(fixture_id)

    return PortfolioBacktestInputFixtureValidationSummary(
        contract_version=contract.version,
        mapping_version=mapping.version,
        fixtures_version=fixtures.version,
        valid_input_count=len(fixtures.valid_inputs),
        invalid_input_count=len(fixtures.invalid_inputs),
        valid_pass_count=valid_pass_count,
        invalid_rejected_count=invalid_rejected_count,
        unexpected_valid_failures=unexpected_valid_failures,
        unexpected_invalid_passes=unexpected_invalid_passes,
        expected_error_mismatches=expected_error_mismatches,
    )


def _contract_from_mapping(payload: dict[str, Any]) -> PortfolioBacktestInputContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "input_sources",
        "allowed_policy_templates",
        "allowed_scenarios",
        "data_contract",
        "rebalance_contract",
        "cost_assumptions",
        "risk_metric_contract",
        "output_contract",
        "required_acceptance_before_running_backtest",
        "recommended_next_phase",
    )
    _require_keys(payload, required, "portfolio_backtest_input_contract")
    return PortfolioBacktestInputContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        input_sources=_mapping_of_mappings(payload["input_sources"], "input_sources"),
        allowed_policy_templates=_str_list(
            payload["allowed_policy_templates"],
            "allowed_policy_templates",
        ),
        allowed_scenarios=_str_list(payload["allowed_scenarios"], "allowed_scenarios"),
        data_contract=_mapping(payload["data_contract"], "data_contract"),
        rebalance_contract=_mapping(payload["rebalance_contract"], "rebalance_contract"),
        cost_assumptions=_mapping(payload["cost_assumptions"], "cost_assumptions"),
        risk_metric_contract=_mapping(payload["risk_metric_contract"], "risk_metric_contract"),
        output_contract=_mapping(payload["output_contract"], "output_contract"),
        required_acceptance_before_running_backtest=_list_of_mappings(
            payload["required_acceptance_before_running_backtest"],
            "required_acceptance_before_running_backtest",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _mapping_from_mapping(payload: dict[str, Any]) -> PortfolioBacktestScenarioMapping:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "scenarios",
        "mapping_validation_rules",
    )
    _require_keys(payload, required, "portfolio_backtest_scenario_mapping")
    return PortfolioBacktestScenarioMapping(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        scenarios=_mapping_of_mappings(payload["scenarios"], "scenarios"),
        mapping_validation_rules=_list_of_mappings(
            payload["mapping_validation_rules"],
            "mapping_validation_rules",
        ),
    )


def _fixtures_from_mapping(payload: dict[str, Any]) -> PortfolioBacktestInputFixtures:
    required = (
        "version",
        "status",
        "contract_path",
        "scenario_mapping_path",
        "objective_zh",
        "caveats_zh",
        "valid_inputs",
        "invalid_inputs",
    )
    _require_keys(payload, required, "portfolio_backtest_input_fixtures")
    return PortfolioBacktestInputFixtures(
        version=int(payload["version"]),
        status=str(payload["status"]),
        contract_path=str(payload["contract_path"]),
        scenario_mapping_path=str(payload["scenario_mapping_path"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        valid_inputs=_list_of_mappings(payload["valid_inputs"], "valid_inputs"),
        invalid_inputs=_list_of_mappings(payload["invalid_inputs"], "invalid_inputs"),
    )


def _validate_prohibited_inputs(data_contract: dict[str, Any]) -> None:
    prohibited = set(
        _str_list(
            data_contract.get("prohibited_inputs_per_period"),
            "data_contract.prohibited_inputs_per_period",
        )
    )
    for field in (
        "live_allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "current_market_recommendation",
    ):
        if field not in prohibited:
            raise PortfolioBacktestContractError(
                f"data_contract.prohibited_inputs_per_period must include {field}"
            )


def _validate_risk_metrics(risk_metric_contract: dict[str, Any]) -> None:
    metrics = set(
        _str_list(
            risk_metric_contract.get("required_metrics"),
            "risk_metric_contract.required_metrics",
        )
    )
    for metric in ("max_drawdown", "turnover", "false_de_risk_cost", "false_re_risk_cost"):
        if metric not in metrics:
            raise PortfolioBacktestContractError(
                f"risk_metric_contract.required_metrics must include {metric}"
            )


def _validate_output_contract(output_contract: dict[str, Any]) -> None:
    prohibited = set(
        _str_list(output_contract.get("prohibited_outputs"), "output_contract.prohibited_outputs")
    )
    for field in (
        "live_allocation",
        "buy_signal",
        "sell_signal",
        "target_weight",
        "portfolio_action",
        "public_dashboard_output",
    ):
        if field not in prohibited:
            raise PortfolioBacktestContractError(
                f"output_contract.prohibited_outputs must include {field}"
            )
    caveats = _str_list(
        output_contract.get("required_output_caveats_zh"),
        "output_contract.required_output_caveats_zh",
    )
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioBacktestContractError(
            "output_contract.required_output_caveats_zh must include 不構成投資建議"
        )


def _validate_contract_caveats(caveats: list[str]) -> None:
    for required in ("不是回測結果", "backtest-only parameters", "不構成投資建議"):
        if not any(required in caveat for caveat in caveats):
            raise PortfolioBacktestContractError(f"caveats_zh must include {required}")


def _validate_mapping_caveats(caveats: list[str]) -> None:
    for required in ("不是回測結果", "不產生 portfolio allocation", "不構成投資建議"):
        if not any(required in caveat for caveat in caveats):
            raise PortfolioBacktestContractError(
                f"portfolio_backtest_scenario_mapping.caveats_zh must include {required}"
            )


def _prohibited_mapping_fields(contract: PortfolioBacktestInputContract) -> set[str]:
    data_fields = _str_list(
        contract.data_contract.get("prohibited_inputs_per_period"),
        "data_contract.prohibited_inputs_per_period",
    )
    output_fields = _str_list(
        contract.output_contract.get("prohibited_outputs"),
        "output_contract.prohibited_outputs",
    )
    return set(data_fields) | set(output_fields)


def _validate_no_prohibited_fields(value: Any, prohibited_fields: set[str], path: str = "") -> None:
    if isinstance(value, dict):
        for key, raw in value.items():
            key_text = str(key)
            current_path = f"{path}.{key_text}" if path else key_text
            if key_text in prohibited_fields:
                raise PortfolioBacktestContractError(
                    f"prohibited field {key_text} found at {current_path}"
                )
            _validate_no_prohibited_fields(raw, prohibited_fields, current_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_no_prohibited_fields(item, prohibited_fields, f"{path}[{index}]")


def _validate_optional_required_metrics(
    backtest_input: dict[str, Any],
    contract: PortfolioBacktestInputContract,
) -> None:
    if "required_metrics" not in backtest_input:
        return
    required_order = _str_list(
        contract.risk_metric_contract.get("required_metrics"),
        "risk_metric_contract.required_metrics",
    )
    required = set(required_order)
    actual = set(_str_list(backtest_input["required_metrics"], "required_metrics"))
    priority_order = ("max_drawdown", "turnover", "false_de_risk_cost", "false_re_risk_cost")
    missing = [metric for metric in priority_order if metric in required and metric not in actual]
    missing.extend(metric for metric in required_order if metric not in actual and metric not in missing)
    if missing:
        raise PortfolioBacktestContractError(f"required_metrics must include {missing[0]}")


def _validate_optional_required_inputs(
    backtest_input: dict[str, Any],
    contract: PortfolioBacktestInputContract,
) -> None:
    if "required_inputs_per_period" not in backtest_input:
        return
    required = set(
        _str_list(
            contract.data_contract.get("required_inputs_per_period"),
            "data_contract.required_inputs_per_period",
        )
    )
    actual = set(_str_list(backtest_input["required_inputs_per_period"], "required_inputs_per_period"))
    missing = sorted(required - actual)
    if missing:
        raise PortfolioBacktestContractError(f"required_inputs_per_period must include {missing[0]}")


def _validate_no_prohibited_text(value: Any) -> None:
    patterns = (
        "目前建議",
        "建議買進",
        "建議賣出",
        "立即買進",
        "立即賣出",
        "買進訊號",
        "賣出訊號",
        "live allocation",
        "target weight",
        "buy signal",
        "sell signal",
    )
    for path, text in _iter_text_fields(value):
        lowered = text.lower()
        for pattern in patterns:
            if pattern.lower() in lowered:
                raise PortfolioBacktestContractError(
                    f"prohibited text pattern {pattern} found at {path}"
                )


def _iter_text_fields(value: Any, path: str = "") -> list[tuple[str, str]]:
    if path == "caveats_zh":
        return []
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        result: list[tuple[str, str]] = []
        for key, raw in value.items():
            key_text = str(key)
            current_path = f"{path}.{key_text}" if path else key_text
            if key_text == "caveats_zh":
                continue
            result.extend(_iter_text_fields(raw, current_path))
        return result
    if isinstance(value, list):
        result = []
        for index, item in enumerate(value):
            result.extend(_iter_text_fields(item, f"{path}[{index}]"))
        return result
    return []


def _validate_backtest_input_caveats(backtest_input: dict[str, Any]) -> None:
    caveats = _str_list(backtest_input.get("caveats_zh"), "caveats_zh")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioBacktestContractError("caveats_zh must include 不構成投資建議")


def _validate_optional_false_flags(backtest_input: dict[str, Any]) -> None:
    for field in ("public_output_allowed", "live_allocation_allowed", "trade_signal_output_allowed"):
        if field in backtest_input and backtest_input[field] is not False:
            raise PortfolioBacktestContractError(f"{field} must be false")


def _fixture_input(fixture: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    backtest_input = fixture.get("input")
    if not isinstance(backtest_input, dict):
        raise PortfolioBacktestContractError(f"{fixture_id}.input must be a mapping")
    return {str(key): raw for key, raw in backtest_input.items()}


def _load_root_mapping(path: str | Path, root_key: str) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioBacktestContractError(f"{root_key} file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioBacktestContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PortfolioBacktestContractError(f"{root_key} YAML must be a mapping")
    root = payload.get(root_key)
    if not isinstance(root, dict):
        raise PortfolioBacktestContractError(f"{root_key} YAML must contain a mapping")
    return {str(key): raw for key, raw in root.items()}


def _require_keys(payload: dict[str, Any], required: tuple[str, ...], field: str) -> None:
    missing = [key for key in required if key not in payload]
    if missing:
        raise PortfolioBacktestContractError(f"{field} missing required field(s): {', '.join(missing)}")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioBacktestContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise PortfolioBacktestContractError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PortfolioBacktestContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PortfolioBacktestContractError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PortfolioBacktestContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise PortfolioBacktestContractError(f"{field} must not contain empty items")
    return result
