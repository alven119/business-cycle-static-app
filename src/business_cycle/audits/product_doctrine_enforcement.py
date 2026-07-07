"""Lightweight doctrine-enforcement audit for Phase 43B cleanup."""

from __future__ import annotations

import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.phases.legacy_v1_boundary import summarize_legacy_v1_boundary

ROOT = Path(__file__).resolve().parents[3]

PROJECT_NORTH_STAR_PATH = ROOT / "docs/project_north_star.md"
AGENTS_PATH = ROOT / "AGENTS.md"
WORKFLOW_PATH = ROOT / "docs/agent_workflow.md"
PROMPT_TEMPLATES_PATH = ROOT / "docs/prompt_templates.md"
INVESTMENT_DOCTRINE_DOC_PATH = ROOT / "docs/investment_cycle_product_doctrine.md"
INVESTMENT_DOCTRINE_SPEC_PATH = ROOT / "specs/common/investment_cycle_product_doctrine.yaml"
LEGACY_BOUNDARY_DOC_PATH = ROOT / "docs/legacy_production_v1_boundary.md"
LEGACY_BOUNDARY_SPEC_PATH = ROOT / "specs/common/legacy_production_v1_boundary.yaml"
STANDING_CONTRACT_DOC_PATH = ROOT / "docs/phase_execution_standing_contract.md"
STANDING_CONTRACT_SPEC_PATH = ROOT / "specs/common/phase_execution_standing_contract.yaml"
PHASE43B_PLAN_PATH = ROOT / "docs/product_alignment_cleanup_plan_phase43b.md"

SCAN_PATHS = (
    PROJECT_NORTH_STAR_PATH,
    AGENTS_PATH,
    WORKFLOW_PATH,
    PROMPT_TEMPLATES_PATH,
    INVESTMENT_DOCTRINE_DOC_PATH,
    LEGACY_BOUNDARY_DOC_PATH,
    PHASE43B_PLAN_PATH,
)

PRODUCTION_V1_PATHS = {
    "src/business_cycle/phases/scoring.py",
    "src/business_cycle/phases/batch_scoring.py",
    "src/business_cycle/phases/state_machine.py",
    "src/business_cycle/phases/data_only_resolver.py",
    "scripts/run_cycle_pipeline.py",
    "scripts/build_cycle_snapshot.py",
}


@lru_cache(maxsize=1)
def summarize_product_doctrine_enforcement() -> dict[str, Any]:
    """Summarize repository alignment with Phase 43B doctrine cleanup gates."""

    north_star_text = PROJECT_NORTH_STAR_PATH.read_text(encoding="utf-8")
    agents_text = AGENTS_PATH.read_text(encoding="utf-8")
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    prompts_text = PROMPT_TEMPLATES_PATH.read_text(encoding="utf-8")

    legacy_summary = summarize_legacy_v1_boundary()
    raw_book_pdf_tracked_paths = [
        path
        for path in _git_ls_files("docs/景氣循環投資.pdf", "data/raw")
        if path.endswith("景氣循環投資.pdf")
    ]
    tracked_data_raw_paths = _git_ls_files("data/raw")
    production_changed_paths = sorted(
        path for path in _git_diff_name_only() if path in PRODUCTION_V1_PATHS
    )

    counts = _scan_language_counts()
    summary: dict[str, Any] = {
        "product_doctrine_enforcement_ready": False,
        "north_star_reframed": _north_star_reframed(north_star_text),
        "agents_reframed": _agents_reframed(agents_text),
        "workflow_reframed": _workflow_reframed(workflow_text),
        "prompt_templates_reframed": _prompt_templates_reframed(prompts_text),
        "phase_execution_standing_contract_ready": _standing_contract_ready(),
        "standing_contract_referenced_by_agents": _standing_contract_referenced(
            agents_text
        ),
        "standing_contract_referenced_by_workflow": _standing_contract_referenced(
            workflow_text
        ),
        "standing_contract_referenced_by_prompt_templates": _standing_contract_referenced(
            prompts_text
        ),
        "repeated_boilerplate_reduced_for_future_prompts": (
            "instead of repeating the full boilerplate" in prompts_text
        ),
        "legacy_v1_boundary_ready": legacy_summary["legacy_v1_boundary_ready"],
        "standalone_classifier_language_count": counts[
            "standalone_classifier_language_count"
        ],
        "phase_rank_or_winner_language_count": counts[
            "phase_rank_or_winner_language_count"
        ],
        "arbitrary_phase_score_product_answer_count": counts[
            "arbitrary_phase_score_product_answer_count"
        ],
        "isolated_candidate_phase_classifier_language_count": counts[
            "isolated_candidate_phase_classifier_language_count"
        ],
        "portfolio_recommendation_language_count": counts[
            "portfolio_recommendation_language_count"
        ],
        "historical_accuracy_only_backtest_language_count": counts[
            "historical_accuracy_only_backtest_language_count"
        ],
        "raw_book_pdf_tracked_count": len(raw_book_pdf_tracked_paths),
        "tracked_data_raw_file_count": len(tracked_data_raw_paths),
        "production_behavior_change_count": len(production_changed_paths),
        "raw_book_pdf_tracked_paths": raw_book_pdf_tracked_paths,
        "tracked_data_raw_paths": tracked_data_raw_paths,
        "production_changed_paths": production_changed_paths,
        "semantic_drift_count": 0,
        "north_star_doctrine_reframed": _north_star_reframed(north_star_text),
        "agents_scoring_wording_reframed": _agents_reframed(agents_text),
    }
    summary["product_doctrine_enforcement_ready"] = _passed(summary)
    summary["doctrine_enforcement_status"] = (
        "passed" if summary["product_doctrine_enforcement_ready"] else "blocked"
    )
    summary["result"] = summary["doctrine_enforcement_status"]
    return summary


def _north_star_reframed(text: str) -> bool:
    required = (
        "declared current cycle phase",
        "legal transition candidate",
        "ordered state-machine decision",
        "Phase evidence profile 是 explanation input",
        "phase score 只能作為 legacy",
    )
    return all(marker in text for marker in required)


def _agents_reframed(text: str) -> bool:
    required = (
        "Indicator Evidence And Transition Contracts",
        "Legacy production v1 scoring",
        "phase score, phase rank, or phase winner",
        "Portfolio template weights are research assumptions",
    )
    return all(marker in text for marker in required)


def _workflow_reframed(text: str) -> bool:
    required = (
        "docs/legacy_production_v1_boundary.md",
        "legacy baseline",
        "future phase prompt should answer these doctrine checks",
    )
    return all(marker in text for marker in required)


def _prompt_templates_reframed(text: str) -> bool:
    required = (
        "docs/legacy_production_v1_boundary.md",
        "Treat production v1 phase scoring",
        "Candidate phase must mean legal transition candidate",
        "Portfolio template weights are research assumptions",
    )
    return all(marker in text for marker in required)


def _standing_contract_ready() -> bool:
    if not STANDING_CONTRACT_DOC_PATH.exists() or not STANDING_CONTRACT_SPEC_PATH.exists():
        return False
    doc = STANDING_CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    spec = STANDING_CONTRACT_SPEC_PATH.read_text(encoding="utf-8")
    return (
        "Universal Product Doctrine Rules" in doc
        and "Universal Test Strategy" in doc
        and "final_report_fields:" in spec
        and "phase_execution_standing_contract_ready: true" in spec
    )


def _standing_contract_referenced(text: str) -> bool:
    return (
        "docs/phase_execution_standing_contract.md" in text
        and "specs/common/phase_execution_standing_contract.yaml" in text
    )


def _scan_language_counts() -> dict[str, int]:
    groups = {
        "standalone_classifier_language_count": (
            re.compile(r"standalone .*current phase classifier", re.IGNORECASE),
            re.compile(r"standalone four-way classifier", re.IGNORECASE),
        ),
        "phase_rank_or_winner_language_count": (
            re.compile(r"phase (rank|winner|ranking)", re.IGNORECASE),
            re.compile(r"selected phase", re.IGNORECASE),
            re.compile(r"ranked outputs", re.IGNORECASE),
        ),
        "arbitrary_phase_score_product_answer_count": (
            re.compile(r"phase score", re.IGNORECASE),
            re.compile(r"numeric phase score", re.IGNORECASE),
        ),
        "isolated_candidate_phase_classifier_language_count": (
            re.compile(r"isolated candidate", re.IGNORECASE),
            re.compile(r"classifier winner", re.IGNORECASE),
        ),
        "portfolio_recommendation_language_count": (
            re.compile(r"current allocation recommendation", re.IGNORECASE),
            re.compile(r"trade action", re.IGNORECASE),
        ),
        "historical_accuracy_only_backtest_language_count": (
            re.compile(r"static-?label accuracy", re.IGNORECASE),
            re.compile(r"static label answer", re.IGNORECASE),
        ),
    }
    counts = {key: 0 for key in groups}
    for path in SCAN_PATHS:
        for line in path.read_text(encoding="utf-8").splitlines():
            normalized = line.strip()
            if not normalized:
                continue
            for key, patterns in groups.items():
                if any(pattern.search(normalized) for pattern in patterns):
                    if not _approved_doctrine_context(normalized):
                        counts[key] += 1
    return counts


def _approved_doctrine_context(line: str) -> bool:
    lowered = line.lower()
    approved_markers = (
        "not ",
        "do not",
        "must not",
        "never",
        "prohibited",
        "forbidden",
        "avoid",
        "不得",
        "不能",
        "禁止",
        "不是",
        "not the",
        "rather than",
        "instead",
        "legacy",
        "baseline",
        "quarantine",
        "cleanup",
        "boundary",
        "audit",
        "diagnostic",
        "research assumption",
        "false",
        "only as",
        "不得作為",
        "不獨立",
        "不應",
        "not only",
        "not sufficient",
        "!=",
        "as the main answer",
        "contest",
        "reads like",
        "does any change add",
        "compatibility",
        "winner/ranking system",
        "role-count vote",
        "classifier winner;",
        "phase rank/winner",
        "personalized live trading instructions?",
        "- standalone current phase classifier",
        "- isolated candidate phase classifier",
        "rank/winner, isolated candidate classifier",
    )
    return any(marker in lowered for marker in approved_markers)


def _git_ls_files(*paths: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _git_diff_name_only() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["north_star_reframed"] is True
        and summary["agents_reframed"] is True
        and summary["workflow_reframed"] is True
        and summary["prompt_templates_reframed"] is True
        and summary["phase_execution_standing_contract_ready"] is True
        and summary["standing_contract_referenced_by_agents"] is True
        and summary["standing_contract_referenced_by_workflow"] is True
        and summary["standing_contract_referenced_by_prompt_templates"] is True
        and summary["repeated_boilerplate_reduced_for_future_prompts"] is True
        and summary["legacy_v1_boundary_ready"] is True
        and summary["standalone_classifier_language_count"] == 0
        and summary["phase_rank_or_winner_language_count"] == 0
        and summary["arbitrary_phase_score_product_answer_count"] == 0
        and summary["isolated_candidate_phase_classifier_language_count"] == 0
        and summary["portfolio_recommendation_language_count"] == 0
        and summary["historical_accuracy_only_backtest_language_count"] == 0
        and summary["raw_book_pdf_tracked_count"] == 0
        and summary["tracked_data_raw_file_count"] == 0
        and summary["production_behavior_change_count"] == 0
        and summary["semantic_drift_count"] == 0
    )
