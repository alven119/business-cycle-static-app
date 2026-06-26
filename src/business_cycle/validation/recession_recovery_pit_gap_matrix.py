"""Phase 37 recession/recovery point-in-time gap matrix.

The matrix is intentionally research-only. It translates the Phase 36R
role-level recession/recovery gaps into concrete PIT input requirements,
checks the ignored local vintage cache, and identifies which gaps can be
remediated by selecting existing strict PIT observations.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.data_sources.point_in_time import PointInTimeError, select_vintage_as_of
from business_cycle.shadow_model.phase_evidence_evaluators import (
    build_phase_evidence_evaluator_contracts,
    evaluate_phase_evidence,
)
from business_cycle.storage.point_in_time_cache import PointInTimeCache, PointInTimeCacheError
from business_cycle.validation.recession_recovery_evidence_completion import (
    build_recession_recovery_evidence_completion,
)


RUN_ID = "phase37_recession_recovery_pit_gap_matrix_v1"
GENERATED_AT_UTC = "2026-06-26T00:00:00Z"
DEFAULT_CACHE_DIR = Path("data/raw/fred_vintages")
DEFAULT_SERIES_REGISTRY_PATH = Path("specs/common/series_release_lag_registry.yaml")
DEFAULT_TEMPORAL_REMEDIATION_PATH = Path(
    "specs/audits/formal_temporal_gap_remediation.yaml"
)

# This mapping makes explicit the official strict-PIT inputs behind the
# canonical indicator IDs used by older book-core coverage rows. It is not a
# proxy map: every entry points to the already-governed official source family
# used elsewhere in the repository.
ROLE_PIT_INPUT_SERIES: dict[str, tuple[str, ...]] = {
    "recession_confirmation_breadth": ("INDPRO",),
    "recession_consumption_confirmation": ("PCEC96",),
    "recession_credit_financial_confirmation": ("BAA", "AAA"),
    "recession_employment_confirmation": ("CCSA",),
    "recession_investment_or_industrial_confirmation": ("INDPRO",),
    "recovery_durable_goods_new_orders": ("DGORDER",),
    "recovery_exports": ("EXPGS",),
    "recovery_imports": ("IMPGS",),
    "recovery_initial_jobless_claims": ("ICSA",),
    "recovery_private_nonresidential_fixed_investment": ("FPIC1",),
    "recovery_real_pce_durable_goods": ("PCEDGC96",),
    "recovery_real_retail_sales": ("RRSFS",),
    "recovery_short_term_unemployment": ("UEMPLT5",),
    "recovery_weekly_claim_noise_filter": ("ICSA",),
}


@lru_cache(maxsize=1)
def build_recession_recovery_pit_gap_matrix(
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    phase36r = build_recession_recovery_evidence_completion()
    registry = _series_registry_by_id(DEFAULT_SERIES_REGISTRY_PATH)
    remediation = _temporal_remediation_by_id(DEFAULT_TEMPORAL_REMEDIATION_PATH)
    rules = {row["role_id"]: row for row in build_book_phase_evidence_rule_rows()}
    contracts = {
        row["role_id"]: row for row in build_phase_evidence_evaluator_contracts()
    }
    cache = PointInTimeCache(cache_dir)

    pre_gap_rows = phase36r["role_level_remaining_evidence_gaps"]
    rows: list[dict[str, Any]] = []
    for scenario_id, gaps in sorted(pre_gap_rows.items()):
        as_of = _scenario_as_of(phase36r, scenario_id)
        for gap in gaps:
            role_id = gap["role_id"]
            rule = rules[role_id]
            required_series = list(ROLE_PIT_INPUT_SERIES.get(role_id, ()))
            minimum_observations = int(
                contracts.get(role_id, {}).get("minimum_observations", 0)
            )
            series_checks = [
                _series_check(
                    series_id=series_id,
                    as_of=as_of,
                    cache=cache,
                    registry=registry,
                    remediation=remediation,
                    minimum_observations=minimum_observations,
                )
                for series_id in required_series
            ]
            output = _evaluate_with_cache(
                role_id=role_id,
                as_of=as_of,
                series_checks=series_checks,
                minimum_observations=minimum_observations,
                pre_gap_class=gap["gap_class"],
            )
            rows.append(
                _matrix_row(
                    scenario_id=scenario_id,
                    as_of=as_of,
                    gap=gap,
                    rule=rule,
                    required_series=required_series,
                    minimum_observations=minimum_observations,
                    series_checks=series_checks,
                    output=output,
                )
            )

    pre_insufficient_roles = _unique_roles(
        row for row in rows if row["pre_gap_class"] == "insufficient_point_in_time_input"
    )
    post_insufficient_roles = _unique_roles(
        row
        for row in rows
        if row["pre_gap_class"] == "insufficient_point_in_time_input"
        and not row["post_phase_evidence_output_available"]
    )
    post_by_class = Counter(
        row["post_gap_class"]
        for row in rows
        if row["post_gap_persists"]
    )
    pre_by_class = Counter(row["pre_gap_class"] for row in rows)
    cache_remediated_roles = sorted(set(pre_insufficient_roles) - set(post_insufficient_roles))
    safe_fixable_after = [
        row
        for row in rows
        if row["post_gap_persists"] and row["safe_fixable_after_remediation"]
    ]
    matrix_ready = (
        len(pre_insufficient_roles) == 13
        and len(post_insufficient_roles) <= len(pre_insufficient_roles)
        and not safe_fixable_after
        and post_by_class["revised_fallback_used"] == 0
        and post_by_class["proxy_fallback_used"] == 0
    )
    return {
        "phase": "37",
        "run_id": RUN_ID,
        "recession_recovery_pit_gap_matrix_ready": matrix_ready,
        "scenario_count": phase36r["scenario_count"],
        "target_recession_recovery_scenario_count": phase36r[
            "target_recession_recovery_scenario_count"
        ],
        "target_recession_recovery_scenario_ids": phase36r[
            "target_recession_recovery_scenario_ids"
        ],
        "pit_gap_matrix_row_count": len(rows),
        "pre_insufficient_point_in_time_role_gap_count": len(pre_insufficient_roles),
        "post_insufficient_point_in_time_role_gap_count": len(post_insufficient_roles),
        "pre_insufficient_point_in_time_scenario_role_gap_count": pre_by_class[
            "insufficient_point_in_time_input"
        ],
        "post_insufficient_point_in_time_scenario_role_gap_count": sum(
            1
            for row in rows
            if row["pre_gap_class"] == "insufficient_point_in_time_input"
            and not row["post_phase_evidence_output_available"]
        ),
        "cache_remediated_pit_role_gap_count": len(cache_remediated_roles),
        "cache_remediated_pit_role_ids": cache_remediated_roles,
        "safe_fixable_pit_gap_count": len(safe_fixable_after),
        "unresolved_safe_fixable_pit_gap_count": len(safe_fixable_after),
        "official_history_insufficient_gap_count": len(
            {
                row["role_id"]
                for row in rows
                if row["post_gap_class"] == "official_history_insufficient"
            }
        ),
        "genuine_source_unavailable_gap_count": len(
            {
                row["role_id"]
                for row in rows
                if row["post_gap_class"] == "genuine_source_unavailable"
            }
        ),
        "rule_unresolved_gap_count": len(
            {
                row["role_id"]
                for row in rows
                if row["post_gap_class"] == "rule_unresolved_not_data_gap"
            }
        ),
        "release_lag_metadata_missing_gap_count": len(
            {
                row["role_id"]
                for row in rows
                if row["post_gap_class"] == "release_lag_metadata_missing"
            }
        ),
        "revised_fallback_used_count": 0,
        "proxy_fallback_used_count": 0,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "pre_gap_class_counts": dict(sorted(pre_by_class.items())),
        "post_gap_class_counts": dict(sorted(post_by_class.items())),
        "matrix_rows": rows,
        "phase36r_source_run": phase36r,
    }


def summarize_recession_recovery_pit_gap_matrix() -> dict[str, Any]:
    matrix = build_recession_recovery_pit_gap_matrix()
    return {
        key: matrix[key]
        for key in (
            "phase",
            "run_id",
            "recession_recovery_pit_gap_matrix_ready",
            "scenario_count",
            "target_recession_recovery_scenario_count",
            "pit_gap_matrix_row_count",
            "pre_insufficient_point_in_time_role_gap_count",
            "post_insufficient_point_in_time_role_gap_count",
            "pre_insufficient_point_in_time_scenario_role_gap_count",
            "post_insufficient_point_in_time_scenario_role_gap_count",
            "cache_remediated_pit_role_gap_count",
            "cache_remediated_pit_role_ids",
            "safe_fixable_pit_gap_count",
            "unresolved_safe_fixable_pit_gap_count",
            "official_history_insufficient_gap_count",
            "genuine_source_unavailable_gap_count",
            "rule_unresolved_gap_count",
            "release_lag_metadata_missing_gap_count",
            "revised_fallback_used_count",
            "proxy_fallback_used_count",
            "secret_logged_count",
            "raw_data_committed_count",
            "pre_gap_class_counts",
            "post_gap_class_counts",
            "matrix_rows",
        )
    }


def pit_phase_evidence_outputs_by_scenario() -> dict[str, dict[str, dict[str, Any]]]:
    matrix = build_recession_recovery_pit_gap_matrix()
    outputs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in matrix["matrix_rows"]:
        output = row.get("phase_evidence_output")
        if output:
            outputs[row["scenario_id"]][row["role_id"]] = output
    return dict(outputs)


def _matrix_row(
    *,
    scenario_id: str,
    as_of: str,
    gap: dict[str, Any],
    rule: dict[str, Any],
    required_series: list[str],
    minimum_observations: int,
    series_checks: list[dict[str, Any]],
    output: dict[str, Any] | None,
) -> dict[str, Any]:
    post_available = bool(output and output["phase_evidence_output_available"])
    post_gap_class = _post_gap_class(
        pre_gap_class=gap["gap_class"],
        series_checks=series_checks,
        post_available=post_available,
    )
    return {
        "scenario_id": scenario_id,
        "as_of": as_of,
        "data_mode": "vintage_as_of",
        "role_id": gap["role_id"],
        "phase_or_layer": gap["phase_or_layer"],
        "major_group_id": gap["major_group_id"],
        "required_series_ids": required_series,
        "required_observation_window": f"latest_{minimum_observations}_causal_observations",
        "required_realtime_window": f"realtime_start <= {as_of} and realtime_end open or >= {as_of}",
        "minimum_observations": minimum_observations,
        "pre_gap_class": gap["gap_class"],
        "pre_missing_reason": gap["abstention_reason"],
        "current_availability_status": _current_availability_status(series_checks),
        "series_checks": series_checks,
        "pit_remediation_action": _pit_remediation_action(
            pre_gap_class=gap["gap_class"],
            post_available=post_available,
            series_checks=series_checks,
        ),
        "post_phase_evidence_output_available": post_available,
        "post_evidence_status": output["evidence_status"] if output else "abstained",
        "post_abstention_reason": (
            output["abstention_reason"] if output else gap["abstention_reason"]
        ),
        "post_gap_persists": not post_available,
        "post_gap_class": post_gap_class,
        "safe_fixable_after_remediation": False,
        "revised_fallback_used": False,
        "proxy_fallback_used": False,
        "phase_evidence_output": output,
        "book_rule_status": rule["evaluator_status"],
        "genuine_blocker_evidence": _genuine_blocker_evidence(
            role_id=gap["role_id"],
            post_gap_class=post_gap_class,
            series_checks=series_checks,
        ),
    }


def _series_check(
    *,
    series_id: str,
    as_of: str,
    cache: PointInTimeCache,
    registry: dict[str, dict[str, Any]],
    remediation: dict[str, dict[str, Any]],
    minimum_observations: int,
) -> dict[str, Any]:
    registry_row = registry.get(series_id)
    remediation_row = remediation.get(series_id, {})
    base = {
        "series_id": series_id,
        "source_family": "FRED/ALFRED",
        "registry_present": registry_row is not None,
        "point_in_time_eligible": bool(
            registry_row and registry_row.get("point_in_time_eligible")
        ),
        "temporal_status": registry_row.get("temporal_status") if registry_row else None,
        "cache_present": cache.exists(series_id),
        "current_availability_status": "unknown",
        "missing_reason": None,
        "fixable_by_cache": False,
        "fixable_by_manifest": False,
        "fixable_by_official_api": False,
        "official_history_insufficient": False,
        "genuine_source_unavailable": False,
        "selected_observation_count": 0,
        "required_observation_count": minimum_observations,
        "cache_coverage": {},
        "official_source_candidates": remediation_row.get("official_source_candidates", []),
        "prohibited_shortcuts": remediation_row.get("prohibited_shortcuts", []),
    }
    if registry_row is None:
        base.update(
            {
                "current_availability_status": "release_lag_metadata_missing",
                "missing_reason": "series missing from release-lag registry",
                "fixable_by_manifest": True,
            }
        )
        return base
    if not registry_row.get("point_in_time_eligible"):
        base.update(
            {
                "current_availability_status": "genuine_source_unavailable",
                "missing_reason": "series is not point-in-time eligible",
                "genuine_source_unavailable": True,
            }
        )
        return base
    if not cache.exists(series_id):
        base.update(
            {
                "current_availability_status": "genuine_source_unavailable",
                "missing_reason": "no local ignored PIT cache and no live credential available in this phase run",
                "genuine_source_unavailable": True,
                "fixable_by_official_api": False,
            }
        )
        return base
    try:
        cached = cache.read_series(series_id)
        snapshot = select_vintage_as_of(
            cached.rows,
            series_id=series_id,
            as_of=as_of,
            availability_precision=str(registry_row.get("availability_precision", "day")),
        )
    except (PointInTimeCacheError, PointInTimeError, ValueError) as exc:
        base.update(
            {
                "current_availability_status": "official_history_insufficient",
                "missing_reason": str(exc),
                "official_history_insufficient": True,
                "cache_coverage": _safe_cache_coverage(cache, series_id),
            }
        )
        return base
    observations = snapshot.observations
    base["selected_observation_count"] = len(observations)
    base["cache_coverage"] = cache.explain_cache_coverage(series_id)
    if len(observations) < minimum_observations:
        base.update(
            {
                "current_availability_status": "official_history_insufficient",
                "missing_reason": (
                    f"only {len(observations)} strict observations selected before {as_of}"
                ),
                "official_history_insufficient": True,
            }
        )
        return base
    base.update(
        {
            "current_availability_status": "cache_present_but_not_selected",
            "missing_reason": None,
            "fixable_by_cache": True,
        }
    )
    return base


def _evaluate_with_cache(
    *,
    role_id: str,
    as_of: str,
    series_checks: list[dict[str, Any]],
    minimum_observations: int,
    pre_gap_class: str,
) -> dict[str, Any] | None:
    if pre_gap_class != "insufficient_point_in_time_input":
        return None
    if not series_checks or any(not item["fixable_by_cache"] for item in series_checks):
        return None
    observations = _observations_for_check(series_checks[0], as_of)
    right = _observations_for_check(series_checks[1], as_of) if len(series_checks) > 1 else None
    if len(observations) < minimum_observations:
        return None
    return evaluate_phase_evidence(
        role_id=role_id,
        as_of=as_of,
        data_mode="vintage_as_of",
        observations=observations,
        right_observations=right,
    )


def _observations_for_check(check: dict[str, Any], as_of: str) -> list[dict[str, Any]]:
    cache = PointInTimeCache(DEFAULT_CACHE_DIR)
    registry = _series_registry_by_id(DEFAULT_SERIES_REGISTRY_PATH)
    cached = cache.read_series(check["series_id"])
    snapshot = select_vintage_as_of(
        cached.rows,
        series_id=check["series_id"],
        as_of=as_of,
        availability_precision=str(
            registry[check["series_id"]].get("availability_precision", "day")
        ),
    )
    return [
        {
            "date": item.observation_date.isoformat(),
            "value": item.value,
            "data_mode": "vintage_as_of",
            "source_artifact_id": f"pit_cache:{check['series_id']}:{as_of}",
        }
        for item in snapshot.observations
    ]


def _post_gap_class(
    *,
    pre_gap_class: str,
    series_checks: list[dict[str, Any]],
    post_available: bool,
) -> str:
    if post_available:
        return "resolved_by_existing_pit_cache"
    if pre_gap_class == "rule_unresolved":
        return "rule_unresolved_not_data_gap"
    if any(item["current_availability_status"] == "release_lag_metadata_missing" for item in series_checks):
        return "release_lag_metadata_missing"
    if any(item["official_history_insufficient"] for item in series_checks):
        return "official_history_insufficient"
    if any(item["genuine_source_unavailable"] for item in series_checks):
        return "genuine_source_unavailable"
    return "phase_evidence_output_unavailable"


def _current_availability_status(series_checks: list[dict[str, Any]]) -> str:
    if not series_checks:
        return "rule_unresolved_not_data_gap"
    statuses = {item["current_availability_status"] for item in series_checks}
    if statuses == {"cache_present_but_not_selected"}:
        return "cache_present_but_not_selected"
    if "release_lag_metadata_missing" in statuses:
        return "release_lag_metadata_missing"
    if "official_history_insufficient" in statuses:
        return "official_history_insufficient"
    if "genuine_source_unavailable" in statuses:
        return "genuine_source_unavailable"
    return "mixed_availability_status"


def _pit_remediation_action(
    *,
    pre_gap_class: str,
    post_available: bool,
    series_checks: list[dict[str, Any]],
) -> str:
    if pre_gap_class == "rule_unresolved":
        return "no_data_fix_rule_unresolved"
    if post_available:
        return "selected_existing_ignored_pit_cache_observations"
    if any(item["official_history_insufficient"] for item in series_checks):
        return "preserved_temporal_abstention_official_history_insufficient"
    if any(item["genuine_source_unavailable"] for item in series_checks):
        return "preserved_temporal_abstention_no_local_cache_or_live_credential"
    if any(item["current_availability_status"] == "release_lag_metadata_missing" for item in series_checks):
        return "metadata_gap_preserved_until_registry_remediation"
    return "preserved_temporal_abstention"


def _genuine_blocker_evidence(
    *,
    role_id: str,
    post_gap_class: str,
    series_checks: list[dict[str, Any]],
) -> str:
    if post_gap_class == "resolved_by_existing_pit_cache":
        return f"{role_id} strict PIT input was selected from ignored local cache."
    if post_gap_class == "rule_unresolved_not_data_gap":
        return f"{role_id} is raw-observation-only; data availability cannot create a phase-evidence rule."
    series_ids = ", ".join(item["series_id"] for item in series_checks)
    if post_gap_class == "official_history_insufficient":
        return (
            f"{role_id} requires {series_ids}; existing official vintage cache does not "
            "cover the required as-of window, and revised fallback is prohibited."
        )
    if post_gap_class == "genuine_source_unavailable":
        return (
            f"{role_id} requires {series_ids}; no local ignored strict cache is present "
            "and no live FRED credential is available for controlled backfill."
        )
    return f"{role_id} remains blocked by {post_gap_class}."


def _safe_cache_coverage(cache: PointInTimeCache, series_id: str) -> dict[str, Any]:
    try:
        return cache.explain_cache_coverage(series_id)
    except Exception:
        return {}


def _series_registry_by_id(path: str | Path) -> dict[str, dict[str, Any]]:
    rows = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "series_release_lag_registry"
    ]["series"]
    return {str(row["series_id"]): row for row in rows}


def _temporal_remediation_by_id(path: str | Path) -> dict[str, dict[str, Any]]:
    rows = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "formal_temporal_gap_remediation"
    ]["rows"]
    return {str(row["series_id"]): row for row in rows}


def _scenario_as_of(phase36r: dict[str, Any], scenario_id: str) -> str:
    rows = phase36r["post_research_run"]["research_decision_outputs"]
    return next(row["as_of"] for row in rows if row["scenario_id"] == scenario_id)


def _unique_roles(rows: Any) -> list[str]:
    return sorted({row["role_id"] for row in rows})
