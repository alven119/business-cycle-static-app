from __future__ import annotations

from business_cycle.audits.qa_phase_lineage import summarize_qa_phase_lineage


def main() -> None:
    summary = summarize_qa_phase_lineage()
    for key in (
        "phase",
        "qa8_closure_artifact_count",
        "qa8_closure_passed",
        "qa9_closure_artifact_count",
        "qa9_closure_passed",
        "phase_sequence_gap_count",
        "freeze_parent_mismatch_count",
        "missing_phase_artifact_count",
        "silent_freeze_rewrite_count",
        "monitoring_freeze_parent_valid",
        "qa8_qa9_lineage_valid",
        "qa8_freeze_id",
        "qa8_freeze_parent_id",
        "qa9_monitoring_freeze_id",
        "qa9_monitoring_parent_model_freeze_id",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
