from __future__ import annotations

from business_cycle.audits.phase11_evidence_rule_leakage import (
    summarize_phase11_evidence_rule_leakage,
)


def main() -> None:
    summary = summarize_phase11_evidence_rule_leakage()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
