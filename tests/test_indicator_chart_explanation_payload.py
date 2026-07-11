from __future__ import annotations

from pathlib import Path

from business_cycle.audits.indicator_transformation_learning_semantics import (
    summarize_indicator_transformation_learning_semantics,
)
from business_cycle.data_sources import SeriesObservation
from business_cycle.render.indicator_chart_explanation_payload import (
    build_indicator_chart_explanation_payload,
    build_indicator_chart_explanation_view_model,
    summarize_indicator_chart_explanation_payload,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.render.indicator_learning_semantics import (
    transform_observations_for_display,
)
from business_cycle.render.technology_manufacturing_cycle import (
    build_technology_manufacturing_cycle_view,
)
from business_cycle.storage.nas_technology_manufacturing_import import (
    summarize_technology_manufacturing_contract,
)
from business_cycle.storage.raw_store import RawCsvStore


def test_phase64_indicator_chart_payload_passes_without_cache() -> None:
    summary = summarize_indicator_chart_explanation_payload()

    assert summary["result"] == "passed"
    assert summary["indicator_chart_explanation_payload_ready"] is True
    assert summary["role_payload_count"] == 39
    assert summary["role_with_diagnostic_transparency_count"] == 39
    assert summary["role_with_score_interpretation_count"] == 39
    assert summary["role_with_ytd_chart_payload_count"] == 39
    assert summary["role_with_trailing_1y_chart_payload_count"] == 39
    assert summary["role_with_trailing_5y_chart_payload_count"] == 39
    assert summary["chart_period_count"] == 3
    assert summary["chart_unavailable_policy_count"] == 39
    assert summary["chart_available_role_count"] == 0
    assert summary["diagnostic_score_product_answer_count"] == 0
    assert summary["prohibited_output_field_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False


def test_phase64_chart_payload_uses_tmp_cache_when_supplied(tmp_path: Path) -> None:
    first_card = next(
        card
        for card in build_indicator_detail_source_risk_value_cards()
        if card["official_series_ids"]
    )
    series_id = first_card["official_series_ids"][0]
    store = RawCsvStore(tmp_path / "cache")
    store.write_observations(
        "fred",
        series_id,
        [
            SeriesObservation(series_id=series_id, date="2021-07-05", value="1.0"),
            SeriesObservation(series_id=series_id, date="2025-08-15", value="2.0"),
            SeriesObservation(series_id=series_id, date="2026-01-31", value="3.0"),
            SeriesObservation(series_id=series_id, date="2026-06-30", value="4.0"),
        ],
    )

    artifact = build_indicator_chart_explanation_payload(
        cache_dir=tmp_path / "cache",
        snapshot_as_of="2026-07-02",
    )
    role_payload = next(
        payload for payload in artifact["role_payloads"] if payload["role_id"] == first_card["role_id"]
    )
    periods = {
        period["period_id"]: period
        for series in role_payload["chart_payload_detail"]["series_charts"]
        if series["series_id"] == series_id
        for period in series["periods"]
    }

    assert artifact["chart_available_role_count"] >= 1
    assert role_payload["chart_payload_detail"]["chart_available"] is True
    assert periods["ytd"]["chart_status"] == "available"
    assert periods["trailing_1y"]["chart_status"] == "available"
    assert periods["trailing_5y"]["chart_status"] == "available"
    assert periods["ytd"]["point_count"] == 2
    assert role_payload["diagnostic_transparency_detail"]["method_recipe_visible"] is True
    assert role_payload["diagnostic_transparency_detail"]["computed_diagnostic_value_present"] is False
    assert role_payload["diagnostic_transparency_detail"]["frequency_handling_zh"]
    assert role_payload["diagnostic_transparency_detail"]["missing_value_handling_zh"]
    assert role_payload["diagnostic_transparency_detail"]["directionality_detail"]
    interpretation = role_payload["diagnostic_transparency_detail"][
        "score_interpretation_zh"
    ]
    assert "分數越高" in interpretation["high_score_zh"]
    assert "分數越低" in interpretation["low_score_zh"]
    assert "分數接近 0" in interpretation["neutral_score_zh"]
    assert role_payload["diagnostic_transparency_detail"]["confidence_reduce_when"]
    assert role_payload["diagnostic_transparency_detail"]["pseudo_code_zh"]
    assert "未使用歷史答案" in role_payload["diagnostic_transparency_detail"][
        "method_assignment_basis_zh"
    ]


def test_phase64_chart_payload_view_model_is_research_only() -> None:
    view_model = build_indicator_chart_explanation_view_model()

    assert view_model["view_id"] == "indicator_chart_explanation_payload"
    assert view_model["research_only"] is True
    assert view_model["role_payload_count"] == 39
    assert view_model["candidate_phase_emitted"] is False
    assert view_model["current_phase_emitted"] is False
    assert view_model["phase_rank_or_score_added_count"] == 0


def test_phase121_display_transformations_are_causal_role_specific_and_audited() -> None:
    audit = summarize_indicator_transformation_learning_semantics()
    yoy_rows, yoy_semantics = transform_observations_for_display(
        [
            {"observation_date": "2025-06-01", "value_numeric": "100"},
            {"observation_date": "2026-06-01", "value_numeric": "110"},
        ],
        role_id="recovery_durable_goods_new_orders",
    )
    moving_rows, moving_semantics = transform_observations_for_display(
        [
            {"observation_date": "2026-06-10", "value_numeric": "100"},
            {"observation_date": "2026-06-17", "value_numeric": "110"},
            {"observation_date": "2026-06-24", "value_numeric": "120"},
            {"observation_date": "2026-07-01", "value_numeric": "130"},
        ],
        role_id="recovery_initial_jobless_claims",
    )

    assert audit["result"] == "passed"
    assert audit["audited_role_count"] == 39
    assert audit["raw_level_mismatch_before_count"] == 31
    assert audit["raw_level_mismatch_after_count"] == 0
    assert audit["role_without_learning_semantics_count"] == 0
    assert yoy_rows[-1]["value_numeric"] == "10"
    assert yoy_rows[-1]["source_value_numeric"] == "110"
    assert yoy_rows[-1]["comparison_observation_date"] == "2025-06-01"
    assert yoy_semantics["transform_label_zh"] == "年增率"
    assert moving_rows[-1]["value_numeric"] == "115"
    assert moving_semantics["transform_label_zh"] == "4 期移動平均"
    assert all(row["phase_support_allowed"] is False for row in yoy_rows + moving_rows)


def test_phase122_technology_cycle_uses_official_yoy_and_preserves_boundaries() -> None:
    rows = []
    for year, base in ((2024, 100), (2025, 110), (2026, 121)):
        for month in range(1, 7):
            rows.append({
                "observation_date": f"{year}-{month:02d}-01",
                "value_numeric": str(base + month),
                "source_artifact_id": f"artifact-{year}",
                "provenance_hash": f"hash-{year}-{month}",
            })
    view = build_technology_manufacturing_cycle_view({
        "snapshot_as_of": "2026-07-11",
        "technology_series_observations": {
            series_id: rows
            for series_id in (
                "DGORDER",
                "A34SNO",
                "A34HNO",
                "TW_MOEA_ICT_EXPORT_ORDERS",
                "TW_MOEA_ELECTRONICS_EXPORT_ORDERS",
            )
        },
    })
    contract = summarize_technology_manufacturing_contract()

    assert contract["result"] == "passed"
    assert contract["newly_wired_source_count"] == 4
    assert view["series_count"] == 5
    assert view["available_series_count"] == 5
    assert view["us_series_count"] == 3
    assert view["taiwan_series_count"] == 2
    assert view["book_core_substitution_allowed"] is False
    assert view["phase_confirmation_allowed"] is False
    assert view["candidate_phase_emitted"] is False
    assert view["current_phase_emitted"] is False
    assert all(card["raw_source_value_preserved"] for card in view["series_cards"])
    assert all(card["phase_support_allowed"] is False for card in view["series_cards"])
    assert all(
        card["latest_yoy_observation"]["comparison_observation_date"].startswith("2025-")
        for card in view["series_cards"]
    )
    electronic = next(card for card in view["series_cards"] if card["series_id"] == "A34HNO")
    assert "不等於半導體" in electronic["definition_risk_zh"]
