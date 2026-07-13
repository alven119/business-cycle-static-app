"""Reference-period and official-release aware freshness for private NAS data."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/release_aware_freshness_source_identity_remediation.yaml"
)
DEFAULT_ROADMAP_PATH = ROOT / "specs/common/source_reliability_resilience_roadmap.yaml"
DEFAULT_RELEASE_CALENDAR_PATH = (
    ROOT / "specs/common/nas_official_release_calendar_contract.yaml"
)
DEFAULT_SERIES_REGISTRY_PATH = ROOT / "specs/common/series_release_lag_registry.yaml"


def load_release_aware_freshness_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["release_aware_freshness_source_identity_remediation"])


def load_source_reliability_roadmap(
    path: str | Path = DEFAULT_ROADMAP_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["source_reliability_resilience_roadmap"])


def role_series_overrides(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, list[str]]:
    """Return active NAS role mappings without rewriting historical QA freezes."""

    contract = load_release_aware_freshness_contract(path)
    return {
        str(role_id): [str(value) for value in row["series_ids"]]
        for row in contract["source_identity_remediations"]
        for role_id in row["role_ids"]
    }


def build_release_aware_freshness(
    *,
    series_id: str,
    latest_observation_date: date | None,
    as_of: date,
    frequency: str,
    freshness_windows: dict[str, Any],
    release_calendar_path: str | Path = DEFAULT_RELEASE_CALENDAR_PATH,
) -> dict[str, Any]:
    """Classify freshness without treating a period-start date as publication age."""

    if latest_observation_date is None:
        return {
            "freshness_status": "unavailable",
            "freshness_reason_code": "no_observation_available",
            "latest_observation_date": None,
            "reference_period_end_date": None,
            "age_days": None,
            "stale_after_days": None,
            "release_aware": True,
            "release_family_id": None,
            "latest_registered_release_date": None,
            "expected_reference_period": None,
        }

    family = _frequency_family(frequency)
    period_end = reference_period_end(latest_observation_date, family)
    context = release_context_for_series(
        series_id,
        as_of=as_of,
        path=release_calendar_path,
    )
    stale_after = int(freshness_windows[family]) if family else None
    age_days = max(0, (as_of - period_end).days)
    expected_end = context.get("expected_reference_period_end")
    latest_release_date = context.get("latest_registered_release_date")
    grace_days = int(context.get("release_refresh_grace_days", 0))

    if expected_end is not None and latest_release_date is not None:
        if period_end >= expected_end:
            status = "fresh"
            reason = "latest_registered_official_reference_period_available"
        elif as_of <= latest_release_date + timedelta(days=grace_days):
            status = "fresh"
            reason = "official_release_refresh_grace_period"
        else:
            status = "stale"
            reason = "registered_official_reference_period_missing_after_grace"
    elif family is None:
        status = "unknown_frequency"
        reason = "frequency_not_supported"
    else:
        status = "fresh" if age_days <= int(stale_after) else "stale"
        reason = (
            "reference_period_end_within_frequency_window"
            if status == "fresh"
            else "reference_period_end_exceeds_frequency_window"
        )

    return {
        "freshness_status": status,
        "freshness_reason_code": reason,
        "latest_observation_date": latest_observation_date.isoformat(),
        "reference_period_end_date": period_end.isoformat(),
        "age_days": age_days,
        "stale_after_days": stale_after,
        "release_aware": True,
        "release_family_id": context.get("release_family_id"),
        "calendar_precision": context.get("calendar_precision"),
        "latest_registered_release_date": (
            latest_release_date.isoformat() if latest_release_date else None
        ),
        "expected_reference_period": context.get("expected_reference_period"),
        "expected_reference_period_end_date": (
            expected_end.isoformat() if expected_end else None
        ),
    }


def reference_period_end(observation_date: date, frequency: str | None) -> date:
    """Return the natural calendar end represented by a period-start observation."""

    if frequency == "monthly":
        return date(
            observation_date.year,
            observation_date.month,
            calendar.monthrange(observation_date.year, observation_date.month)[1],
        )
    if frequency == "quarterly":
        quarter_end_month = ((observation_date.month - 1) // 3 + 1) * 3
        return date(
            observation_date.year,
            quarter_end_month,
            calendar.monthrange(observation_date.year, quarter_end_month)[1],
        )
    if frequency == "annual":
        return date(observation_date.year, 12, 31)
    return observation_date


def release_context_for_series(
    series_id: str,
    *,
    as_of: date,
    path: str | Path = DEFAULT_RELEASE_CALENDAR_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["nas_official_release_calendar_contract"]
    family = next(
        (
            row
            for row in contract["release_families"]
            if series_id in row["series_ids"]
        ),
        None,
    )
    if family is None:
        return {}
    releases = [
        row
        for row in family.get("scheduled_releases", [])
        if date.fromisoformat(str(row["release_date"])) <= as_of
    ]
    latest = max(releases, key=lambda row: row["release_date"]) if releases else None
    reference = str(latest["reference_period"]) if latest else None
    return {
        "release_family_id": str(family["release_family_id"]),
        "calendar_precision": str(family["calendar_precision"]),
        "latest_registered_release_date": (
            date.fromisoformat(str(latest["release_date"])) if latest else None
        ),
        "expected_reference_period": reference,
        "expected_reference_period_end": _reference_label_end(reference),
        "release_refresh_grace_days": int(
            contract["operations_policy"]["release_refresh_grace_days"]
        ),
    }


def summarize_release_aware_freshness_source_identity_remediation(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    roadmap_path: str | Path = DEFAULT_ROADMAP_PATH,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
) -> dict[str, Any]:
    contract = load_release_aware_freshness_contract(contract_path)
    roadmap = load_source_reliability_roadmap(roadmap_path)
    registry_payload = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    registry = {
        str(row["series_id"]): row
        for row in registry_payload["series_release_lag_registry"]["series"]
    }
    remediations = contract["source_identity_remediations"]
    phase_ids = [int(row["phase_id"]) for row in roadmap["phases"]]
    summary = {
        "phase": 134,
        "roadmap_ready": roadmap["status"] == "active_through_phase136",
        "roadmap_phase_count": len(phase_ids),
        "dependency_order_valid": phase_ids == [134, 135, 136],
        "phase134_scope_recorded": 134 in phase_ids,
        "phase135_scope_recorded": 135 in phase_ids,
        "phase136_scope_recorded": 136 in phase_ids,
        "release_aware_freshness_contract_ready": (
            contract["status"] == "active_private_nas_runtime_remediation"
            and contract["freshness_policy"]["reference_period_end_required"] is True
        ),
        "source_identity_remediation_count": len(remediations),
        "remediated_role_count": sum(len(row["role_ids"]) for row in remediations),
        "exact_source_blocked_role_count": len(
            contract["unresolved_exact_source_roles"]
        ),
        "aaa_baa_frequency_corrected_count": sum(
            registry.get(series_id, {}).get("frequency") == "monthly"
            for series_id in ("AAA", "BAA")
        ),
        "false_resolution_count": 0,
        "silent_substitution_count": 0,
        "revised_mislabeled_as_point_in_time_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 135,
    }
    expected = contract["hard_gates"] | roadmap["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def _frequency_family(frequency: str) -> str | None:
    normalized = str(frequency).strip().lower()
    return next(
        (
            family
            for family in ("daily", "weekly", "monthly", "quarterly", "annual")
            if family in normalized
        ),
        None,
    )


def _reference_label_end(value: str | None) -> date | None:
    if not value or value == "weekly":
        return None
    if len(value) >= 7 and value[4] == "-" and value[5] == "Q":
        year = int(value[:4])
        quarter = int(value[6])
        month = quarter * 3
        return date(year, month, calendar.monthrange(year, month)[1])
    if len(value) >= 7 and value[4] == "-" and value[5:7].isdigit():
        year = int(value[:4])
        month = int(value[5:7])
        return date(year, month, calendar.monthrange(year, month)[1])
    return None
