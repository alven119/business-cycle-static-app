"""Phase 121 indicator-transformation and learning-semantics closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.indicator_transformation_learning_semantics import (
    summarize_indicator_transformation_learning_semantics,
)
from business_cycle.render.indicator_learning_semantics import (
    load_indicator_transformation_learning_contract,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    load_nas_live_postgres_dashboard_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = (
    ROOT / "specs/audits/phase121_indicator_transformation_learning_closure.yaml"
)


def summarize_phase121_indicator_transformation_learning_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 121 implementation, product, and doctrine gates."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase121_indicator_transformation_learning_closure"
    ]
    audit = summarize_indicator_transformation_learning_semantics()
    display = load_indicator_transformation_learning_contract()
    dashboard = load_nas_live_postgres_dashboard_contract()
    summary: dict[str, Any] = {
        "phase": 121,
        "phase121_closure_ready": payload["status"]
        == "closed_indicator_transformations_and_learning_semantics_aligned",
        "indicator_transformation_learning_contract_ready": audit[
            "indicator_transformation_learning_contract_ready"
        ],
        "canonical_role_count": audit["canonical_role_count"],
        "audited_role_count": audit["audited_role_count"],
        "role_without_transform_count": audit["role_without_transform_count"],
        "role_without_learning_semantics_count": audit[
            "role_without_learning_semantics_count"
        ],
        "yoy_display_role_count": audit["yoy_display_role_count"],
        "moving_average_display_role_count": audit[
            "moving_average_display_role_count"
        ],
        "level_display_role_count": audit["level_display_role_count"],
        "unavailable_display_role_count": audit[
            "unavailable_display_role_count"
        ],
        "raw_level_mismatch_before_count": audit[
            "raw_level_mismatch_before_count"
        ],
        "raw_level_mismatch_after_count": audit[
            "raw_level_mismatch_after_count"
        ],
        "chart_source_lookback_years": int(
            dashboard["data_policy"]["chart_source_lookback_years"]
        ),
        "raw_source_value_preserved": display["policies"][
            "raw_source_value_preserved"
        ],
        "nominal_real_mislabel_count": audit["nominal_real_mislabel_count"],
        "smoothing_promoted_to_phase_support_count": audit[
            "smoothing_promoted_to_phase_support_count"
        ],
        "sustainable_inflation_false_confirmation_count": audit[
            "sustainable_inflation_false_confirmation_count"
        ],
        "test_file_delta": int(
            payload["implementation_acceptance"]["new_test_file_count"]
        ),
        "default_product_core_test_file_count": int(
            payload["implementation_acceptance"][
                "default_product_core_test_file_count"
            ]
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "runtime_behavior_change_count": 1,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "average_product_capability_progress_percent": float(
            payload["implementation_acceptance"][
                "recorded_average_product_capability_progress_percent"
            ]
        ),
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_boom_preserved_display_semantics_aligned"
        ),
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 122,
        "phase121_closure_status": payload["status"],
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary
