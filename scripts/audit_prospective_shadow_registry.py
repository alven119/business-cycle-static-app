from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.shadow_model.prospective_registry_store import (
    ProspectiveRegistryStore,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry-dir",
        type=Path,
        default=Path("data/prospective/shadow_observations"),
    )
    args = parser.parse_args()
    summary = ProspectiveRegistryStore(args.registry_dir).audit()
    for key in (
        "phase",
        "record_count",
        "chain_valid",
        "duplicate_count",
        "out_of_order_count",
        "backfill_count",
        "version_mismatch_count",
        "provenance_failure_count",
        "candidate_without_capability_count",
        "inspection_violation_count",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
