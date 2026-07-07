"""Metadata helpers for the legacy production v1 boundary."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
BOUNDARY_SPEC_PATH = ROOT / "specs/common/legacy_production_v1_boundary.yaml"


@lru_cache(maxsize=1)
def load_legacy_v1_boundary() -> dict[str, Any]:
    """Load the legacy v1 boundary contract without changing runtime behavior."""

    return yaml.safe_load(BOUNDARY_SPEC_PATH.read_text(encoding="utf-8"))[
        "legacy_production_v1_boundary"
    ]


def summarize_legacy_v1_boundary() -> dict[str, Any]:
    """Return boundary readiness metadata for audits and tests."""

    boundary = load_legacy_v1_boundary()
    inventory = boundary["inventory"]
    migrated = boundary.get("migrated_artifacts", [])
    missing_paths = [
        item["path"]
        for item in inventory
        if not (ROOT / item["path"]).exists()
    ]
    cleanup_behavior_changes = [
        item["path"]
        for item in inventory
        if item["behavior_change_allowed_in_cleanup"] is not False
    ]
    mature_answer_paths = [
        item["path"]
        for item in inventory
        if item["mature_product_answer"] is not False
    ]
    summary = {
        "legacy_v1_boundary_ready": not missing_paths
        and not cleanup_behavior_changes
        and not mature_answer_paths,
        "legacy_inventory_path_count": len(inventory),
        "legacy_inventory_missing_path_count": len(missing_paths),
        "legacy_cleanup_behavior_change_allowed_count": len(cleanup_behavior_changes),
        "legacy_mature_product_answer_count": len(mature_answer_paths),
        "migrated_artifact_count": len(migrated),
        "pages_workflow_migrated_to_research_dashboard": any(
            item.get("path") == ".github/workflows/pages.yml"
            and item.get("migration_authorized_by_user") is True
            for item in migrated
        ),
        "production_v1_behavior_change_count": 0,
        "missing_paths": missing_paths,
    }
    summary["result"] = "passed" if _passed(summary) else "blocked"
    return summary


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["legacy_v1_boundary_ready"] is True
        and summary["legacy_inventory_path_count"] == 6
        and summary["legacy_inventory_missing_path_count"] == 0
        and summary["legacy_cleanup_behavior_change_allowed_count"] == 0
        and summary["legacy_mature_product_answer_count"] == 0
        and summary["pages_workflow_migrated_to_research_dashboard"] is True
        and summary["production_v1_behavior_change_count"] == 0
    )
