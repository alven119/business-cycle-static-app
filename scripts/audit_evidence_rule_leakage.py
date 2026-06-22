from __future__ import annotations

from business_cycle.audits.evidence_rule_leakage import summarize_evidence_rule_leakage


def main() -> int:
    summary = summarize_evidence_rule_leakage()
    for key in (
        "phase",
        "evidence_rule_leakage_guard_ready",
        "scenario_id_reference_count",
        "historical_date_reference_count",
        "expected_label_reference_count",
        "nber_reference_count",
        "return_metric_reference_count",
        "scenario_branch_count",
        "historical_observation_copied_as_threshold_count",
        "post_diagnostic_rule_change_without_new_version_count",
        "historical_result_used_for_rule_selection_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["evidence_rule_leakage_guard_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
