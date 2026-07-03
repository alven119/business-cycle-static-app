"""Phase68 closure for phase-start governance, numeric overlay, and test index."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle import data_sources
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.audits.test_suite_index import summarize_test_suite_index
from business_cycle.cycle_state.declared_boom_start_governance import (
    summarize_declared_boom_start_governance,
)
from business_cycle.render.transition_timing_replay_preview import (
    summarize_transition_timing_replay_preview,
)
from business_cycle.storage.raw_store import RawCsvStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase68_phase_start_numeric_test_index_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase68_phase_start_numeric_test_index_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase68 hard gates using only tmp fixture data."""

    expected = _load_expected(path)
    start = summarize_declared_boom_start_governance()
    numeric_preview = _tmp_numeric_preview_summary()
    test_index = summarize_test_suite_index()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "68",
        "phase_id": 68,
        "phase_label": "governed_phase_start_numeric_overlay_and_test_index",
        "declared_boom_start_governance_ready": start[
            "declared_boom_start_governance_ready"
        ],
        "declared_current_phase": start["declared_current_phase"],
        "legal_next_phase": start["legal_next_phase"],
        "declared_phase_start_date_current_value": start[
            "declared_phase_start_date_current_value"
        ],
        "declared_phase_start_date_status": start[
            "declared_phase_start_date_status"
        ],
        "phase_age_status_current_value": start["phase_age_status_current_value"],
        "governed_start_date_confirmed": start["governed_start_date_confirmed"],
        "user_confirmation_required": start["user_confirmation_required"],
        "registry_write_allowed": start["registry_write_allowed"],
        "declared_registry_modified": start["declared_registry_modified"],
        "phase_age_false_precision_count": start["phase_age_false_precision_count"],
        "numeric_cache_overlay_supported": numeric_preview[
            "numeric_cache_overlay_supported"
        ],
        "actual_numeric_cache_fixture_role_count": numeric_preview[
            "actual_numeric_cache_role_count"
        ],
        "lane_with_actual_numeric_context_fixture_count": numeric_preview[
            "lane_with_actual_numeric_context_count"
        ],
        "test_suite_index_ready": test_index["test_suite_index_ready"],
        "default_product_core_test_file_count": test_index[
            "default_product_core_test_file_count"
        ],
        "duplicate_test_guard_key_count": test_index[
            "duplicate_test_guard_key_count"
        ],
        "new_test_preflight_policy_ready": test_index[
            "new_test_preflight_policy_ready"
        ],
        "similar_test_extension_policy_ready": test_index[
            "similar_test_extension_policy_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "current_data_used_to_infer_declared_phase_count": numeric_preview[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": numeric_preview[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": numeric_preview[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": numeric_preview[
            "role_count_voting_added_count"
        ],
        "candidate_phase_emitted": numeric_preview["candidate_phase_emitted"],
        "current_phase_emitted": numeric_preview["current_phase_emitted"],
        "production_behavior_change_count": numeric_preview[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": numeric_preview["semantic_drift_count"],
        "phase68_closure_status": (
            "closed_governed_phase_start_intake_numeric_overlay_and_test_index_ready"
        ),
    }
    summary["phase68_phase_start_numeric_test_index_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase68_phase_start_numeric_test_index_ready"]
        else "blocked"
    )
    return summary


def _tmp_numeric_preview_summary() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="phase68_numeric_", dir="/tmp") as tmp:
        cache_dir = Path(tmp) / "raw"
        store = RawCsvStore(cache_dir)
        store.write_observations(
            "fred",
            "ICSA",
            [
                data_sources.SeriesObservation(
                    series_id="ICSA",
                    date="2026-01-03",
                    value="230000",
                ),
                data_sources.SeriesObservation(
                    series_id="ICSA",
                    date="2026-06-27",
                    value="245000",
                ),
            ],
        )
        return summarize_transition_timing_replay_preview(
            cache_dir=cache_dir,
            snapshot_as_of="2026-07-03",
        )


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase68_phase_start_numeric_test_index_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "phase68_phase_start_numeric_test_index_ready":
            continue
        if key.endswith("_minimum"):
            summary_key = key.removesuffix("_minimum")
            if summary.get(summary_key, 0) < value:
                return False
        elif summary.get(key) != value:
            return False
    return True
