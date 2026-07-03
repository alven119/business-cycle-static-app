"""Portfolio policy replay schedule contract helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from business_cycle.portfolio.policy_research_baseline import REQUIRED_TEMPLATE_IDS

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPLAY_SCHEDULE_PATH = (
    ROOT / "specs/portfolio/portfolio_policy_replay_schedule_contract.yaml"
)

PROHIBITED_SCHEDULE_OUTPUT_FIELDS = {
    "current_allocation",
    "target_weight",
    "target_weights",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "rebalance_now",
    "live_allocation",
    "portfolio_action",
    "current_market_recommendation",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "standalone_phase_score",
}


class PortfolioPolicyReplayScheduleError(ValueError):
    """Raised when the replay schedule contract is invalid."""


@dataclass(frozen=True)
class PortfolioPolicyReplayScheduleContract:
    """Machine-readable portfolio policy replay schedule contract."""

    version: int
    status: str
    phase_id: int
    contract_id: str
    objective_zh: str
    dependencies: dict[str, Any]
    allowed_inputs: list[str]
    prohibited_inputs: list[str]
    output_policy: dict[str, Any]
    schedule_rows: list[dict[str, Any]]
    disabled_runtime_guards: dict[str, Any]
    hard_gates: dict[str, Any]


def load_portfolio_policy_replay_schedule_contract(
    path: str | Path = DEFAULT_REPLAY_SCHEDULE_PATH,
) -> PortfolioPolicyReplayScheduleContract:
    """Load the Phase77 replay schedule contract."""

    payload = _load_root_mapping(path)
    contract = PortfolioPolicyReplayScheduleContract(
        version=int(payload["version"]),
        status=str(payload["status"]),
        phase_id=int(payload["phase_id"]),
        contract_id=str(payload["contract_id"]),
        objective_zh=str(payload["objective_zh"]),
        dependencies=_mapping(payload["dependencies"], "dependencies"),
        allowed_inputs=_string_list(payload["allowed_inputs"], "allowed_inputs"),
        prohibited_inputs=_string_list(payload["prohibited_inputs"], "prohibited_inputs"),
        output_policy=_mapping(payload["output_policy"], "output_policy"),
        schedule_rows=_mapping_list(payload["schedule_rows"], "schedule_rows"),
        disabled_runtime_guards=_mapping(
            payload["disabled_runtime_guards"],
            "disabled_runtime_guards",
        ),
        hard_gates=_mapping(payload["hard_gates"], "hard_gates"),
    )
    validate_portfolio_policy_replay_schedule_contract(contract)
    return contract


def validate_portfolio_policy_replay_schedule_contract(
    contract: PortfolioPolicyReplayScheduleContract,
) -> None:
    """Validate replay schedule structure and disabled execution guards."""

    if contract.phase_id != 77:
        raise PortfolioPolicyReplayScheduleError("phase_id must be 77")
    if contract.status != "preregistered_research_schedule_only":
        raise PortfolioPolicyReplayScheduleError(
            "status must be preregistered_research_schedule_only"
        )
    if not contract.schedule_rows:
        raise PortfolioPolicyReplayScheduleError("schedule_rows must not be empty")
    missing = REQUIRED_TEMPLATE_IDS - _scheduled_template_ids(contract)
    if missing:
        raise PortfolioPolicyReplayScheduleError(
            f"schedule missing required templates: {', '.join(sorted(missing))}"
        )
    invalid = _scheduled_template_ids(contract) - REQUIRED_TEMPLATE_IDS
    if invalid:
        raise PortfolioPolicyReplayScheduleError(
            f"schedule contains invalid templates: {', '.join(sorted(invalid))}"
        )
    _validate_output_policy(contract.output_policy)
    _validate_disabled_guards(contract.disabled_runtime_guards)
    for row in contract.schedule_rows:
        _validate_schedule_row(row)


def summarize_portfolio_policy_replay_schedule(
    path: str | Path = DEFAULT_REPLAY_SCHEDULE_PATH,
) -> dict[str, Any]:
    """Return Phase77 replay schedule hard-gate fields."""

    contract = load_portfolio_policy_replay_schedule_contract(path)
    scheduled_ids = _scheduled_template_ids(contract)
    missing_ids = REQUIRED_TEMPLATE_IDS - scheduled_ids
    invalid_ids = scheduled_ids - REQUIRED_TEMPLATE_IDS
    schedule_row_count = len(contract.schedule_rows)
    template_with_schedule_count = len(scheduled_ids & REQUIRED_TEMPLATE_IDS)
    execution_allowed_now_count = sum(
        bool(row.get("execution_allowed_now")) for row in contract.schedule_rows
    )
    backtest_execution_count = sum(
        bool(row.get("backtest_execution_allowed")) for row in contract.schedule_rows
    )
    current_allocation_recommendation_count = sum(
        bool(row.get("current_allocation_recommendation_allowed"))
        for row in contract.schedule_rows
    )
    trade_signal_output_count = sum(
        bool(row.get("trade_signal_allowed")) for row in contract.schedule_rows
    )
    live_allocation_output_count = sum(
        bool(row.get("live_allocation_allowed")) for row in contract.schedule_rows
    )
    prohibited_schedule_output_field_count = sum(
        _schedule_row_prohibited_output_count(row) for row in contract.schedule_rows
    )
    disabled_guards = contract.disabled_runtime_guards
    summary: dict[str, Any] = {
        "phase": "77",
        "phase_id": 77,
        "portfolio_policy_replay_schedule_contract_ready": True,
        "contract_id": contract.contract_id,
        "schedule_row_count": schedule_row_count,
        "template_with_schedule_count": template_with_schedule_count,
        "missing_template_schedule_count": len(missing_ids),
        "invalid_template_reference_count": len(invalid_ids),
        "execution_allowed_now_count": execution_allowed_now_count,
        "backtest_execution_count": backtest_execution_count,
        "portfolio_policy_replay_execution_count": int(
            bool(disabled_guards.get("portfolio_policy_replay_execution_enabled"))
        ),
        "current_allocation_recommendation_count": (
            current_allocation_recommendation_count
        ),
        "trade_signal_output_count": trade_signal_output_count,
        "live_allocation_output_count": live_allocation_output_count,
        "prohibited_schedule_output_field_count": (
            prohibited_schedule_output_field_count
        ),
        "schedule_families": sorted(
            {str(row["schedule_family"]) for row in contract.schedule_rows}
        ),
        "scheduled_template_ids": sorted(scheduled_ids),
        "candidate_phase_emitted": bool(
            disabled_guards.get("candidate_phase_emission_enabled")
        ),
        "current_phase_emitted": bool(
            disabled_guards.get("current_phase_emission_enabled")
        ),
        "production_behavior_change_count": int(
            bool(disabled_guards.get("production_integration_enabled"))
        ),
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_policy_replay_schedule_ready"
        ),
        "portfolio_policy_research_alignment": (
            "policy_replay_schedule_preregistered_no_execution_or_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "policy_replay_schedule_ready_no_backtest_execution"
        ),
    }
    summary["result"] = "passed" if _passes(summary, contract.hard_gates) else "blocked"
    return summary


def build_portfolio_policy_replay_schedule_view_model(
    path: str | Path = DEFAULT_REPLAY_SCHEDULE_PATH,
) -> dict[str, Any]:
    """Build a dashboard/artifact-ready research schedule view model."""

    contract = load_portfolio_policy_replay_schedule_contract(path)
    return {
        "view_id": "portfolio_policy_replay_schedule",
        "view_title": "Portfolio Policy Replay Schedule",
        "output_mode": contract.output_policy["output_mode"],
        "research_only": True,
        "schedule_rows": contract.schedule_rows,
        "allowed_inputs": contract.allowed_inputs,
        "prohibited_inputs": contract.prohibited_inputs,
        "trust_metadata": {
            "source_contract": contract.contract_id,
            "template_schema_dependency": contract.dependencies["template_schema"],
            "template_fixture_dependency": contract.dependencies["template_fixtures"],
            "backtest_execution_enabled": False,
            "current_allocation_recommendation_enabled": False,
            "trade_signal_enabled": False,
        },
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
    }


def _load_root_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioPolicyReplayScheduleError("YAML must be a mapping")
    root = payload.get("portfolio_policy_replay_schedule_contract")
    if not isinstance(root, dict):
        raise PortfolioPolicyReplayScheduleError(
            "YAML must contain portfolio_policy_replay_schedule_contract"
        )
    return {str(key): value for key, value in root.items()}


def _validate_output_policy(output_policy: dict[str, Any]) -> None:
    if output_policy.get("output_mode") != "research_schedule_only":
        raise PortfolioPolicyReplayScheduleError(
            "output_policy.output_mode must be research_schedule_only"
        )
    for key in (
        "execution_allowed_now",
        "backtest_execution_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
        "public_output_allowed",
    ):
        if bool(output_policy.get(key)):
            raise PortfolioPolicyReplayScheduleError(f"output_policy.{key} must be false")
    prohibited = set(_string_list(output_policy.get("prohibited_fields"), "prohibited_fields"))
    missing = PROHIBITED_SCHEDULE_OUTPUT_FIELDS - prohibited
    if missing:
        raise PortfolioPolicyReplayScheduleError(
            f"output_policy.prohibited_fields missing: {', '.join(sorted(missing))}"
        )


def _validate_disabled_guards(disabled_guards: dict[str, Any]) -> None:
    for key in (
        "portfolio_policy_replay_execution_enabled",
        "backtest_execution_enabled",
        "current_allocation_recommendation_enabled",
        "live_allocation_enabled",
        "trade_signal_enabled",
        "candidate_phase_emission_enabled",
        "current_phase_emission_enabled",
        "production_integration_enabled",
    ):
        if bool(disabled_guards.get(key)):
            raise PortfolioPolicyReplayScheduleError(f"{key} must be false")


def _validate_schedule_row(row: dict[str, Any]) -> None:
    required = {
        "schedule_id",
        "template_id",
        "schedule_family",
        "research_trigger_context_zh",
        "allowed_state_inputs",
        "required_transition_inputs",
        "data_mode_policy",
        "rebalance_clock_policy",
        "cost_assumption_policy",
        "execution_allowed_now",
        "backtest_execution_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
        "caveats_zh",
    }
    missing = required - set(row)
    if missing:
        raise PortfolioPolicyReplayScheduleError(
            f"schedule row missing required fields: {', '.join(sorted(missing))}"
        )
    if str(row["template_id"]) not in REQUIRED_TEMPLATE_IDS:
        raise PortfolioPolicyReplayScheduleError(f"invalid template_id: {row['template_id']}")
    for key in (
        "execution_allowed_now",
        "backtest_execution_allowed",
        "current_allocation_recommendation_allowed",
        "trade_signal_allowed",
        "live_allocation_allowed",
    ):
        if bool(row.get(key)):
            raise PortfolioPolicyReplayScheduleError(
                f"{row['schedule_id']} must keep {key}=false"
            )
    if not row["allowed_state_inputs"]:
        raise PortfolioPolicyReplayScheduleError(
            f"{row['schedule_id']} must declare allowed_state_inputs"
        )
    if not row["caveats_zh"]:
        raise PortfolioPolicyReplayScheduleError(
            f"{row['schedule_id']} must declare caveats_zh"
        )


def _schedule_row_prohibited_output_count(row: dict[str, Any]) -> int:
    return sum(1 for field in PROHIBITED_SCHEDULE_OUTPUT_FIELDS if field in row)


def _scheduled_template_ids(contract: PortfolioPolicyReplayScheduleContract) -> set[str]:
    return {str(row.get("template_id")) for row in contract.schedule_rows}


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _mapping(raw: Any, field: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise PortfolioPolicyReplayScheduleError(f"{field} must be a mapping")
    return {str(key): value for key, value in raw.items()}


def _mapping_list(raw: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise PortfolioPolicyReplayScheduleError(f"{field} must be a list of mappings")
    return [{str(key): value for key, value in item.items()} for item in raw]


def _string_list(raw: Any, field: str) -> list[str]:
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise PortfolioPolicyReplayScheduleError(f"{field} must be a list of strings")
    return list(raw)
