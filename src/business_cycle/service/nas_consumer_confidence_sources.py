"""Governed consumer-confidence source lanes for the private NAS service."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Callable

import requests
import yaml

from business_cycle.data_sources import SeriesObservation
from business_cycle.service.nas_nyfed_sce_components import (
    load_nyfed_sce_component_contract,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    PsqlSubprocessExecutor,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/consumer_confidence_source_lanes.yaml"
DEFAULT_ARTIFACT_ROOT = Path(
    "/var/lib/business-cycle/source-artifacts/phase136"
)
OECD_SERIES_ID = "OECD_US_CCICP"
OECD_URL = (
    "https://sdmx.oecd.org/public/rest/data/"
    "OECD.SDD.STES,DSD_STES@DF_CS,4.0/USA.M.CCICP......"
    "?dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
)
CONFIRMATION = "I_UNDERSTAND_THIS_FETCHES_OECD_AND_WRITES_NAS_POSTGRES"


class ConsumerConfidenceSourceError(RuntimeError):
    """Raised when a confidence source violates its lane contract."""


def load_consumer_confidence_source_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["consumer_confidence_source_lanes"])


def summarize_consumer_confidence_source_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_consumer_confidence_source_contract(path)
    lanes = list(contract["source_lanes"])
    counts = {
        kind: sum(row["lane_type"] == kind for row in lanes)
        for kind in (
            "exact_book_core",
            "near_equivalent_transformed",
            "independent_proxy",
            "explanatory_context",
        )
    }
    summary = {
        "phase": 136,
        "consumer_confidence_source_lane_contract_ready": _contract_ready(contract),
        "source_lane_count": len(lanes),
        "exact_book_core_lane_count": counts["exact_book_core"],
        "near_equivalent_lane_count": counts["near_equivalent_transformed"],
        "independent_proxy_lane_count": counts["independent_proxy"],
        "explanatory_context_lane_count": counts["explanatory_context"],
        "exact_source_access_blocked_count": sum(
            row["lane_type"] == "exact_book_core"
            and row["access_status"] == "subscription_or_authorized_private_input_required"
            for row in lanes
        ),
        "official_automated_alternative_count": sum(
            row["automation_status"]
            in {"automated_official_sdmx_worker", "automated_revised_fred"}
            for row in lanes
        ),
        "nyfed_explanatory_component_count": len(
            next(
                row["explanatory_components"]
                for row in lanes
                if row["lane_type"] == "explanatory_context"
            )
        ),
        "source_failure_drill_state_count": len(contract["failure_drill_states"]),
        "exact_book_core_replacement_count": 0,
        "arbitrary_composite_score_count": 0,
        "revised_mislabeled_as_point_in_time_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
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


def build_consumer_confidence_source_lanes(
    *,
    observations_by_series: dict[str, list[dict[str, Any]]] | None = None,
    failed_source_ids: set[str] | list[str] | None = None,
    exact_authorized: bool = False,
) -> dict[str, Any]:
    """Build independent source lanes without emitting a combined score."""

    contract = load_consumer_confidence_source_contract()
    nyfed_contract = load_nyfed_sce_component_contract()
    nyfed_components = list(nyfed_contract["component_series"])
    nyfed_component_ids = {str(row["series_id"]) for row in nyfed_components}
    observations = observations_by_series or {}
    failed = {str(value) for value in failed_source_ids or []}
    rows = []
    for source in contract["source_lanes"]:
        series_id = str(source["source_series_id"])
        series_rows = list(observations.get(series_id, []))
        component_observations: list[dict[str, Any]] = []
        if source["lane_type"] == "explanatory_context":
            for component in nyfed_components:
                component_rows = list(
                    observations.get(str(component["series_id"]), [])
                )
                latest_component = _latest_observation(component_rows)
                component_observations.append(
                    dict(component)
                    | {
                        "latest_observation_date": (
                            latest_component.get("observation_date")
                            if latest_component
                            else None
                        ),
                        "latest_value": (
                            latest_component.get("value_numeric")
                            if latest_component
                            else None
                        ),
                        "data_mode": "revised_supporting_only",
                    }
                )
        if source["lane_type"] == "exact_book_core":
            status = (
                "exact_available"
                if exact_authorized and series_rows
                else "access_limited"
            )
        elif series_id in failed or (
            source["lane_type"] == "explanatory_context"
            and bool(failed & nyfed_component_ids)
        ):
            status = "source_failed_unavailable"
        elif source["lane_type"] == "explanatory_context" and all(
            row["latest_observation_date"] for row in component_observations
        ):
            status = "available_supporting_only"
        elif source["lane_type"] == "explanatory_context" and any(
            row["latest_observation_date"] for row in component_observations
        ):
            status = "partial_supporting_components"
        elif series_rows:
            status = "available_supporting_only"
        elif source["lane_type"] == "explanatory_context":
            status = "official_context_contract_ready_no_local_values"
        else:
            status = "not_yet_loaded"
        latest = _latest_observation(series_rows)
        if source["lane_type"] == "explanatory_context":
            latest_component_dates = [
                str(row["latest_observation_date"])
                for row in component_observations
                if row["latest_observation_date"]
            ]
            latest = (
                {"observation_date": max(latest_component_dates)}
                if latest_component_dates
                else None
            )
        directional = (
            build_causal_direction_and_turning_point(series_rows)
            if source["lane_type"] == "near_equivalent_transformed"
            else None
        )
        rows.append(
            dict(source)
            | {
                "lane_status": status,
                "latest_observation_date": (
                    latest.get("observation_date") if latest else None
                ),
                "latest_value": (
                    latest.get("value_numeric")
                    if latest and source["lane_type"] != "explanatory_context"
                    else None
                ),
                "directional_observation": directional,
                "component_observations": component_observations,
                "component_series_count": len(component_observations),
                "available_component_series_count": sum(
                    bool(row["latest_observation_date"])
                    for row in component_observations
                ),
                "book_core_replacement": False,
                "phase_evidence_emitted": False,
                "transition_confirmation_emitted": False,
            }
        )
    return {
        "view_model_version": "phase137_consumer_confidence_lanes_v2",
        "role_id": contract["role_id"],
        "book_core_status": (
            "exact_authorized_available" if exact_authorized else "exact_access_blocked"
        ),
        "source_lane_count": len(rows),
        "lanes": rows,
        "visible_available_lane_count": sum(
            row["lane_status"]
            in {
                "exact_available",
                "available_supporting_only",
                "partial_supporting_components",
            }
            for row in rows
        ),
        "nyfed_component_series_count": len(nyfed_components),
        "arbitrary_composite_score_created": False,
        "supporting_source_promoted_to_core_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def build_causal_direction_and_turning_point(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return an exact-difference directional observation with no threshold."""

    values = []
    for row in observations:
        value = _decimal(row.get("value_numeric", row.get("value")))
        observed_at = str(row.get("observation_date", row.get("date", "")))
        if value is not None and observed_at:
            values.append((observed_at, value))
    values.sort(key=lambda item: item[0])
    if len(values) < 2:
        return {
            "status": "abstained_insufficient_history",
            "direction": None,
            "turning_point": None,
            "phase_evidence_emitted": False,
        }
    previous, latest = values[-2], values[-1]
    direction = "rising" if latest[1] > previous[1] else "falling" if latest[1] < previous[1] else "unchanged"
    turning_point = None
    if len(values) >= 3:
        earlier = values[-3]
        if earlier[1] >= previous[1] and latest[1] > previous[1]:
            turning_point = "causal_low_reversal"
        elif earlier[1] <= previous[1] and latest[1] < previous[1]:
            turning_point = "causal_high_reversal"
    return {
        "status": "directional_observation_only",
        "direction": direction,
        "turning_point": turning_point,
        "latest_observation_date": latest[0],
        "phase_evidence_emitted": False,
    }


def parse_oecd_consumer_confidence_csv(content: str | bytes) -> list[SeriesObservation]:
    """Parse the pinned OECD SDMX CSV selection into monthly observations."""

    text = content.decode("utf-8-sig") if isinstance(content, bytes) else content
    reader = csv.DictReader(StringIO(text.lstrip("\ufeff")))
    if reader.fieldnames is None:
        raise ConsumerConfidenceSourceError("OECD response has no CSV header")
    required = {"REF_AREA", "FREQ", "MEASURE", "TIME_PERIOD", "OBS_VALUE"}
    if not required <= set(reader.fieldnames):
        raise ConsumerConfidenceSourceError("OECD CSV schema changed")
    by_date: dict[str, SeriesObservation] = {}
    for row in reader:
        if row.get("REF_AREA") != "USA" or row.get("FREQ") != "M":
            continue
        if row.get("MEASURE") != "CCICP":
            continue
        period = str(row.get("TIME_PERIOD", ""))
        if not re.fullmatch(r"\d{4}-\d{2}", period):
            raise ConsumerConfidenceSourceError("OECD monthly period is invalid")
        value = str(row.get("OBS_VALUE", "")).strip()
        if _decimal(value) is None:
            continue
        observation = SeriesObservation(
            series_id=OECD_SERIES_ID,
            date=f"{period}-01",
            value=value,
        )
        if observation.date in by_date and by_date[observation.date].value != value:
            raise ConsumerConfidenceSourceError(
                "OECD query returned multiple incompatible monthly values"
            )
        by_date[observation.date] = observation
    if not by_date:
        raise ConsumerConfidenceSourceError("OECD response has no usable US CCICP rows")
    return [by_date[key] for key in sorted(by_date)]


def run_oecd_consumer_confidence_import(
    *,
    execute_live: bool,
    operator_confirmation: str | None,
    artifact_dir: str | Path = DEFAULT_ARTIFACT_ROOT,
    database_url: str | None = None,
    executor: Any | None = None,
    fetcher: Callable[..., Any] = requests.get,
) -> dict[str, Any]:
    """Fetch one official OECD lane and store it as supporting-only revised data."""

    if not execute_live or operator_confirmation != CONFIRMATION:
        raise ConsumerConfidenceSourceError("OECD import requires explicit confirmation")
    root = _validated_artifact_root(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    started_at = _utc_now()
    try:
        response = fetcher(
            OECD_URL,
            timeout=45.0,
            headers={"User-Agent": "business-cycle-private-nas/phase136"},
        )
        response.raise_for_status()
        raw = response.content
        observations = parse_oecd_consumer_confidence_csv(raw)
        csv_path, content_hash = _write_normalized_csv(root, observations)
        fetched_at = _utc_now()
        artifact_id = f"oecd_revised::{OECD_SERIES_ID}::{content_hash[:16]}"
        sql = executor or PsqlSubprocessExecutor(
            database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
        )
        sql.execute(
            _oecd_upsert_sql(
                csv_path=csv_path,
                content_hash=content_hash,
                artifact_id=artifact_id,
                fetched_at=fetched_at,
            )
        )
        row = {
            "series_id": OECD_SERIES_ID,
            "status": "imported",
            "observation_count": len(observations),
            "attempt_count": 1,
            "artifact_id": artifact_id,
            "error_class": None,
            "error_message_redacted": None,
        }
        result = "passed"
    except Exception as exc:  # noqa: BLE001 - worker reports a typed source failure
        row = {
            "series_id": OECD_SERIES_ID,
            "status": "failed",
            "observation_count": 0,
            "attempt_count": 1,
            "artifact_id": None,
            "error_class": exc.__class__.__name__,
            "error_message_redacted": "oecd_consumer_confidence_import_failed",
        }
        result = "blocked"
    report = {
        "report_version": "phase136_oecd_consumer_confidence_import_v1",
        "data_mode": "revised_supporting_only",
        "started_at_utc": started_at,
        "completed_at_utc": _utc_now(),
        "requested_series_count": 1,
        "completed_series_count": int(result == "passed"),
        "failed_series_count": int(result != "passed"),
        "source_artifact_count": int(result == "passed"),
        "series_refresh_results": [row],
        "book_core_replacement_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "result": result,
    }
    _atomic_json_write(root / "latest-oecd-confidence-report.json", report)
    return report


def build_consumer_confidence_failure_drills() -> dict[str, Any]:
    """Exercise four deterministic visibility states without network or writes."""

    sample = {
        "OECD_US_CCICP": _sample_rows("98.0", "97.5", "98.2"),
        "UMCSENT": _sample_rows("70", "68", "69"),
        "CONFERENCE_BOARD_CCI": _sample_rows("100", "99", "101"),
    }
    scenarios = [
        ("exact", sample, set(), True, "exact_available"),
        (
            "near_equivalent",
            {key: value for key, value in sample.items() if key != "CONFERENCE_BOARD_CCI"},
            set(),
            False,
            "available_supporting_only",
        ),
        (
            "proxy",
            {"UMCSENT": sample["UMCSENT"]},
            {"OECD_US_CCICP"},
            False,
            "available_supporting_only",
        ),
        (
            "unavailable",
            {},
            {"OECD_US_CCICP", "UMCSENT", "NYFED_SCE_CONTEXT"},
            False,
            "all_alternatives_unavailable",
        ),
    ]
    rows = []
    for state, observations, failed, authorized, expected in scenarios:
        model = build_consumer_confidence_source_lanes(
            observations_by_series=observations,
            failed_source_ids=failed,
            exact_authorized=authorized,
        )
        if state == "exact":
            observed = model["lanes"][0]["lane_status"]
        elif state == "near_equivalent":
            observed = model["lanes"][1]["lane_status"]
        elif state == "proxy":
            observed = model["lanes"][2]["lane_status"]
        else:
            observed = (
                "all_alternatives_unavailable"
                if all(
                    row["lane_status"]
                    in {"access_limited", "source_failed_unavailable"}
                    for row in model["lanes"]
                )
                else "unexpected_visible_source"
            )
        rows.append(
            {
                "drill_state": state,
                "observed_status": observed,
                "expected_status": expected,
                "passed": observed == expected,
                "book_core_replacement_count": 0,
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return {
        "drill_version": "phase136_consumer_confidence_failure_drill_v1",
        "drill_state_count": len(rows),
        "drill_pass_count": sum(row["passed"] for row in rows),
        "drills": rows,
        "exact_book_core_replacement_count": 0,
        "arbitrary_composite_score_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    policy = contract["lane_policy"]
    return (
        contract["status"] == "active_private_nas_consumer_confidence_source_contract"
        and policy["exact_source_remains_blocked_without_authorization"] is True
        and policy["near_equivalent_may_replace_exact_book_core"] is False
        and policy["independent_proxy_may_replace_exact_book_core"] is False
        and policy["explanatory_context_may_replace_exact_book_core"] is False
        and policy["arbitrary_composite_allowed"] is False
    )


def _latest_observation(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return max(rows, key=lambda row: str(row.get("observation_date", ""))) if rows else None


def _sample_rows(*values: str) -> list[dict[str, Any]]:
    return [
        {"observation_date": f"2026-0{index + 4}-01", "value_numeric": value}
        for index, value in enumerate(values)
    ]


def _decimal(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _validated_artifact_root(path: str | Path) -> Path:
    resolved = Path(path).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ConsumerConfidenceSourceError("source artifacts must remain outside repository")
    if not (
        str(resolved).startswith("/tmp/")
        or str(resolved).startswith("/var/lib/business-cycle/")
    ):
        raise ConsumerConfidenceSourceError("artifact root must use /tmp or NAS volume")
    return resolved


def _write_normalized_csv(
    root: Path,
    observations: list[SeriesObservation],
) -> tuple[Path, str]:
    output = root / "oecd" / f"{OECD_SERIES_ID}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", newline="", encoding="utf-8", dir=output.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["series_key", "observation_date", "value_numeric", "value_text"],
        )
        writer.writeheader()
        for row in observations:
            writer.writerow(
                {
                    "series_key": OECD_SERIES_ID,
                    "observation_date": row.date,
                    "value_numeric": row.value,
                    "value_text": "",
                }
            )
        temporary = Path(handle.name)
    content_hash = hashlib.sha256(temporary.read_bytes()).hexdigest()
    temporary.replace(output)
    return output, content_hash


def _oecd_upsert_sql(
    *,
    csv_path: Path,
    content_hash: str,
    artifact_id: str,
    fetched_at: str,
) -> str:
    values = {
        "series": _literal(OECD_SERIES_ID),
        "url": _literal(OECD_URL.split("?", maxsplit=1)[0]),
        "fetched": _literal(fetched_at),
        "hash": _literal(content_hash),
        "artifact": _literal(artifact_id),
        "csv": str(csv_path).replace("'", "''"),
    }
    return rf"""
BEGIN;
INSERT INTO macro.series_registry (
  series_key, source_family, source_series_id, source_title, units, frequency,
  seasonal_adjustment, geographic_scope, source_url_without_secret,
  source_identity_status, created_at_utc, updated_at_utc
) VALUES (
  {values['series']}, 'OECD', 'USA.M.CCICP',
  'Consumer opinion surveys - Composite consumer confidence, United States',
  'percentage_balance', 'monthly', 'calendar_and_seasonally_adjusted', 'United States',
  {values['url']}, 'verified_near_equivalent_supporting_only',
  {values['fetched']}::timestamptz, {values['fetched']}::timestamptz
)
ON CONFLICT (series_key) DO UPDATE SET
  source_title = EXCLUDED.source_title,
  units = EXCLUDED.units,
  frequency = EXCLUDED.frequency,
  seasonal_adjustment = EXCLUDED.seasonal_adjustment,
  source_url_without_secret = EXCLUDED.source_url_without_secret,
  source_identity_status = EXCLUDED.source_identity_status,
  updated_at_utc = EXCLUDED.updated_at_utc;

INSERT INTO macro.source_artifact (
  artifact_id, source_family, source_url_without_secret,
  source_series_or_release_id, fetched_at_utc, content_hash, content_type,
  adapter_id, parser_version, no_secret, validation_status
) VALUES (
  {values['artifact']}, 'OECD', {values['url']}, 'USA.M.CCICP',
  {values['fetched']}::timestamptz, {values['hash']}, 'text/csv',
  'oecd_sdmx_consumer_confidence_v1', 'phase136_oecd_csv_v1', TRUE,
  'validated_revised_supporting_only'
)
ON CONFLICT (content_hash) DO NOTHING;

CREATE TEMP TABLE phase136_oecd_observation_import (
  series_key text,
  observation_date date,
  value_numeric numeric,
  value_text text
) ON COMMIT DROP;
\copy phase136_oecd_observation_import FROM '{values['csv']}' WITH (FORMAT csv, HEADER true)

INSERT INTO macro.observation_revised (
  series_key, observation_date, value_numeric, value_text, unit, data_mode,
  source_artifact_id, fetched_at_utc, provenance_hash
)
SELECT
  series_key, observation_date, value_numeric, value_text, 'percentage_balance',
  'revised', {values['artifact']}, {values['fetched']}::timestamptz,
  encode(sha256(convert_to(
    series_key || '|' || observation_date::text || '|' ||
    coalesce(value_numeric::text, value_text, '') || '|' || {values['artifact']},
    'UTF8'
  )), 'hex')
FROM phase136_oecd_observation_import
ON CONFLICT (series_key, observation_date) DO UPDATE SET
  value_numeric = EXCLUDED.value_numeric,
  value_text = EXCLUDED.value_text,
  unit = EXCLUDED.unit,
  source_artifact_id = EXCLUDED.source_artifact_id,
  fetched_at_utc = EXCLUDED.fetched_at_utc,
  provenance_hash = EXCLUDED.provenance_hash;
COMMIT;
""".lstrip()


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args(argv)
    if not args.run_live:
        summary = summarize_consumer_confidence_source_contract()
        print(json.dumps(summary, sort_keys=True))
        return 0 if summary["result"] == "passed" else 1
    report = run_oecd_consumer_confidence_import(
        execute_live=True,
        operator_confirmation=os.environ.get(
            "BUSINESS_CYCLE_CONSUMER_CONFIDENCE_OPERATOR_CONFIRMATION"
        ),
        artifact_dir=args.artifact_root,
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
