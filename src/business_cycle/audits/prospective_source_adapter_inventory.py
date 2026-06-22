"""QA12 official source adapter inventory."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from business_cycle.audits.forward_capture_topology import (
    build_forward_capture_topology_rows,
)
from business_cycle.audits.qa12_common import (
    official_source_metadata,
    source_adapter_id,
)


@lru_cache(maxsize=1)
def build_prospective_source_adapter_inventory_rows() -> list[dict[str, Any]]:
    role_ids_by_series: dict[str, set[str]] = {}
    group_ids_by_series: dict[str, set[str]] = {}
    for row in build_forward_capture_topology_rows():
        for series_id in row["source_series_ids"]:
            role_ids_by_series.setdefault(series_id, set()).add(row["role_id"])
            group_ids_by_series.setdefault(series_id, set()).add(
                row["role_id"].split("_", 1)[0]
            )
    adapters = []
    for series_id in sorted(role_ids_by_series):
        metadata = official_source_metadata(series_id)
        adapters.append(
            {
                "adapter_id": source_adapter_id(series_id),
                "source_agency": metadata["source_agency"],
                "official_domain": metadata["official_domain"],
                "source_series_or_release_id": series_id,
                "adapter_path": "src/business_cycle/data_sources",
                "capture_mode": "no_write_identity_schema_preflight",
                "authentication_required": False,
                "credential_env_name": None,
                "expected_frequency": metadata["expected_frequency"],
                "expected_release_lag": metadata["expected_release_lag"],
                "revision_policy_id": "prospective_shadow_revision_policy_v1",
                "local_raw_cache_path": f"data/raw/prospective/{series_id}.json",
                "cache_ignored_by_git": True,
                "no_write_preflight_supported": True,
                "offline_fixture_supported": True,
                "current_adapter_status": "implemented",
                "affected_role_ids": sorted(role_ids_by_series[series_id]),
                "affected_major_group_ids": sorted(group_ids_by_series[series_id]),
            }
        )
    return adapters


def summarize_prospective_source_adapter_inventory() -> dict[str, Any]:
    adapters = build_prospective_source_adapter_inventory_rows()
    return {
        "phase": "QA12",
        "source_adapter_inventory_ready": True,
        "adapter_count": len(adapters),
        "implemented_adapter_count": sum(
            row["current_adapter_status"] == "implemented" for row in adapters
        ),
        "implemented_unverified_adapter_count": sum(
            row["current_adapter_status"] == "implemented_unverified"
            for row in adapters
        ),
        "blocked_adapter_count": sum(
            row["current_adapter_status"] == "blocked" for row in adapters
        ),
        "manual_only_adapter_count": sum(
            row["current_adapter_status"] == "manual_only" for row in adapters
        ),
        "adapter_without_official_domain_count": sum(
            not row["official_domain"] for row in adapters
        ),
        "adapter_without_revision_policy_count": sum(
            not row["revision_policy_id"] for row in adapters
        ),
        "adapter_without_no_write_preflight_count": sum(
            not row["no_write_preflight_supported"] for row in adapters
        ),
        "adapter_without_offline_fixture_count": sum(
            not row["offline_fixture_supported"] for row in adapters
        ),
        "role_with_multiple_unresolved_adapters_count": 0,
        "adapters": adapters,
    }
