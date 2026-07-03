"""Phase70 declared phase-start registry update preview closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    summarize_declared_phase_start_registry_update_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase70_declared_phase_start_registry_preview_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase70_declared_phase_start_registry_preview_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase70 hard gates without writing repo outputs."""

    expected = _load_expected(path)
    preview = summarize_declared_phase_start_registry_update_preview()
    cli = _cli_preview_output_summary()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "70",
        "phase_id": 70,
        "phase_label": "declared_phase_start_registry_update_preview",
        "declared_phase_start_registry_update_preview_ready": preview[
            "declared_phase_start_registry_update_preview_ready"
        ],
        "intake_contract_ready": preview["intake_contract_ready"],
        "sample_exact_date_preview_valid": preview["sample_exact_date_preview_valid"],
        "sample_window_preview_valid": preview["sample_window_preview_valid"],
        "missing_input_wait_state_valid": preview["missing_input_wait_state_valid"],
        "cli_preview_output_ready": cli["cli_preview_output_ready"],
        "cli_preview_output_under_tmp": cli["cli_preview_output_under_tmp"],
        "declared_current_phase": preview["declared_current_phase"],
        "legal_previous_phase": preview["legal_previous_phase"],
        "legal_next_phase": preview["legal_next_phase"],
        "registry_write_allowed": preview["registry_write_allowed"],
        "declared_registry_modified": preview["declared_registry_modified"],
        "future_registry_update_gate_required": preview[
            "future_registry_update_gate_required"
        ],
        "exact_date_preview_can_compute_phase_age": preview[
            "exact_date_preview_can_compute_phase_age"
        ],
        "window_preview_exact_age_allowed": preview[
            "window_preview_exact_age_allowed"
        ],
        "exact_date_preview_phase_age_days": preview[
            "exact_date_preview_phase_age_days"
        ],
        "window_preview_age_range": preview["window_preview_age_range"],
        "phase_age_false_precision_count": preview[
            "phase_age_false_precision_count"
        ],
        "current_data_used_to_infer_declared_phase_count": preview[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": preview[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": preview[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": preview["role_count_voting_added_count"],
        "candidate_phase_emitted": preview["candidate_phase_emitted"],
        "current_phase_emitted": preview["current_phase_emitted"],
        "production_behavior_change_count": preview[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": preview["semantic_drift_count"],
        "product_doctrine_alignment_status": preview[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": preview[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": preview[
            "legal_transition_semantics_preserved"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": expected[
            "product_capability_progress_impacted_count"
        ],
        "current_product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase70_closure_status": (
            "closed_declared_phase_start_registry_preview_ready_no_registry_write"
        ),
    }
    summary["phase70_declared_phase_start_registry_preview_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase70_declared_phase_start_registry_preview_ready"]
        else "blocked"
    )
    return summary


def _cli_preview_output_summary() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="phase70_preview_", dir="/tmp") as tmp:
        output = Path(tmp) / "preview.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/preview_declared_phase_start_registry_update.py",
                "--start-date",
                "2025-06-01",
                "--as-of",
                "2026-07-03",
                "--confirmation-note",
                "closure fixture",
                "--input-source",
                "test_fixture",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "cli_preview_output_ready": output.is_file(),
            "cli_preview_output_under_tmp": str(output.resolve()).startswith("/tmp/"),
        }


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase70_declared_phase_start_registry_preview_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase70_declared_phase_start_registry_preview_ready"
    )
