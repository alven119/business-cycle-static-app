"""QA11 retrospective observation-only diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.audits.book_core_forward_data_gaps import (
    summarize_book_core_forward_data_gaps,
)
from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)


def run_shadow_role_observation_diagnostic(
    *,
    as_of: str,
    data_mode: str,
    point_in_time_cache_dir: str | Path | None = None,
    output: str | Path | None = None,
) -> dict[str, Any]:
    gaps = summarize_book_core_forward_data_gaps()
    groups = summarize_major_group_observation_coverage()
    observable = gaps["runtime_observable_role_count"]
    unavailable = gaps["role_count"] - observable
    output_count = observable if data_mode == "revised" else 0
    abstention_count = observable - output_count
    summary = {
        "phase": "QA11",
        "as_of": as_of,
        "requested_data_mode": data_mode,
        "actual_data_mode": data_mode,
        "point_in_time_cache_dir_used": bool(point_in_time_cache_dir),
        "role_count": gaps["role_count"],
        "runtime_observable_role_count": observable,
        "observation_output_count": output_count,
        "phase_evidence_output_count": 0,
        "abstention_count": abstention_count,
        "unavailable_count": unavailable,
        "observation_ready_major_group_count": groups[
            "observation_ready_major_group_count"
        ],
        "phase_evidence_evaluable_major_group_count": groups[
            "phase_evidence_evaluable_major_group_count"
        ],
        "candidate_input_complete_major_group_count": groups[
            "candidate_input_complete_major_group_count"
        ],
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "expected_label_used": False,
        "accuracy_metric_computed": False,
        "performance_metric_computed": False,
        "context_prior_used": False,
        "strict_fallback_count": 0,
    }
    if output:
        Path(output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def summarize_retrospective_observation_diagnostics() -> dict[str, Any]:
    diagnostics = {
        "2000_strict": run_shadow_role_observation_diagnostic(
            as_of="2000-03-31",
            data_mode="vintage_as_of",
        ),
        "2008_strict": run_shadow_role_observation_diagnostic(
            as_of="2008-09-30",
            data_mode="vintage_as_of",
        ),
        "2019_strict": run_shadow_role_observation_diagnostic(
            as_of="2019-12-31",
            data_mode="vintage_as_of",
        ),
        "2019_revised": run_shadow_role_observation_diagnostic(
            as_of="2019-12-31",
            data_mode="revised",
        ),
    }
    safe = all(
        row["candidate_selection_enabled"] is False
        and row["candidate_phase_emitted"] is False
        and row["expected_label_used"] is False
        and row["accuracy_metric_computed"] is False
        and row["performance_metric_computed"] is False
        and row["context_prior_used"] is False
        and row["strict_fallback_count"] == 0
        for row in diagnostics.values()
    )
    return {
        "phase": "QA11",
        "retrospective_observation_diagnostics_ready": safe,
        "diagnostics": diagnostics,
    }

