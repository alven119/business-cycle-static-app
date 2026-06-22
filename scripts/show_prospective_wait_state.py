from __future__ import annotations

from business_cycle.audits.prospective_wait_state import summarize_prospective_wait_state


def main() -> None:
    summary = summarize_prospective_wait_state()
    for key in (
        "phase",
        "wait_state_governance_ready",
        "current_wait_state",
        "next_check_date",
        "earliest_possible_manual_append_at",
        "qa13_allowed_now",
        "qa13_earliest_as_of",
        "real_registry_append_allowed_now",
        "candidate_monitoring_allowed_now",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

