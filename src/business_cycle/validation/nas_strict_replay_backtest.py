"""Phase 125 strict PIT evidence replay and research backtest execution."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Protocol

import yaml

from business_cycle.data_sources.base import SeriesObservation
from business_cycle.data_sources.fred_provider import FredProvider
from business_cycle.portfolio.cash_flow_research_backtest import (
    run_cash_flow_research_backtest,
)
from business_cycle.storage.nas_live_postgres_dashboard import PsqlReadOnlyExecutor
from business_cycle.storage.nas_strict_replay_input_timeline import (
    DEFAULT_STATUS_PATH as DEFAULT_TIMELINE_PATH,
    load_nas_strict_replay_input_timeline_status,
)
from business_cycle.service.nas_v1_operational_acceptance import (
    persist_strict_replay_artifact,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
    load_nas_live_ordered_cycle_evidence_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_strict_replay_backtest_contract.yaml"
DEFAULT_STATUS_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase125/"
    "latest-strict-replay-backtest.json"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "current_allocation",
    "target_weight",
    "target_weights",
}


class StrictReplayExecutor(Protocol):
    def query_json(self, sql: str) -> dict[str, Any]: ...


class MarketDataProvider(Protocol):
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]: ...


def load_nas_strict_replay_backtest_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_strict_replay_backtest_contract"])


def build_nas_strict_replay_backtest(
    *,
    executor: StrictReplayExecutor,
    market_provider: MarketDataProvider,
    timeline_status: dict[str, Any],
    generated_at: datetime | None = None,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Execute only complete strict months and explicit research parameters."""

    contract = load_nas_strict_replay_backtest_contract(contract_path)
    timeline_rows = list(timeline_status.get("timeline_rows", []))
    complete_rows = [row for row in timeline_rows if not row["abstention_required"]]
    blocked_rows = [row for row in timeline_rows if row["abstention_required"]]
    complete_scenarios = sorted({str(row["scenario_id"]) for row in complete_rows})
    all_scenarios = sorted({str(row["scenario_id"]) for row in timeline_rows})
    evidence_payload = executor.query_json(_strict_evidence_sql(complete_rows))
    if str(evidence_payload.get("transaction_read_only", "")).lower() not in {
        "on",
        "true",
    }:
        raise RuntimeError("Phase 125 strict replay query is not read-only")
    evidence_rows = _execute_evidence_replay(
        complete_rows=complete_rows,
        source_rows=list(evidence_payload.get("observation_rows", [])),
    )
    market_panel, market_lineage = _build_market_panel(
        provider=market_provider,
        contract=contract,
    )
    parameter_runs = _parameter_runs()
    results: list[dict[str, Any]] = []
    market_blocked_scenarios: list[str] = []
    for scenario_id in complete_scenarios:
        periods = sorted(
            str(row["as_of"])
            for row in complete_rows
            if str(row["scenario_id"]) == scenario_id
        )
        if any(period not in market_panel for period in periods):
            market_blocked_scenarios.append(scenario_id)
            continue
        for parameter in parameter_runs:
            results.append(
                run_cash_flow_research_backtest(
                    scenario_id=scenario_id,
                    policy_template_id=parameter["policy_template_id"],
                    parameter_id=parameter["parameter_id"],
                    periods=periods,
                    asset_returns=market_panel,
                    equity_parameter=parameter["equity_parameter"],
                    defensive_asset=parameter["defensive_asset"],
                    initial_value=float(
                        contract["backtest_assumptions"]["initial_value"]
                    ),
                    annual_contribution=float(
                        contract["backtest_assumptions"]["annual_contribution"]
                    ),
                    transaction_cost_bps=float(
                        contract["backtest_assumptions"]["transaction_cost_bps"]
                    ),
                )
            )
    generated = generated_at or datetime.now(timezone.utc)
    artifact: dict[str, Any] = {
        "artifact_id": "phase125_strict_pit_replay_backtest_v1",
        "artifact_version": contract["version"],
        "phase": 125,
        "phase_id": 125,
        "generated_at_utc": generated.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "nas_strict_replay_backtest_contract_ready": (
            contract["status"] == "active_private_nas_research_execution"
            and contract["strict_replay_policy"]["revised_fallback_allowed"]
            is False
            and contract["output_policy"]["no_tuning_from_results"] is True
        ),
        "strict_replay_scenario_count": len(all_scenarios),
        "strict_replay_complete_scenario_count": len(complete_scenarios),
        "strict_replay_blocked_scenario_count": len(all_scenarios)
        - len(complete_scenarios),
        "strict_replay_executed_month_count": len(complete_rows),
        "strict_replay_abstention_month_count": len(blocked_rows),
        "evidence_replay_output_count": len(evidence_rows),
        "evidence_replay_rows": evidence_rows,
        "blocked_scenario_rows": _blocked_scenario_rows(timeline_rows),
        "market_data_source_count": len(contract["market_data_policy"]["sources"]),
        "source_substitution_risk_disclosed_count": sum(
            bool(row.get("data_risk"))
            for row in contract["market_data_policy"]["sources"].values()
        ),
        "market_data_lineage": market_lineage,
        "market_data_blocked_scenarios": market_blocked_scenarios,
        "cash_flow_aware_kernel_ready": True,
        "research_backtest_results": results,
        "research_backtest_result_count": len(results),
        "unitized_nav_result_count": sum(
            bool(row["monthly_rows"]) for row in results
        ),
        "xirr_result_count": sum(
            row["metrics"]["money_weighted_return_xirr"] is not None
            for row in results
        ),
        "dynamic_transition_policy_execution_count": 0,
        "dynamic_transition_policy_blocked_reason": (
            contract["backtest_assumptions"][
                "historical_transition_timeline_blocker"
            ]
        ),
        "book_benchmark_result_count": 0,
        "revised_fallback_count": 0,
        "historical_label_used_count": 0,
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "semantic_drift_count": 0,
        "trust_metadata": {
            "strict_timeline_hash": timeline_status.get("timeline_hash"),
            "strict_macro_inputs_are_point_in_time": True,
            "market_returns_are_realized_research_outcomes_not_runtime_inputs": True,
            "equity_proxy_is_not_book_benchmark": True,
            "long_treasury_is_modeled_proxy": True,
            "dynamic_transition_policy_executed": False,
            "results_used_for_rule_tuning": False,
        },
        "allowed_uses": [
            "private_historical_evidence_replay",
            "constant_parameter_portfolio_sensitivity_research",
            "cash_flow_methodology_validation",
        ],
        "prohibited_uses": [
            "current_allocation_instruction",
            "trade_action",
            "book_benchmark_claim",
            "historical_rule_tuning",
            "future_performance_claim",
        ],
    }
    artifact["prohibited_output_field_count"] = _recursive_key_count(
        artifact, PROHIBITED_FIELDS
    )
    artifact["artifact_hash"] = _hash_payload(
        {
            "evidence_replay_rows": evidence_rows,
            "research_backtest_results": results,
            "market_data_lineage": market_lineage,
        }
    )
    artifact["result"] = (
        "passed"
        if _matches(artifact, contract["hard_gates"])
        and not market_blocked_scenarios
        and artifact["prohibited_output_field_count"] == 0
        else "blocked"
    )
    return artifact


def run_nas_strict_replay_backtest(
    *,
    execute_live: bool,
    output: str | Path,
    database_url: str | None = None,
    executor: StrictReplayExecutor | None = None,
    market_provider: MarketDataProvider | None = None,
    timeline_path: str | Path = DEFAULT_TIMELINE_PATH,
) -> dict[str, Any]:
    if not execute_live:
        raise ValueError("Phase 125 requires --execute-live")
    output_path = _validated_output_path(output)
    reader = executor or PsqlReadOnlyExecutor(
        database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", ""),
        statement_timeout_milliseconds=120000,
    )
    artifact = build_nas_strict_replay_backtest(
        executor=reader,
        market_provider=market_provider or FredProvider(timeout_seconds=60.0),
        timeline_status=load_nas_strict_replay_input_timeline_status(timeline_path),
    )
    return persist_strict_replay_artifact(output_path, artifact)


def load_nas_strict_replay_backtest_status(
    path: str | Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return {
            "artifact_version": "phase125_strict_pit_replay_backtest_v1",
            "result": "not_started",
            "strict_replay_complete_scenario_count": 0,
            "research_backtest_result_count": 0,
        }
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid Phase 125 replay/backtest status")
    return payload


def _execute_evidence_replay(
    *,
    complete_rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        grouped[
            (str(row["scenario_id"]), str(row["as_of"]), str(row["series_key"]))
        ].append(row)
    role_contracts = load_nas_live_ordered_cycle_evidence_contract()[
        "role_evaluators"
    ]
    outputs = []
    for timeline_row in complete_rows:
        scenario_id = str(timeline_row["scenario_id"])
        as_of = str(timeline_row["as_of"])
        roles = []
        for role_id, role_contract in role_contracts.items():
            inputs = []
            for series_id in role_contract["required_series_ids"]:
                rows = grouped.get((scenario_id, as_of, str(series_id)), [])
                inputs.append(
                    {
                        "series_id": str(series_id),
                        "observations": [
                            {
                                "date": str(row["observation_date"]),
                                "value": float(row["value_numeric"]),
                                "source_artifact_id": row["source_artifact_id"],
                                "provenance_hash": row["provenance_hash"],
                            }
                            for row in rows
                            if row.get("value_numeric") is not None
                        ],
                    }
                )
            roles.append(
                {
                    "role_id": role_id,
                    "snapshot_status": "vintage_snapshot_ready",
                    "freshness_status": "historical_as_of",
                    "evidence_input_series": inputs,
                    "source_lineage": [
                        {
                            "source_mode": "postgres_observation_vintage",
                            "scenario_id": scenario_id,
                            "as_of": as_of,
                        }
                    ],
                }
            )
        replay = build_live_ordered_cycle_evidence(
            {
                "snapshot_as_of": as_of,
                "data_mode": "vintage_as_of",
                "role_snapshots": roles,
                "declared_cycle_state": {
                    "declared_current_phase": "boom",
                    "legal_next_phase": "recession",
                },
            }
        )
        outputs.append(
            {
                "scenario_id": scenario_id,
                "as_of": as_of,
                "data_mode": "vintage_as_of",
                "lane_states": {
                    lane_id: lane["lane_status"]
                    for lane_id, lane in replay["lanes"].items()
                },
                "role_states": {
                    role_id: role["evidence_status"]
                    for role_id, role in replay["role_evidence"].items()
                },
                "explicit_abstention_role_count": replay[
                    "explicit_abstention_role_count"
                ],
                "why_not_confirmation": replay["why_not_confirmation"],
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return outputs


def _build_market_panel(
    *,
    provider: MarketDataProvider,
    contract: dict[str, Any],
) -> tuple[dict[str, dict[str, float]], list[dict[str, Any]]]:
    policy = contract["market_data_policy"]
    by_asset: dict[str, list[SeriesObservation]] = {}
    lineage = []
    for asset, source in policy["sources"].items():
        rows = provider.fetch_series_observations(
            str(source["series_id"]),
            observation_start=str(policy["observation_start"]),
        )
        by_asset[str(asset)] = rows
        lineage.append(
            {
                "asset": asset,
                **source,
                "observation_count": sum(row.value != "." for row in rows),
                "source_url_without_secret": (
                    "https://fred.stlouisfed.org/series/" + str(source["series_id"])
                ),
            }
        )
    equity = _monthly_values(by_asset["equity"], aggregation="last")
    cash_rate = _monthly_values(by_asset["cash"], aggregation="average")
    treasury_yield = _monthly_values(
        by_asset["long_treasury_proxy"], aggregation="last"
    )
    months = sorted(set(equity) & set(cash_rate) & set(treasury_yield))
    panel: dict[str, dict[str, float]] = {}
    previous_equity: float | None = None
    previous_yield: float | None = None
    duration = float(policy["modeled_long_treasury_duration_years"])
    for month in months:
        equity_value = equity[month]
        yield_value = treasury_yield[month]
        if previous_equity is not None and previous_yield is not None:
            panel[month] = {
                "equity": equity_value / previous_equity - 1.0,
                "cash": cash_rate[month] / 1200.0,
                "long_treasury_proxy": (
                    previous_yield / 1200.0
                    - duration * (yield_value - previous_yield) / 100.0
                ),
            }
        previous_equity = equity_value
        previous_yield = yield_value
    return panel, lineage


def _monthly_values(
    rows: list[SeriesObservation],
    *,
    aggregation: str,
) -> dict[str, float]:
    grouped: dict[tuple[int, int], list[tuple[date, float]]] = defaultdict(list)
    for row in rows:
        if row.value == ".":
            continue
        day = date.fromisoformat(row.date)
        grouped[(day.year, day.month)].append((day, float(row.value)))
    output = {}
    for values in grouped.values():
        values.sort()
        month_end = date(
            values[-1][0].year,
            values[-1][0].month,
            _calendar_month_end(values[-1][0].year, values[-1][0].month),
        ).isoformat()
        output[month_end] = (
            sum(value for _, value in values) / len(values)
            if aggregation == "average"
            else values[-1][1]
        )
    return output


def _strict_evidence_sql(complete_rows: list[dict[str, Any]]) -> str:
    if not complete_rows:
        raise ValueError("no strict-complete rows available")
    month_values = ",\n".join(
        f"({_literal(str(row['scenario_id']))}, {_literal(str(row['as_of']))}::date)"
        for row in complete_rows
    )
    series_ids = sorted(
        {
            str(series_id)
            for role in load_nas_live_ordered_cycle_evidence_contract()[
                "role_evaluators"
            ].values()
            for series_id in role["required_series_ids"]
        }
    )
    series_values = ", ".join(_literal(series_id) for series_id in series_ids)
    return f"""
WITH replay_months(scenario_id, as_of) AS (VALUES
{month_values}
), selected AS (
  SELECT DISTINCT ON (
    m.scenario_id, m.as_of, v.series_key, v.observation_date
  ) m.scenario_id, m.as_of, v.series_key, v.observation_date,
    v.value_numeric, v.source_artifact_id, v.provenance_hash
  FROM replay_months m
  JOIN macro.observation_vintage v
    ON v.series_key IN ({series_values})
   AND v.observation_date <= m.as_of
   AND v.observation_date >= m.as_of - INTERVAL '25 months'
   AND v.realtime_start <= m.as_of
   AND (v.realtime_end IS NULL OR v.realtime_end >= m.as_of)
  ORDER BY m.scenario_id, m.as_of, v.series_key, v.observation_date,
           v.realtime_start DESC
)
SELECT json_build_object(
  'transaction_read_only', current_setting('transaction_read_only'),
  'observation_rows', COALESCE((SELECT json_agg(json_build_object(
    'scenario_id', scenario_id,
    'as_of', to_char(as_of, 'YYYY-MM-DD'),
    'series_key', series_key,
    'observation_date', to_char(observation_date, 'YYYY-MM-DD'),
    'value_numeric', value_numeric,
    'source_artifact_id', source_artifact_id,
    'provenance_hash', provenance_hash
  ) ORDER BY scenario_id, as_of, series_key, observation_date) FROM selected), '[]'::json)
)::text;
""".strip()


def _blocked_scenario_rows(timeline_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in timeline_rows:
        grouped[str(row["scenario_id"])].append(row)
    return [
        {
            "scenario_id": scenario_id,
            "month_count": len(rows),
            "strict_complete_month_count": sum(
                not row["abstention_required"] for row in rows
            ),
            "strict_abstention_month_count": sum(
                row["abstention_required"] for row in rows
            ),
            "backtest_execution_status": (
                "strict_pit_ready_for_constant_parameter_research"
                if all(not row["abstention_required"] for row in rows)
                else "abstained_missing_official_pit_inputs"
            ),
        }
        for scenario_id, rows in sorted(grouped.items())
    ]


def _parameter_runs() -> list[dict[str, Any]]:
    return [
        _parameter("passive_all_stock_baseline", "passive_equity_100", 1.0, "cash"),
        _parameter("stock_cash_initial", "stock_cash_50", 0.5, "cash"),
        _parameter("stock_cash_advanced", "stock_cash_70", 0.7, "cash"),
        _parameter(
            "stock_long_treasury_initial",
            "stock_treasury_50",
            0.5,
            "long_treasury_proxy",
        ),
        _parameter(
            "stock_long_treasury_advanced",
            "stock_treasury_70",
            0.7,
            "long_treasury_proxy",
        ),
        _parameter("boom_70_50_30_template", "boom_cash_70", 0.7, "cash"),
        _parameter("boom_70_50_30_template", "boom_cash_50", 0.5, "cash"),
        _parameter("boom_70_50_30_template", "boom_cash_30", 0.3, "cash"),
    ]


def _parameter(
    template: str,
    parameter: str,
    equity: float,
    defensive_asset: str,
) -> dict[str, Any]:
    return {
        "policy_template_id": template,
        "parameter_id": parameter,
        "equity_parameter": equity,
        "defensive_asset": defensive_asset,
    }


def _validated_output_path(path: str | Path) -> Path:
    output = Path(path)
    resolved = output.resolve()
    allowed = (
        resolved.as_posix().startswith("/tmp/")
        or resolved.as_posix().startswith(
            "/var/lib/business-cycle/source-artifacts/phase125/"
        )
    )
    if not output.is_absolute() or not allowed:
        raise ValueError("Phase 125 output must be under /tmp or phase125 artifacts")
    return output


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


def _calendar_month_end(year: int, month: int) -> int:
    next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
    return (next_month - date.resolution).day


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _matches(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _recursive_key_count(value: Any, prohibited: set[str]) -> int:
    if isinstance(value, dict):
        return sum(key in prohibited for key in value) + sum(
            _recursive_key_count(item, prohibited) for item in value.values()
        )
    if isinstance(value, list):
        return sum(_recursive_key_count(item, prohibited) for item in value)
    return 0


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Run the governed Phase 125 execution from an installed NAS image."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    artifact = run_nas_strict_replay_backtest(
        execute_live=args.execute_live,
        output=args.output,
    )
    for key in (
        "result",
        "strict_replay_complete_scenario_count",
        "strict_replay_blocked_scenario_count",
        "strict_replay_executed_month_count",
        "strict_replay_abstention_month_count",
        "evidence_replay_output_count",
        "research_backtest_result_count",
        "unitized_nav_result_count",
        "xirr_result_count",
        "book_benchmark_result_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
    ):
        print(f"{key}={str(artifact[key]).lower()}")
    return 0 if artifact["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
