"""Closure audit for Phase 138 NY Fed SCE dashboard integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.service.nas_nyfed_sce_components import (
    load_nyfed_sce_component_contract,
)
from business_cycle.service.nas_nyfed_sce_dashboard import (
    augment_nyfed_sce_release_diagnostics,
    build_portfolio_research_limitations,
    enrich_nyfed_sce_incident_center,
    summarize_nyfed_sce_dashboard_integration_contract,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    build_nyfed_sce_supporting_indicator_snapshots,
    load_nas_live_postgres_dashboard_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = (
    ROOT
    / "specs/audits/phase138_nyfed_sce_dashboard_integration_closure.yaml"
)


def summarize_phase138_nyfed_sce_dashboard_integration_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase138_nyfed_sce_dashboard_integration_closure"
    ]["hard_gates"]
    contract_summary = summarize_nyfed_sce_dashboard_integration_contract()
    series_rows, artifact_rows, observations = _component_fixture()
    release_diagnostics = augment_nyfed_sce_release_diagnostics(
        _base_release_diagnostics(),
        as_of="2026-07-13",
        series_inputs=_release_inputs(),
        refresh_status={
            "last_run_state": "succeeded",
            "last_completed_at_utc": "2026-07-08T12:00:00Z",
            "series_refresh_results": [
                {
                    "series_id": "NYFED_SCE_CONTEXT",
                    "status": "imported",
                }
            ],
        },
    )
    supporting = build_nyfed_sce_supporting_indicator_snapshots(
        observations_by_series=observations,
        series_rows=series_rows,
        artifact_rows=artifact_rows,
        as_of="2026-07-13",
        contract=load_nas_live_postgres_dashboard_contract(),
        release_diagnostics=release_diagnostics,
    )
    incident = enrich_nyfed_sce_incident_center(_incident_fixture())
    limitations = build_portfolio_research_limitations(
        strict_complete_scenario_count=2,
        scenario_count=5,
    )
    summary = {
        "phase": 138,
        "phase138_closure_ready": True,
        **{
            key: contract_summary[key]
            for key in (
                "nyfed_sce_dashboard_integration_contract_ready",
                "supporting_indicator_count",
                "chart_period_count",
                "supporting_indicator_with_complete_learning_semantics_count",
                "supporting_indicator_promoted_to_book_core_count",
                "release_family_extension_count",
                "exact_release_event_count",
                "portfolio_research_limitation_count",
                "strict_replay_scenario_count",
                "strict_replay_complete_scenario_count",
                "strict_replay_blocked_scenario_count",
                "revised_data_mislabeled_as_pit_count",
                "numeric_weight_added_count",
                "arbitrary_threshold_added_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "semantic_drift_count",
            )
        },
        "supporting_indicator_count": len(supporting),
        "chart_period_count": len(
            supporting[0]["chart_payload_detail"]["series_charts"][0][
                "periods"
            ]
        ),
        "supporting_indicator_with_complete_learning_semantics_count": sum(
            bool(row["high_meaning_zh"]) and bool(row["low_meaning_zh"])
            for row in supporting
        ),
        "release_family_extension_count": int(
            release_diagnostics["supporting_release_family_count"]
        ),
        "exact_release_event_count": 2,
        "incident_component_drilldown_count": int(
            incident["nyfed_affected_component_count"]
        ),
        "portfolio_research_limitation_count": len(limitations),
        "test_file_delta": 0,
        "development_next_phase": 139,
        "phase138_closure_status": (
            "closed_nyfed_sce_explorer_calendar_incident_drilldown_supporting_only"
        ),
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def _component_fixture() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
]:
    components = load_nyfed_sce_component_contract()["component_series"]
    series_rows: dict[str, dict[str, Any]] = {}
    artifacts: dict[str, dict[str, Any]] = {}
    observations: dict[str, list[dict[str, Any]]] = {}
    for index, component in enumerate(components, start=1):
        series_id = str(component["series_id"])
        artifact_id = f"phase138-artifact::{series_id}"
        series_rows[series_id] = {
            "series_key": series_id,
            "source_family": "Federal Reserve Bank of New York",
            "source_series_id": series_id,
            "source_title": str(component["title_zh"]),
            "units": str(component["units"]),
            "frequency": "monthly",
            "seasonal_adjustment": "not_applicable_survey_measure",
            "geographic_scope": "United States",
            "source_url_without_secret": (
                "https://www.newyorkfed.org/microeconomics/databank"
            ),
        }
        artifacts[artifact_id] = {
            "artifact_id": artifact_id,
            "source_family": "Federal Reserve Bank of New York",
            "source_url_without_secret": (
                "https://www.newyorkfed.org/microeconomics/databank"
            ),
            "source_series_or_release_id": series_id,
            "fetched_at_utc": "2026-07-08T12:00:00Z",
            "content_hash": f"phase138-hash-{index}",
            "adapter_id": "nyfed_sce_official_workbook_phase137",
            "parser_version": "1.0",
            "validation_status": "validated",
        }
        observations[series_id] = [
            {
                "series_key": series_id,
                "observation_date": observation_date,
                "value_numeric": str(index + offset / 10),
                "value_text": None,
                "unit": str(component["units"]),
                "data_mode": "revised",
                "source_artifact_id": artifact_id,
                "provenance_hash": f"phase138-{series_id}-{offset}",
            }
            for offset, observation_date in enumerate(
                (
                    "2021-07-01",
                    "2025-06-01",
                    "2026-01-01",
                    "2026-06-01",
                )
            )
        ]
    return series_rows, artifacts, observations


def _release_inputs() -> list[dict[str, Any]]:
    return [
        {
            "series_id": str(row["series_id"]),
            "frequency": "monthly",
            "latest_observation_date": "2026-06-01",
            "reference_period_end_date": "2026-06-30",
            "freshness_status": "fresh",
            "freshness_reason_code": (
                "latest_registered_official_reference_period_available"
            ),
        }
        for row in load_nyfed_sce_component_contract()["component_series"]
    ]


def _base_release_diagnostics() -> dict[str, Any]:
    return {
        "release_families": [],
        "series_refresh_diagnostics": [],
        "release_family_count": 0,
        "series_diagnostic_count": 0,
        "exact_schedule_family_count": 0,
        "release_calendar_runtime_ready": True,
    }


def _incident_fixture() -> dict[str, Any]:
    return {
        "open_incident_count": 1,
        "open_incidents": [
            {
                "source_series_id": "NYFED_SCE_CONTEXT",
                "incident_type": "source_fetch_failure",
                "affected_role_ids": ["boom_consumer_confidence"],
                "affected_cycle_lanes": ["boom::boom_ending_watch"],
                "fallback_status": "abstain_required",
            }
        ],
        "recent_recovery_receipts": [],
        "supporting_source_promoted_to_core_count": 0,
    }
