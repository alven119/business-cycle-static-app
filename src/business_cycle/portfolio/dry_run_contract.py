"""Load and validate portfolio backtest dry-run engine contracts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class PortfolioBacktestDryRunContractError(ValueError):
    """Raised when portfolio backtest dry-run contract validation fails."""


@dataclass(frozen=True)
class PortfolioBacktestDryRunContract:
    """Machine-readable portfolio backtest dry-run contract."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    input_contracts: dict[str, dict[str, Any]]
    dry_run_scope: dict[str, dict[str, Any]]
    dry_run_input_schema: dict[str, Any]
    dry_run_output_schema: dict[str, Any]
    stdout_contract: dict[str, Any]
    required_acceptance_before_dry_run_fixtures: list[dict[str, Any]]
    recommended_next_phase: dict[str, Any]


@dataclass(frozen=True)
class PortfolioBacktestDryRunFixtures:
    """Machine-readable portfolio backtest dry-run fixtures."""

    version: int
    status: str
    dry_run_contract_path: str
    backtest_input_contract_path: str
    backtest_input_fixtures_path: str
    objective_zh: str
    caveats_zh: list[str]
    valid_dry_run_outputs: list[dict[str, Any]]
    invalid_dry_run_outputs: list[dict[str, Any]]


@dataclass(frozen=True)
class PortfolioBacktestDryRunFixtureValidationSummary:
    """Summary returned by dry-run fixture validation."""

    contract_version: int
    fixtures_version: int
    valid_output_count: int
    invalid_output_count: int
    valid_pass_count: int
    invalid_rejected_count: int
    unexpected_valid_failures: list[dict[str, str]]
    unexpected_invalid_passes: list[str]
    expected_error_mismatches: list[dict[str, str]]
    output_written: bool
    data_backtests_output_written: bool
    public_output_written: bool
    allocation_output_generated: bool
    trade_signal_generated: bool

    @property
    def passed(self) -> bool:
        """Return true when all dry-run fixture expectations were met."""

        return (
            self.valid_pass_count == self.valid_output_count
            and self.invalid_rejected_count == self.invalid_output_count
            and not self.unexpected_valid_failures
            and not self.unexpected_invalid_passes
            and not self.expected_error_mismatches
            and not self.output_written
            and not self.data_backtests_output_written
            and not self.public_output_written
            and not self.allocation_output_generated
            and not self.trade_signal_generated
        )


def load_portfolio_backtest_dry_run_contract(
    path: str | Path,
) -> PortfolioBacktestDryRunContract:
    """Load and validate portfolio backtest dry-run contract YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioBacktestDryRunContractError(
            f"portfolio_backtest_dry_run_contract file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioBacktestDryRunContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_contract YAML must be a mapping"
        )
    raw = payload.get("portfolio_backtest_dry_run_contract")
    if not isinstance(raw, dict):
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_contract YAML must contain a mapping"
        )
    contract = _contract_from_mapping({str(key): value for key, value in raw.items()})
    validate_portfolio_backtest_dry_run_contract(contract)
    return contract


def validate_portfolio_backtest_dry_run_contract(
    contract: PortfolioBacktestDryRunContract,
) -> None:
    """Validate parsed portfolio backtest dry-run contract."""

    if not isinstance(contract.version, int):
        raise PortfolioBacktestDryRunContractError("version must exist and be an integer")
    if not contract.status:
        raise PortfolioBacktestDryRunContractError("status must be non-empty")
    if not contract.input_contracts:
        raise PortfolioBacktestDryRunContractError("input_contracts must exist")
    if not contract.dry_run_scope:
        raise PortfolioBacktestDryRunContractError("dry_run_scope must exist")
    if not contract.dry_run_input_schema:
        raise PortfolioBacktestDryRunContractError("dry_run_input_schema must exist")
    if not contract.dry_run_output_schema:
        raise PortfolioBacktestDryRunContractError("dry_run_output_schema must exist")
    if not contract.stdout_contract:
        raise PortfolioBacktestDryRunContractError("stdout_contract must exist")
    if str(contract.recommended_next_phase.get("phase_id") or "") != "8F":
        raise PortfolioBacktestDryRunContractError("recommended_next_phase.phase_id must be 8F")
    _validate_disallowed_scope(contract.dry_run_scope)
    _validate_output_schema(contract.dry_run_output_schema)
    _validate_stdout_contract(contract.stdout_contract)
    _validate_caveats(contract.caveats_zh)


def summarize_portfolio_backtest_dry_run_contract(
    contract: PortfolioBacktestDryRunContract,
) -> dict[str, Any]:
    """Return a concise machine-readable dry-run contract summary."""

    validate_portfolio_backtest_dry_run_contract(contract)
    allowed = _mapping(contract.dry_run_scope.get("allowed"), "dry_run_scope.allowed")
    disallowed = _mapping(contract.dry_run_scope.get("disallowed"), "dry_run_scope.disallowed")
    output_schema = _mapping(contract.dry_run_output_schema, "dry_run_output_schema")
    stdout_contract = _mapping(contract.stdout_contract, "stdout_contract")
    next_phase = contract.recommended_next_phase
    return {
        "version": contract.version,
        "status": contract.status,
        "allowed_scope_count": len(allowed),
        "disallowed_scope_count": len(disallowed),
        "prohibited_output_field_count": len(
            _str_list(output_schema.get("prohibited_fields"), "dry_run_output_schema.prohibited_fields")
        ),
        "stdout_required_line_count": len(
            _str_list(stdout_contract.get("required_lines"), "stdout_contract.required_lines")
        ),
        "compute_returns_allowed": not bool(disallowed["compute_returns"]),
        "allocation_output_allowed": not bool(disallowed["compute_live_allocation"]),
        "trade_signal_output_allowed": not bool(disallowed["produce_trade_signal"]),
        "data_backtests_output_allowed": not bool(disallowed["write_data_backtests_output"]),
        "public_output_allowed": not bool(disallowed["write_public_output"]),
        "recommended_next_phase": next_phase["phase_id"],
        "reason": " ".join(str(next_phase["reason_zh"]).split()),
    }


def load_portfolio_backtest_dry_run_fixtures(
    path: str | Path,
) -> PortfolioBacktestDryRunFixtures:
    """Load portfolio backtest dry-run fixtures YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise PortfolioBacktestDryRunContractError(
            f"portfolio_backtest_dry_run_fixtures file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PortfolioBacktestDryRunContractError(f"Invalid YAML in {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_fixtures YAML must be a mapping"
        )
    raw = payload.get("portfolio_backtest_dry_run_fixtures")
    if not isinstance(raw, dict):
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_fixtures YAML must contain a mapping"
        )
    return _fixtures_from_mapping({str(key): value for key, value in raw.items()})


def validate_portfolio_backtest_dry_run_output(
    output: dict[str, Any],
    contract: PortfolioBacktestDryRunContract,
) -> None:
    """Validate one dry-run structural output object against the contract."""

    if not isinstance(output, dict):
        raise PortfolioBacktestDryRunContractError("dry-run output must be a mapping")
    allowed_fields = _str_list(
        contract.dry_run_output_schema.get("allowed_fields"),
        "dry_run_output_schema.allowed_fields",
    )
    required = (
        "dry_run_id",
        "backtest_input_id",
        "scenario_id",
        "policy_template_id",
        "parameter_set_id",
        "validation_status",
        "structural_summary",
        "required_metric_count",
        "required_input_count",
        "caveats_zh",
        "next_required_phase",
    )
    missing = [field for field in required if field not in output or field not in allowed_fields]
    if missing:
        raise PortfolioBacktestDryRunContractError(
            f"dry-run output missing required field(s): {', '.join(missing)}"
        )
    prohibited = set(
        _str_list(
            contract.dry_run_output_schema.get("prohibited_fields"),
            "dry_run_output_schema.prohibited_fields",
        )
    )
    _validate_no_prohibited_fields(output, prohibited)
    _validate_structural_summary(output)
    _validate_output_caveats(output)
    _validate_no_prohibited_text(output, contract)


def validate_portfolio_backtest_dry_run_fixtures(
    fixtures: PortfolioBacktestDryRunFixtures,
    contract: PortfolioBacktestDryRunContract,
) -> PortfolioBacktestDryRunFixtureValidationSummary:
    """Validate all valid and invalid dry-run output fixtures."""

    unexpected_valid_failures: list[dict[str, str]] = []
    unexpected_invalid_passes: list[str] = []
    expected_error_mismatches: list[dict[str, str]] = []
    valid_pass_count = 0
    invalid_rejected_count = 0

    for fixture in fixtures.valid_dry_run_outputs:
        fixture_id = str(fixture.get("fixture_id") or "")
        try:
            validate_portfolio_backtest_dry_run_output(_fixture_output(fixture, fixture_id), contract)
        except PortfolioBacktestDryRunContractError as exc:
            unexpected_valid_failures.append({"fixture_id": fixture_id, "error": str(exc)})
        else:
            valid_pass_count += 1

    for fixture in fixtures.invalid_dry_run_outputs:
        fixture_id = str(fixture.get("fixture_id") or "")
        expected = str(fixture.get("expected_error_contains") or "")
        try:
            validate_portfolio_backtest_dry_run_output(_fixture_output(fixture, fixture_id), contract)
        except PortfolioBacktestDryRunContractError as exc:
            invalid_rejected_count += 1
            error = str(exc)
            if expected and expected not in error:
                expected_error_mismatches.append(
                    {"fixture_id": fixture_id, "expected": expected, "error": error}
                )
        else:
            unexpected_invalid_passes.append(fixture_id)

    return PortfolioBacktestDryRunFixtureValidationSummary(
        contract_version=contract.version,
        fixtures_version=fixtures.version,
        valid_output_count=len(fixtures.valid_dry_run_outputs),
        invalid_output_count=len(fixtures.invalid_dry_run_outputs),
        valid_pass_count=valid_pass_count,
        invalid_rejected_count=invalid_rejected_count,
        unexpected_valid_failures=unexpected_valid_failures,
        unexpected_invalid_passes=unexpected_invalid_passes,
        expected_error_mismatches=expected_error_mismatches,
        output_written=False,
        data_backtests_output_written=False,
        public_output_written=False,
        allocation_output_generated=False,
        trade_signal_generated=False,
    )


def _contract_from_mapping(payload: dict[str, Any]) -> PortfolioBacktestDryRunContract:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "input_contracts",
        "dry_run_scope",
        "dry_run_input_schema",
        "dry_run_output_schema",
        "stdout_contract",
        "required_acceptance_before_dry_run_fixtures",
        "recommended_next_phase",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_contract missing required field(s): "
            f"{', '.join(missing)}"
        )
    return PortfolioBacktestDryRunContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        input_contracts=_mapping_of_mappings(payload["input_contracts"], "input_contracts"),
        dry_run_scope=_mapping_of_mappings(payload["dry_run_scope"], "dry_run_scope"),
        dry_run_input_schema=_mapping(payload["dry_run_input_schema"], "dry_run_input_schema"),
        dry_run_output_schema=_mapping(payload["dry_run_output_schema"], "dry_run_output_schema"),
        stdout_contract=_mapping(payload["stdout_contract"], "stdout_contract"),
        required_acceptance_before_dry_run_fixtures=_list_of_mappings(
            payload["required_acceptance_before_dry_run_fixtures"],
            "required_acceptance_before_dry_run_fixtures",
        ),
        recommended_next_phase=_mapping(payload["recommended_next_phase"], "recommended_next_phase"),
    )


def _fixtures_from_mapping(payload: dict[str, Any]) -> PortfolioBacktestDryRunFixtures:
    required = (
        "version",
        "status",
        "dry_run_contract_path",
        "backtest_input_contract_path",
        "backtest_input_fixtures_path",
        "objective_zh",
        "caveats_zh",
        "valid_dry_run_outputs",
        "invalid_dry_run_outputs",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise PortfolioBacktestDryRunContractError(
            "portfolio_backtest_dry_run_fixtures missing required field(s): "
            f"{', '.join(missing)}"
        )
    return PortfolioBacktestDryRunFixtures(
        version=int(payload["version"]),
        status=str(payload["status"]),
        dry_run_contract_path=str(payload["dry_run_contract_path"]),
        backtest_input_contract_path=str(payload["backtest_input_contract_path"]),
        backtest_input_fixtures_path=str(payload["backtest_input_fixtures_path"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        valid_dry_run_outputs=_list_of_mappings(
            payload["valid_dry_run_outputs"],
            "valid_dry_run_outputs",
        ),
        invalid_dry_run_outputs=_list_of_mappings(
            payload["invalid_dry_run_outputs"],
            "invalid_dry_run_outputs",
        ),
    )


def _validate_disallowed_scope(dry_run_scope: dict[str, dict[str, Any]]) -> None:
    disallowed = _mapping(dry_run_scope.get("disallowed"), "dry_run_scope.disallowed")
    for field in (
        "compute_returns",
        "compute_live_allocation",
        "produce_trade_signal",
        "write_data_backtests_output",
        "write_public_output",
    ):
        if disallowed.get(field) is not True:
            raise PortfolioBacktestDryRunContractError(f"dry_run_scope.disallowed.{field} must be true")


def _validate_output_schema(output_schema: dict[str, Any]) -> None:
    prohibited = set(
        _str_list(
            output_schema.get("prohibited_fields"),
            "dry_run_output_schema.prohibited_fields",
        )
    )
    for field in (
        "total_return",
        "max_drawdown",
        "turnover",
        "portfolio_weights",
        "allocation",
        "target_weight",
        "buy_signal",
        "sell_signal",
        "portfolio_action",
        "public_dashboard_output",
    ):
        if field not in prohibited:
            raise PortfolioBacktestDryRunContractError(
                f"dry_run_output_schema.prohibited_fields must include {field}"
            )
    caveats = _str_list(
        output_schema.get("required_caveats_zh"),
        "dry_run_output_schema.required_caveats_zh",
    )
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioBacktestDryRunContractError(
            "dry_run_output_schema.required_caveats_zh must include 不構成投資建議"
        )


def _validate_stdout_contract(stdout_contract: dict[str, Any]) -> None:
    required_lines = set(
        _str_list(stdout_contract.get("required_lines"), "stdout_contract.required_lines")
    )
    for line in (
        "output_written=false",
        "data_backtests_output_written=false",
        "public_output_written=false",
        "allocation_output_generated=false",
        "trade_signal_generated=false",
        "result=passed",
    ):
        if line not in required_lines:
            raise PortfolioBacktestDryRunContractError(
                f"stdout_contract.required_lines must include {line}"
            )
    patterns = _mapping_of_str_lists(
        stdout_contract.get("prohibited_text_patterns"),
        "stdout_contract.prohibited_text_patterns",
    )
    flattened = {pattern for values in patterns.values() for pattern in values}
    for pattern in ("買進訊號", "賣出訊號", "buy signal", "sell signal", "target weight"):
        if pattern not in flattened:
            raise PortfolioBacktestDryRunContractError(
                f"stdout_contract.prohibited_text_patterns must include {pattern}"
            )


def _validate_caveats(caveats: list[str]) -> None:
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioBacktestDryRunContractError("caveats_zh must include 不構成投資建議")


def _validate_no_prohibited_fields(value: Any, prohibited_fields: set[str], path: str = "") -> None:
    if isinstance(value, dict):
        for key, raw in value.items():
            key_text = str(key)
            current_path = f"{path}.{key_text}" if path else key_text
            if key_text in prohibited_fields:
                raise PortfolioBacktestDryRunContractError(
                    f"prohibited field {key_text} found at {current_path}"
                )
            _validate_no_prohibited_fields(raw, prohibited_fields, current_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_no_prohibited_fields(item, prohibited_fields, f"{path}[{index}]")


def _validate_structural_summary(output: dict[str, Any]) -> None:
    summary = _mapping(output.get("structural_summary"), "structural_summary")
    for field in (
        "output_written",
        "data_backtests_output_written",
        "public_output_written",
        "allocation_generated",
        "trade_signal_generated",
    ):
        if summary.get(field) is not False:
            raise PortfolioBacktestDryRunContractError(f"structural_summary.{field} must be false")


def _validate_output_caveats(output: dict[str, Any]) -> None:
    caveats = _str_list(output.get("caveats_zh"), "caveats_zh")
    if not any("不構成投資建議" in caveat for caveat in caveats):
        raise PortfolioBacktestDryRunContractError("caveats_zh must include 不構成投資建議")


def _validate_no_prohibited_text(
    output: dict[str, Any],
    contract: PortfolioBacktestDryRunContract,
) -> None:
    patterns_by_language = _mapping_of_str_lists(
        contract.stdout_contract.get("prohibited_text_patterns"),
        "stdout_contract.prohibited_text_patterns",
    )
    patterns = [pattern for values in patterns_by_language.values() for pattern in values]
    for path, text in _iter_text_fields(output):
        lowered = text.lower()
        for pattern in patterns:
            if pattern.lower() in lowered:
                raise PortfolioBacktestDryRunContractError(
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


def _fixture_output(fixture: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    output = fixture.get("output")
    if not isinstance(output, dict):
        raise PortfolioBacktestDryRunContractError(f"{fixture_id}.output must be a mapping")
    return {str(key): raw for key, raw in output.items()}


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioBacktestDryRunContractError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _mapping_of_mappings(value: Any, field: str) -> dict[str, dict[str, Any]]:
    mapping = _mapping(value, field)
    result: dict[str, dict[str, Any]] = {}
    for key, raw in mapping.items():
        if not isinstance(raw, dict):
            raise PortfolioBacktestDryRunContractError(f"{field}.{key} must be a mapping")
        result[key] = {str(child_key): child_raw for child_key, child_raw in raw.items()}
    return result


def _mapping_of_str_lists(value: Any, field: str) -> dict[str, list[str]]:
    mapping = _mapping(value, field)
    return {key: _str_list(raw, f"{field}.{key}") for key, raw in mapping.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise PortfolioBacktestDryRunContractError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise PortfolioBacktestDryRunContractError(f"{field}[{index}] must be a mapping")
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PortfolioBacktestDryRunContractError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise PortfolioBacktestDryRunContractError(f"{field} must not contain empty items")
    return result
