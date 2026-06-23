from __future__ import annotations

import argparse

from business_cycle.audits.phase10_blocked_source_preflight import (
    run_phase10_blocked_source_preflight,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-blocked", action="store_true")
    parser.add_argument("--role-id")
    parser.add_argument("--adapter-id")
    parser.add_argument("--source-family")
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    summary = run_phase10_blocked_source_preflight(output_path=args.output)
    for key in (
        "phase",
        "no_write_preflight_ready",
        "preflight_role_count",
        "preflight_pass_count",
        "preflight_blocked_count",
        "preflight_failure_count",
        "registry_write_attempt_count",
        "prospective_write_attempt_count",
        "production_write_attempt_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
