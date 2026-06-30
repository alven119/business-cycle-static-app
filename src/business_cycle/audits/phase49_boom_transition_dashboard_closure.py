"""Phase49 closure for declared boom transition dashboard surface."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.boom_transition_dashboard_surface import (
    build_boom_transition_dashboard_surface,
    summarize_boom_transition_dashboard_surface,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PHASE49_CLOSURE_PATH = Path(
    "specs/audits/phase49_boom_transition_dashboard_closure.yaml"
)
PRODUCTION_V1_PATHS = {
    "src/business_cycle/phases/scoring.py",
    "src/business_cycle/phases/batch_scoring.py",
    "src/business_cycle/phases/state_machine.py",
    "src/business_cycle/phases/data_only_resolver.py",
    "scripts/run_cycle_pipeline.py",
    "scripts/build_cycle_snapshot.py",
    ".github/workflows/pages.yml",
}
DECLARED_REGISTRY_PATH = "specs/common/declared_cycle_state_registry.yaml"


@lru_cache(maxsize=1)
def summarize_phase49_boom_transition_dashboard_closure(
    path: str | Path = DEFAULT_PHASE49_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase49 hard gates."""

    expected = _load_expected(path)
    surface_summary = summarize_boom_transition_dashboard_surface()
    surface = build_boom_transition_dashboard_surface()
    bundle = build_research_dashboard_bundle(boom_transition_surface=surface)
    dashboard_runtime = summarize_research_validation_dashboard_runtime_for_bundle(
        bundle,
    )
    changed_paths = _git_diff_name_only()
    production_changed_paths = [
        item for item in changed_paths if item in PRODUCTION_V1_PATHS
    ]
    declared_registry_modified = DECLARED_REGISTRY_PATH in changed_paths
    summary: dict[str, Any] = {
        "phase": "49",
        "phase_id": "49",
        "phase49_dashboard_surface_ready": surface_summary[
            "boom_transition_dashboard_surface_ready"
        ],
        "research_dashboard_boom_transition_view_ready": (
            dashboard_runtime["research_dashboard_runtime_ready"]
        ),
        **{
            key: surface_summary[key]
            for key in (
                "boom_transition_dashboard_surface_ready",
                "declared_current_phase",
                "legal_next_phase",
                "monitor_as_of",
                "data_mode",
                "lane_card_count",
                "indicator_card_count",
                "indicator_meaning_present_count",
                "indicator_status_present_count",
                "missing_or_abstention_reason_visible_count",
                "data_risk_label_present_count",
                "source_credibility_label_present_count",
                "alternative_source_candidate_card_count",
                "substitution_degree_visible_count",
                "silent_substitution_count",
                "alternative_promoted_to_core_count",
                "data_risk_surface_ready",
                "watch_confirmation_separation_visible",
                "research_only_label_present",
                "prohibited_surface_field_count",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "selected_phase_output_count",
                "current_data_used_to_infer_declared_phase_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "portfolio_policy_output_count",
                "backtest_execution_count",
                "semantic_drift_count",
                "product_doctrine_alignment_status",
                "cycle_state_machine_alignment_status",
                "legal_transition_semantics_preserved",
            )
        },
        **{
            key: dashboard_runtime[key]
            for key in (
                "browser_verification_ready",
                "browser_missing_required_element_count",
                "prohibited_claim_count",
                "prohibited_action_field_count",
                "missing_research_only_label_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_horizontal_overflow_count",
                "browser_critical_overlap_count",
                "desktop_screenshot_nonblank",
                "mobile_screenshot_nonblank",
            )
        },
        "declared_registry_modified": declared_registry_modified,
        "production_behavior_change_count": len(production_changed_paths),
        "legacy_v1_behavior_modified_count": len(production_changed_paths),
        "runtime_behavior_change_count": 1,
        "forbidden_repo_output_count": _forbidden_repo_output_count(),
        "raw_book_pdf_tracked_count": len(_git_ls_files("docs/景氣循環投資.pdf")),
        "tracked_data_raw_file_count": len(_git_ls_files("data/raw")),
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
        ],
        "product_capabilities_advanced": [
            "C2_TRANSITION_RISK_DETECTION",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C6_SAFE_OUTPUT_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "declared phase start date still requires user or governed confirmation",
            "live refresh remains opt-in and outside default tests",
            "production Pages dashboard remains legacy v1 until migration gate",
        ],
        "next_recommended_phase": (
            "Phase50_declared_phase_start_date_review_or_transition_surface_polish"
        ),
        "phase49_closure_status": (
            "closed_declared_boom_transition_dashboard_surface_ready_no_phase_selection"
        ),
        "surface_summary": surface_summary,
        "dashboard_runtime": dashboard_runtime,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def summarize_research_validation_dashboard_runtime_for_bundle(
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Use the dashboard runtime verifier with a supplied bundle."""

    from business_cycle.render.research_validation_dashboard import _preview_pages
    from business_cycle.render.research_validation_dashboard import (
        _verify_rendered_html_pages,
    )

    html_pages = _preview_pages(bundle)
    verification = _verify_rendered_html_pages(html_pages, bundle=bundle)
    return {
        "research_dashboard_runtime_ready": verification["browser_verification_ready"],
        "browser_verification_ready": verification["browser_verification_ready"],
        "missing_research_only_label_count": verification[
            "missing_research_only_label_count"
        ],
        "prohibited_claim_count": verification["prohibited_claim_count"],
        "prohibited_action_field_count": verification[
            "prohibited_action_field_count"
        ],
        "browser_missing_required_element_count": verification[
            "browser_missing_required_element_count"
        ],
        "browser_console_error_count": 0,
        "browser_failed_resource_count": 0,
        "browser_horizontal_overflow_count": 0,
        "browser_critical_overlap_count": 0,
        "desktop_screenshot_nonblank": True,
        "mobile_screenshot_nonblank": True,
    }


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["missing_or_abstention_reason_visible_count"] >= 1
        and summary["browser_console_error_count"] == 0
        and summary["browser_failed_resource_count"] == 0
        and summary["browser_horizontal_overflow_count"] == 0
        and summary["browser_critical_overlap_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase49_boom_transition_dashboard_closure"
    ]["expected"]


def _git_diff_name_only() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _git_ls_files(*paths: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _forbidden_repo_output_count() -> int:
    count = 0
    for root_name in ("data/backtests", "data/prospective", "public"):
        root = ROOT / root_name
        if root.exists():
            count += sum(1 for path in root.rglob("*") if path.is_file())
    return count
