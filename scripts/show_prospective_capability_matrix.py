from __future__ import annotations

from business_cycle.audits.prospective_capability_matrix import (
    summarize_prospective_capability_matrix,
)


def main() -> None:
    summary = summarize_prospective_capability_matrix()
    for key in (
        "phase",
        "prospective_capability_matrix_ready",
        "capability_cell_count",
        "capability_unknown_count",
        "capability_inconsistent_count",
        "downstream_ready_without_upstream_ready_count",
        "candidate_ready_without_phase_evidence_count",
        "production_ready_without_candidate_ready_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

