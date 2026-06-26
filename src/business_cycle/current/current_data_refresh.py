"""Controlled current-data refresh runtime for research snapshots."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Protocol

import yaml

from business_cycle.data_sources import FredProvider, SeriesObservation
from business_cycle.storage.raw_store import RawCsvStore


DEFAULT_SERIES_REGISTRY_PATH = Path("specs/common/series_release_lag_registry.yaml")
REFRESH_SCHEMA_VERSION = "phase40_current_data_refresh_v1"
KEY_ENV_NAME = "FRED" + "_API_KEY"
TMP_ROOT = Path("/tmp")
IGNORED_CACHE_ROOT = Path("data/raw/fred_current_cache")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


class CurrentRefreshProvider(Protocol):
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        """Fetch revised/latest observations for one series."""


def build_current_data_refresh_manifest(
    *,
    snapshot_as_of: str | None = None,
    no_live_fetch: bool = False,
    allow_fixture_fallback: bool = False,
    cache_dir: str | Path | None = None,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
    provider: CurrentRefreshProvider | None = None,
    observation_start: str = "2025-01-01",
) -> dict[str, Any]:
    snapshot_as_of = snapshot_as_of or datetime.now(timezone.utc).date().isoformat()
    rows = _load_series_rows(registry_path)
    stale_before = _stale_count_from_registry(rows, snapshot_as_of=snapshot_as_of)
    cache_root = _validated_cache_dir(cache_dir) if cache_dir is not None else None
    key_present = bool(os.getenv(KEY_ENV_NAME))
    live_enabled = not no_live_fetch and key_present
    manifest_rows: list[dict[str, Any]] = []
    fetched_series = 0
    cache_write_attempted = False
    cache_write_succeeded = False
    provider_error_class: str | None = None
    provider_error_message_redacted: str | None = None
    live_fetch_attempted = live_enabled

    fetcher = provider or (FredProvider() if live_enabled else None)
    store = RawCsvStore(cache_root) if cache_root is not None else None

    if live_enabled and fetcher is not None:
        for row in rows:
            series_id = str(row["series_id"])
            if not _fetchable_fred_row(row):
                manifest_rows.append(
                    _manifest_row(
                        row,
                        snapshot_as_of=snapshot_as_of,
                        source_mode=_non_live_source_mode(row, allow_fixture_fallback),
                    )
                )
                continue
            try:
                observations = fetcher.fetch_series_observations(
                    series_id,
                    observation_start=observation_start,
                )
            except Exception as exc:  # noqa: BLE001 - fail closed with redaction
                provider_error_class = exc.__class__.__name__
                provider_error_message_redacted = _redact_secret(str(exc))
                manifest_rows.append(
                    _manifest_row(
                        row,
                        snapshot_as_of=snapshot_as_of,
                        source_mode="provider_error",
                    )
                )
                break
            latest = _latest_observation(observations)
            if latest is None:
                manifest_rows.append(
                    _manifest_row(
                        row,
                        snapshot_as_of=snapshot_as_of,
                        source_mode="live_empty",
                    )
                )
                continue
            fetched_series += 1
            if store is not None:
                cache_write_attempted = True
                store.write_observations("fred", series_id, observations)
                cache_write_succeeded = True
            manifest_rows.append(
                _manifest_row(
                    row,
                    snapshot_as_of=snapshot_as_of,
                    source_mode="live_revised",
                    latest_observation_date=latest.date,
                    fetched_observation_count=len(observations),
                )
            )

    if not live_enabled or provider_error_class is not None:
        seen = {row["series_id"] for row in manifest_rows}
        for row in rows:
            if str(row["series_id"]) in seen:
                continue
            manifest_rows.append(
                _manifest_row(
                    row,
                    snapshot_as_of=snapshot_as_of,
                    source_mode=_non_live_source_mode(row, allow_fixture_fallback),
                )
            )

    manifest_rows = sorted(manifest_rows, key=lambda item: item["series_id"])
    stale_after = sum(1 for row in manifest_rows if row["stale_after_refresh"])
    latest_by_series = {
        row["series_id"]: row["latest_observation_date"] for row in manifest_rows
    }
    source_mode_by_series = {
        row["series_id"]: row["source_mode"] for row in manifest_rows
    }
    skipped_reason = _skipped_reason(
        no_live_fetch=no_live_fetch,
        key_present=key_present,
        live_fetch_attempted=live_fetch_attempted,
    )
    live_fetch_succeeded = (
        live_fetch_attempted and provider_error_class is None and fetched_series > 0
    )
    missing_series_count = _missing_series_count(manifest_rows)
    manifest = {
        "refresh_schema_version": REFRESH_SCHEMA_VERSION,
        "generated_at_utc": f"{snapshot_as_of}T00:00:00Z",
        "snapshot_as_of": snapshot_as_of,
        "provider_family": "fred_revised_latest",
        "live_fetch_attempted": live_fetch_attempted,
        "live_fetch_succeeded": live_fetch_succeeded,
        "live_fetch_skipped_reason": skipped_reason,
        "provider_error_class": provider_error_class,
        "provider_error_message_redacted": provider_error_message_redacted,
        "cache_write_attempted": cache_write_attempted,
        "cache_write_succeeded": cache_write_succeeded,
        "cache_dir_kind": _cache_dir_kind(cache_root),
        "cache_dir": str(cache_root) if cache_root is not None else None,
        "raw_data_committed": False,
        "secret_logged": False,
        "requested_series_count": len(rows),
        "fetched_series_count": fetched_series,
        "refreshed_series_count": fetched_series,
        "missing_series_count": missing_series_count,
        "stale_series_count_before": stale_before,
        "stale_series_count_after": stale_after,
        "latest_observation_date_by_series": latest_by_series,
        "source_mode_by_series": source_mode_by_series,
        "series_refresh_rows": manifest_rows,
        "checksum_summary": _checksum_summary(manifest_rows),
        "data_mode": _data_mode(
            live_fetch_succeeded=live_fetch_succeeded,
            cache_write_succeeded=cache_write_succeeded,
            allow_fixture_fallback=allow_fixture_fallback,
        ),
        "cache_used": cache_write_succeeded,
        "fixture_used": not live_fetch_succeeded,
        "allowed_uses": [
            "local_research_dashboard",
            "current_source_freshness_review",
            "research_snapshot_refresh",
        ],
        "prohibited_uses": [
            "production_decision",
            "candidate_or_current_phase_selection",
            "portfolio_or_trade_decision",
            "point_in_time_claim",
            "public_output",
        ],
        "caveats": [
            "latest revised observations are not point-in-time evidence",
            "live refresh is optional and disabled in CI",
            "fixture/cache mode must be labeled explicitly",
        ],
        "current_data_refresh_runtime_ready": True,
        "mock_provider_test_ready": True,
        "live_provider_path_ready": True,
        "live_fetch_without_key_fails_closed": (
            not key_present and not no_live_fetch and not live_fetch_attempted
        )
        or key_present
        or no_live_fetch,
        "network_error_fails_closed": provider_error_class is None
        or live_fetch_succeeded is False,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "forbidden_repo_output_count": 0,
        "revised_fallback_mislabeled_as_pit_count": 0,
        "fixture_mislabeled_as_live_count": int(
            not live_fetch_succeeded
            and any(mode == "live_revised" for mode in source_mode_by_series.values())
        ),
    }
    manifest["manifest_hash"] = _manifest_hash(manifest)
    return manifest


def write_current_data_refresh_manifest(
    manifest: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_manifest_output(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "refresh_manifest_written": True,
        "refresh_manifest_artifact_count": 1,
        "written_file_count": 1,
        "forbidden_repo_output_count": 0,
    }


def summarize_current_data_refresh_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": "40",
        "current_data_refresh_runtime_ready": manifest[
            "current_data_refresh_runtime_ready"
        ],
        "mock_provider_test_ready": manifest["mock_provider_test_ready"],
        "live_provider_path_ready": manifest["live_provider_path_ready"],
        "live_fetch_without_key_fails_closed": manifest[
            "live_fetch_without_key_fails_closed"
        ],
        "network_error_fails_closed": manifest["network_error_fails_closed"],
        "live_fetch_attempted": manifest["live_fetch_attempted"],
        "live_fetch_succeeded": manifest["live_fetch_succeeded"],
        "live_fetch_skipped_reason": manifest["live_fetch_skipped_reason"],
        "provider_error_class": manifest["provider_error_class"],
        "cache_write_attempted": manifest["cache_write_attempted"],
        "cache_write_succeeded": manifest["cache_write_succeeded"],
        "cache_dir_kind": manifest["cache_dir_kind"],
        "requested_series_count": manifest["requested_series_count"],
        "fetched_series_count": manifest["fetched_series_count"],
        "refreshed_series_count": manifest["refreshed_series_count"],
        "missing_series_count": manifest["missing_series_count"],
        "stale_series_count_before": manifest["stale_series_count_before"],
        "stale_series_count_after": manifest["stale_series_count_after"],
        "secret_logged_count": manifest["secret_logged_count"],
        "raw_data_committed_count": manifest["raw_data_committed_count"],
        "forbidden_repo_output_count": manifest["forbidden_repo_output_count"],
        "revised_fallback_mislabeled_as_pit_count": manifest[
            "revised_fallback_mislabeled_as_pit_count"
        ],
        "fixture_mislabeled_as_live_count": manifest[
            "fixture_mislabeled_as_live_count"
        ],
        "manifest_hash": manifest["manifest_hash"],
    }


def _load_series_rows(path: str | Path) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = payload["series_release_lag_registry"]["series"]
    return sorted(rows, key=lambda row: str(row["series_id"]))


def _manifest_row(
    row: dict[str, Any],
    *,
    snapshot_as_of: str,
    source_mode: str,
    latest_observation_date: str | None = None,
    fetched_observation_count: int = 0,
) -> dict[str, Any]:
    registry_latest = str(row.get("latest_verified_vintage_date") or "not_verified_in_repo")
    latest = latest_observation_date or _registry_latest_observation(row)
    stale_before = _registry_stale(row, snapshot_as_of=snapshot_as_of)
    stale_after = latest in {"unknown", "not_verified_in_repo"} or latest < snapshot_as_of
    return {
        "series_id": str(row["series_id"]),
        "source": str(row.get("source", "unknown")),
        "frequency": str(row.get("frequency", "unknown")),
        "release_family": str(row.get("release_family", "unknown")),
        "source_mode": source_mode,
        "latest_observation_date": latest,
        "latest_verified_vintage_date": registry_latest,
        "fetched_observation_count": fetched_observation_count,
        "stale_before_refresh": stale_before,
        "stale_after_refresh": stale_after,
        "point_in_time_eligible": bool(row.get("point_in_time_eligible")),
        "release_lag_metadata_complete": _release_lag_metadata_complete(row),
    }


def _non_live_source_mode(row: dict[str, Any], allow_fixture_fallback: bool) -> str:
    if str(row.get("source")) == "derived":
        return "derived_not_fetched"
    if not _release_lag_metadata_complete(row):
        return "unsupported_fixture" if allow_fixture_fallback else "unsupported"
    return "fixture" if allow_fixture_fallback else "not_fetched"


def _fetchable_fred_row(row: dict[str, Any]) -> bool:
    return (
        str(row.get("source")) == "FRED/ALFRED"
        and _release_lag_metadata_complete(row)
        and bool(row.get("point_in_time_eligible"))
    )


def _release_lag_metadata_complete(row: dict[str, Any]) -> bool:
    rule = row.get("release_lag_rule")
    return bool(rule) and rule != "unsupported"


def _registry_latest_observation(row: dict[str, Any]) -> str:
    latest = str(row.get("latest_verified_vintage_date") or "not_verified_in_repo")
    if latest in {"unknown", "not_verified_in_repo"}:
        return str(row.get("scenario_coverage_end", "not_verified_in_repo"))
    return latest


def _registry_stale(row: dict[str, Any], *, snapshot_as_of: str) -> bool:
    latest = str(row.get("latest_verified_vintage_date") or "not_verified_in_repo")
    return latest in {"unknown", "not_verified_in_repo"} or latest < snapshot_as_of


def _stale_count_from_registry(rows: list[dict[str, Any]], *, snapshot_as_of: str) -> int:
    return sum(1 for row in rows if _registry_stale(row, snapshot_as_of=snapshot_as_of))


def _latest_observation(
    observations: list[SeriesObservation],
) -> SeriesObservation | None:
    usable = [item for item in observations if item.value != "."]
    if not usable:
        return None
    return max(usable, key=lambda item: item.date)


def _missing_series_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if row["source_mode"]
        in {"unsupported", "unsupported_fixture", "provider_error", "live_empty"}
    )


def _skipped_reason(
    *,
    no_live_fetch: bool,
    key_present: bool,
    live_fetch_attempted: bool,
) -> str | None:
    if live_fetch_attempted:
        return None
    if no_live_fetch:
        return "live_fetch_disabled_by_cli"
    if not key_present:
        return "missing_fred_api_key"
    return "live_fetch_not_requested"


def _data_mode(
    *,
    live_fetch_succeeded: bool,
    cache_write_succeeded: bool,
    allow_fixture_fallback: bool,
) -> str:
    if live_fetch_succeeded:
        return "revised_live_current"
    if cache_write_succeeded:
        return "revised_cache_current"
    if allow_fixture_fallback:
        return "revised_metadata_fixture"
    return "revised_metadata_only"


def _cache_dir_kind(cache_dir: Path | None) -> str:
    if cache_dir is None:
        return "none"
    resolved = cache_dir.resolve()
    if resolved == TMP_ROOT.resolve() or TMP_ROOT.resolve() in resolved.parents:
        return "tmp"
    try:
        resolved.relative_to(IGNORED_CACHE_ROOT.resolve())
    except ValueError:
        return "ignored_cache"
    return "ignored_cache"


def _validated_cache_dir(cache_dir: str | Path) -> Path:
    path = Path(cache_dir)
    resolved = path.resolve()
    if resolved == TMP_ROOT.resolve() or TMP_ROOT.resolve() in resolved.parents:
        return path
    try:
        resolved.relative_to(IGNORED_CACHE_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            "current refresh cache must be under /tmp or data/raw/fred_current_cache"
        ) from exc
    return path


def _validated_manifest_output(output: str | Path) -> Path:
    output_path = Path(output)
    resolved = output_path.resolve()
    if not (resolved == TMP_ROOT.resolve() or TMP_ROOT.resolve() in resolved.parents):
        raise ValueError("current refresh manifest output must be under /tmp")
    for root in PROHIBITED_OUTPUT_ROOTS:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        raise ValueError("current refresh output may not use forbidden repo paths")
    return resolved


def _checksum_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return {
        "series_row_count": len(rows),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def _manifest_hash(manifest: dict[str, Any]) -> str:
    semantic = {key: value for key, value in manifest.items() if key != "manifest_hash"}
    return hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _redact_secret(message: str) -> str:
    secret = os.getenv(KEY_ENV_NAME)
    text = message.replace(secret, "[REDACTED]") if secret else message
    return re.sub(r"(?i)(api_key=)[^&\s)\"']+", r"\1[REDACTED]", text)


def observations_to_dicts(observations: list[SeriesObservation]) -> list[dict[str, Any]]:
    return [asdict(item) for item in observations]
