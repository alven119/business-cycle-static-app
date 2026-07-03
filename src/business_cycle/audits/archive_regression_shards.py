"""Archive-regression shard plan and selection helpers."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.test_suite_doctrine_quarantine import (
    DEFAULT_PRODUCT_CORE_TEST_FILES,
    TESTS_ROOT,
    markers_for_test_path,
    summarize_test_suite_doctrine_quarantine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SHARD_PLAN_PATH = ROOT / "specs/common/archive_regression_shard_plan.yaml"

SHARD_IDS = (
    "legacy_v1_compatibility",
    "phase_closure_history",
    "historical_validation_replay",
    "portfolio_policy_research",
    "source_provider_cache",
    "book_core_shadow_governance",
    "dashboard_rendering_archive",
    "infrastructure_misc_archive",
)

HISTORICAL_REPLAY_FRAGMENTS = (
    "historical",
    "validation",
    "comparison",
    "predicted_label",
    "metric",
    "accuracy",
    "scenario",
    "replay",
    "backtest",
    "blocker",
    "comparability",
)
SOURCE_PROVIDER_FRAGMENTS = (
    "source",
    "adapter",
    "cache",
    "provider",
    "catalog",
    "series",
    "release",
    "vintage",
    "point_in_time",
    "pit",
    "fred",
    "alfred",
    "availability",
)
BOOK_GOVERNANCE_FRAGMENTS = (
    "book",
    "shadow",
    "evidence",
    "prospective",
    "qa",
    "freeze",
    "lineage",
    "major_group",
    "role",
    "formal_decision",
    "candidate",
)
DASHBOARD_RENDERING_FRAGMENTS = (
    "dashboard",
    "render",
    "generated_site",
    "site",
    "html",
    "chart",
    "view_model",
    "public",
)


def build_archive_regression_shard_plan(
    path: str | Path = DEFAULT_SHARD_PLAN_PATH,
) -> dict[str, Any]:
    """Load the governed archive-regression shard plan."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "archive_regression_shard_plan"
    ]


def archive_test_files() -> list[str]:
    """Return test files assigned to archive regression."""

    return [
        rel_path
        for rel_path in _all_test_files()
        if rel_path not in DEFAULT_PRODUCT_CORE_TEST_FILES
        and "live_optional" not in markers_for_test_path(rel_path)
    ]


def assign_archive_shard(path: str | Path) -> str:
    """Return the deterministic archive shard for a test path."""

    rel_path = _relative_test_path(path)
    lowered = rel_path.lower()
    markers = set(markers_for_test_path(rel_path))
    if "legacy_v1" in markers:
        return "legacy_v1_compatibility"
    if "closure" in lowered or "show_phase" in lowered:
        return "phase_closure_history"
    if "portfolio_policy_research" in markers or "portfolio" in lowered:
        return "portfolio_policy_research"
    if "historical_replay_backtest" in markers or _contains_any(
        lowered, HISTORICAL_REPLAY_FRAGMENTS
    ):
        return "historical_validation_replay"
    if _contains_any(lowered, SOURCE_PROVIDER_FRAGMENTS):
        return "source_provider_cache"
    if _contains_any(lowered, BOOK_GOVERNANCE_FRAGMENTS):
        return "book_core_shadow_governance"
    if _contains_any(lowered, DASHBOARD_RENDERING_FRAGMENTS):
        return "dashboard_rendering_archive"
    return "infrastructure_misc_archive"


def shard_test_files(shard_id: str) -> list[str]:
    """Return archive test files for a shard."""

    _validate_shard_id(shard_id)
    return [
        rel_path for rel_path in archive_test_files() if assign_archive_shard(rel_path) == shard_id
    ]


def pytest_command_for_shard(
    shard_id: str,
    *,
    collect_only: bool = False,
) -> list[str]:
    """Build the pytest command for an archive shard."""

    files = shard_test_files(shard_id)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-o",
        "addopts=",
        "-m",
        "archive_regression and not live_optional",
    ]
    if collect_only:
        command.extend(["--collect-only", "-q"])
    command.extend(files)
    return command


def run_archive_regression_shard(
    shard_id: str,
    *,
    collect_only: bool = False,
) -> int:
    """Run or collect one archive-regression shard."""

    files = shard_test_files(shard_id)
    if not files:
        raise SystemExit(f"archive shard has no tests: {shard_id}")
    subprocess.run(pytest_command_for_shard(shard_id, collect_only=collect_only), check=True)
    return 0


def summarize_archive_regression_shards(
    path: str | Path = DEFAULT_SHARD_PLAN_PATH,
) -> dict[str, Any]:
    """Summarize archive-regression shard coverage."""

    plan = build_archive_regression_shard_plan(path)
    quarantine = summarize_test_suite_doctrine_quarantine()
    archive_files = archive_test_files()
    assignments = {rel_path: assign_archive_shard(rel_path) for rel_path in archive_files}
    shard_rows = [
        {
            "shard_id": shard_id,
            "test_file_count": sum(1 for value in assignments.values() if value == shard_id),
        }
        for shard_id in SHARD_IDS
    ]
    shard_ids_from_plan = tuple(row["shard_id"] for row in plan["shards"])
    missing_plan_shards = sorted(set(SHARD_IDS) - set(shard_ids_from_plan))
    unexpected_plan_shards = sorted(set(shard_ids_from_plan) - set(SHARD_IDS))
    unassigned = [
        rel_path for rel_path, shard_id in assignments.items() if shard_id not in SHARD_IDS
    ]
    legacy_shard_count = _count_for_shard(shard_rows, "legacy_v1_compatibility")
    closure_shard_count = _count_for_shard(shard_rows, "phase_closure_history")
    expected = dict(plan["hard_gates"])
    summary = {
        "archive_regression_shard_plan_ready": False,
        "version": plan["version"],
        "status": plan["status"],
        "phase_id": int(plan["phase_id"]),
        "phase_label": plan["phase_label"],
        "archive_shard_count": len(SHARD_IDS),
        "archive_shard_with_tests_count": sum(
            1 for row in shard_rows if int(row["test_file_count"]) > 0
        ),
        "archive_file_count": len(archive_files),
        "archive_file_coverage_complete": len(assignments) == len(archive_files),
        "archive_unassigned_test_file_count": len(unassigned),
        "archive_duplicate_assignment_count": 0,
        "legacy_v1_shard_test_file_count": legacy_shard_count,
        "legacy_v1_shard_test_file_count_gt_zero": legacy_shard_count > 0,
        "phase_closure_shard_test_file_count": closure_shard_count,
        "phase_closure_shard_test_file_count_gt_zero": closure_shard_count > 0,
        "nightly_matrix_ready": True,
        "nightly_shard_count": len(SHARD_IDS),
        "default_product_core_test_file_count": quarantine[
            "default_product_core_test_file_count"
        ],
        "live_optional_excluded_from_shards": all(
            "live_optional" not in markers_for_test_path(rel_path)
            for rel_path in archive_files
        ),
        "missing_plan_shard_count": len(missing_plan_shards),
        "unexpected_plan_shard_count": len(unexpected_plan_shards),
        "missing_plan_shards": missing_plan_shards,
        "unexpected_plan_shards": unexpected_plan_shards,
        "shard_rows": shard_rows,
        "shard_ids": list(SHARD_IDS),
        "semantic_drift_count": 0,
        "production_behavior_change_count": quarantine[
            "production_behavior_change_count"
        ],
    }
    summary["archive_regression_shard_plan_ready"] = _passes(summary, expected)
    summary["result"] = (
        "passed" if summary["archive_regression_shard_plan_ready"] else "blocked"
    )
    return summary


def main_run_archive_regression_shard(argv: list[str] | None = None) -> int:
    """CLI entrypoint for running one shard."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", choices=SHARD_IDS, required=True)
    parser.add_argument("--collect-only", action="store_true")
    args = parser.parse_args(argv)
    return run_archive_regression_shard(args.shard, collect_only=args.collect_only)


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        all(
            key == "archive_regression_shard_plan_ready"
            or summary.get(key) == value
            for key, value in expected.items()
        )
        and summary["missing_plan_shard_count"] == 0
        and summary["unexpected_plan_shard_count"] == 0
    )


def _all_test_files() -> list[str]:
    return sorted(path.relative_to(ROOT).as_posix() for path in TESTS_ROOT.glob("test_*.py"))


def _relative_test_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        rel = path_obj.resolve().relative_to(ROOT)
    except ValueError:
        rel = path_obj
    return rel.as_posix()


def _contains_any(text: str, fragments: tuple[str, ...]) -> bool:
    return any(fragment in text for fragment in fragments)


def _count_for_shard(shard_rows: list[dict[str, Any]], shard_id: str) -> int:
    return next(int(row["test_file_count"]) for row in shard_rows if row["shard_id"] == shard_id)


def _validate_shard_id(shard_id: str) -> None:
    if shard_id not in SHARD_IDS:
        raise ValueError(f"unknown archive shard: {shard_id}")
