"""Real-data diagnostics for QA6 shadow aggregation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.qa6_readiness_semantics import (
    summarize_qa6_readiness_semantics,
)
from business_cycle.shadow_model.aggregation_contract import (
    load_aggregation_contract,
)
from business_cycle.shadow_model.runner import run_shadow_evidence_model
from business_cycle.shadow_model.structural_eligibility import (
    evaluate_structural_eligibility,
)


def run_shadow_aggregation_diagnostics(
    *,
    as_of: str,
    data_mode: str,
    output: str | Path | None = None,
) -> dict[str, Any]:
    """Run QA6 aggregation diagnostics without candidate selection."""

    shadow = run_shadow_evidence_model(as_of=as_of, data_mode=data_mode)
    eligibility = evaluate_structural_eligibility(shadow["role_evidence"])
    readiness = summarize_qa6_readiness_semantics()
    phase_profiles = eligibility["phase_profiles"]
    summary = {
        "phase": "QA6",
        "model_id": "book_faithful_shadow_v2_alpha2",
        "aggregation_contract_id": load_aggregation_contract()[
            "aggregation_contract_id"
        ],
        "as_of": as_of,
        "requested_data_mode": data_mode,
        "actual_data_mode": data_mode,
        "role_evidence_count": len(shadow["role_evidence"]),
        "structurally_mapped_role_count": readiness[
            "structurally_mapped_role_count"
        ],
        "evidence_evaluable_role_count": 0,
        "raw_transform_only_role_count": shadow["raw_transform_only_count"],
        "unavailable_role_count": shadow["unavailable_role_count"],
        "structurally_routable_major_group_count": readiness[
            "structurally_routable_major_group_count"
        ],
        "evidence_evaluable_major_group_count": sum(
            row["evidence_evaluable_group_count"] for row in phase_profiles
        ),
        "aggregation_eligible_major_group_count": 0,
        "aggregation_eligible_phase_count": eligibility[
            "aggregation_eligible_phase_count"
        ],
        "candidate_selection_enabled": False,
        "candidate_phase_computed": False,
        "candidate_phase": None,
        "context_prior_used": False,
        "display_hint_used": False,
        "known_label_used": False,
        "performance_metric_computed": False,
        "strict_fallback_count": shadow["strict_fallback_count"],
        "public_output_written": False,
        "phase_profiles": phase_profiles,
    }
    if output is not None:
        output_path = Path(output)
        if output_path.as_posix().startswith(("data/backtests", "public")):
            raise ValueError("QA6 diagnostics may only write to explicit non-public paths")
        output_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
    return summary
