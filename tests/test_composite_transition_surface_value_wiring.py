from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.current.composite_transition_surface_values import (
    build_composite_transition_surface_value_rows,
    summarize_composite_transition_surface_value_wiring,
)
from business_cycle.current.current_data_refresh import (
    LIVE_OPERATOR_CONFIRMATION,
    build_current_data_refresh_manifest,
)
from business_cycle.data_sources import SeriesObservation


class FakeProvider:
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        return [
            SeriesObservation(series_id=series_id, date="2026-04-30", value="10.0"),
            SeriesObservation(series_id=series_id, date="2026-05-31", value="11.0"),
            SeriesObservation(series_id=series_id, date="2026-06-30", value="12.0"),
        ]


def test_phase53_composite_transition_surface_value_wiring_passes() -> None:
    summary = summarize_composite_transition_surface_value_wiring()

    assert summary["result"] == "passed"
    assert summary["composite_transition_surface_value_wiring_ready"] is True
    assert summary["role_count"] == 12
    assert summary["transition_surface_role_count"] == 5
    assert summary["composite_or_rule_gap_role_count"] == 7
    assert summary["source_metadata_ready_role_count"] == 12
    assert summary["value_context_visible_role_count"] == 12
    assert summary["composite_alignment_status_visible_count"] == 12
    assert summary["explicit_abstention_reason_count"] == 12
    assert summary["phase_support_added_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0


def test_phase53_preserves_source_identity_and_supporting_boundaries() -> None:
    rows = {
        row["role_id"]: row for row in build_composite_transition_surface_value_rows()
    }

    assert rows["growth_real_disposable_income_vs_consumption"][
        "official_source_series_ids"
    ] == ["DSPIC96", "PCEC96"]
    assert rows["growth_sustainable_inflation_interpretation"][
        "official_source_series_ids"
    ] == ["CPILFESL", "PCEPILFE"]
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "official_source_series_ids"
    ] == ["FEDFUNDS"]
    assert rows["growth_sustainable_inflation_interpretation"][
        "phase_support_added"
    ] is False
    assert rows["trough_policy_financial_not_sufficient_alone"][
        "transformation_semantics_status"
    ] == "supporting_policy_context_visible_not_recovery_confirmation"


def test_phase53_can_load_tmp_numeric_context_without_phase_support(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret-token")
    manifest = build_current_data_refresh_manifest(
        cache_dir=tmp_path / "cache",
        provider=FakeProvider(),
        execute_live=True,
        operator_confirmation=LIVE_OPERATOR_CONFIRMATION,
    )
    summary = summarize_composite_transition_surface_value_wiring(
        refresh_manifest=manifest,
    )

    assert summary["result"] == "passed"
    assert summary["numeric_value_loaded_role_count"] == 12
    assert summary["phase_support_added_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
