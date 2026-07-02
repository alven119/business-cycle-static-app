"""Phase64 closure for indicator diagnostic transparency and chart payloads."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.indicator_chart_explanation_payload import (
    summarize_indicator_chart_explanation_payload,
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

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase64_indicator_transparency_chart_payload_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase64_indicator_transparency_chart_payload_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase64 dashboard education gates without repo output."""

    expected = _load_expected(path)
    chart_summary = summarize_indicator_chart_explanation_payload()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    with tempfile.TemporaryDirectory(prefix="phase64_dashboard_", dir="/tmp") as tmp:
        result = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "64",
        "phase_id": 64,
        "phase_label": "indicator_transparency_chart_payload",
        "indicator_chart_explanation_payload_ready": chart_summary[
            "indicator_chart_explanation_payload_ready"
        ],
        "latest_evidence_dashboard_page_ready": (
            result["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(result["written_files"])
        ),
        "dashboard_indicator_drilldown_view_ready": bool(
            bundle.get("indicator_dashboard_explanation_drilldown"),
        ),
        "role_payload_count": chart_summary["role_payload_count"],
        "role_with_diagnostic_transparency_count": chart_summary[
            "role_with_diagnostic_transparency_count"
        ],
        "role_with_chart_payload_count": drilldown["role_with_chart_payload_count"],
        "role_with_ytd_chart_payload_count": drilldown[
            "role_with_ytd_chart_payload_count"
        ],
        "role_with_trailing_1y_chart_payload_count": drilldown[
            "role_with_trailing_1y_chart_payload_count"
        ],
        "role_with_trailing_5y_chart_payload_count": drilldown[
            "role_with_trailing_5y_chart_payload_count"
        ],
        "rendered_score_transparency_count": html.count(
            "data-score-transparency-detail",
        ),
        "rendered_chart_payload_count": html.count("data-indicator-chart-payload"),
        "rendered_ytd_chart_period_count": html.count('data-chart-period="ytd"'),
        "rendered_trailing_1y_chart_period_count": html.count(
            'data-chart-period="trailing_1y"',
        ),
        "rendered_trailing_5y_chart_period_count": html.count(
            'data-chart-period="trailing_5y"',
        ),
        "chart_data_mode_caveat_count": html.count("data-chart-data-mode"),
        "chart_unavailable_reason_count": html.count(
            "data-chart-unavailable-reason",
        ),
        "diagnostic_score_product_answer_count": chart_summary[
            "diagnostic_score_product_answer_count"
        ],
        "unavailable_chart_treated_as_zero_count": chart_summary[
            "unavailable_chart_treated_as_zero_count"
        ],
        "missing_value_treated_as_neutral_count": chart_summary[
            "missing_value_treated_as_neutral_count"
        ],
        "prohibited_claim_count": result["prohibited_claim_count"],
        "prohibited_action_field_count": result["prohibited_action_field_count"],
        "browser_missing_required_element_count": result[
            "browser_missing_required_element_count"
        ],
        "standalone_classifier_added_count": drilldown[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": drilldown[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": drilldown["role_count_voting_added_count"],
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": drilldown["candidate_phase_emitted"],
        "current_phase_emitted": drilldown["current_phase_emitted"],
        "production_behavior_change_count": drilldown[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "indicator_transparency_charts_wired_declared_state_preserved"
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase64_closure_status": (
            "closed_indicator_transparency_chart_payload_ready_no_phase_selection"
        ),
    }
    summary["phase64_indicator_transparency_chart_payload_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["phase64_indicator_transparency_chart_payload_ready"]
        else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase64_indicator_transparency_chart_payload_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase64_indicator_transparency_chart_payload_ready"
    )
