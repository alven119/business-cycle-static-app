"""Phase 119 read-only monthly strict replay input timeline."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Protocol

import yaml

from business_cycle.storage.nas_live_postgres_dashboard import PsqlReadOnlyExecutor

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_strict_replay_input_timeline_contract.yaml"
)
SCENARIO_PATH = ROOT / "specs/audits/historical_validation_scenario_manifest.yaml"
SOURCE_SCOPE_PATH = ROOT / "specs/common/nas_postgres_live_revised_import_contract.yaml"
DEFAULT_STATUS_PATH = Path(
    "/var/lib/business-cycle/source-artifacts/phase119/"
    "latest-strict-replay-input-timeline.json"
)


class ReplayInputExecutor(Protocol):
    def query_json(self, sql: str) -> dict[str, Any]: ...


def load_nas_strict_replay_input_timeline_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_strict_replay_input_timeline_contract"])


def summarize_nas_strict_replay_input_timeline_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_nas_strict_replay_input_timeline_contract(path)
    policy = contract["replay_input_policy"]
    login = contract["lan_login_policy"]
    ux = contract["product_ux_blueprint"]
    summary = {
        "phase": 119,
        "nas_strict_replay_input_timeline_contract_ready": (
            contract["status"] == "active_private_nas_read_only_rehearsal"
            and policy["data_mode"] == "vintage_as_of"
            and policy["revised_fallback_allowed"] is False
            and policy["lookback_sufficiency_claim_allowed"] is False
        ),
        "scenario_count": int(policy["scenario_count"]),
        "expected_month_end_row_count": int(
            policy["expected_month_end_row_count"]
        ),
        "required_direct_series_count": int(
            policy["required_direct_series_count"]
        ),
        "private_lan_http_login_contract_ready": (
            login["private_lan_http_cookie_allowed"] is True
            and login["allowed_hosts"]
            == ["192.168.1.116", "192.168.1.116:18080"]
            and login["arbitrary_host_http_cookie_allowed"] is False
            and login["public_exposure_allowed"] is False
        ),
        "tailscale_https_secure_cookie_preserved": login[
            "tailscale_https_secure_cookie_required"
        ],
        "professional_dashboard_ux_blueprint_ready": (
            len(ux["primary_navigation"]) == 6
            and len(ux["indicator_detail_requirements"]) >= 9
            and len(ux["replay_lab_requirements"]) >= 8
            and len(ux["portfolio_research_requirements"]) >= 5
        ),
        "model_execution_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 120,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary


def build_nas_strict_replay_input_timeline(
    *,
    executor: ReplayInputExecutor,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Read PIT presence for every scenario month; never run a model."""

    contract = load_nas_strict_replay_input_timeline_contract()
    scenarios = _scenario_rows()
    series_ids = _direct_series_ids()
    payload = executor.query_json(_timeline_sql(scenarios, series_ids))
    if str(payload.get("transaction_read_only", "")).lower() not in {"on", "true"}:
        raise RuntimeError("strict replay input timeline session is not read-only")
    source_rows = payload.get("timeline_rows", [])
    if not isinstance(source_rows, list):
        raise RuntimeError("strict replay input timeline returned invalid rows")

    required = set(series_ids)
    rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        available = sorted(
            str(value) for value in source_row.get("available_series_ids", [])
        )
        missing = sorted(required.difference(available))
        rows.append(
            {
                "scenario_id": str(source_row["scenario_id"]),
                "as_of": str(source_row["as_of"]),
                "data_mode": "vintage_as_of",
                "required_series_count": len(series_ids),
                "available_series_count": len(available),
                "missing_series_count": len(missing),
                "available_series_ids": available,
                "missing_series_ids": missing,
                "replay_input_state": (
                    contract["replay_input_policy"]["complete_series_state"]
                    if not missing
                    else contract["replay_input_policy"]["missing_series_state"]
                ),
                "abstention_required": bool(missing),
                "blocked_reason_codes": (
                    ["missing_official_point_in_time_input"] if missing else []
                ),
                "lookback_sufficiency_claimed": False,
            }
        )
    rows.sort(key=lambda row: (row["scenario_id"], row["as_of"]))
    expected = int(contract["replay_input_policy"]["expected_month_end_row_count"])
    if len(rows) != expected:
        raise RuntimeError("strict replay input timeline row count mismatch")

    scenario_summaries = _scenario_summaries(rows, scenarios)
    generated = generated_at or datetime.now(timezone.utc)
    artifact: dict[str, Any] = {
        "artifact_version": "phase119_strict_replay_input_timeline_v1",
        "generated_at_utc": generated.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "data_mode": "vintage_as_of",
        "scenario_count": len(scenarios),
        "month_end_row_count": len(rows),
        "required_direct_series_count": len(series_ids),
        "complete_month_count": sum(not row["abstention_required"] for row in rows),
        "abstention_month_count": sum(row["abstention_required"] for row in rows),
        "scenario_summaries": scenario_summaries,
        "timeline_rows": rows,
        "transaction_read_only": True,
        "revised_fallback_count": 0,
        "lookback_sufficiency_claim_count": 0,
        "model_execution_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "result": "passed",
    }
    artifact["timeline_hash"] = _hash_payload(
        {
            "scenario_summaries": scenario_summaries,
            "timeline_rows": rows,
        }
    )
    return artifact


def run_nas_strict_replay_input_timeline(
    *,
    execute_live: bool,
    output: str | Path,
    executor: ReplayInputExecutor | None = None,
    database_url: str | None = None,
) -> dict[str, Any]:
    if not execute_live:
        raise ValueError("Phase119 live timeline requires --execute-live")
    resolved_url = database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    reader = executor or PsqlReadOnlyExecutor(
        resolved_url,
        statement_timeout_milliseconds=60000,
    )
    artifact = build_nas_strict_replay_input_timeline(executor=reader)
    output_path = _validated_output_path(output)
    _atomic_json_write(output_path, artifact)
    return artifact


def load_nas_strict_replay_input_timeline_status(
    path: str | Path = DEFAULT_STATUS_PATH,
) -> dict[str, Any]:
    status_path = Path(path)
    if not status_path.exists():
        return {
            "artifact_version": "phase119_strict_replay_input_timeline_v1",
            "scenario_count": 5,
            "month_end_row_count": 0,
            "complete_month_count": 0,
            "abstention_month_count": 0,
            "result": "not_started",
        }
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid Phase119 strict replay input timeline status")
    return payload


def _scenario_summaries(
    rows: list[dict[str, Any]],
    scenarios: list[dict[str, str]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["scenario_id"]].append(row)
    summaries = []
    for scenario in scenarios:
        scenario_rows = grouped[scenario["scenario_id"]]
        complete = sum(not row["abstention_required"] for row in scenario_rows)
        summaries.append(
            {
                "scenario_id": scenario["scenario_id"],
                "validation_window_start": scenario["validation_window_start"],
                "validation_window_end": scenario["validation_window_end"],
                "month_count": len(scenario_rows),
                "complete_month_count": complete,
                "abstention_month_count": len(scenario_rows) - complete,
                "first_complete_month": next(
                    (
                        row["as_of"]
                        for row in scenario_rows
                        if not row["abstention_required"]
                    ),
                    None,
                ),
                "scenario_input_state": (
                    "complete_for_all_months"
                    if complete == len(scenario_rows)
                    else "partial_with_explicit_abstention"
                ),
            }
        )
    return summaries


def _timeline_sql(
    scenarios: list[dict[str, str]],
    series_ids: list[str],
) -> str:
    scenario_values = ",\n".join(
        "(" + ", ".join(
            (
                _literal(row["scenario_id"]),
                _literal(row["validation_window_start"]) + "::date",
                _literal(row["validation_window_end"]) + "::date",
            )
        ) + ")"
        for row in scenarios
    )
    series_values = ",\n".join(f"({_literal(value)})" for value in series_ids)
    return f"""
WITH scenarios(scenario_id, window_start, window_end) AS (
  VALUES
{scenario_values}
),
required(series_key) AS (
  VALUES
{series_values}
),
scenario_months AS (
  SELECT s.scenario_id,
         (month_start + interval '1 month - 1 day')::date AS as_of
  FROM scenarios s
  CROSS JOIN LATERAL generate_series(
    date_trunc('month', s.window_start)::date,
    date_trunc('month', s.window_end)::date,
    interval '1 month'
  ) AS month_start
),
availability AS (
  SELECT m.scenario_id, m.as_of, r.series_key,
         EXISTS (
           SELECT 1 FROM macro.observation_vintage v
           WHERE v.series_key = r.series_key
             AND v.observation_date <= m.as_of
             AND v.realtime_start <= m.as_of
             AND v.realtime_end >= m.as_of
         ) AS available
  FROM scenario_months m CROSS JOIN required r
),
timeline_rows AS (
  SELECT scenario_id, as_of,
         array_agg(series_key ORDER BY series_key)
           FILTER (WHERE available) AS available_series_ids
  FROM availability
  GROUP BY scenario_id, as_of
)
SELECT json_build_object(
  'transaction_read_only', current_setting('transaction_read_only'),
  'timeline_rows',
    (SELECT json_agg(json_build_object(
       'scenario_id', scenario_id,
       'as_of', to_char(as_of, 'YYYY-MM-DD'),
       'available_series_ids', coalesce(available_series_ids, ARRAY[]::text[])
     ) ORDER BY scenario_id, as_of) FROM timeline_rows)
)::text;
""".strip()


def _scenario_rows() -> list[dict[str, str]]:
    manifest = yaml.safe_load(SCENARIO_PATH.read_text(encoding="utf-8"))[
        "historical_validation_scenario_manifest"
    ]
    return [
        {
            "scenario_id": str(row["scenario_id"]),
            "validation_window_start": str(row["validation_window_start"]),
            "validation_window_end": str(row["validation_window_end"]),
        }
        for row in manifest["scenario_rows"]
    ]


def _direct_series_ids() -> list[str]:
    contract = yaml.safe_load(SOURCE_SCOPE_PATH.read_text(encoding="utf-8"))[
        "nas_postgres_live_revised_import_contract"
    ]
    return [str(value) for value in contract["source_policy"]["direct_series_ids"]]


def _validated_output_path(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError("Phase119 timeline output must remain outside repository")
    allowed = str(resolved).startswith("/tmp/") or str(resolved).startswith(
        "/var/lib/business-cycle/source-artifacts/phase119/"
    )
    if not allowed:
        raise ValueError("Phase119 output must use /tmp or NAS phase119 volume")
    return resolved


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_STATUS_PATH))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.execute_live:
        summary = summarize_nas_strict_replay_input_timeline_contract()
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["result"] == "passed" else 1
    artifact = run_nas_strict_replay_input_timeline(
        execute_live=True,
        output=args.output,
    )
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0 if artifact["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
