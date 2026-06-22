from __future__ import annotations

import argparse

from business_cycle.shadow_model.source_preflight import run_source_preflight


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-forward-ready", action="store_true")
    parser.add_argument("--role-id")
    parser.add_argument("--major-group")
    parser.add_argument("--adapter-id")
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--force-refresh-metadata", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    summary = run_source_preflight(
        no_write=args.no_write,
        reuse_existing=args.reuse_existing,
        no_network=args.no_network,
        output_path=args.output,
    )
    for key in (
        "phase",
        "no_write_source_preflight_ready",
        "adapter_preflight_requested_count",
        "adapter_preflight_attempted_count",
        "adapter_preflight_pass_count",
        "adapter_preflight_blocked_count",
        "role_live_preflight_ready_count",
        "role_live_preflight_blocked_count",
        "major_group_live_preflight_ready_count",
        "source_identity_mismatch_count",
        "schema_mismatch_count",
        "release_semantics_mismatch_count",
        "registry_write_attempt_count",
        "post_preflight_rule_change_count",
        "post_preflight_threshold_change_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

