"""Official macro source wiring for current research evidence gaps."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SERIES_REGISTRY_PATH = ROOT / "specs/common/series_release_lag_registry.yaml"
PHASE52_ID = "Phase52"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "trade_action",
    "buy_signal",
    "sell_signal",
}

ALIAS_TO_OFFICIAL_SERIES: dict[str, tuple[str, ...]] = {
    "initial_jobless_claims": ("ICSA",),
    "continuing_jobless_claims": ("CCSA",),
    "short_term_unemployment": ("UEMPLT5",),
    "durable_goods_orders": ("DGORDER",),
    "exports_goods_services": ("EXPGS",),
    "imports_goods_services": ("IMPGS",),
    "industrial_production": ("INDPRO",),
    "real_personal_consumption_expenditures": ("PCEC96",),
    "real_private_fixed_investment": ("FPIC1",),
    "real_pce_durable_goods": ("PCEDGC96",),
    "real_retail_sales": ("RRSFS",),
    "PAYEMS": ("PAYEMS",),
    "CPILFESL": ("CPILFESL",),
    "PCEPILFE": ("PCEPILFE",),
    "PSAVERT": ("PSAVERT",),
    "PRFIC1": ("PRFIC1",),
    "DRBLACBS": ("DRBLACBS",),
    "DRCLACBS": ("DRCLACBS",),
    "W006RC1Q027SBEA": ("W006RC1Q027SBEA",),
    "CBIC1": ("CBIC1",),
    "BUSINV": ("BUSINV",),
    "SLCEC1": ("SLCEC1",),
}

SOURCE_IDENTITY_CORRECTIONS = {
    "real_personal_consumption_expenditures": {
        "incorrect_candidate_series_id": "PCECC96",
        "corrected_official_series_id": "PCEC96",
        "reason": "repository registry and recession candidate contracts use PCEC96 for real PCE",
    }
}


def resolve_official_series_ids(series_ids: list[str] | tuple[str, ...]) -> list[str]:
    """Resolve semantic indicator aliases to official current-refresh series IDs."""

    resolved: list[str] = []
    for series_id in series_ids:
        mapped = ALIAS_TO_OFFICIAL_SERIES.get(str(series_id), (str(series_id),))
        for official_id in mapped:
            if official_id not in resolved:
                resolved.append(official_id)
    return resolved


def build_official_macro_source_wiring_rows(
    *,
    gap_rows: list[dict[str, Any]] | None = None,
    registry_path: str | Path = DEFAULT_SERIES_REGISTRY_PATH,
) -> list[dict[str, Any]]:
    """Build Phase52 one-row-per-role official macro source wiring."""

    from business_cycle.audits.macro_indicator_gap_alternative_sources import (
        build_macro_indicator_gap_alternative_source_rows,
    )

    registry = _series_registry(registry_path)
    gap_rows = gap_rows or build_macro_indicator_gap_alternative_source_rows()
    rows: list[dict[str, Any]] = []
    for gap in gap_rows:
        if gap["planned_resolution_phase"] != PHASE52_ID:
            continue
        candidate = _select_current_refresh_candidate(gap)
        official_series_ids = resolve_official_series_ids(gap["required_series_ids"])
        registry_entries = [registry.get(series_id) for series_id in official_series_ids]
        missing_series = [
            series_id
            for series_id, entry in zip(official_series_ids, registry_entries, strict=False)
            if entry is None
        ]
        disabled_series = [
            series_id
            for series_id, entry in zip(official_series_ids, registry_entries, strict=False)
            if entry is not None and entry.get("current_refresh_fetch_enabled") is False
        ]
        metadata_incomplete = [
            series_id
            for series_id, entry in zip(official_series_ids, registry_entries, strict=False)
            if entry is not None and not _registry_entry_complete(entry)
        ]
        source_corrections = [
            {
                "role_id": gap["role_id"],
                **SOURCE_IDENTITY_CORRECTIONS[series_id],
            }
            for series_id in gap["required_series_ids"]
            if series_id in SOURCE_IDENTITY_CORRECTIONS
        ]
        primary_deferred = candidate["candidate_id"] != gap["preferred_candidate_id"]
        wired = not missing_series and not disabled_series and not metadata_incomplete
        rows.append(
            {
                "role_id": gap["role_id"],
                "phase_or_layer": gap["phase_or_layer"],
                "major_group_id": gap["major_group_id"],
                "source_alias_ids": gap["required_series_ids"],
                "official_series_ids": official_series_ids,
                "current_refresh_adapter_ids": [
                    f"fred_current_refresh::{series_id}"
                    for series_id in official_series_ids
                ],
                "selected_candidate_id": candidate["candidate_id"],
                "phase51_preferred_candidate_id": gap["preferred_candidate_id"],
                "primary_direct_release_adapter_deferred": primary_deferred,
                "source_family": candidate["source_family"],
                "source_credibility_tier": candidate["source_credibility_tier"],
                "substitution_degree": candidate["substitution_degree"],
                "automation_feasibility": candidate["automation_feasibility"],
                "data_risk_level": candidate["data_risk_level"],
                "book_core_replacement_allowed": candidate[
                    "book_core_replacement_allowed"
                ],
                "current_refresh_registry_present": not missing_series,
                "release_lag_metadata_complete": not metadata_incomplete,
                "current_refresh_fetch_enabled": not disabled_series,
                "source_identity_corrections": source_corrections,
                "wiring_status": "wired" if wired else "blocked",
                "blocked_reason_codes": _blocked_reasons(
                    missing_series=missing_series,
                    disabled_series=disabled_series,
                    metadata_incomplete=metadata_incomplete,
                ),
                "silent_substitution": False,
                "alternative_promoted_to_core": False,
                "allowed_uses": [
                    "current_research_evidence_source_resolution",
                    "transition_surface_data_risk_explanation",
                    "future_current_dashboard_gap_reduction_input",
                ],
                "prohibited_uses": [
                    "formal_current_phase_decision",
                    "candidate_phase_selection",
                    "production_decision",
                    "portfolio_or_trade_decision",
                ],
            }
        )
    return rows


def summarize_official_macro_source_adapter_wiring() -> dict[str, Any]:
    """Summarize Phase52 official macro source wiring gates."""

    rows = build_official_macro_source_wiring_rows()
    unique_series = sorted(
        {series_id for row in rows for series_id in row["official_series_ids"]}
    )
    wired_rows = [row for row in rows if row["wiring_status"] == "wired"]
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    family_counts = Counter(row["source_family"] for row in rows)
    risk_counts = Counter(row["data_risk_level"] for row in rows)
    missing_risk = [row for row in rows if not row["data_risk_level"]]
    missing_substitution = [row for row in rows if not row["substitution_degree"]]
    registry_missing = [
        row for row in rows if not row["current_refresh_registry_present"]
    ]
    metadata_incomplete = [
        row for row in rows if not row["release_lag_metadata_complete"]
    ]
    disabled = [row for row in rows if not row["current_refresh_fetch_enabled"]]
    summary = {
        "official_macro_source_adapter_wiring_ready": (
            bool(rows)
            and len(wired_rows) == len(rows)
            and not missing_risk
            and not missing_substitution
            and not registry_missing
            and not metadata_incomplete
            and not disabled
        ),
        "phase52_candidate_role_count": len(rows),
        "official_wired_role_count": len(wired_rows),
        "unique_official_series_count": len(unique_series),
        "unique_official_series_ids": unique_series,
        "phase52_phase_counts": dict(sorted(phase_counts.items())),
        "source_family_counts": dict(sorted(family_counts.items())),
        "data_risk_level_counts": dict(sorted(risk_counts.items())),
        "source_risk_label_missing_count": len(missing_risk),
        "substitution_degree_missing_count": len(missing_substitution),
        "registry_missing_series_count": sum(
            len(row["blocked_reason_codes"])
            for row in registry_missing
            if "missing_current_refresh_registry_series" in row["blocked_reason_codes"]
        ),
        "release_lag_metadata_incomplete_count": len(metadata_incomplete),
        "current_refresh_disabled_series_count": len(disabled),
        "direct_release_adapter_deferred_count": sum(
            row["primary_direct_release_adapter_deferred"] for row in rows
        ),
        "source_identity_correction_count": sum(
            len(row["source_identity_corrections"]) for row in rows
        ),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "alternative_promoted_to_core_count": sum(
            row["alternative_promoted_to_core"] for row in rows
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prohibited_output_field_count": _contains_prohibited_field(rows),
        "rows": rows,
    }
    summary["result"] = "passed" if _passes(summary) else "blocked"
    return summary


def _select_current_refresh_candidate(gap: dict[str, Any]) -> dict[str, Any]:
    for candidate in gap["alternative_source_candidates"]:
        if candidate["automation_feasibility"] == "adapter_reuse":
            return candidate
    return gap["alternative_source_candidates"][0]


def _series_registry(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = payload["series_release_lag_registry"]["series"]
    return {str(row["series_id"]): row for row in rows}


def _registry_entry_complete(entry: dict[str, Any]) -> bool:
    return (
        bool(entry.get("release_lag_rule"))
        and entry.get("release_lag_rule") != "unsupported"
        and entry.get("source") == "FRED/ALFRED"
        and entry.get("point_in_time_eligible") is True
    )


def _blocked_reasons(
    *,
    missing_series: list[str],
    disabled_series: list[str],
    metadata_incomplete: list[str],
) -> list[str]:
    reasons = []
    if missing_series:
        reasons.append("missing_current_refresh_registry_series")
    if disabled_series:
        reasons.append("current_refresh_disabled")
    if metadata_incomplete:
        reasons.append("release_lag_metadata_incomplete")
    return reasons


def _passes(summary: dict[str, Any]) -> bool:
    return (
        summary["official_macro_source_adapter_wiring_ready"] is True
        and summary["phase52_candidate_role_count"] == 29
        and summary["official_wired_role_count"] == 29
        and summary["unique_official_series_count"] >= 15
        and summary["source_risk_label_missing_count"] == 0
        and summary["substitution_degree_missing_count"] == 0
        and summary["registry_missing_series_count"] == 0
        and summary["release_lag_metadata_incomplete_count"] == 0
        and summary["current_refresh_disabled_series_count"] == 0
        and summary["silent_substitution_count"] == 0
        and summary["alternative_promoted_to_core_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["production_behavior_change_count"] == 0
        and summary["prohibited_output_field_count"] == 0
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0
