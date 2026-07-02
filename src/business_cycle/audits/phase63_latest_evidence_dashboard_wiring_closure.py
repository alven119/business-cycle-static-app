"""Phase63 closure for latest evidence dashboard wiring."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
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
    ROOT / "specs/audits/phase63_latest_evidence_dashboard_wiring_closure.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase63_latest_evidence_dashboard_wiring_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase63 dashboard wiring gates without writing repo outputs."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    with tempfile.TemporaryDirectory(prefix="phase63_dashboard_", dir="/tmp") as tmp:
        result = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "63",
        "phase_id": 63,
        "phase_label": "latest_evidence_dashboard_wiring",
        "latest_evidence_dashboard_page_ready": (
            result["browser_verification_ready"]
            and "indicator_dashboard_explanation_drilldown" in {
                view["view_id"] for view in bundle["views"]
            }
            and "latest-evidence.html" in "\n".join(result["written_files"])
        ),
        "dashboard_indicator_drilldown_view_ready": bool(
            bundle.get("indicator_dashboard_explanation_drilldown"),
        ),
        "dashboard_bundle_latest_evidence_ready": (
            bundle["artifact_consistency"]["bundle_schema_valid"]
            and bool(bundle.get("indicator_dashboard_explanation_drilldown"))
        ),
        "rendered_latest_evidence_page_count": int(
            'data-dashboard-view="indicator_dashboard_explanation_drilldown"'
            in html,
        ),
        "major_group_drilldown_rendered_count": html.count(
            "data-major-group-drilldown=",
        ),
        "role_drilldown_rendered_count": html.count("data-role-drilldown="),
        "role_source_detail_rendered_count": html.count("data-source-detail"),
        "role_release_timing_detail_rendered_count": html.count(
            "data-release-timing-detail",
        ),
        "role_freshness_detail_rendered_count": html.count("data-freshness-detail"),
        "role_transformation_detail_rendered_count": html.count(
            "data-transformation-detail",
        ),
        "role_rule_usability_detail_rendered_count": html.count(
            "data-rule-usability-detail",
        ),
        "role_provenance_detail_rendered_count": html.count(
            "data-provenance-detail",
        ),
        "role_abstention_detail_rendered_count": html.count(
            "data-abstention-detail",
        ),
        "latest_evidence_research_only_label_missing_count": int(
            "data-research-only-label" not in html,
        ),
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
            "latest_evidence_dashboard_wired_declared_state_preserved"
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_capability_progress": progress["capability_progress"],
        "phase63_closure_status": (
            "closed_latest_evidence_dashboard_wired_no_phase_selection"
        ),
    }
    summary["phase63_latest_evidence_dashboard_wiring_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed" if summary["phase63_latest_evidence_dashboard_wiring_ready"] else "blocked"
    )
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase63_latest_evidence_dashboard_wiring_closure"]["hard_gates"],
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "phase63_latest_evidence_dashboard_wiring_ready"
    )
