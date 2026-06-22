from __future__ import annotations

from business_cycle.audits.prospective_source_adapter_inventory import (
    summarize_prospective_source_adapter_inventory,
)


def main() -> None:
    summary = summarize_prospective_source_adapter_inventory()
    for key in (
        "phase",
        "source_adapter_inventory_ready",
        "adapter_count",
        "implemented_adapter_count",
        "implemented_unverified_adapter_count",
        "blocked_adapter_count",
        "manual_only_adapter_count",
        "adapter_without_official_domain_count",
        "adapter_without_revision_policy_count",
        "adapter_without_no_write_preflight_count",
        "adapter_without_offline_fixture_count",
        "role_with_multiple_unresolved_adapters_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

