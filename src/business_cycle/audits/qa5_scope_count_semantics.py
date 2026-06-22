"""QA5 scope count and formal-v1 primary partition semantics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.formal_indicator_scope_matrix import (
    build_formal_indicator_scope_matrix,
)
from business_cycle.audits.repository_inventory import collect_repository_inventory


COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")
MANIFEST_PATH = Path("specs/audits/canonical_book_requirement_manifest.yaml")


def summarize_qa5_scope_count_semantics() -> dict[str, Any]:
    """Return mutually exclusive QA5 count partitions."""

    matrix = build_formal_indicator_scope_matrix()
    inventory = collect_repository_inventory()
    coverage_rows = _coverage_rows()
    manifest = _manifest_rows()
    existing_indicator_ids = {
        item["inventory_id"].removeprefix("indicator:")
        for item in inventory["items"]
        if item["inventory_type"] in {"formal_indicator", "experimental_indicator"}
    }
    matrix_ids = [row["indicator_or_role_id"] for row in matrix]
    duplicate_matrix_ids = {
        row_id for row_id, count in Counter(matrix_ids).items() if count > 1
    }
    formal_rows = [
        row for row in matrix if row["row_type"] == "existing_indicator" and row["current_formal_v1"]
    ]
    primary_rows = [
        {
            "indicator_id": row["indicator_or_role_id"],
            "primary_classification": _formal_primary_classification(row),
        }
        for row in formal_rows
    ]
    primary_counts = Counter(row["primary_classification"] for row in primary_rows)
    canonical_role_without_matrix = [
        row["coverage_requirement_id"]
        for row in coverage_rows
        if row.get("coverage_requirement_id")
        and not _role_has_matrix_identity(row, matrix, existing_indicator_ids)
    ]
    matrix_without_identity = [
        row["indicator_or_role_id"]
        for row in matrix
        if not _matrix_row_has_identity(row, coverage_rows, existing_indicator_ids)
    ]
    formal_v1_count = sum(
        item["inventory_type"] == "formal_indicator" for item in inventory["items"]
    )
    partition_sum = sum(primary_counts.values())
    return {
        "phase": "QA5",
        "scope_count_semantics_ready": partition_sum == formal_v1_count
        and not duplicate_matrix_ids
        and not canonical_role_without_matrix
        and not matrix_without_identity,
        "book_core_requirement_count": sum(
            row["book_fidelity_class"] == "book_core" for row in manifest
        ),
        "book_supporting_requirement_count": sum(
            row["book_fidelity_class"] == "book_supporting" for row in manifest
        ),
        "modern_methodology_requirement_count": sum(
            row["book_fidelity_class"] == "not_book_requirement" for row in manifest
        ),
        "project_safety_requirement_count": 0,
        "canonical_book_indicator_role_count": len(coverage_rows),
        "normal_cycle_indicator_role_count": sum(
            row["phase"] in {"recovery_indicators", "growth_indicators", "boom_ending_indicators"}
            for row in coverage_rows
        ),
        "regime_indicator_role_count": 0,
        "transition_indicator_role_count": sum(
            row["phase"] == "recession_trough_requirements" for row in coverage_rows
        ),
        "formal_v1_indicator_count": formal_v1_count,
        "experimental_indicator_count": sum(
            item["inventory_type"] == "experimental_indicator"
            for item in inventory["items"]
        ),
        "existing_unique_indicator_count": len(existing_indicator_ids),
        "missing_book_core_role_count": sum(
            row["row_type"] == "missing_book_core_role" for row in matrix
        ),
        "indicator_matrix_row_identity_count": len(matrix),
        "formal_v1_retain_as_v2_core_count": primary_counts["retain_as_v2_core"],
        "formal_v1_retain_as_v2_supporting_count": primary_counts[
            "retain_as_v2_supporting"
        ],
        "formal_v1_retain_as_modern_extension_count": primary_counts[
            "retain_as_modern_extension"
        ],
        "formal_v1_exclude_from_v2_shadow_scope_count": primary_counts[
            "exclude_from_v2_shadow_scope"
        ],
        "formal_v1_primary_partition_sum": partition_sum,
        "formal_v1_primary_partition_valid": partition_sum == formal_v1_count,
        "overlapping_primary_classification_count": 0,
        "duplicate_indicator_matrix_row_count": len(duplicate_matrix_ids),
        "canonical_role_without_matrix_row_count": len(canonical_role_without_matrix),
        "matrix_row_without_canonical_or_existing_identity_count": len(
            matrix_without_identity
        ),
        "formal_v1_primary_rows": primary_rows,
    }


def _formal_primary_classification(row: dict[str, Any]) -> str:
    classification = row["scope_classification"]
    if classification == "retain_in_proposed_v2":
        return "retain_as_v2_core"
    if classification == "demote_to_supporting":
        return "retain_as_v2_supporting"
    if classification == "retain_as_modern_extension":
        return "retain_as_modern_extension"
    return "exclude_from_v2_shadow_scope"


def _role_has_matrix_identity(
    role: dict[str, Any],
    matrix: list[dict[str, Any]],
    existing_indicator_ids: set[str],
) -> bool:
    if role["formal_or_experimental"] == "missing":
        return any(
            row["indicator_or_role_id"] == f"missing_role::{role['coverage_requirement_id']}"
            for row in matrix
        )
    return role["indicator_id"] in existing_indicator_ids


def _matrix_row_has_identity(
    row: dict[str, Any],
    coverage_rows: list[dict[str, Any]],
    existing_indicator_ids: set[str],
) -> bool:
    row_id = row["indicator_or_role_id"]
    if row["row_type"] == "existing_indicator":
        return row_id in existing_indicator_ids
    if row["row_type"] == "missing_book_core_role":
        role_id = row_id.removeprefix("missing_role::")
        return any(role.get("coverage_requirement_id") == role_id for role in coverage_rows)
    return False


def _coverage_rows() -> list[dict[str, Any]]:
    rows = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]["indicators"]
    return [row for row in rows if row.get("coverage_requirement_id")]


def _manifest_rows() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))[
        "canonical_book_requirement_manifest"
    ]["requirements"]

