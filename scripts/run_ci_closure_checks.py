#!/usr/bin/env python
"""Run CI closure-check bundles without wiring shadow commands into workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys


FULL_CLOSURE_SCRIPTS = (
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
