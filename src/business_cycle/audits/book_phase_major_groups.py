"""QA5 book phase major-group and subrole mapping."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MAJOR_GROUP_PATH = Path("specs/audits/book_phase_major_group_contract.yaml")
COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")


def build_book_phase_subroles(
    path: str | Path = DEFAULT_MAJOR_GROUP_PATH,
) -> list[dict[str, Any]]:
    """Build one major-group mapping row per canonical indicator role."""

    spec = _load_spec(path)
    coverage = _coverage_rows()
    rows: list[dict[str, Any]] = []
    for role in coverage:
        role_id = role["coverage_requirement_id"]
        phase = _phase_id(role["phase"])
        rows.append(
            {
                "role_id": role_id,
                "phase": phase,
                "major_group_id": spec["role_mappings"][role_id],
                "role_type": spec.get("role_types", {}).get(
                    role_id, spec["defaults"]["role_type"]
                ),
                "minimum_group_requirement": bool(
                    spec["defaults"]["minimum_group_requirement"]
                ),
                "complete_group_requirement": bool(
                    spec["defaults"]["complete_group_requirement"]
                ),
                "substitution_allowed": bool(spec["defaults"]["substitution_allowed"]),
                "substitution_equivalence_required": bool(
                    spec["defaults"]["substitution_equivalence_required"]
                ),
            }
        )
    return rows


def summarize_book_phase_major_group_readiness(
    path: str | Path = DEFAULT_MAJOR_GROUP_PATH,
) -> dict[str, Any]:
    """Return major-group hard-gate counts."""

    spec = _load_spec(path)
    rows = build_book_phase_subroles(path)
    role_ids = [row["role_id"] for row in rows]
    mapped_groups = {
        phase: {row["major_group_id"] for row in rows if row["phase"] == phase}
        for phase in ("recovery", "growth", "boom", "recession_trough")
    }
    missing_group_roles = [row for row in rows if not row["major_group_id"]]
    duplicates = {role_id for role_id, count in Counter(role_ids).items() if count > 1}
    major_groups_without_core = []
    for phase, groups in spec["major_groups"].items():
        for group in groups:
            if not any(
                row["phase"] == phase
                and row["major_group_id"] == group
                and row["role_type"]
                in {"required_core", "alternative_core_evidence", "supporting"}
                for row in rows
            ):
                major_groups_without_core.append(f"{phase}:{group}")
    ready = (
        len(spec["major_groups"]["recovery"]) == 4
        and len(spec["major_groups"]["growth"]) == 4
        and len(spec["major_groups"]["boom"]) == 7
        and not missing_group_roles
        and not duplicates
        and not major_groups_without_core
    )
    return {
        "phase": "QA5",
        "major_group_contract_ready": ready,
        "recovery_major_group_count": len(mapped_groups["recovery"]),
        "growth_major_group_count": len(mapped_groups["growth"]),
        "boom_major_group_count": len(mapped_groups["boom"]),
        "recession_trough_major_group_count": len(
            mapped_groups["recession_trough"]
        ),
        "subrole_count": len(rows),
        "subrole_without_major_group_count": len(missing_group_roles),
        "subrole_mapped_to_multiple_major_groups_count": len(duplicates),
        "major_group_without_core_role_count": len(major_groups_without_core),
        "requirement_count_coverage_ready": True,
        "major_group_coverage_ready": ready,
        "subroles": rows,
    }


def major_group_for_role(role_id: str) -> str:
    """Return major group id for a canonical role."""

    spec = _load_spec(DEFAULT_MAJOR_GROUP_PATH)
    return str(spec["role_mappings"][role_id])


def _load_spec(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_phase_major_group_contract"
    ]


def _coverage_rows() -> list[dict[str, Any]]:
    rows = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))[
        "book_indicator_coverage"
    ]["indicators"]
    return [row for row in rows if row.get("coverage_requirement_id")]


def _phase_id(raw_phase: str) -> str:
    return {
        "recovery_indicators": "recovery",
        "growth_indicators": "growth",
        "boom_ending_indicators": "boom",
        "recession_trough_requirements": "recession_trough",
    }[raw_phase]
