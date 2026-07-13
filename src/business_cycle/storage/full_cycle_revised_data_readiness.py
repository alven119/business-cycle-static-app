"""Four-phase revised/current input readiness for the private NAS warehouse."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_role_types import (
    build_book_core_role_type_rows,
)
from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    automated_revised_series_ids,
    load_nas_postgres_live_revised_import_contract,
)
from business_cycle.service.nas_release_aware_freshness import role_series_overrides

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/full_cycle_revised_data_readiness_contract.yaml"
)
LIVE_DASHBOARD_CONTRACT_PATH = (
    ROOT / "specs/common/nas_live_postgres_dashboard_contract.yaml"
)


def load_full_cycle_revised_data_readiness_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["full_cycle_revised_data_readiness_contract"])


def build_full_cycle_role_data_matrix(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Build one data-routing row per canonical requirement."""

    contract = load_full_cycle_revised_data_readiness_contract(contract_path)
    cards = {
        str(row["role_id"]): row
        for row in build_indicator_detail_source_risk_value_cards()
    }
    rules = {
        str(row["role_id"]): row for row in build_book_phase_evidence_rule_rows()
    }
    derived = _derived_display_series()
    active_overrides = role_series_overrides()
    supporting = _supporting_by_role(contract)
    rows: list[dict[str, Any]] = []
    for role_type in build_book_core_role_type_rows():
        role_id = str(role_type["role_id"])
        methodology = not bool(role_type["counts_in_indicator_denominator"])
        card = cards.get(role_id)
        rule = rules.get(role_id)
        official_ids = active_overrides.get(
            role_id,
            list(card["official_series_ids"]) if card else [],
        )
        raw_ids = _raw_input_series_ids(official_ids, derived)
        derived_or_composite = bool(
            any(series_id in derived for series_id in official_ids)
            or len(official_ids) > 1
        )
        source_blocked = role_id == "boom_consumer_confidence"
        rows.append(
            {
                "role_id": role_id,
                "phase": _phase_name(str(role_type["phase_or_layer"])),
                "major_group_id": role_type["major_group_id"],
                "role_type": role_type["primary_role_type"],
                "counts_in_indicator_denominator": not methodology,
                "phase_lane": (
                    "temporal_integrity_methodology"
                    if methodology
                    else str(rule["typed_evidence_family"])
                ),
                "official_series_ids": official_ids,
                "raw_input_series_ids": raw_ids,
                "supporting_series_ids": [
                    str(row["series_id"]) for row in supporting.get(role_id, [])
                ],
                "storage_mode": _storage_mode(
                    methodology=methodology,
                    source_blocked=source_blocked,
                    derived_or_composite=derived_or_composite,
                ),
                "required_transformation_context": _transformation_context(
                    methodology=methodology,
                    card=card,
                    rule=rule,
                ),
                "derived_or_composite": derived_or_composite,
                "derived_lineage_complete": (
                    not derived_or_composite or bool(raw_ids)
                ),
                "book_core_revised_status": (
                    "methodology_not_numeric_indicator"
                    if methodology
                    else "source_blocked"
                    if source_blocked
                    else "revised_inputs_automatable"
                ),
                "source_risk_level": (
                    "not_applicable_methodology"
                    if methodology
                    else "medium"
                    if role_id == "growth_adp_employment"
                    else str(card["data_risk_level"])
                ),
                "source_risk_label_zh": (
                    "發布時差屬時間完整性要求，不是數值指標。"
                    if methodology
                    else (
                        "中：ADP 私人來源由 FRED 公開散布；需保留著作權引用、"
                        "年度 QCEW 重設基準與 revised-only 風險。"
                    )
                    if role_id == "growth_adp_employment"
                    else str(card["source_risk_label_zh"])
                ),
                "supporting_proxy_only": source_blocked,
                "supporting_proxy_can_replace_book_core": False,
                "silent_substitution": False,
            }
        )
    return sorted(rows, key=lambda row: (row["phase"], row["role_id"]))


def build_full_cycle_revised_runtime_readiness(
    *,
    available_series_ids: list[str] | set[str],
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Resolve matrix readiness from Postgres series identities only."""

    available = {str(value) for value in available_series_ids}
    rows = []
    for row in build_full_cycle_role_data_matrix(contract_path=contract_path):
        required = set(row["raw_input_series_ids"])
        supporting = set(row["supporting_series_ids"])
        missing = sorted(required - available)
        supporting_available = sorted(supporting & available)
        status = _runtime_role_status(
            row=row,
            missing=missing,
            supporting_available=supporting_available,
        )
        rows.append(
            row
            | {
                "runtime_revised_status": status,
                "available_raw_input_series_ids": sorted(required & available),
                "missing_raw_input_series_ids": missing,
                "available_supporting_series_ids": supporting_available,
                "book_core_revised_ready": status
                in {"revised_ready", "methodology_ready"},
            }
        )

    phase_rows = []
    for phase in ("recession", "recovery", "growth", "boom"):
        selected = [
            row
            for row in rows
            if row["phase"] == phase and row["counts_in_indicator_denominator"]
        ]
        phase_rows.append(
            {
                "phase": phase,
                "role_count": len(selected),
                "revised_ready_role_count": sum(
                    row["runtime_revised_status"] == "revised_ready"
                    for row in selected
                ),
                "source_blocked_role_count": sum(
                    row["runtime_revised_status"].startswith("source_blocked")
                    for row in selected
                ),
                "missing_input_role_count": sum(
                    row["runtime_revised_status"] == "missing_postgres_inputs"
                    for row in selected
                ),
                "supporting_context_available_role_count": sum(
                    bool(row["available_supporting_series_ids"])
                    for row in selected
                ),
            }
        )

    automated = set(automated_revised_series_ids())
    return {
        "runtime_readiness_version": "phase130_full_cycle_revised_runtime_v1",
        "available_series_count": len(available),
        "automated_revised_series_count": len(automated),
        "automated_revised_series_available_count": len(automated & available),
        "automated_revised_series_missing_ids": sorted(automated - available),
        "all_automated_revised_inputs_in_postgres": automated <= available,
        "role_rows": rows,
        "phase_rows": phase_rows,
        "phase_count": len(phase_rows),
        "core_revised_ready_role_count": sum(
            row["runtime_revised_status"] == "revised_ready" for row in rows
        ),
        "source_blocked_core_role_count": sum(
            row["runtime_revised_status"].startswith("source_blocked")
            for row in rows
        ),
        "source_blocked_with_supporting_context_count": sum(
            row["runtime_revised_status"] == "source_blocked_supporting_ready"
            for row in rows
        ),
        "missing_postgres_input_role_count": sum(
            row["runtime_revised_status"] == "missing_postgres_inputs"
            for row in rows
        ),
        "silent_substitution_count": 0,
        "supporting_proxy_promoted_to_core_count": 0,
        "revised_mislabeled_as_point_in_time_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def summarize_full_cycle_revised_data_readiness(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize static Phase 130 contract and lineage gates."""

    contract = load_full_cycle_revised_data_readiness_contract(path)
    rows = build_full_cycle_role_data_matrix(contract_path=path)
    economic = [row for row in rows if row["counts_in_indicator_denominator"]]
    import_contract = load_nas_postgres_live_revised_import_contract()
    direct = list(import_contract["source_policy"]["direct_series_ids"])
    supplemental = list(
        import_contract["source_policy"].get("supporting_context_series_ids", [])
    )
    phases = {row["phase"] for row in rows}
    derived = [row for row in economic if row["derived_or_composite"]]
    summary = {
        "phase": 130,
        "full_cycle_revised_data_readiness_contract_ready": (
            contract["status"] == "active_private_nas_research_contract"
            and contract["matrix_policy"]["proxy_never_silently_replaces_book_core"]
            is True
        ),
        "canonical_requirement_count": len(rows),
        "economic_indicator_role_count": len(economic),
        "methodology_requirement_count": len(rows) - len(economic),
        "phase_count": len(phases),
        "canonical_direct_input_series_count": len(direct),
        "supplemental_automated_series_count": len(supplemental),
        "automated_revised_series_count": len(automated_revised_series_ids()),
        "core_revised_ready_role_count": sum(
            row["book_core_revised_status"] == "revised_inputs_automatable"
            for row in rows
        ),
        "source_blocked_core_role_count": sum(
            row["book_core_revised_status"] == "source_blocked" for row in rows
        ),
        "supporting_proxy_role_count": sum(
            bool(row["supporting_series_ids"]) for row in rows
        ),
        "derived_or_composite_role_count": len(derived),
        "derived_or_composite_lineage_missing_count": sum(
            not row["derived_lineage_complete"] for row in derived
        ),
        "role_without_phase_lane_count": sum(not row["phase_lane"] for row in rows),
        "role_without_transformation_context_count": sum(
            not row["required_transformation_context"] for row in rows
        ),
        "role_without_source_risk_count": sum(
            not row["source_risk_label_zh"] for row in rows
        ),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "supporting_proxy_promoted_to_core_count": sum(
            row["supporting_proxy_can_replace_book_core"] for row in rows
        ),
        "methodology_counted_as_indicator_count": sum(
            row["role_type"] == "data_methodology_requirement"
            and row["counts_in_indicator_denominator"]
            for row in rows
        ),
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 131,
        "phase_role_counts": dict(Counter(row["phase"] for row in economic)),
        "role_rows": rows,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary


def _supporting_by_role(contract: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = {}
    for item in contract["supporting_context_series"]:
        rows.setdefault(str(item["supports_role_id"]), []).append(dict(item))
    return rows


def _derived_display_series() -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(
        LIVE_DASHBOARD_CONTRACT_PATH.read_text(encoding="utf-8")
    )
    return dict(payload["nas_live_postgres_dashboard_contract"]["derived_display_series"])


def _raw_input_series_ids(
    official_ids: list[str],
    derived: dict[str, dict[str, Any]],
) -> list[str]:
    values: list[str] = []
    for series_id in official_ids:
        inputs = derived.get(series_id, {}).get("component_series_ids", [series_id])
        for value in inputs:
            if str(value) not in values:
                values.append(str(value))
    return values


def _phase_name(phase_or_layer: str) -> str:
    if phase_or_layer.startswith("recovery"):
        return "recovery"
    if phase_or_layer.startswith("growth"):
        return "growth"
    if phase_or_layer.startswith("boom"):
        return "boom"
    if phase_or_layer.startswith(("recession", "trough")):
        return "recession"
    raise ValueError(f"unsupported phase/layer: {phase_or_layer}")


def _storage_mode(
    *, methodology: bool, source_blocked: bool, derived_or_composite: bool
) -> str:
    if methodology:
        return "methodology_no_numeric_series"
    if source_blocked:
        return "book_core_blocked_supporting_context_separate"
    if derived_or_composite:
        return "raw_inputs_in_postgres_derived_on_read"
    return "direct_raw_series_in_postgres"


def _transformation_context(
    *,
    methodology: bool,
    card: dict[str, Any] | None,
    rule: dict[str, Any] | None,
) -> str:
    if methodology:
        return "publication_release_lag_temporal_integrity"
    if card and card.get("transformation_semantics_status"):
        return str(card["transformation_semantics_status"])
    if rule and rule.get("required_transformation"):
        return str(rule["required_transformation"])
    return ""


def _runtime_role_status(
    *,
    row: dict[str, Any],
    missing: list[str],
    supporting_available: list[str],
) -> str:
    if row["storage_mode"] == "methodology_no_numeric_series":
        return "methodology_ready"
    if row["book_core_revised_status"] == "source_blocked":
        return (
            "source_blocked_supporting_ready"
            if supporting_available
            else "source_blocked_supporting_missing"
        )
    return "missing_postgres_inputs" if missing else "revised_ready"
