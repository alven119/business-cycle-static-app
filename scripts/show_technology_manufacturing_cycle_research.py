from __future__ import annotations

from business_cycle.storage.nas_technology_manufacturing_import import (
    summarize_technology_manufacturing_contract,
)


def main() -> int:
    summary = summarize_technology_manufacturing_contract()
    for key, value in summary.items():
        if key != "result":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"result={summary['result']}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
