#!/usr/bin/env python
"""Explain one point-in-time snapshot selection from the local authoritative cache."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.point_in_time_coverage import scenario_month_end_dates
from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.indicators.point_in_time_derived import derive_rrsfs_snapshot
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series-id", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--cache-dir", default="data/raw/fred_vintages")
    parser.add_argument("--scenarios-path", default="specs/backtests/scenarios.yaml")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    explanation = explain_snapshot(
        series_id=args.series_id,
        as_of=args.as_of,
        cache_dir=Path(args.cache_dir),
        scenarios_path=Path(args.scenarios_path),
    )
    for key, value in explanation.items():
        print(f"{key}={_format(value)}")
    return 0


def explain_snapshot(
    *,
    series_id: str,
    as_of: str,
    cache_dir: Path,
    scenarios_path: Path,
) -> dict[str, Any]:
    cache = PointInTimeCache(cache_dir)
    clean_series_id = series_id.strip().upper()
    if clean_series_id == "RRSFS":
        return _explain_rrsfs_derived(as_of=as_of, cache_dir=cache_dir, scenarios_path=scenarios_path)
    base: dict[str, Any] = {
        "series_id": clean_series_id,
        "as_of": as_of,
        "cache_path": str(cache.csv_path(clean_series_id)),
        "manifest_path": str(cache.manifest_path(clean_series_id)),
        "temporal_evidence_class": "exact_vintage_interval",
        "point_in_time": False,
        "revised_fallback_used": False,
        "proxy_used": False,
    }
    try:
        cached = cache.read_series(clean_series_id)
    except PointInTimeCacheError as exc:
        return {
            **base,
            "snapshot_as_of_ready": False,
            "full_required_horizon_ready": False,
            "full_required_horizon_coverage_ratio": 0.0,
            "selected_observation_date": None,
            "selected_realtime_start": None,
            "selected_realtime_end": None,
            "cache_manifest_checksum_valid": False,
            "missing_reason": str(exc),
        }
    full_summary = _full_horizon_summary(
        rows=cached.rows,
        series_id=clean_series_id,
        scenarios_path=scenarios_path,
    )
    try:
        snapshot = select_vintage_as_of(cached.rows, series_id=clean_series_id, as_of=as_of)
    except PointInTimeError as exc:
        return {
            **base,
            **cache.explain_cache_coverage(clean_series_id),
            **full_summary,
            "snapshot_as_of_ready": False,
            "selected_observation_date": None,
            "selected_realtime_start": None,
            "selected_realtime_end": None,
            "cache_manifest_checksum_valid": True,
            "missing_reason": _missing_reason(as_of=as_of, earliest=str(cached.manifest.get("earliest_realtime_start")), error=str(exc)),
        }
    if not snapshot.observations:
        return {
            **base,
            **cache.explain_cache_coverage(clean_series_id),
            **full_summary,
            "snapshot_as_of_ready": False,
            "selected_observation_date": None,
            "selected_realtime_start": None,
            "selected_realtime_end": None,
            "cache_manifest_checksum_valid": True,
            "missing_reason": _missing_reason(as_of=as_of, earliest=str(cached.manifest.get("earliest_realtime_start")), error="strict snapshot has no observations"),
        }
    selected = snapshot.observations[-1]
    return {
        **base,
        **cache.explain_cache_coverage(clean_series_id),
        **full_summary,
        "snapshot_as_of_ready": True,
        "selected_observation_date": selected.observation_date.isoformat(),
        "latest_legally_available_observation_date": selected.observation_date.isoformat(),
        "selected_realtime_start": selected.realtime_start.isoformat(),
        "selected_realtime_end": (
            None if selected.realtime_end is None else selected.realtime_end.isoformat()
        ),
        "point_in_time": True,
        "cache_manifest_checksum_valid": True,
        "missing_reason": "none",
    }


def _explain_rrsfs_derived(
    *,
    as_of: str,
    cache_dir: Path,
    scenarios_path: Path,
) -> dict[str, Any]:
    cache = PointInTimeCache(cache_dir)
    base = {
        "series_id": "RRSFS",
        "as_of": as_of,
        "cache_path": str(cache.csv_path("RRSFS")),
        "manifest_path": str(cache.manifest_path("RRSFS")),
        "temporal_evidence_class": "derived_point_in_time",
        "point_in_time": False,
        "revised_fallback_used": False,
        "proxy_used": False,
        "full_required_horizon_ready": False,
        "full_required_horizon_coverage_ratio": 0.0,
    }
    try:
        rsafs = cache.read_series("RSAFS")
        cpi = cache.read_series("CPIAUCSL")
        rsafs_snapshot = select_vintage_as_of(rsafs.rows, series_id="RSAFS", as_of=as_of)
        cpi_snapshot = select_vintage_as_of(cpi.rows, series_id="CPIAUCSL", as_of=as_of)
        value = derive_rrsfs_snapshot(
            as_of=as_of,
            rsafs_snapshot=rsafs_snapshot,
            cpi_snapshot=cpi_snapshot,
        )
    except (PointInTimeCacheError, PointInTimeError) as exc:
        return {
            **base,
            "snapshot_as_of_ready": False,
            "selected_observation_date": None,
            "selected_realtime_start": None,
            "selected_realtime_end": None,
            "cache_manifest_checksum_valid": False,
            "missing_reason": str(exc),
            "blocker_class": "derived_input_not_strict_ready",
        }
    full_summary = _full_horizon_summary(rows=rsafs.rows, series_id="RSAFS", scenarios_path=scenarios_path)
    strict_ready = _rrsfs_contract_strict_ready()
    return {
        **base,
        **full_summary,
        "candidate_snapshot_ready": True,
        "snapshot_as_of_ready": strict_ready,
        "selected_observation_date": value.selected_reference_month,
        "latest_legally_available_observation_date": value.selected_reference_month,
        "selected_realtime_start": value.availability_date,
        "selected_realtime_end": None,
        "point_in_time": strict_ready,
        "cache_manifest_checksum_valid": True,
        "formula_id": value.formula_id,
        "formula_version": value.formula_version,
        "input_snapshot_ids": ",".join(value.input_snapshot_ids),
        "missing_reason": "none" if strict_ready else "derived_formula_or_input_archive_not_strict_ready",
        "blocker_class": "none" if strict_ready else "derived_contract_not_strict_ready",
    }


def _rrsfs_contract_strict_ready() -> bool:
    path = Path("specs/audits/rrsfs_point_in_time_derivation.yaml")
    if not path.exists():
        return False
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return bool(payload.get("rrsfs_point_in_time_derivation", {}).get("strict_ready"))


def _full_horizon_summary(
    *,
    rows: list[dict[str, str]],
    series_id: str,
    scenarios_path: Path,
) -> dict[str, Any]:
    dates = scenario_month_end_dates(scenarios_path)
    covered = 0
    for as_of in dates:
        try:
            snapshot = select_vintage_as_of(rows, series_id=series_id, as_of=as_of)
        except PointInTimeError:
            continue
        covered += int(bool(snapshot.observations))
    total = len(dates)
    return {
        "first_required_as_of": min(dates) if dates else None,
        "last_required_as_of": max(dates) if dates else None,
        "full_required_horizon_ready": total > 0 and covered == total,
        "full_required_horizon_coverage_ratio": 0.0 if total == 0 else round(covered / total, 6),
        "unresolved_required_pair_count": total - covered,
    }


def _missing_reason(*, as_of: str, earliest: str, error: str) -> str:
    if earliest and earliest != "None" and as_of < earliest:
        return "history_before_exact_vintage_coverage"
    if "no observations" in error.lower():
        return "no_legally_available_observation"
    return error


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
