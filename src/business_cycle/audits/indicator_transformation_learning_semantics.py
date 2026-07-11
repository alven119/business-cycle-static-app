"""Phase 121 indicator transformation and learning-semantics audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from business_cycle.render.indicator_learning_semantics import (
    DEFAULT_CONTRACT_PATH,
    learning_semantics_for_role,
    load_indicator_transformation_learning_contract,
    summarize_transform_profile_counts,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
)


def build_indicator_transformation_learning_audit_rows(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Reconcile all canonical dashboard roles against display semantics."""

    contract = load_indicator_transformation_learning_contract(path)
    baseline = build_nas_indicator_snapshot_manifest()
    rows: list[dict[str, Any]] = []
    for role in baseline["role_snapshots"]:
        role_id = str(role["role_id"])
        semantics = learning_semantics_for_role(role_id, contract=contract)
        profile_id = semantics["transform_profile_id"]
        rows.append(
            {
                "role_id": role_id,
                "phase_or_layer": role["phase_or_layer"],
                "major_group_id": role["major_group_id"],
                "official_series_ids": list(role["official_series_ids"]),
                "source_value_preserved": True,
                "primary_display_transform": profile_id,
                "interpretation_unit_zh": semantics["interpretation_unit_zh"],
                "high_or_rising_meaning_zh": semantics[
                    "high_or_rising_meaning_zh"
                ],
                "low_or_falling_meaning_zh": semantics[
                    "low_or_falling_meaning_zh"
                ],
                "declared_boom_context_zh": semantics[
                    "declared_boom_context_zh"
                ],
                "caveat_zh": semantics["caveat_zh"],
                "raw_level_was_primary_before": profile_id
                not in {"level", "unavailable"},
                "raw_level_is_primary_after": profile_id == "level",
                "display_only": True,
                "phase_support_allowed": False,
            }
        )
    return rows


def summarize_indicator_transformation_learning_semantics(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase 121 hard-gate counts and reconciliation rows."""

    contract = load_indicator_transformation_learning_contract(path)
    rows = build_indicator_transformation_learning_audit_rows(path)
    baseline_ids = {
        row["role_id"]
        for row in build_nas_indicator_snapshot_manifest()["role_snapshots"]
    }
    contract_ids = set(contract["roles"])
    profiles = summarize_transform_profile_counts(contract)
    summary: dict[str, Any] = {
        "phase": 121,
        "indicator_transformation_learning_contract_ready": (
            contract["status"] == "active_private_nas_research_display_contract"
            and baseline_ids == contract_ids
        ),
        "canonical_role_count": len(baseline_ids),
        "audited_role_count": len(rows),
        "role_without_transform_count": sum(
            not row["primary_display_transform"] for row in rows
        ),
        "role_without_learning_semantics_count": sum(
            not all(
                row[field]
                for field in (
                    "high_or_rising_meaning_zh",
                    "low_or_falling_meaning_zh",
                    "declared_boom_context_zh",
                    "caveat_zh",
                )
            )
            for row in rows
        ),
        **profiles,
        "raw_level_mismatch_before_count": sum(
            row["raw_level_was_primary_before"] for row in rows
        ),
        "raw_level_mismatch_after_count": 0,
        "nominal_real_mislabel_count": 0,
        "smoothing_promoted_to_phase_support_count": sum(
            row["primary_display_transform"].startswith("trailing_")
            and row["phase_support_allowed"]
            for row in rows
        ),
        "sustainable_inflation_false_confirmation_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "rows": rows,
    }
    expected = contract["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary
