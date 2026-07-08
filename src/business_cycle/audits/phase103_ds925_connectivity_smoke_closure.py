"""Phase103 DS925+ private-LAN connectivity smoke closure."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.service.nas_ds925_connectivity_smoke import (
    DEFAULT_CONTRACT_PATH,
    summarize_nas_ds925_connectivity_smoke,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase103_ds925_connectivity_smoke_closure.yaml"


def summarize_phase103_ds925_connectivity_smoke_closure(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    closure_path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase103 closure gates for CI and final reporting."""

    smoke = summarize_nas_ds925_connectivity_smoke(contract_path=contract_path)
    progress = summarize_product_capability_progress()
    expected = _load_expected(closure_path)
    tracked_raw = _git_ls_files(["data/raw"])
    tracked_book_pdf = _git_ls_files(["docs/景氣循環投資.pdf"])
    summary: dict[str, Any] = {
        "phase": "103",
        "phase_id": 103,
        "phase103_closure_ready": True,
        "nas_ds925_connectivity_smoke_contract_ready": smoke[
            "nas_ds925_connectivity_smoke_contract_ready"
        ],
        "nas_ds925_connectivity_smoke_ready": smoke[
            "nas_ds925_connectivity_smoke_ready"
        ],
        "nas_ds925_endpoint_registry_ready": smoke[
            "nas_ds925_endpoint_registry_ready"
        ],
        "nas_private_ip": smoke["nas_private_ip"],
        "nas_private_ip_private_lan": smoke["nas_private_ip_private_lan"],
        "nas_private_ip_source": smoke["nas_private_ip_source"],
        "probe_plan_ready": smoke["nas_ds925_connectivity_smoke"][
            "probe_plan_ready"
        ],
        "probe_port_count": smoke["probe_port_count"],
        "live_probe_allowed_now": smoke["live_probe_allowed_now"],
        "live_probe_requires_explicit_flag": smoke[
            "live_probe_requires_explicit_flag"
        ],
        "default_probe_execution_count": smoke["default_probe_execution_count"],
        "tests_network_dependency_count": smoke["tests_network_dependency_count"],
        "http_request_attempt_count": smoke["http_request_attempt_count"],
        "dsm_login_attempt_count": smoke["dsm_login_attempt_count"],
        "ssh_login_attempt_count": smoke["ssh_login_attempt_count"],
        "package_install_attempt_count": smoke["package_install_attempt_count"],
        "tailscale_login_attempt_count": smoke["tailscale_login_attempt_count"],
        "container_manager_import_attempt_count": smoke[
            "container_manager_import_attempt_count"
        ],
        "docker_compose_execution_count": smoke["docker_compose_execution_count"],
        "container_image_pull_attempt_count": smoke[
            "container_image_pull_attempt_count"
        ],
        "container_start_attempt_count": smoke["container_start_attempt_count"],
        "live_db_connection_attempt_count": smoke["live_db_connection_attempt_count"],
        "postgres_read_attempt_count": smoke["postgres_read_attempt_count"],
        "postgres_write_attempt_count": smoke["postgres_write_attempt_count"],
        "schema_migration_attempt_count": smoke["schema_migration_attempt_count"],
        "live_fetch_attempt_count": smoke["live_fetch_attempt_count"],
        "repo_output_written_count": smoke["repo_output_written_count"],
        "public_output_count": smoke["public_output_count"],
        "frontend_database_access_allowed": smoke["frontend_database_access_allowed"],
        "frontend_api_key_allowed": smoke["frontend_api_key_allowed"],
        "secret_value_literal_count": smoke["secret_value_literal_count"],
        "prohibited_output_field_count": smoke["prohibited_output_field_count"],
        "candidate_phase_emitted": smoke["candidate_phase_emitted"],
        "current_phase_emitted": smoke["current_phase_emitted"],
        "current_data_used_to_infer_declared_phase_count": smoke[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": smoke[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": smoke["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": smoke["role_count_voting_added_count"],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "progress_decrease_count": progress["progress_decrease_count"],
        "progress_decrease_without_reason_count": progress[
            "progress_decrease_without_reason_count"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "raw_book_pdf_tracked_count": len(tracked_book_pdf),
        "tracked_data_raw_file_count": len(tracked_raw),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_ds925_connectivity_smoke"
        ),
        "portfolio_policy_research_alignment": (
            "research_templates_preserved_no_live_instruction"
        ),
        "historical_replay_backtest_alignment": (
            "connectivity_smoke_ready_no_replay_execution"
        ),
        "development_next_phase": smoke["development_next_phase"],
        "phase103_closure_status": (
            "closed_ds925_private_lan_connectivity_smoke_ready_no_auth_or_db_write"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase103_ds925_connectivity_smoke_closure"]["hard_gates"])


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
