from __future__ import annotations

from business_cycle.audits.macro_indicator_gap_alternative_sources import (
    build_macro_indicator_gap_alternative_source_rows,
    summarize_macro_indicator_gap_alternative_sources,
)


def test_macro_indicator_gap_alternatives_cover_all_current_gaps() -> None:
    rows = build_macro_indicator_gap_alternative_source_rows()
    summary = summarize_macro_indicator_gap_alternative_sources()

    assert summary["result"] == "passed"
    assert summary["macro_gap_alternative_registry_ready"] is True
    assert summary["gap_role_count"] == len(rows)
    assert summary["gap_role_count"] >= 30
    assert summary["gap_with_alternative_candidate_count"] == summary["gap_role_count"]
    assert summary["source_risk_label_missing_count"] == 0
    assert summary["substitution_degree_missing_count"] == 0
    assert summary["planned_resolution_phase_missing_count"] == 0


def test_macro_indicator_gap_alternatives_preserve_no_silent_substitution() -> None:
    summary = summarize_macro_indicator_gap_alternative_sources()

    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert summary["prohibited_output_field_count"] == 0


def test_macro_indicator_gap_alternatives_stage_proxy_roles_later() -> None:
    rows = build_macro_indicator_gap_alternative_source_rows()
    by_role = {row["role_id"]: row for row in rows}

    assert by_role["growth_adp_employment"]["planned_resolution_phase"] == "Phase54"
    assert by_role["growth_adp_employment"]["book_core_replacement_allowed"] is False
    assert by_role["boom_consumer_confidence"]["planned_resolution_phase"] == "Phase54"
    assert by_role["boom_consumer_confidence"]["book_core_replacement_allowed"] is False
    assert (
        by_role["growth_sustainable_inflation_interpretation"][
            "planned_resolution_phase"
        ]
        == "Phase53"
    )
