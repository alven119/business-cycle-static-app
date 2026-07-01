from __future__ import annotations

from business_cycle.audits.low_cost_macro_source_completion import (
    build_low_cost_macro_source_completion_rows,
    summarize_low_cost_macro_source_completion,
)


def test_low_cost_macro_source_completion_passes() -> None:
    summarize_low_cost_macro_source_completion.cache_clear()
    build_low_cost_macro_source_completion_rows.cache_clear()
    summary = summarize_low_cost_macro_source_completion()

    assert summary["result"] == "passed"
    assert summary["low_cost_macro_source_completion_ready"] is True
    assert summary["remaining_phase54_role_count"] == 2
    assert summary["low_cost_path_defined_role_count"] == 2
    assert summary["user_supplied_authorized_input_contract_count"] == 2
    assert summary["supporting_proxy_only_role_count"] == 2
    assert summary["macromicro_api_candidate_count"] == 0
    assert summary["unaffordable_paid_api_candidate_count"] == 0
    assert summary["book_core_replacement_without_license_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_phase54_rows_preserve_no_silent_substitution() -> None:
    rows = {
        row["role_id"]: row for row in build_low_cost_macro_source_completion_rows()
    }

    assert set(rows) == {"growth_adp_employment", "boom_consumer_confidence"}
    adp = rows["growth_adp_employment"]
    confidence = rows["boom_consumer_confidence"]

    assert adp["direct_source_family"] == "ADP"
    assert adp["book_core_replacement_without_license_allowed"] is False
    assert adp["payems_replaces_adp"] is False
    assert adp["supporting_proxy_can_replace_book_core_count"] == 0

    assert confidence["direct_source_family"] == "Conference Board"
    assert confidence["book_core_replacement_without_license_allowed"] is False
    assert confidence["generic_sentiment_replaces_consumer_confidence"] is False
    assert confidence["supporting_proxy_can_replace_book_core_count"] == 0


def test_phase54_excludes_macromicro_paid_api() -> None:
    summary = summarize_low_cost_macro_source_completion()

    assert "財經M平方 API" in summary["excluded_source_families"]
    assert summary["macromicro_api_candidate_count"] == 0
    assert summary["unaffordable_paid_api_candidate_count"] == 0
    for row in summary["rows"]:
        source_values = [
            row["direct_source_candidate_id"],
            row["direct_source_family"],
            *[
                candidate["candidate_id"]
                for candidate in row["supporting_proxy_candidates"]
            ],
            *[
                candidate["source_family"]
                for candidate in row["supporting_proxy_candidates"]
            ],
        ]
        serialized = str(source_values).lower()
        assert "macromicro" not in serialized
        assert "財經m平方" not in serialized
