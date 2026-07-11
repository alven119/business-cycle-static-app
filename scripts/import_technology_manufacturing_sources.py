from __future__ import annotations

import argparse
import json
import os

from business_cycle.storage.nas_technology_manufacturing_import import (
    run_technology_manufacturing_import,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--operator-confirmation")
    args = parser.parse_args()
    confirmation = args.operator_confirmation or os.environ.get(
        "BUSINESS_CYCLE_TECHNOLOGY_REFRESH_OPERATOR_CONFIRMATION"
    )
    report = run_technology_manufacturing_import(
        execute_live=args.execute_live,
        operator_confirmation=confirmation,
        artifact_dir=args.artifact_dir,
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
