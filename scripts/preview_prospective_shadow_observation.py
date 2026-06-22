from __future__ import annotations

from datetime import date

from business_cycle.shadow_model.prospective_forward_gate import (
    ForwardGateRequest,
    evaluate_forward_gate,
)


def main() -> None:
    result = evaluate_forward_gate(
        ForwardGateRequest(
            clock_date=date.today(),
            dry_run=True,
            metadata_only=True,
            no_write=True,
        )
    )
    for key in (
        "gate_status",
        "canonical_observation_period",
        "canonical_as_of",
        "write_attempted",
        "record_written",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
    ):
        value = result[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print("real_registry_write_attempt_count=0")
    print("real_registry_record_written_count=0")


if __name__ == "__main__":
    main()
