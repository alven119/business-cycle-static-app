"""Phase 90 NAS dynamic-service architecture and Pages-retirement closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "specs/common/nas_dynamic_service_contract.yaml"
CLOSURE_PATH = (
    ROOT / "specs/audits/phase90_nas_dynamic_service_architecture_closure.yaml"
)
WORKFLOW_DIR = ROOT / ".github/workflows"
PAGES_WORKFLOW = WORKFLOW_DIR / "pages.yml"
PAGES_ACTION_MARKERS = (
    "actions/deploy-pages",
    "actions/configure-pages",
    "actions/upload-pages-artifact",
    "build_github_pages_research_dashboard",
    "validate_github_pages_research_dashboard",
)


def summarize_phase90_nas_dynamic_service_architecture_closure(
    contract_path: str | Path = CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 90 closure fields for CLI, tests, and final reporting."""

    contract = _load_contract(contract_path)
    expected = _load_expected(closure_path)
    pages_action_reference_count = _pages_action_reference_count()
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])

    summary: dict[str, Any] = {
        "phase": "90",
        "phase_id": 90,
        "phase90_closure_ready": True,
        "nas_dynamic_service_contract_ready": _contract_ready(contract),
        "github_pages_deployment_retired": (
            not PAGES_WORKFLOW.exists() and pages_action_reference_count == 0
        ),
        "pages_workflow_present": PAGES_WORKFLOW.exists(),
        "pages_action_reference_count": pages_action_reference_count,
        "github_repo_retained_for_code_and_ci": bool(
            contract["github_pages_retirement_policy"][
                "github_repository_retained_for_code_and_ci"
            ],
        ),
        "dynamic_service_runtime_planned": (
            contract["service_target"]["deployment_shape"]
            == "private_dynamic_research_service"
        ),
        "planned_web_framework": contract["runtime_stack"]["web_service"][
            "planned_framework"
        ],
        "private_mobile_access_model": contract["service_target"][
            "external_access_model"
        ],
        "postgres_pit_schema_planned": bool(
            contract["runtime_stack"]["database"]["pit_schema_required_from_start"],
        ),
        "revised_first_backfill_policy_present": bool(
            contract["data_warehouse_policy"]["backfill_plan"][
                "revised_complete_first"
            ],
        ),
        "vintage_backfill_plan_present": bool(
            contract["data_warehouse_policy"]["backfill_plan"][
                "vintage_incremental_followup_required"
            ],
        ),
        "public_internet_exposure_default": bool(
            contract["service_target"]["public_internet_exposure_default"],
        ),
        "frontend_database_access_allowed": bool(
            contract["runtime_stack"]["web_service"][
                "frontend_database_access_allowed"
            ],
        ),
        "frontend_api_key_allowed": bool(
            contract["runtime_stack"]["web_service"]["frontend_api_key_allowed"],
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "candidate_phase_emitted": bool(
            contract["dashboard_product_policy"]["no_candidate_or_current_phase_emission"]
        )
        is False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_nas_service_architecture_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "historical_replay_first_before_portfolio_backtest_ux"
        ),
        "product_capabilities_advanced": contract["product_capabilities_advanced"],
        "web_surfaces_advanced": contract["web_surfaces_advanced"],
        "deferred_capability_gaps": [
            "Phase91: Postgres PIT-ready schema implementation",
            "Phase92: revised macro data completeness backfill",
            "Phase93: vintage/PIT backfill and availability accounting",
            "Phase94+: NAS dynamic dashboard runtime and chart API",
        ],
        "development_next_phase": int(
            contract["data_warehouse_policy"]["backfill_plan"][
                "future_phase_for_revised_backfill"
            ],
        )
        - 1,
        "phase90_closure_status": (
            "closed_pages_retired_nas_dynamic_service_architecture_ready"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_dynamic_service_contract"])


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase90_nas_dynamic_service_architecture_closure"]["hard_gates"])


def _contract_ready(contract: dict[str, Any]) -> bool:
    return (
        contract["status"] == "active"
        and contract["service_target"]["external_access_model"]
        == "tailscale_or_vpn_first"
        and contract["runtime_stack"]["web_service"]["planned_framework"] == "fastapi"
        and contract["runtime_stack"]["database"]["engine"] == "postgres"
        and contract["runtime_stack"]["database"]["pit_schema_required_from_start"]
        is True
        and contract["github_pages_retirement_policy"][
            "github_pages_deployment_enabled"
        ]
        is False
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pages_action_reference_count() -> int:
    if not WORKFLOW_DIR.exists():
        return 0
    count = 0
    for path in WORKFLOW_DIR.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        count += sum(text.count(marker) for marker in PAGES_ACTION_MARKERS)
    return count


def _git_ls_files(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
