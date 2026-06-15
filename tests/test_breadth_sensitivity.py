from __future__ import annotations

from pathlib import Path

from business_cycle.backtests import (
    build_breadth_sensitivity_summary,
    load_breadth_sensitivity_matrix,
    validate_breadth_sensitivity_matrix,
)

MATRIX_PATH = Path("specs/backtests/breadth_sensitivity_matrix.yaml")


def test_breadth_sensitivity_matrix_can_be_loaded() -> None:
    matrix = load_breadth_sensitivity_matrix(MATRIX_PATH)

    assert matrix.version == 1
    assert matrix.status == "draft"
    assert len(matrix.variants) >= 5
    validate_breadth_sensitivity_matrix(matrix)


def test_breadth_sensitivity_matrix_variant_ids_unique_and_targets_present() -> None:
    matrix = load_breadth_sensitivity_matrix(MATRIX_PATH)
    variant_ids = [variant["variant_id"] for variant in matrix.variants]
    target_ids = {target["target_id"] for target in matrix.acceptance_targets}

    assert len(variant_ids) == len(set(variant_ids))
    assert "block_covid_2019_false_recession" in target_ids
    assert "keep_dotcom_in_window" in target_ids
    assert "keep_gfc_in_window" in target_ids
    assert "avoid_out_of_sample_false_recession" in target_ids


def test_breadth_sensitivity_summary_pass_criteria() -> None:
    matrix = load_breadth_sensitivity_matrix(MATRIX_PATH)
    summary = build_breadth_sensitivity_summary(
        experiment_id="test",
        matrix=matrix,
        variant_results=[
            variant_result(
                "v_pass",
                covid_early=False,
                dotcom_status="in_window",
                gfc_status="in_window",
                euro_recession=None,
                late_recession=None,
            ),
            variant_result(
                "v_fail",
                covid_early=True,
                dotcom_status="in_window",
                gfc_status="in_window",
                euro_recession=None,
                late_recession=None,
            ),
        ],
    )

    assert summary["aggregate"]["variant_pass_count"] == 1
    assert summary["aggregate"]["variant_fail_count"] == 1
    assert summary["recommended_variants"] == ["v_pass"]
    assert summary["aggregate"]["variants_blocking_covid_false_recession"] == ["v_pass"]
    assert summary["aggregate"]["variants_preserving_dotcom_and_gfc"] == ["v_pass", "v_fail"]


def test_breadth_sensitivity_no_recommended_variants_notes_phase_7f() -> None:
    matrix = load_breadth_sensitivity_matrix(MATRIX_PATH)
    summary = build_breadth_sensitivity_summary(
        experiment_id="test",
        matrix=matrix,
        variant_results=[
            variant_result(
                "v_fail",
                covid_early=True,
                dotcom_status="in_window",
                gfc_status="in_window",
                euro_recession=None,
                late_recession=None,
            )
        ],
    )

    assert summary["recommended_variants"] == []
    assert any("Phase 7F" in note for note in summary["notes_zh"])
    assert any("修訂後歷史資料" in caveat for caveat in summary["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in summary["caveats_zh"])


def variant_result(
    variant_id: str,
    *,
    covid_early: bool,
    dotcom_status: str,
    gfc_status: str,
    euro_recession: str | None,
    late_recession: str | None,
) -> dict:
    return {
        "variant": {"variant_id": variant_id, "display_name_zh": variant_id},
        "summary": {"aggregate": {"scenario_with_failures_count": 0}},
        "review": {
            "scenarios": [
                {
                    "scenario_id": "dotcom_bubble",
                    "first_recession_current_as_of": "2001-01-31",
                    "recession_timing_status": dotcom_status,
                },
                {
                    "scenario_id": "global_financial_crisis",
                    "first_recession_current_as_of": "2008-10-31",
                    "recession_timing_status": gfc_status,
                },
                {
                    "scenario_id": "euro_debt_slowdown",
                    "first_recession_current_as_of": euro_recession,
                },
                {
                    "scenario_id": "late_cycle_2018",
                    "first_recession_current_as_of": late_recession,
                },
            ],
            "aggregate": {
                "pass_count": 4,
                "fail_count": 1 if covid_early else 0,
                "early_false_recession_count": 1 if covid_early else 0,
            },
        },
        "covid_diagnostic": {
            "first_recession_current_as_of": "2019-02-28" if covid_early else None,
            "early_false_recession": covid_early,
        },
    }
