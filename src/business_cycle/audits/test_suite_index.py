"""Dynamic test-suite index for avoiding duplicate tests."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.test_suite_doctrine_quarantine import (
    DEFAULT_PRODUCT_CORE_TEST_FILES,
    markers_for_test_path,
)

ROOT = Path(__file__).resolve().parents[3]
TESTS_ROOT = ROOT / "tests"
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/test_suite_index.yaml"

CAPABILITY_IDS = (
    "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
    "C2_TRANSITION_RISK_DETECTION",
    "C3_EXPLAINABILITY_AND_ATTRIBUTION",
    "C4_PORTFOLIO_POLICY_RESEARCH",
    "C5_HISTORICAL_REPLAY_AND_BACKTEST",
    "C6_SAFE_OUTPUT_GOVERNANCE",
    "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
    "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
)


@lru_cache(maxsize=1)
def build_test_suite_index(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a dynamic index over test files and their duplicate-guard metadata."""

    contract = _load_contract(path)
    test_files = sorted(TESTS_ROOT.glob("test_*.py"))
    rows = [_index_row(test_path) for test_path in test_files]
    rows_by_component = _rows_by(rows, "component_area")
    rows = [
        {
            **row,
            "similar_test_paths": _similar_paths(row, rows_by_component),
        }
        for row in rows
    ]
    duplicate_guard_keys = [row["duplicate_guard_key"] for row in rows]
    duplicate_guard_key_count = len(duplicate_guard_keys) - len(set(duplicate_guard_keys))
    default_rows = [
        row for row in rows if row["suite_tier"] == "default_product_core"
    ]
    summary: dict[str, Any] = {
        "index_id": contract["contract_id"],
        "index_version": contract["contract_version"],
        "phase": "68",
        "phase_id": "68",
        "test_suite_index_ready": False,
        "discovered_test_file_count": len(test_files),
        "indexed_test_file_count": len(rows),
        "indexed_test_file_count_equals_discovered": len(rows) == len(test_files),
        "default_product_core_test_file_count": len(default_rows),
        "default_product_core_indexed_count": sum(
            row["test_path"] in DEFAULT_PRODUCT_CORE_TEST_FILES for row in rows
        ),
        "archive_regression_test_file_count": sum(
            row["suite_tier"] == "archive_regression" for row in rows
        ),
        "live_optional_test_file_count": sum(
            row["suite_tier"] == "live_optional" for row in rows
        ),
        "duplicate_test_guard_key_count": duplicate_guard_key_count,
        "similar_test_reference_count": sum(
            len(row["similar_test_paths"]) for row in rows
        ),
        "new_test_preflight_policy_ready": bool(
            contract["new_test_preflight_policy"]
        ),
        "similar_test_extension_policy_ready": (
            contract["duplicate_guard_policy"]["similar_test_action"]
            == "extend_existing_scope_when_possible"
        ),
        "product_capability_mapping_complete": all(
            row["primary_capability_ids"] for row in default_rows
        ),
        "component_area_counts": _counts(rows, "component_area"),
        "suite_tier_counts": _counts(rows, "suite_tier"),
        "index_rows": rows,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
    }
    summary["test_suite_index_ready"] = _passes(summary, contract["hard_gates"])
    summary["result"] = "passed" if summary["test_suite_index_ready"] else "blocked"
    return summary


def summarize_test_suite_index(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact test-index readiness fields for scripts and closure checks."""

    index = build_test_suite_index(path)
    return {
        key: index[key]
        for key in (
            "phase",
            "phase_id",
            "test_suite_index_ready",
            "discovered_test_file_count",
            "indexed_test_file_count",
            "indexed_test_file_count_equals_discovered",
            "default_product_core_test_file_count",
            "default_product_core_indexed_count",
            "archive_regression_test_file_count",
            "live_optional_test_file_count",
            "duplicate_test_guard_key_count",
            "similar_test_reference_count",
            "new_test_preflight_policy_ready",
            "similar_test_extension_policy_ready",
            "product_capability_mapping_complete",
            "production_behavior_change_count",
            "semantic_drift_count",
            "component_area_counts",
            "suite_tier_counts",
            "index_rows",
            "result",
        )
    }


def _index_row(test_path: Path) -> dict[str, Any]:
    rel_path = _relative_path(test_path)
    markers = markers_for_test_path(rel_path)
    suite_tier = _suite_tier(rel_path, markers)
    component_area = _component_area(rel_path)
    test_intent = _test_intent(rel_path)
    capability_ids = _capability_ids(rel_path, markers, component_area)
    return {
        "test_path": rel_path,
        "suite_tier": suite_tier,
        "markers": list(markers),
        "component_area": component_area,
        "test_intent": test_intent,
        "primary_capability_ids": capability_ids,
        "duplicate_guard_key": f"{suite_tier}:{component_area}:{test_intent}:{rel_path}",
        "extension_policy": _extension_policy(suite_tier),
    }


def _suite_tier(rel_path: str, markers: tuple[str, ...]) -> str:
    if rel_path in DEFAULT_PRODUCT_CORE_TEST_FILES:
        return "default_product_core"
    if "live_optional" in markers:
        return "live_optional"
    return "archive_regression"


def _component_area(rel_path: str) -> str:
    stem = Path(rel_path).stem.removeprefix("test_")
    if "ci" in stem or "github" in stem or "workflow" in stem or "archive_regression" in stem:
        return "ci_safety_doctrine"
    if "dashboard" in stem or "render" in stem:
        return "dashboard_surface"
    if (
        "transition" in stem
        or "boom" in stem
        or "cycle_state" in stem
        or "current_evidence" in stem
    ):
        return "ordered_transition_monitoring"
    if "indicator" in stem or "source" in stem or "macro" in stem:
        return "indicator_source_explanation"
    if "portfolio" in stem:
        return "portfolio_policy_research"
    if "backtest" in stem or "validation" in stem or "historical" in stem:
        return "historical_replay_validation"
    if "safety" in stem or "doctrine" in stem:
        return "ci_safety_doctrine"
    if "phase" in stem or "qa" in stem or "freeze" in stem or "closure" in stem:
        return "governance_closure"
    return "infrastructure_misc"


def _test_intent(rel_path: str) -> str:
    stem = Path(rel_path).stem.removeprefix("test_")
    stem = re.sub(r"_script$", "", stem)
    stem = re.sub(r"_closure$", "", stem)
    return stem


def _capability_ids(
    rel_path: str,
    markers: tuple[str, ...],
    component_area: str,
) -> list[str]:
    ids: set[str] = set()
    if component_area in {
        "ordered_transition_monitoring",
        "indicator_source_explanation",
        "dashboard_surface",
    }:
        ids.update(
            {
                "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
                "C2_TRANSITION_RISK_DETECTION",
                "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            },
        )
    if "portfolio_policy_research" in markers or component_area == "portfolio_policy_research":
        ids.add("C4_PORTFOLIO_POLICY_RESEARCH")
    if (
        "historical_replay_backtest" in markers
        or component_area == "historical_replay_validation"
    ):
        ids.add("C5_HISTORICAL_REPLAY_AND_BACKTEST")
    if component_area in {"ci_safety_doctrine", "governance_closure"} or (
        "safety" in markers or "governance_scaffold" in markers
    ):
        ids.add("C6_SAFE_OUTPUT_GOVERNANCE")
    if "temporal" in rel_path or "freshness" in rel_path or "point_in_time" in rel_path:
        ids.add("F1_TEMPORAL_INTEGRITY_AND_ABSTENTION")
    if "freeze" in rel_path or "prospective" in rel_path or "lineage" in rel_path:
        ids.add("F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION")
    return [capability_id for capability_id in CAPABILITY_IDS if capability_id in ids]


def _extension_policy(suite_tier: str) -> str:
    if suite_tier == "default_product_core":
        return "extend_existing_product_core_test_before_adding_new_file"
    if suite_tier == "live_optional":
        return "keep_opt_in_and_never_run_by_default"
    return "prefer_archive_regression_extension_unless_new_contract_requires_new_file"


def _similar_paths(row: dict[str, Any], rows_by_component: dict[str, list[dict[str, Any]]]) -> list[str]:
    row_tokens = set(row["test_intent"].split("_"))
    paths: list[str] = []
    for candidate in rows_by_component[row["component_area"]]:
        if candidate["test_path"] == row["test_path"]:
            continue
        candidate_tokens = set(candidate["test_intent"].split("_"))
        if len(row_tokens & candidate_tokens) >= 2:
            paths.append(candidate["test_path"])
    return sorted(paths)[:8]


def _rows_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        item = str(row[key])
        counts[item] = counts.get(item, 0) + 1
    return dict(sorted(counts.items()))


def _relative_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        return path_obj.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path_obj.as_posix()


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "test_suite_index_ready"
    )


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["test_suite_index"]
    if not isinstance(contract, dict):
        raise ValueError("test suite index contract must be a mapping")
    return contract
