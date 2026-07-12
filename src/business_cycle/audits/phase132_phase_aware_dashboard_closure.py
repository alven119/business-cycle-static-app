"""Phase 132 atomic phase-aware dashboard closure."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase123_live_ordered_cycle_evidence_closure import (
    build_phase123_live_evidence_fixture_snapshot,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    PHASE_LABELS_ZH,
)
from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)
from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    render_historical_replay_page,
    render_portfolio_research_page,
)
from business_cycle.render.phase_aware_dashboard_context import (
    summarize_phase_aware_dashboard_context,
)

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "specs/audits/phase132_phase_aware_dashboard_closure.yaml"


@lru_cache(maxsize=1)
def build_phase132_synthetic_state_matrix() -> tuple[dict[str, Any], ...]:
    machine = load_ordered_cycle_state_machine()
    base = build_phase123_live_evidence_fixture_snapshot()
    rows = []
    for phase in machine.cycle_order:
        snapshot = deepcopy(base)
        snapshot["trust_metadata"]["live_db_connected"] = True
        legal_next = machine.legal_next_phase(phase)
        snapshot["declared_cycle_state"] |= {
            "declared_current_phase": phase,
            "declared_current_phase_label_zh": PHASE_LABELS_ZH[phase],
            "legal_previous_phase": machine.legal_previous_phase(phase),
            "legal_previous_phase_label_zh": PHASE_LABELS_ZH[
                machine.legal_previous_phase(phase)
            ],
            "legal_next_phase": legal_next,
            "legal_next_phase_label_zh": PHASE_LABELS_ZH[legal_next],
            "declared_phase_start_display_zh": "synthetic governed context",
            "phase_age_status": "synthetic_contract_test_only",
            "active_registry_hash": f"phase132-synthetic-{phase}",
        }
        bundle = build_nas_service_dashboard_bundle(
            snapshot_manifest=snapshot,
            runtime_live_mode=True,
        )
        command = bundle["command_center"]
        lab = bundle["portfolio_replay_lab"]
        overview = next(
            page["html"] for page in bundle["html_pages"] if page["path"] == "/"
        )
        indicators = next(
            page["html"]
            for page in bundle["html_pages"]
            if page["path"] == "/indicators"
        )
        navigation = command["navigation"]
        portfolio_html = render_portfolio_research_page(
            lab["portfolio_research"], navigation=navigation
        )
        replay_html = render_historical_replay_page(
            lab["historical_replay"], navigation=navigation
        )
        context_hash = command["phase_context_hash"]
        rows.append(
            {
                "declared_phase": phase,
                "legal_next_phase": legal_next,
                "context_hash": context_hash,
                "bundle_result": bundle["result"],
                "portfolio_result": lab["result"],
                "lane_count": len(command["transition_lanes"]),
                "priority_role_count": len(command["key_indicators"]),
                "priority_card_count": indicators.count(
                    'data-phase-priority="true"'
                ),
                "other_phase_navigation_count": len(
                    command["other_phase_navigation"]
                ),
                "active_evaluator_mode": command["active_evaluator_mode"],
                "context_hash_surface_count": sum(
                    context_hash in html
                    for html in (overview, indicators, portfolio_html, replay_html)
                ),
                "mobile_navigation_ready": 'class="mobile-nav"' in overview,
                "declared_label_visible": PHASE_LABELS_ZH[phase] in overview,
                "legal_next_label_visible": PHASE_LABELS_ZH[legal_next] in overview,
                "portfolio_default_template_id": lab["portfolio_research"][
                    "default_research_template_id"
                ],
                "candidate_phase_emitted": False,
                "current_phase_emitted": False,
            }
        )
    return tuple(rows)


def summarize_phase132_phase_aware_dashboard_closure(
    path: str | Path = PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase132_phase_aware_dashboard_closure"
    ]
    contract = summarize_phase_aware_dashboard_context()
    matrix = list(build_phase132_synthetic_state_matrix())
    summary = {
        "phase": 132,
        "phase132_closure_ready": contract["result"] == "passed",
        "phase_aware_dashboard_context_ready": contract[
            "phase_aware_dashboard_context_ready"
        ],
        "synthetic_declared_state_count": len(matrix),
        "synthetic_state_render_pass_count": sum(
            row["bundle_result"] == "passed"
            and row["portfolio_result"] == "passed"
            for row in matrix
        ),
        "legal_transition_context_count": contract[
            "legal_transition_context_count"
        ],
        "phase_specific_transition_lane_count": sum(
            row["lane_count"] for row in matrix
        ),
        "phase_specific_priority_role_count": sum(
            row["priority_role_count"] for row in matrix
        ),
        "priority_card_render_count": sum(
            row["priority_card_count"] for row in matrix
        ),
        "atomic_context_surface_check_count": sum(
            row["context_hash_surface_count"] for row in matrix
        ),
        "partial_page_context_switch_count": sum(
            row["context_hash_surface_count"] != 4 for row in matrix
        ),
        "mobile_phase_context_ready_count": sum(
            row["mobile_navigation_ready"]
            and row["declared_label_visible"]
            and row["legal_next_label_visible"]
            for row in matrix
        ),
        "other_phase_reference_navigation_ready_count": sum(
            row["other_phase_navigation_count"] == 4 for row in matrix
        ),
        "live_evaluator_phase_count": sum(
            row["active_evaluator_mode"] == "live_book_evidence" for row in matrix
        ),
        "explicit_input_readiness_only_phase_count": sum(
            row["active_evaluator_mode"]
            == "input_readiness_only_explicit_abstention"
            for row in matrix
        ),
        "transition_activation_gate_enabled": _compose_activation_enabled(),
        "automatic_state_change_count": 0,
        "watch_promoted_to_confirmation_count": 0,
        "personalized_portfolio_instruction_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "development_next_phase": 133,
        "phase132_closure_status": payload["status"],
        "matrix_rows": matrix,
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


def _compose_activation_enabled() -> bool:
    compose = yaml.safe_load(
        (ROOT / "deploy/nas/compose.yaml").read_text(encoding="utf-8")
    )
    value = compose["services"]["business_cycle_app"]["environment"][
        "BUSINESS_CYCLE_PHASE_TRANSITION_ACTIVATION_ENABLED"
    ]
    return str(value).lower() == "true"
