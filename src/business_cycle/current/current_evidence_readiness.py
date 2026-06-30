"""Research-only current evidence readiness profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_core_data_contracts import build_book_core_data_contracts
from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
    safely_operationalizable_role_ids,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.current.current_freshness_semantics import (
    DEFAULT_PHASE41_BLOCKED_MANIFEST,
    DEFAULT_PHASE41_LIVE_MANIFEST,
    freshness_rows_by_series,
    summarize_current_freshness_semantics,
)
from business_cycle.current.official_macro_source_wiring import (
    resolve_official_series_ids,
)
from business_cycle.storage.raw_store import RawCsvStore
from business_cycle.shadow_model.phase_evidence_evaluators import evaluate_phase_evidence


CURRENT_EVIDENCE_READINESS_VERSION = "phase42_current_evidence_readiness_v1"
MODEL_ID = "book_faithful_shadow_v2_alpha39"
FREEZE_ID = "book_faithful_shadow_v2_alpha39"
PHASE_ORDER = ("recovery", "growth", "boom", "recession")
LAYER_TO_PHASE = {
    "recovery_indicators": "recovery",
    "growth_indicators": "growth",
    "boom_ending_indicators": "boom",
    "recession_trough_requirements": "recession",
}
TRANSITION_LAYERS = {"boom_ending_indicators", "recession_trough_requirements"}
PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "predicted_current_phase",
    "selected_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "trade_action",
    "buy_signal",
    "sell_signal",
}


def build_current_evidence_readiness(
    *,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest(
        refresh_manifest_path=refresh_manifest_path,
        refresh_manifest=refresh_manifest,
    )
    freshness = summarize_current_freshness_semantics(refresh_manifest=manifest)
    freshness_by_series = freshness_rows_by_series(freshness)
    contracts = {row["role_id"]: row for row in build_book_core_data_contracts()}
    rules = build_book_phase_evidence_rule_rows()
    safe_roles = safely_operationalizable_role_ids()
    store = _store_from_manifest(manifest)
    role_rows = [
        _role_readiness_row(
            rule,
            contract=contracts[rule["role_id"]],
            freshness_by_series=freshness_by_series,
            safe_roles=safe_roles,
            store=store,
            snapshot_as_of=manifest["snapshot_as_of"],
            data_mode=manifest["data_mode"],
        )
        for rule in rules
        if rule["phase_or_layer"] in LAYER_TO_PHASE
    ]
    profiles = {
        phase: _phase_profile(phase, role_rows)
        for phase in PHASE_ORDER
    }
    summary = {
        "current_evidence_readiness_version": CURRENT_EVIDENCE_READINESS_VERSION,
        "snapshot_as_of": manifest["snapshot_as_of"],
        "data_mode": manifest["data_mode"],
        "refresh_mode": freshness["refresh_mode"],
        "model_id": MODEL_ID,
        "freeze_id": FREEZE_ID,
        "output_mode": "research_only",
        "phase_profiles": profiles,
        "phase_profile_count": len(profiles),
        "global_blockers": _global_blockers(freshness, role_rows),
        "allowed_uses": [
            "local_research_dashboard",
            "current_evidence_readiness_review",
            "abstention_explanation",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
        "trust_metadata": {
            "data_last_updated_at": f"{manifest['snapshot_as_of']}T00:00:00Z",
            "data_completeness": "partial_or_abstained",
            "stale_or_missing_status": "frequency_release_lag_aware",
            "model_version": MODEL_ID,
            "freeze_id": FREEZE_ID,
            "validation_status": (
                "current_evidence_profile_available_no_current_phase_or_performance"
            ),
            "output_label": "research_only",
        },
        "candidate_selection_enabled": False,
        "current_evidence_readiness_ready": True,
        "selected_phase_output_count": 0,
        "phase_rank_output_count": 0,
        "numeric_phase_score_output_count": 0,
        "role_count_voting_added_count": 0,
        "formal_phase_eligible_count": 0,
        "candidate_phase_eligible_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "why_not_formal_phase_present": True,
        "blocker_summary_present": True,
        "research_only_label_present": True,
        "prohibited_field_count": 0,
        "freshness_summary": freshness,
        "role_readiness_rows": role_rows,
    }
    summary["prohibited_field_count"] = _contains_prohibited_field(summary)
    summary["result"] = "passed" if _passes(summary) else "blocked"
    return summary


def summarize_current_evidence_readiness(
    *,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = build_current_evidence_readiness(
        refresh_manifest_path=refresh_manifest_path,
        refresh_manifest=refresh_manifest,
    )
    return {
        "phase": "42",
        "current_evidence_readiness_ready": readiness[
            "current_evidence_readiness_ready"
        ],
        "snapshot_as_of": readiness["snapshot_as_of"],
        "data_mode": readiness["data_mode"],
        "refresh_mode": readiness["refresh_mode"],
        "model_id": readiness["model_id"],
        "freeze_id": readiness["freeze_id"],
        "phase_profile_count": readiness["phase_profile_count"],
        "phase_profiles": readiness["phase_profiles"],
        "current_phase_emitted": readiness["current_phase_emitted"],
        "candidate_phase_emitted": readiness["candidate_phase_emitted"],
        "selected_phase_output_count": readiness["selected_phase_output_count"],
        "phase_rank_output_count": readiness["phase_rank_output_count"],
        "numeric_phase_score_output_count": readiness[
            "numeric_phase_score_output_count"
        ],
        "role_count_voting_added_count": readiness[
            "role_count_voting_added_count"
        ],
        "formal_phase_eligible_count": readiness["formal_phase_eligible_count"],
        "candidate_phase_eligible_count": readiness[
            "candidate_phase_eligible_count"
        ],
        "why_not_formal_phase_present": readiness[
            "why_not_formal_phase_present"
        ],
        "blocker_summary_present": readiness["blocker_summary_present"],
        "research_only_label_present": readiness["research_only_label_present"],
        "global_blockers": readiness["global_blockers"],
        "result": readiness["result"],
    }


def _load_manifest(
    *,
    refresh_manifest_path: str | Path | None,
    refresh_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    if refresh_manifest is not None:
        return refresh_manifest
    if refresh_manifest_path is not None:
        return json.loads(Path(refresh_manifest_path).read_text(encoding="utf-8"))
    if DEFAULT_PHASE41_LIVE_MANIFEST.exists():
        return json.loads(DEFAULT_PHASE41_LIVE_MANIFEST.read_text(encoding="utf-8"))
    if DEFAULT_PHASE41_BLOCKED_MANIFEST.exists():
        return json.loads(DEFAULT_PHASE41_BLOCKED_MANIFEST.read_text(encoding="utf-8"))
    return build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )


def _role_readiness_row(
    rule: dict[str, Any],
    *,
    contract: dict[str, Any],
    freshness_by_series: dict[str, dict[str, Any]],
    safe_roles: set[str],
    store: RawCsvStore | None,
    snapshot_as_of: str,
    data_mode: str,
) -> dict[str, Any]:
    role_id = rule["role_id"]
    required_series = [str(item) for item in contract["current_series_ids"]]
    official_series = resolve_official_series_ids(required_series)
    series_rows = [freshness_by_series.get(item) for item in official_series]
    missing_series = [
        series_id
        for series_id, row in zip(required_series, series_rows, strict=False)
        if row is None or row["freshness_status"] == "missing_source"
    ]
    unavailable_series = [
        row["series_id"]
        for row in series_rows
        if row and row["freshness_status"] == "unavailable_for_current_mode"
    ]
    stale_series = [
        row["series_id"]
        for row in series_rows
        if row and row["freshness_status"] == "genuinely_stale"
    ]
    not_current_series = [
        row["series_id"]
        for row in series_rows
        if row and row["freshness_status"] in {
            "not_applicable_to_current_mode",
            "source_disabled_for_current_refresh",
        }
    ]
    blockers = []
    if role_id not in safe_roles:
        blockers.append("phase_evidence_rule_not_operational")
    if missing_series:
        blockers.append(f"missing_data:{','.join(missing_series)}")
    if unavailable_series:
        blockers.append(f"unavailable_data:{','.join(unavailable_series)}")
    if stale_series:
        blockers.append(f"stale_data:{','.join(stale_series)}")
    if not_current_series:
        blockers.append(f"not_current_mode:{','.join(not_current_series)}")
    observations = _observations_for(official_series[:1], store)
    right_observations = _observations_for(official_series[1:2], store)
    if role_id in safe_roles and not blockers and observations:
        output = evaluate_phase_evidence(
            role_id=role_id,
            as_of=snapshot_as_of,
            data_mode="revised",
            observations=observations,
            right_observations=right_observations,
        )
        status = output["evidence_status"]
        current_output_available = output["phase_evidence_output_available"]
    else:
        if role_id in safe_roles and not blockers and not observations:
            blockers.append("current_observations_not_loaded")
        status = "abstained" if blockers else "unavailable"
        current_output_available = False
    return {
        "role_id": role_id,
        "phase": LAYER_TO_PHASE[rule["phase_or_layer"]],
        "phase_or_layer": rule["phase_or_layer"],
        "major_group_id": rule["major_group_id"],
        "required_series_ids": required_series,
        "evaluator_status": rule["evaluator_status"],
        "current_evidence_status": status,
        "source_series_alias_ids": required_series,
        "official_source_series_ids": official_series,
        "current_phase_evidence_output_available": current_output_available,
        "supportive": status == "supportive",
        "contradictory": status == "contradictory",
        "mixed": False,
        "unavailable": status in {"unavailable", "abstained"},
        "abstained": status == "abstained",
        "observation_only": role_id not in safe_roles,
        "blocker_reason_codes": blockers,
        "data_mode": data_mode,
        "candidate_selection_eligible": False,
        "formal_phase_eligible": False,
    }


def _observations_for(
    series_ids: list[str],
    store: RawCsvStore | None,
) -> list[dict[str, Any]] | None:
    if not series_ids or store is None:
        return None
    series_id = series_ids[0]
    try:
        observations = store.read_observations("fred", series_id)
    except FileNotFoundError:
        return None
    usable = [item for item in observations if item.value not in {"", "."}]
    if len(usable) < 3:
        return None
    return [
        {
            "date": item.date,
            "value": float(item.value),
            "data_mode": "revised",
            "source_artifact_id": f"current_cache::{series_id}:{item.date}",
        }
        for item in usable[-6:]
    ]


def _phase_profile(
    phase: str,
    role_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [row for row in role_rows if row["phase"] == phase]
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["major_group_id"], []).append(row)
    group_states = [_group_state(group_rows) for group_rows in groups.values()]
    supportive = [row for row in rows if row["supportive"]]
    contradictory = [row for row in rows if row["contradictory"]]
    blockers = _top_blockers(rows)
    evaluable_count = len([row for row in rows if row["current_phase_evidence_output_available"]])
    return {
        "phase_id": phase,
        "display_label": _phase_label(phase),
        "profile_kind": "current_research_evidence_profile",
        "major_group_count": len(groups),
        "major_group_ready_count": sum(state == "ready" for state in group_states),
        "major_group_partial_count": sum(state == "partial" for state in group_states),
        "major_group_missing_count": sum(state == "missing" for state in group_states),
        "supportive_evidence_count": len(supportive),
        "contradictory_evidence_count": len(contradictory),
        "mixed_evidence_count": 0,
        "unavailable_evidence_count": sum(row["unavailable"] for row in rows),
        "abstention_count": sum(row["abstained"] for row in rows),
        "observation_only_count": sum(row["observation_only"] for row in rows),
        "transition_watch_count": sum(
            row["phase_or_layer"] in TRANSITION_LAYERS for row in rows
        ),
        "formal_confirmation_count": 0,
        "evidence_completeness_ratio": round(
            evaluable_count / len(rows),
            4,
        )
        if rows
        else 0.0,
        "top_supportive_roles": [row["role_id"] for row in supportive[:4]],
        "top_contradictory_roles": [row["role_id"] for row in contradictory[:4]],
        "top_blockers": blockers[:5],
        "formal_phase_eligible": False,
        "candidate_phase_eligible": False,
        "why_not_formal_phase": _why_not_formal(blockers),
    }


def _group_state(rows: list[dict[str, Any]]) -> str:
    evaluable = [row for row in rows if row["current_phase_evidence_output_available"]]
    if len(evaluable) == len(rows):
        return "ready"
    if evaluable:
        return "partial"
    return "missing"


def _top_blockers(rows: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        for blocker in row["blocker_reason_codes"]:
            entry = f"{row['role_id']}::{blocker}"
            if entry not in blockers:
                blockers.append(entry)
    return blockers


def _why_not_formal(blockers: list[str]) -> list[str]:
    reasons = [
        "formal current phase output is disabled by governance gate",
        "candidate phase output is disabled",
        "economic validation is not complete",
        "latest revised data is not point-in-time evidence",
    ]
    if blockers:
        reasons.append("one or more required roles are missing, stale, or unresolved")
    return reasons


def _global_blockers(
    freshness: dict[str, Any],
    role_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    unresolved_rules = sum(row["observation_only"] for row in role_rows)
    return {
        "stale_data": freshness["stale_series_count_after"],
        "missing_data": freshness["missing_series_count"],
        "unresolved_rule": unresolved_rules,
        "insufficient_pit_or_non_pit_caveat": (
            "latest revised data is not point-in-time evidence"
        ),
        "formal_decision_disabled": True,
        "economic_validation_not_complete": True,
        "top_blockers": _top_blockers(role_rows)[:10],
    }


def _store_from_manifest(manifest: dict[str, Any]) -> RawCsvStore | None:
    cache_dir = manifest.get("cache_dir")
    if not cache_dir:
        return None
    path = Path(cache_dir)
    if not path.exists():
        return None
    return RawCsvStore(path)


def _phase_label(phase: str) -> str:
    return {
        "recovery": "Recovery / 復甦",
        "growth": "Growth / 成長",
        "boom": "Boom / 榮景",
        "recession": "Recession / 衰退",
    }[phase]


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _passes(readiness: dict[str, Any]) -> bool:
    return (
        readiness["current_evidence_readiness_ready"] is True
        and readiness["phase_profile_count"] == 4
        and readiness["current_phase_emitted"] is False
        and readiness["candidate_phase_emitted"] is False
        and readiness["selected_phase_output_count"] == 0
        and readiness["phase_rank_output_count"] == 0
        and readiness["numeric_phase_score_output_count"] == 0
        and readiness["role_count_voting_added_count"] == 0
        and readiness["formal_phase_eligible_count"] == 0
        and readiness["candidate_phase_eligible_count"] == 0
        and readiness["why_not_formal_phase_present"] is True
        and readiness["blocker_summary_present"] is True
        and readiness["research_only_label_present"] is True
        and readiness["prohibited_field_count"] == 0
    )
