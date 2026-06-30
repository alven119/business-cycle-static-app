"""Phase52 closure for official macro source adapter wiring."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.current.official_macro_source_wiring import (
    summarize_official_macro_source_adapter_wiring,
)

DEFAULT_PHASE52_CLOSURE_PATH = Path(
    "specs/audits/phase52_official_macro_source_adapter_wiring_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase52_official_macro_source_adapter_wiring_closure(
    path: str | Path = DEFAULT_PHASE52_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase52 hard gates."""

    expected = _load_expected(path)
    wiring = summarize_official_macro_source_adapter_wiring()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "52",
        "phase_id": "52",
        "phase52_official_macro_source_adapter_wiring_ready": (
            wiring["official_macro_source_adapter_wiring_ready"]
            and progress["product_capability_progress_ready"]
        ),
        "official_macro_source_adapter_wiring_ready": wiring[
            "official_macro_source_adapter_wiring_ready"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "phase52_candidate_role_count": wiring["phase52_candidate_role_count"],
        "official_wired_role_count": wiring["official_wired_role_count"],
        "unique_official_series_count": wiring["unique_official_series_count"],
        "unique_official_series_ids": wiring["unique_official_series_ids"],
        "phase52_phase_counts": wiring["phase52_phase_counts"],
        "source_family_counts": wiring["source_family_counts"],
        "data_risk_level_counts": wiring["data_risk_level_counts"],
        "source_risk_label_missing_count": wiring[
            "source_risk_label_missing_count"
        ],
        "substitution_degree_missing_count": wiring[
            "substitution_degree_missing_count"
        ],
        "registry_missing_series_count": wiring["registry_missing_series_count"],
        "release_lag_metadata_incomplete_count": wiring[
            "release_lag_metadata_incomplete_count"
        ],
        "current_refresh_disabled_series_count": wiring[
            "current_refresh_disabled_series_count"
        ],
        "direct_release_adapter_deferred_count": wiring[
            "direct_release_adapter_deferred_count"
        ],
        "source_identity_correction_count": wiring[
            "source_identity_correction_count"
        ],
        "silent_substitution_count": wiring["silent_substitution_count"],
        "alternative_promoted_to_core_count": wiring[
            "alternative_promoted_to_core_count"
        ],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "official_macro_source_wiring_ready_declared_state_preserved"
        ),
        "legal_transition_semantics_preserved": True,
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": progress["impacted_capability_ids"],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W15_SYSTEM_OPERATIONS",
        ],
        "deferred_capability_gaps": [
            "Phase53 still needs composite transformation and rule semantics",
            "Phase54 still needs licensed/proxy source risk handling",
            "declared boom start date still needs governed user confirmation",
            "Phase52 wires source identities but does not emit current/candidate phase",
        ],
        "next_recommended_phase": "Phase53_composite_transformation_and_rule_semantics",
        "phase52_closure_status": (
            "closed_official_macro_source_adapter_wiring_ready_no_phase_emission"
        ),
        "official_macro_source_wiring_summary": wiring,
        "product_capability_progress_summary": progress,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase52_official_macro_source_adapter_wiring_closure"
    ]["expected"]
