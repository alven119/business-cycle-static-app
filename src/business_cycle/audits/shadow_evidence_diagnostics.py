"""QA8 retrospective evidence diagnostics with candidate output disabled."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.evidence_evaluability import (
    summarize_shadow_role_readiness_recalculation,
)
from business_cycle.shadow_model.evidence_evaluators import (
    build_book_explicit_evaluator_registry,
    evaluate_book_explicit_rule,
)
from business_cycle.shadow_model.runner import run_shadow_evidence_model


def run_shadow_evidence_diagnostics(
    *,
    as_of: str,
    data_mode: str,
    output: str | Path | None = None,
    point_in_time_cache_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Run QA8 evidence diagnostics without emitting candidate phases."""

    _ = point_in_time_cache_dir
    shadow = run_shadow_evidence_model(as_of=as_of, data_mode=data_mode)
    readiness = summarize_shadow_role_readiness_recalculation()
    evaluator_results = [
        evaluate_book_explicit_rule(
            role_id=row["role_id"],
            observations=[],
            as_of=as_of,
            data_mode=data_mode,
        )
        for row in build_book_explicit_evaluator_registry()
        if row["implemented"]
    ]
    status_counts = {
        "matched": sum(
            row["rule_match_status"] == "matched" for row in evaluator_results
        ),
        "not_matched": sum(
            row["rule_match_status"] == "not_matched" for row in evaluator_results
        ),
        "indeterminate": sum(
            row["rule_match_status"] == "indeterminate" for row in evaluator_results
        ),
        "abstained": sum(
            row["rule_match_status"] == "abstained" for row in evaluator_results
        ),
    }
    summary = {
        "phase": "QA8",
        "model_id": "book_faithful_shadow_v2_alpha4",
        "as_of": as_of,
        "requested_data_mode": data_mode,
        "actual_data_mode": data_mode,
        "role_count": readiness["role_count"]
        if "role_count" in readiness
        else shadow["role_evidence_count"],
        "implemented_evaluator_role_count": readiness[
            "implemented_evaluator_role_count"
        ],
        "rule_match_evaluable_role_count": readiness[
            "rule_match_evaluable_role_count"
        ],
        "evidence_evaluable_role_count": readiness["evidence_evaluable_role_count"],
        "candidate_selection_eligible_role_count": readiness[
            "candidate_selection_eligible_role_count"
        ],
        "matched_rule_count": status_counts["matched"],
        "not_matched_rule_count": status_counts["not_matched"],
        "indeterminate_rule_count": status_counts["indeterminate"],
        "abstained_rule_count": status_counts["abstained"],
        "raw_transform_only_role_count": shadow["raw_transform_only_count"],
        "unavailable_role_count": shadow["unavailable_role_count"],
        "retrospective_candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "known_label_used": False,
        "performance_metric_computed": False,
        "context_prior_used": False,
        "strict_fallback_count": shadow["strict_fallback_count"],
        "rule_evaluations": evaluator_results,
    }
    if output is not None:
        output_path = Path(output)
        if output_path.as_posix().startswith(("data/backtests", "public")):
            raise ValueError("QA8 evidence diagnostics may not write public outputs")
        output_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
    return summary


def summarize_required_shadow_evidence_diagnostics() -> dict[str, dict[str, Any]]:
    """Return the four required QA8 diagnostic runs without writing files."""

    return {
        "strict_2000": run_shadow_evidence_diagnostics(
            as_of="2000-03-31", data_mode="vintage_as_of"
        ),
        "strict_2008": run_shadow_evidence_diagnostics(
            as_of="2008-09-30", data_mode="vintage_as_of"
        ),
        "strict_2019": run_shadow_evidence_diagnostics(
            as_of="2019-12-31", data_mode="vintage_as_of"
        ),
        "revised_2019": run_shadow_evidence_diagnostics(
            as_of="2019-12-31", data_mode="revised"
        ),
    }
