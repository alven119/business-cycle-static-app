"""Phase109 Tailscale private HTTPS acceptance closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_tailscale_private_https import (
    summarize_nas_tailscale_private_https,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase109_nas_tailscale_private_https_closure.yaml"


def summarize_phase109_nas_tailscale_private_https_closure(
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return the operator-attested Phase109 private HTTPS acceptance gates."""

    private_https = summarize_nas_tailscale_private_https()
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "109",
        "phase_id": 109,
        "phase109_checkpoint_ready": True,
        "nas_tailscale_private_https_contract_ready": private_https[
            "nas_tailscale_private_https_contract_ready"
        ],
        "nas_tailscale_private_https_package_ready": private_https[
            "nas_tailscale_private_https_package_ready"
        ],
        "phase108_dependency_ready": private_https["phase108_dependency_ready"],
        "runtime_https_cookie_contract_ready": private_https[
            "runtime_https_cookie_contract_ready"
        ],
        "runtime_login_rate_limit_ready": private_https[
            "runtime_login_rate_limit_ready"
        ],
        "runtime_security_headers_ready": private_https[
            "runtime_security_headers_ready"
        ],
        "tailscale_live_state_reconciled": private_https[
            "tailscale_live_state_reconciled"
        ],
        "tailscale_backend_online_observed": private_https[
            "tailscale_backend_online_observed"
        ],
        "tailscale_installed_version_observed": private_https[
            "tailscale_installed_version_observed"
        ],
        "tailscale_serve_configured": private_https["tailscale_serve_configured"],
        "tailscale_funnel_configured": private_https[
            "tailscale_funnel_configured"
        ],
        "mobile_cellular_smoke_passed": private_https[
            "mobile_cellular_smoke_passed"
        ],
        "private_https_acceptance_status": private_https[
            "private_https_acceptance_status"
        ],
        "private_https_accepted": private_https["private_https_accepted"],
        "operator_action_required": private_https["operator_action_required"],
        "postgres_business_table_count_observed": private_https[
            "postgres_business_table_count_observed"
        ],
        "production_readiness_rebaseline_required": private_https[
            "production_readiness_rebaseline_required"
        ],
        "production_readiness_rebaseline_reason_count": private_https[
            "production_readiness_rebaseline_reason_count"
        ],
        "product_progress_percentage_change_count": private_https[
            "product_progress_percentage_change_count"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_phase_id": progress["phase_id"],
        "public_exposure_enabled": private_https["public_exposure_enabled"],
        "secure_value_committed_count": private_https[
            "secure_value_committed_count"
        ],
        "candidate_phase_emitted": private_https["candidate_phase_emitted"],
        "current_phase_emitted": private_https["current_phase_emitted"],
        "standalone_classifier_added_count": private_https[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": private_https[
            "phase_rank_or_score_added_count"
        ],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_private_https_only"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_unchanged_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": "no_replay_or_backtest_execution",
        "development_next_phase": private_https["development_next_phase"],
        "phase109_closure_status": (
            "closed_tailscale_private_https_and_mobile_acceptance"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase109_nas_tailscale_private_https_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _git_ls_files(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]
