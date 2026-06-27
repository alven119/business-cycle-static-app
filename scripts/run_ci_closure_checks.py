#!/usr/bin/env python
"""Run CI closure-check bundles without wiring shadow commands into workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys


FULL_CLOSURE_SCRIPTS = (
    "scripts/show_phase42_current_freshness_and_evidence_profile_closure.py",
    "scripts/show_phase41_live_current_refresh_smoke_closure.py",
    "scripts/show_phase40_current_data_refresh_closure.py",
    "scripts/show_phase39_current_research_snapshot_closure.py",
    "scripts/show_phase38_research_validation_dashboard_closure.py",
    "scripts/show_phase37_recession_recovery_pit_remediation_closure.py",
    "scripts/show_phase36r_recession_recovery_evidence_completion_closure.py",
    "scripts/show_phase36_historical_validation_result_realization_closure.py",
    "scripts/show_phase35_historical_comparability_realization_closure.py",
    "scripts/show_phase34_autonomous_blocker_unblock_closure.py",
    "scripts/show_phase33_blocker_resolution_execution_closure.py",
    "scripts/show_phase32_genuine_blocker_resolution_plan_closure.py",
    "scripts/show_phase31_validation_blockage_remediation_closure.py",
    "scripts/show_phase30_validation_blockage_diagnostics_closure.py",
    "scripts/show_phase29_historical_accuracy_metrics_closure.py",
    "scripts/show_phase28_predicted_label_comparison_closure.py",
    "scripts/show_phase27_predicted_label_artifact_closure.py",
    "scripts/show_phase26_predicted_label_mapping_contract_closure.py",
    "scripts/show_phase25_research_decision_output_closure.py",
    "scripts/show_phase24_research_decision_output_contract_closure.py",
    "scripts/show_phase23_comparison_coverage_metrics_closure.py",
    "scripts/show_phase22_label_comparison_artifact_closure.py",
    "scripts/show_phase21_metric_preregistration_closure.py",
    "scripts/show_phase20_historical_validation_dry_run_closure.py",
    "scripts/show_phase19_validation_execution_readiness_closure.py",
    "scripts/show_phase18_historical_input_readiness_closure.py",
    "scripts/show_phase17_historical_manifest_closure.py",
    "scripts/show_qa12_major_group_manual_start_closure.py",
    "scripts/run_qa0_integrity_audit.py",
)

NIGHTLY_CLOSURE_SCRIPTS = (
    "scripts/show_phase42_current_freshness_and_evidence_profile_closure.py",
    "scripts/show_phase41_live_current_refresh_smoke_closure.py",
    "scripts/show_phase40_current_data_refresh_closure.py",
    "scripts/show_phase39_current_research_snapshot_closure.py",
    "scripts/show_phase38_research_validation_dashboard_closure.py",
    "scripts/show_phase37_recession_recovery_pit_remediation_closure.py",
    "scripts/show_phase36r_recession_recovery_evidence_completion_closure.py",
    "scripts/show_phase36_historical_validation_result_realization_closure.py",
    "scripts/show_phase35_historical_comparability_realization_closure.py",
    "scripts/show_phase34_autonomous_blocker_unblock_closure.py",
    "scripts/show_phase33_blocker_resolution_execution_closure.py",
    "scripts/show_phase32_genuine_blocker_resolution_plan_closure.py",
    "scripts/show_phase31_validation_blockage_remediation_closure.py",
    "scripts/show_phase30_validation_blockage_diagnostics_closure.py",
    "scripts/show_phase29_historical_accuracy_metrics_closure.py",
    "scripts/show_phase28_predicted_label_comparison_closure.py",
    "scripts/show_phase27_predicted_label_artifact_closure.py",
    "scripts/show_phase26_predicted_label_mapping_contract_closure.py",
    "scripts/show_phase25_research_decision_output_closure.py",
    "scripts/show_phase24_research_decision_output_contract_closure.py",
    "scripts/show_phase23_comparison_coverage_metrics_closure.py",
    "scripts/show_phase22_label_comparison_artifact_closure.py",
    "scripts/show_phase21_metric_preregistration_closure.py",
    "scripts/show_phase20_historical_validation_dry_run_closure.py",
    "scripts/show_phase19_validation_execution_readiness_closure.py",
    "scripts/show_phase18_historical_input_readiness_closure.py",
    "scripts/show_phase17_historical_manifest_closure.py",
    "scripts/show_phase16_validation_harness_closure.py",
    "scripts/show_phase15_validation_protocol_closure.py",
    "scripts/show_phase14_non_emitting_decision_runtime_closure.py",
    "scripts/show_phase13_formal_decision_contract_closure.py",
    "scripts/show_phase12_book_core_gap_resolution_closure.py",
    "scripts/show_phase11_book_core_phase_evidence_closure.py",
    "scripts/show_phase10_book_core_source_adapter_closure.py",
    "scripts/show_qa12_major_group_manual_start_closure.py",
    "scripts/run_qa0_integrity_audit.py",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=("full", "nightly"), required=True)
    args = parser.parse_args(argv)

    scripts = FULL_CLOSURE_SCRIPTS if args.tier == "full" else NIGHTLY_CLOSURE_SCRIPTS
    for script in scripts:
        print(f"running {script}", flush=True)
        subprocess.run([sys.executable, script], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
