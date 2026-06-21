"""Controlled in-memory real backtest prototype for fixture data."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import pstdev
from typing import Any

import yaml


class ControlledRealBacktestPrototypeError(ValueError):
    """Raised when controlled real backtest prototype validation fails."""


@dataclass(frozen=True)
class ControlledRealBacktestPrototypeFixtures:
    """Controlled prototype fixture bundle."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    prototype_cases: list[dict[str, Any]]
    required_metric_ids: list[str]
    prohibited_fixture_fields: list[str]


@dataclass(frozen=True)
class ControlledBacktestCaseResult:
    """In-memory controlled backtest case result."""

    case_id: str
    scenario_id: str
    policy_template_id: str
    parameter_set_id: str
    portfolio_value_path: list[float]
    portfolio_returns: list[float]
    metrics: dict[str, float]


@dataclass(frozen=True)
class ControlledRealBacktestPrototypeRunResult:
    """In-memory controlled prototype aggregate result."""

    fixtures_version: int
    fixtures_status: str
    case_results: list[ControlledBacktestCaseResult]
    required_metric_ids: list[str]


def load_controlled_real_backtest_prototype_fixtures(
    path: str | Path,
) -> ControlledRealBacktestPrototypeFixtures:
    """Load controlled real backtest prototype fixtures YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise ControlledRealBacktestPrototypeError(
            f"controlled_real_backtest_prototype_fixtures file does not exist: {yaml_path}"
        )
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ControlledRealBacktestPrototypeError(
            f"Invalid YAML in {yaml_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise ControlledRealBacktestPrototypeError(
            "controlled_real_backtest_prototype_fixtures YAML must be a mapping"
        )
    raw = payload.get("controlled_real_backtest_prototype_fixtures")
    if not isinstance(raw, dict):
        raise ControlledRealBacktestPrototypeError(
            "controlled_real_backtest_prototype_fixtures YAML must contain a mapping"
        )
    fixtures = _fixtures_from_mapping({str(key): value for key, value in raw.items()})
    validate_controlled_prototype_fixtures(fixtures)
    return fixtures


def validate_controlled_prototype_fixtures(
    fixtures: ControlledRealBacktestPrototypeFixtures,
) -> None:
    """Validate controlled prototype fixtures."""

    if not isinstance(fixtures.version, int):
        raise ControlledRealBacktestPrototypeError(
            "version must exist and be an integer"
        )
    if not fixtures.status:
        raise ControlledRealBacktestPrototypeError("status must be non-empty")
    if not fixtures.prototype_cases:
        raise ControlledRealBacktestPrototypeError("prototype_cases must exist")
    _validate_required_metrics(fixtures.required_metric_ids)
    if not fixtures.prohibited_fixture_fields:
        raise ControlledRealBacktestPrototypeError("prohibited_fixture_fields must exist")
    for case in fixtures.prototype_cases:
        _validate_case(case, fixtures.prohibited_fixture_fields)
    if not any("不構成投資建議" in caveat for caveat in fixtures.caveats_zh):
        raise ControlledRealBacktestPrototypeError(
            "caveats_zh must include 不構成投資建議"
        )


def run_controlled_backtest_case(case: dict[str, Any]) -> ControlledBacktestCaseResult:
    """Run one controlled fixture case in memory."""

    _validate_case(case, [])
    stock_returns = _float_list(
        _mapping(case["asset_return_series"], "asset_return_series")["stock_return"],
        "asset_return_series.stock_return",
    )
    bond_returns = _float_list(
        _mapping(case["asset_return_series"], "asset_return_series")["bond_return"],
        "asset_return_series.bond_return",
    )
    stock_weights = _float_list(
        _mapping(case["backtest_policy_weights"], "backtest_policy_weights")["stock"],
        "backtest_policy_weights.stock",
    )
    bond_weights = _float_list(
        _mapping(case["backtest_policy_weights"], "backtest_policy_weights")["bond"],
        "backtest_policy_weights.bond",
    )
    portfolio_returns = [
        stock_weight * stock_return + bond_weight * bond_return
        for stock_weight, stock_return, bond_weight, bond_return in zip(
            stock_weights,
            stock_returns,
            bond_weights,
            bond_returns,
            strict=True,
        )
    ]
    initial_value = float(case["initial_value"])
    value_path = [initial_value]
    for portfolio_return in portfolio_returns:
        value_path.append(value_path[-1] * (1.0 + portfolio_return))

    metrics = {
        "total_return": value_path[-1] / initial_value - 1.0,
        "annualized_return": (value_path[-1] / initial_value) ** (
            12.0 / len(portfolio_returns)
        )
        - 1.0,
        "volatility": pstdev(portfolio_returns) * sqrt(12.0),
        "max_drawdown": _max_drawdown(value_path),
        "turnover": _turnover(stock_weights, bond_weights),
    }
    return ControlledBacktestCaseResult(
        case_id=str(case["case_id"]),
        scenario_id=str(case["scenario_id"]),
        policy_template_id=str(case["policy_template_id"]),
        parameter_set_id=str(case["parameter_set_id"]),
        portfolio_value_path=value_path,
        portfolio_returns=portfolio_returns,
        metrics=metrics,
    )


def run_controlled_real_backtest_prototype(
    fixtures: ControlledRealBacktestPrototypeFixtures,
) -> ControlledRealBacktestPrototypeRunResult:
    """Run all controlled fixture cases in memory."""

    validate_controlled_prototype_fixtures(fixtures)
    return ControlledRealBacktestPrototypeRunResult(
        fixtures_version=fixtures.version,
        fixtures_status=fixtures.status,
        case_results=[
            run_controlled_backtest_case(case) for case in fixtures.prototype_cases
        ],
        required_metric_ids=list(fixtures.required_metric_ids),
    )


def summarize_controlled_real_backtest_prototype(
    run_result: ControlledRealBacktestPrototypeRunResult,
) -> dict[str, Any]:
    """Summarize controlled prototype run without exposing a metric table."""

    case_count = len(run_result.case_results)
    computed_metric_ids = {
        metric_id
        for case_result in run_result.case_results
        for metric_id in case_result.metrics
    }
    required_metric_ids = set(run_result.required_metric_ids)
    result = "passed" if required_metric_ids.issubset(computed_metric_ids) else "failed"
    return {
        "version": run_result.fixtures_version,
        "status": run_result.fixtures_status,
        "case_count": case_count,
        "prototype_run_count": case_count,
        "computed_metric_count": len(computed_metric_ids),
        "required_metric_count": len(run_result.required_metric_ids),
        "in_memory_only": True,
        "controlled_metric_computation_allowed": True,
        "result_file_written": False,
        "data_backtests_output_written": False,
        "public_output_written": False,
        "output_directory_created": False,
        "allocation_output_generated": False,
        "trade_signal_generated": False,
        "live_recommendation_generated": False,
        "dashboard_integration": False,
        "result": result,
        "recommended_next_phase": "9B1",
        "reason": (
            "已完成 controlled in-memory prototype。下一步應定義 market return "
            "data contract，仍不得自動寫 output 或接 dashboard。"
        ),
    }


def _fixtures_from_mapping(payload: dict[str, Any]) -> ControlledRealBacktestPrototypeFixtures:
    required = (
        "version",
        "status",
        "objective_zh",
        "caveats_zh",
        "prototype_cases",
        "required_metric_ids",
        "prohibited_fixture_fields",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise ControlledRealBacktestPrototypeError(
            "controlled_real_backtest_prototype_fixtures missing required field(s): "
            f"{', '.join(missing)}"
        )
    return ControlledRealBacktestPrototypeFixtures(
        version=int(payload["version"]),
        status=str(payload["status"]),
        objective_zh=str(payload["objective_zh"]),
        caveats_zh=_str_list(payload["caveats_zh"], "caveats_zh"),
        prototype_cases=_list_of_mappings(payload["prototype_cases"], "prototype_cases"),
        required_metric_ids=_str_list(payload["required_metric_ids"], "required_metric_ids"),
        prohibited_fixture_fields=_str_list(
            payload["prohibited_fixture_fields"],
            "prohibited_fixture_fields",
        ),
    )


def _validate_required_metrics(metric_ids: list[str]) -> None:
    required = {
        "total_return",
        "annualized_return",
        "volatility",
        "max_drawdown",
        "turnover",
    }
    missing = sorted(required - set(metric_ids))
    if missing:
        raise ControlledRealBacktestPrototypeError(
            f"required_metric_ids missing metric(s): {', '.join(missing)}"
        )


def _validate_case(case: dict[str, Any], prohibited_fields: list[str]) -> None:
    if prohibited_fields:
        _reject_prohibited_fields(case, prohibited_fields)
    _reject_prohibited_text(case)
    if case.get("data_mode") != "controlled_fixture_only":
        raise ControlledRealBacktestPrototypeError(
            "prototype case data_mode must be controlled_fixture_only"
        )
    if case.get("backtest_only") is not True:
        raise ControlledRealBacktestPrototypeError("prototype case backtest_only must be true")
    behavior = _mapping(case.get("expected_behavior"), "expected_behavior")
    if behavior.get("in_memory_only") is not True:
        raise ControlledRealBacktestPrototypeError(
            "expected_behavior.in_memory_only must be true"
        )
    if behavior.get("controlled_metric_computation_allowed") is not True:
        raise ControlledRealBacktestPrototypeError(
            "expected_behavior.controlled_metric_computation_allowed must be true"
        )
    for field in (
        "output_write_allowed",
        "public_output_allowed",
        "allocation_output_allowed",
        "trade_signal_allowed",
    ):
        if behavior.get(field) is not False:
            raise ControlledRealBacktestPrototypeError(
                f"expected_behavior.{field} must be false"
            )
    _validate_series_lengths(case)


def _validate_series_lengths(case: dict[str, Any]) -> None:
    periods = _str_list(case.get("periods"), "periods")
    returns = _mapping(case.get("asset_return_series"), "asset_return_series")
    weights = _mapping(case.get("backtest_policy_weights"), "backtest_policy_weights")
    series = {
        "asset_return_series.stock_return": _float_list(
            returns.get("stock_return"),
            "asset_return_series.stock_return",
        ),
        "asset_return_series.bond_return": _float_list(
            returns.get("bond_return"),
            "asset_return_series.bond_return",
        ),
        "backtest_policy_weights.stock": _float_list(
            weights.get("stock"),
            "backtest_policy_weights.stock",
        ),
        "backtest_policy_weights.bond": _float_list(
            weights.get("bond"),
            "backtest_policy_weights.bond",
        ),
    }
    for field, values in series.items():
        if len(values) != len(periods):
            raise ControlledRealBacktestPrototypeError(
                f"{field} length must match periods length"
            )


def _reject_prohibited_fields(value: Any, prohibited_fields: list[str]) -> None:
    prohibited = set(prohibited_fields)
    for path, nested in _walk_nested(value):
        if path and path[-1] in prohibited:
            raise ControlledRealBacktestPrototypeError(
                f"prohibited fixture field present: {path[-1]}"
            )
        if isinstance(nested, str):
            for field in prohibited:
                if field in nested:
                    raise ControlledRealBacktestPrototypeError(
                        f"prohibited fixture field text present: {field}"
                    )


def _reject_prohibited_text(value: Any) -> None:
    patterns = (
        "目前建議",
        "建議買進",
        "建議賣出",
        "買進訊號",
        "賣出訊號",
        "target weight",
        "buy signal",
        "sell signal",
        "investment advice",
    )
    for _path, nested in _walk_nested(value):
        if isinstance(nested, str):
            for pattern in patterns:
                if pattern in nested:
                    raise ControlledRealBacktestPrototypeError(
                        f"prohibited text pattern present: {pattern}"
                    )


def _max_drawdown(value_path: list[float]) -> float:
    peak = value_path[0]
    max_drawdown = 0.0
    for value in value_path:
        peak = max(peak, value)
        drawdown = value / peak - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown


def _turnover(stock_weights: list[float], bond_weights: list[float]) -> float:
    turnover = 0.0
    for index in range(1, len(stock_weights)):
        turnover += (
            abs(stock_weights[index] - stock_weights[index - 1])
            + abs(bond_weights[index] - bond_weights[index - 1])
        ) / 2.0
    return turnover


def _walk_nested(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, nested in value.items():
            items.extend(_walk_nested(nested, (*path, str(key))))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            items.extend(_walk_nested(nested, (*path, str(index))))
    return items


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ControlledRealBacktestPrototypeError(f"{field} must be a mapping")
    return {str(key): raw for key, raw in value.items()}


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ControlledRealBacktestPrototypeError(f"{field} must be a non-empty list")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ControlledRealBacktestPrototypeError(
                f"{field}[{index}] must be a mapping"
            )
        result.append({str(key): raw for key, raw in item.items()})
    return result


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ControlledRealBacktestPrototypeError(f"{field} must be a non-empty list")
    result = [str(item) for item in value]
    if any(not item for item in result):
        raise ControlledRealBacktestPrototypeError(f"{field} must not contain empty items")
    return result


def _float_list(value: Any, field: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise ControlledRealBacktestPrototypeError(f"{field} must be a non-empty list")
    try:
        return [float(item) for item in value]
    except (TypeError, ValueError) as exc:
        raise ControlledRealBacktestPrototypeError(
            f"{field} must contain numeric values"
        ) from exc
