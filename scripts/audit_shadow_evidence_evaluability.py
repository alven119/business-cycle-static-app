from __future__ import annotations

from business_cycle.audits.evidence_evaluability import summarize_evidence_evaluability


def main() -> None:
    summary = summarize_evidence_evaluability()
    for key in (
        "phase",
        "evaluability_root_cause_audit_ready",
        "role_count",
        "evaluable_role_count",
        "non_evaluable_role_count",
        "reason_classified_role_count",
        "unclassified_non_evaluable_reason_count",
        "global_evaluability_kill_switch_count",
        "evaluability_blocked_by_unrelated_role_count",
        "evaluable_role_without_complete_gate_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    for reason, count in summary["non_evaluable_reason_counts"].items():
        print(f"reason_count[{reason}]={count}")


if __name__ == "__main__":
    main()
