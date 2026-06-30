from __future__ import annotations

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)
from business_cycle.current.official_macro_source_wiring import (
    resolve_official_series_ids,
    summarize_official_macro_source_adapter_wiring,
)


def test_phase52_official_macro_source_wiring_passes() -> None:
    summary = summarize_official_macro_source_adapter_wiring()

    assert summary["result"] == "passed"
    assert summary["official_macro_source_adapter_wiring_ready"] is True
    assert summary["phase52_candidate_role_count"] == 29
    assert summary["official_wired_role_count"] == 29
    assert summary["unique_official_series_count"] >= 15
    assert summary["registry_missing_series_count"] == 0
    assert summary["release_lag_metadata_incomplete_count"] == 0
    assert summary["source_risk_label_missing_count"] == 0
    assert summary["substitution_degree_missing_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["alternative_promoted_to_core_count"] == 0
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["production_behavior_change_count"] == 0
    assert "PAYEMS" in summary["unique_official_series_ids"]
    assert "PCEC96" in summary["unique_official_series_ids"]


def test_phase52_alias_resolution_preserves_source_identity_correction() -> None:
    assert resolve_official_series_ids(["real_personal_consumption_expenditures"]) == [
        "PCEC96"
    ]
    assert resolve_official_series_ids(["initial_jobless_claims"]) == ["ICSA"]

    summary = summarize_official_macro_source_adapter_wiring()
    assert summary["source_identity_correction_count"] == 1
    corrections = [
        correction
        for row in summary["rows"]
        for correction in row["source_identity_corrections"]
    ]
    assert corrections[0]["incorrect_candidate_series_id"] == "PCECC96"
    assert corrections[0]["corrected_official_series_id"] == "PCEC96"


def test_current_research_readiness_uses_official_series_without_phase_emission() -> None:
    manifest = build_current_data_refresh_manifest(
        snapshot_as_of="2026-06-26",
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    readiness = build_current_evidence_readiness(refresh_manifest=manifest)
    by_role = {row["role_id"]: row for row in readiness["role_readiness_rows"]}

    assert by_role["growth_nonfarm_payrolls"]["source_series_alias_ids"] == [
        "PAYEMS"
    ]
    assert by_role["growth_nonfarm_payrolls"]["official_source_series_ids"] == [
        "PAYEMS"
    ]
    assert by_role["recovery_initial_jobless_claims"][
        "source_series_alias_ids"
    ] == ["initial_jobless_claims"]
    assert by_role["recovery_initial_jobless_claims"][
        "official_source_series_ids"
    ] == ["ICSA"]
    assert readiness["candidate_phase_emitted"] is False
    assert readiness["current_phase_emitted"] is False
    assert readiness["selected_phase_output_count"] == 0
    assert readiness["phase_rank_output_count"] == 0
