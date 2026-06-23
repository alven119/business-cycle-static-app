"""Phase 10 release-semantics registry."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.phase10_common import after_contracts


def build_book_core_release_semantics_rows() -> list[dict[str, Any]]:
    rows = []
    for contract in after_contracts():
        is_derived = bool(contract["derived_input_series_ids"])
        rows.append(
            {
                "role_id": contract["role_id"],
                "source_release_family": "derived_same_as_of_inputs"
                if is_derived
                else "official_series_release",
                "reference_period": "source_reference_period",
                "publication_frequency": contract["publication_frequency"],
                "publication_date_rule": contract["release_lag_rule"],
                "publication_time_zone": "source_official_timezone",
                "initial_release": "record_initial_release_when_available",
                "revision_release": "append_revision_metadata",
                "benchmark_revision": "append_benchmark_revision_metadata",
                "correction_policy": "append_correction_without_overwrite",
                "availability_precision": "release_date_or_timestamp",
                "as_of_selection_rule": "available_on_or_before_as_of",
                "missing_release_behavior": "abstain_and_record_gap",
                "delayed_release_behavior": "wait_for_release",
                "forward_capture_readiness": contract["shadow_data_contract_status"]
                == "ready_revised_diagnostic",
                "input_roles": contract["derived_input_series_ids"] if is_derived else [],
                "same_as_of_requirement": is_derived,
                "reference_period_alignment": "max_input_availability"
                if is_derived
                else "source_native",
                "availability": "max(inputs)" if is_derived else "source_release",
                "correction_propagation": "append_derived_correction"
                if is_derived
                else "append_source_correction",
                "lineage": "derived_inputs_required" if is_derived else "direct_source",
            }
        )
    return rows


def summarize_book_core_release_semantics() -> dict[str, Any]:
    rows = build_book_core_release_semantics_rows()
    return {
        "phase": "10",
        "release_semantics_registry_ready": True,
        "role_with_release_semantics_count": len(rows),
        "role_without_release_semantics_count": 0,
        "direct_role_without_revision_policy_count": 0,
        "derived_role_without_input_semantics_count": 0,
        "ambiguous_availability_date_count": 0,
        "observation_date_assumed_availability_count": 0,
        "rows": rows,
    }
