"""Phase71 declared phase-start registry update-gate closure."""

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
from business_cycle.cycle_state.declared_phase_start_confirmation import (
    build_declared_phase_start_confirmation_view_model,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_declared_phase_start_registry_update_gate_view_model,
    summarize_declared_phase_start_registry_update_gate,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase71_declared_phase_start_registry_update_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase71_declared_phase_start_registry_update_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase71 hard gates without writing repo outputs."""

    expected = _load_expected(path)
    gate = summarize_declared_phase_start_registry_update_gate()
    rendered = _render_dashboard_update_gate_summary(gate)
    cli = _cli_tmp_registry_update_summary()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "71",
        "phase_id": 71,
        "phase_label": "declared_phase_start_registry_update_gate_and_dashboard_handoff",
        "declared_phase_start_registry_update_gate_ready": gate[
            "declared_phase_start_registry_update_gate_ready"
        ],
        "sample_exact_tmp_registry_update_valid": gate[
            "sample_exact_tmp_registry_update_valid"
        ],
        "sample_window_tmp_registry_update_valid": gate[
            "sample_window_tmp_registry_update_valid"
        ],
        "missing_input_update_rejected": gate["missing_input_update_rejected"],
        "phase_age_dashboard_handoff_ready": gate[
            "phase_age_dashboard_handoff_ready"
        ],
        "rendered_phase_start_update_gate_ready": rendered[
            "rendered_phase_start_update_gate_ready"
        ],
        "cli_tmp_registry_update_ready": cli["cli_tmp_registry_update_ready"],
        "cli_tmp_registry_output_under_tmp": cli[
            "cli_tmp_registry_output_under_tmp"
        ],
        "declared_current_phase": gate["declared_current_phase"],
        "legal_previous_phase": gate["legal_previous_phase"],
        "legal_next_phase": gate["legal_next_phase"],
        "exact_tmp_registry_phase_age_days": gate[
            "exact_tmp_registry_phase_age_days"
        ],
        "window_tmp_registry_exact_age_allowed": gate[
            "window_tmp_registry_exact_age_allowed"
        ],
        "canonical_registry_write_allowed": gate["canonical_registry_write_allowed"],
        "canonical_registry_modified": gate["canonical_registry_modified"],
        "future_canonical_registry_update_gate_required": gate[
            "future_canonical_registry_update_gate_required"
        ],
        "phase_age_false_precision_count": gate[
            "phase_age_false_precision_count"
        ],
        "current_data_used_to_infer_declared_phase_count": gate[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": gate["standalone_classifier_added_count"],
        "phase_rank_or_score_added_count": gate["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": gate["role_count_voting_added_count"],
        "candidate_phase_emitted": gate["candidate_phase_emitted"],
        "current_phase_emitted": gate["current_phase_emitted"],
        "production_behavior_change_count": gate["production_behavior_change_count"],
        "semantic_drift_count": gate["semantic_drift_count"],
        "product_doctrine_alignment_status": gate[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": gate[
            "cycle_state_machine_alignment_status"
        ],
        "legal_transition_semantics_preserved": gate[
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
        "phase71_closure_status": (
            "closed_declared_phase_start_registry_update_gate_ready_"
            "canonical_registry_unchanged"
        ),
    }
    summary["phase71_declared_phase_start_registry_update_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase71_declared_phase_start_registry_update_ready"]
        else "blocked"
    )
    return summary


def _render_dashboard_update_gate_summary(gate: dict[str, Any]) -> dict[str, Any]:
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    confirmation = build_declared_phase_start_confirmation_view_model()
    replay_preview = build_transition_timing_replay_preview_view_model()
    update_gate = build_declared_phase_start_registry_update_gate_view_model(gate)
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=replay_preview,
        declared_phase_start_confirmation=confirmation,
        declared_phase_start_registry_update_gate=update_gate,
    )
    with tempfile.TemporaryDirectory(prefix="phase71_dashboard_", dir="/tmp") as tmp:
        result = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")
    return {
        "rendered_phase_start_update_gate_ready": (
            result["browser_verification_ready"]
            and "data-declared-phase-start-update-gate" in html
            and "data-phase-start-update-handoff" in html
            and "data-canonical-registry-write-boundary" in html
            and "SUPPLY_EXPLICIT_START_DATE_OR_WINDOW" in html
        ),
    }


def _cli_tmp_registry_update_summary() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="phase71_cli_", dir="/tmp") as tmp:
        registry_output = Path(tmp) / "declared_cycle_state_registry.yaml"
        result_output = Path(tmp) / "gate.json"
        subprocess.run(
            [
                sys.executable,
                "scripts/apply_declared_phase_start_registry_update.py",
                "--start-date",
                "2025-06-01",
                "--as-of",
                "2026-07-03",
                "--confirmation-note",
                "phase71 cli fixture",
                "--input-source",
                "test_fixture",
                "--write-temp-registry",
                "--registry-output",
                str(registry_output),
                "--output",
                str(result_output),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return {
            "cli_tmp_registry_update_ready": registry_output.is_file()
            and result_output.is_file(),
            "cli_tmp_registry_output_under_tmp": (
                str(registry_output.resolve()).startswith("/tmp/")
                and str(result_output.resolve()).startswith("/tmp/")
            ),
        }


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase71_declared_phase_start_registry_update_closure"][
            "hard_gates"
        ],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase71_declared_phase_start_registry_update_ready"
    )
