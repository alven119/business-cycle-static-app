"""QA7 real-data shadow candidate diagnostics that must abstain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.evidence_evaluability import summarize_evidence_evaluability
from business_cycle.shadow_model.candidate_selection import (
    load_shadow_candidate_selection_contract,
)
from business_cycle.shadow_model.runner import run_shadow_evidence_model
from business_cycle.shadow_model.structural_eligibility import (
    evaluate_structural_eligibility,
)


def run_shadow_candidate_diagnostics(
    *,
    as_of: str,
    data_mode: str,
    output: str | Path | None = None,
    point_in_time_cache_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Run QA7 real-data candidate diagnostics with selection disabled."""

    _ = point_in_time_cache_dir
    shadow = run_shadow_evidence_model(as_of=as_of, data_mode=data_mode)
    eligibility = evaluate_structural_eligibility(shadow["role_evidence"])
    evaluability = summarize_evidence_evaluability()
    contract = load_shadow_candidate_selection_contract()
    summary = {
        "phase": "QA7",
        "model_id": "book_faithful_shadow_v2_alpha3",
        "rule_registry_version": "shadow_evidence_rules_v1",
        "candidate_selection_contract_id": contract[
            "candidate_selection_contract_id"
        ],
        "as_of": as_of,
        "requested_data_mode": data_mode,
        "actual_data_mode": data_mode,
        "role_count": evaluability["role_count"],
        "evidence_evaluable_role_count": evaluability["evaluable_role_count"],
        "raw_transform_only_role_count": shadow["raw_transform_only_count"],
        "unavailable_role_count": shadow["unavailable_role_count"],
        "aggregation_eligible_phase_count": eligibility[
            "aggregation_eligible_phase_count"
        ],
        "real_data_candidate_selection_enabled": False,
        "candidate_selection_status": "abstained_incomplete_evidence",
        "candidate_phase": None,
        "abstention_reasons": [
            "real_data_candidate_selection_disabled",
            "evidence_not_evaluable",
        ],
        "context_prior_used": False,
        "display_hint_used": False,
        "known_label_used": False,
        "performance_metric_computed": False,
        "public_output_written": False,
        "strict_fallback_count": shadow["strict_fallback_count"],
    }
    if output is not None:
        output_path = Path(output)
        if output_path.as_posix().startswith(("data/backtests", "public")):
            raise ValueError("QA7 candidate diagnostics may not write public outputs")
        output_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
    return summary


def summarize_required_shadow_candidate_diagnostics() -> dict[str, dict[str, Any]]:
    """Return the four required QA7 diagnostic runs without writing files."""

    return {
        "strict_2000": run_shadow_candidate_diagnostics(
            as_of="2000-03-31", data_mode="vintage_as_of"
        ),
        "strict_2008": run_shadow_candidate_diagnostics(
            as_of="2008-09-30", data_mode="vintage_as_of"
        ),
        "strict_2019": run_shadow_candidate_diagnostics(
            as_of="2019-12-31", data_mode="vintage_as_of"
        ),
        "revised_2019": run_shadow_candidate_diagnostics(
            as_of="2019-12-31", data_mode="revised"
        ),
    }
