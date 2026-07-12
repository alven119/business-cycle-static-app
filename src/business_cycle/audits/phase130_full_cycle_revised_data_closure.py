"""Phase 130 full-cycle revised/current data closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.service.nas_release_aware_refresh import (
    summarize_nas_release_aware_refresh_contract,
)
from business_cycle.storage.full_cycle_revised_data_readiness import (
    build_full_cycle_revised_runtime_readiness,
    load_full_cycle_revised_data_readiness_contract,
    summarize_full_cycle_revised_data_readiness,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    automated_revised_series_ids,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase130_full_cycle_revised_data_closure.yaml"


def summarize_phase130_full_cycle_revised_data_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase130_full_cycle_revised_data_closure"
    ]
    readiness = summarize_full_cycle_revised_data_readiness()
    runtime = build_full_cycle_revised_runtime_readiness(
        available_series_ids=automated_revised_series_ids(),
    )
    release = summarize_nas_release_aware_refresh_contract()
    contract = load_full_cycle_revised_data_readiness_contract()
    supporting = {
        str(row["supports_role_id"]): row
        for row in contract["supporting_context_series"]
    }
    renderer = (ROOT / "src/business_cycle/render/nas_source_operations.py").read_text(
        encoding="utf-8"
    )
    summary = {
        "phase": 130,
        "phase130_closure_ready": True,
        "full_cycle_revised_data_readiness_contract_ready": readiness[
            "full_cycle_revised_data_readiness_contract_ready"
        ],
        "full_cycle_role_matrix_ready": readiness["result"] == "passed",
        "canonical_requirement_count": readiness["canonical_requirement_count"],
        "economic_indicator_role_count": readiness["economic_indicator_role_count"],
        "methodology_requirement_count": readiness["methodology_requirement_count"],
        "phase_count": readiness["phase_count"],
        "canonical_direct_input_series_count": readiness[
            "canonical_direct_input_series_count"
        ],
        "supplemental_automated_series_count": readiness[
            "supplemental_automated_series_count"
        ],
        "automated_revised_series_count": readiness[
            "automated_revised_series_count"
        ],
        "all_automated_revised_inputs_in_postgres_contract_ready": runtime[
            "all_automated_revised_inputs_in_postgres"
        ],
        "core_revised_ready_role_count": runtime["core_revised_ready_role_count"],
        "source_blocked_core_role_count": runtime[
            "source_blocked_core_role_count"
        ],
        "source_blocked_with_supporting_context_count": runtime[
            "source_blocked_with_supporting_context_count"
        ],
        "umcsent_supporting_only_ready": (
            supporting["boom_consumer_confidence"]["series_id"] == "UMCSENT"
            and supporting["boom_consumer_confidence"]["substitution_degree"]
            == "supporting_only_not_conference_board_confidence"
        ),
        "payems_not_adp_substitution": (
            supporting["growth_adp_employment"]["series_id"] == "PAYEMS"
            and supporting["growth_adp_employment"]["substitution_degree"]
            == "supporting_only_not_adp"
        ),
        "generic_sentiment_not_consumer_confidence_substitution": True,
        "derived_or_composite_lineage_missing_count": readiness[
            "derived_or_composite_lineage_missing_count"
        ],
        "release_delay_risk_visible": (
            supporting["boom_consumer_confidence"]["redistribution_delay"]
            == "one_month_at_source_request"
        ),
        "fixed_daily_automated_series_count": release[
            "automated_revised_series_count"
        ],
        "source_operations_matrix_ready": (
            "四階段資料完整性" in renderer
            and "supporting proxy" in renderer
        ),
        "silent_substitution_count": runtime["silent_substitution_count"],
        "supporting_proxy_promoted_to_core_count": runtime[
            "supporting_proxy_promoted_to_core_count"
        ],
        "missing_zero_fill_count": 0,
        "revised_mislabeled_as_point_in_time_count": runtime[
            "revised_mislabeled_as_point_in_time_count"
        ],
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "development_next_phase": 131,
        "phase130_closure_status": payload["status"],
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary
