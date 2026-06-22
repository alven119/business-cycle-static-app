from __future__ import annotations

import argparse

from business_cycle.shadow_model.prospective_period_manifest import (
    build_first_period_manifest,
    summarize_first_period_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    build_first_period_manifest(period=args.period, output_path=args.output)
    summary = summarize_first_period_manifest()
    for key in (
        "phase",
        "first_period_manifest_ready",
        "protocol_id",
        "monitoring_freeze_id",
        "observation_period",
        "canonical_as_of",
        "manifest_role_count",
        "manifest_major_group_count",
        "role_without_release_rule_count",
        "group_without_complete_core_manifest_count",
        "manifest_duplicate_role_count",
        "derived_manifest_without_inputs_count",
        "earliest_append_before_canonical_as_of_count",
        "manifest_hash_valid",
        "earliest_possible_manual_append_at",
        "manifest_hash",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

