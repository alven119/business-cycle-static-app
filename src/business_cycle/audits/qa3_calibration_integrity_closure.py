"""QA3 calibration integrity and validation governance closure."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.calibration_leakage import summarize_calibration_leakage
from business_cycle.audits.context_dependency_governance import (
    summarize_context_dependency_governance,
)
from business_cycle.audits.data_only_model_freeze import (
    summarize_data_only_model_baseline_freeze,
)
from business_cycle.audits.data_only_shadow_evaluation import (
    run_data_only_shadow_evaluation,
)
from business_cycle.audits.model_parameter_drift import summarize_model_parameter_drift
from business_cycle.audits.model_parameter_inventory import (
    summarize_model_parameter_inventory,
)
from business_cycle.audits.pre_registered_validation import (
    summarize_pre_registered_validation_protocol,
)
from business_cycle.audits.production_hardcoding import summarize_production_hardcoding
from business_cycle.audits.qa2_context_ablation_closure import (
    summarize_data_only_path_contract,
    summarize_production_compatibility,
)
from business_cycle.audits.scenario_exposure import (
    summarize_scenario_exposure_registry,
)


DEFAULT_CLOSURE_PATH = Path("specs/audits/qa3_calibration_integrity_closure.yaml")


def summarize_qa3_calibration_integrity_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA3 hard gates without changing model behavior."""

    expected = _load_expected(path)
    inventory = summarize_model_parameter_inventory()
    drift = summarize_model_parameter_drift()
    exposure = summarize_scenario_exposure_registry()
    hardcoding = summarize_production_hardcoding()
    freeze = summarize_data_only_model_baseline_freeze()
    protocol = summarize_pre_registered_validation_protocol()
    leakage = summarize_calibration_leakage()
    shadow = run_data_only_shadow_evaluation()
    context = summarize_context_dependency_governance()
    qa2_data_only = summarize_data_only_path_contract()
    qa2_production = summarize_production_compatibility()
    qa2_data_only_structural = (
        qa2_data_only["data_only_function_external_context_parameter_count"] == 0
        and qa2_data_only["data_only_external_context_access_count"] == 0
        and qa2_data_only["data_only_display_text_access_count"] == 0
    )
    change_counts = _forbidden_change_counts()

    summary = {
        "phase": "QA3",
        "parameter_inventory_ready": inventory["parameter_inventory_ready"],
        "parameter_drift_detection_ready": drift[
            "parameter_inventory_drift_detection_ready"
        ]
        and drift["unmapped_parameter_count"] == 0
        and drift["parameter_hash_mismatch_count"] == 0
        and drift["parameter_classification_drift_count"] == 0,
        "scenario_exposure_registry_ready": exposure[
            "scenario_exposure_registry_ready"
        ],
        "all_current_scenarios_development_only": (
            exposure["previously_seen_scenario_count"] == 5
            and exposure["development_scenario_count"] == 5
            and exposure["independent_validation_scenario_count"] == 0
            and exposure["untouched_holdout_scenario_count"] == 0
        ),
        "production_hardcoding_audit_ready": hardcoding[
            "production_hardcoding_audit_ready"
        ]
        and hardcoding["unreviewed_hard_coding_count"] == 0,
        "data_only_baseline_freeze_ready": freeze[
            "data_only_baseline_freeze_ready"
        ],
        "pre_registered_validation_protocol_ready": protocol[
            "pre_registered_validation_protocol_ready"
        ],
        "prospective_holdout_registered": protocol["prospective_holdout_registered"],
        "prospective_holdout_result_inspected": protocol[
            "prospective_holdout_result_inspected"
        ],
        "calibration_leakage_audit_ready": leakage["calibration_leakage_audit_ready"],
        "data_only_shadow_evaluation_ready": shadow["data_only_shadow_evaluation_ready"],
        "context_dependency_governance_ready": context[
            "context_dependency_governance_ready"
        ],
        "parameter_tuning_executed": False,
        **change_counts,
        "performance_backtest_executed": False,
        "holdout_result_inspected": False,
        "production_default_behavior_changed_count": qa2_production[
            "production_default_behavior_changed_count"
        ],
        "data_only_model_structurally_validated": qa2_data_only_structural,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "final_holdout_ready": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "qa4_allowed": True,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa3_closure_status": expected["qa3_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "inventory": inventory,
        "drift": drift,
        "scenario_exposure": exposure,
        "production_hardcoding": hardcoding,
        "freeze": freeze,
        "pre_registered_validation": protocol,
        "calibration_leakage": leakage,
        "data_only_shadow_evaluation": shadow,
        "context_dependency_governance": context,
    }
    summary["result"] = "passed" if _qa3_passed(summary, expected) else "blocked"
    return summary


def _qa3_passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, expected_value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != expected_value:
            return False
    inventory = summary["inventory"]
    drift = summary["drift"]
    exposure = summary["scenario_exposure"]
    hardcoding = summary["production_hardcoding"]
    freeze = summary["freeze"]
    protocol = summary["pre_registered_validation"]
    leakage = summary["calibration_leakage"]
    shadow = summary["data_only_shadow_evaluation"]
    context = summary["context_dependency_governance"]
    return (
        inventory["unclassified_parameter_count"] == 0
        and inventory["duplicate_parameter_id_count"] == 0
        and inventory["orphaned_parameter_path_count"] == 0
        and drift["unmapped_parameter_count"] == 0
        and drift["parameter_hash_mismatch_count"] == 0
        and drift["parameter_classification_drift_count"] == 0
        and exposure["previously_seen_scenario_count"] == 5
        and exposure["development_scenario_count"] == 5
        and exposure["independent_validation_scenario_count"] == 0
        and exposure["untouched_holdout_scenario_count"] == 0
        and exposure["performance_claim_eligible_scenario_count"] == 0
        and exposure["scenario_without_exposure_history_count"] == 0
        and hardcoding["production_hard_coded_scenario_id_count"] == 0
        and hardcoding["production_hard_coded_date_count"] == 0
        and hardcoding["production_scenario_name_branch_count"] == 0
        and hardcoding["production_event_specific_override_count"] == 0
        and freeze["freeze_hash_valid"] is True
        and freeze["frozen_file_missing_count"] == 0
        and freeze["frozen_file_hash_mismatch_count"] == 0
        and freeze["unfrozen_decision_file_count"] == 0
        and freeze["secret_in_freeze_manifest_count"] == 0
        and protocol["holdout_protocol_complete"] is True
        and protocol["result_peeking_allowed"] is False
        and leakage["unacknowledged_contaminated_parameter_count"] == 0
        and leakage["false_out_of_sample_claim_count"] == 0
        and shadow["parameter_selection_from_shadow_result_count"] == 0
        and shadow["performance_metric_computed_count"] == 0
        and shadow["shadow_result_written_to_public_count"] == 0
        and shadow["all_rows_use_frozen_model_version"] is True
        and shadow["all_real_data_rows_strict_complete"] is True
        and shadow["data_only_external_context_read_count"] == 0
        and context["production_context_dependency_acknowledged"] is True
        and context["production_context_decoupling_allowed_now"] is False
        and context["production_default_preserved"] is True
        and context["mislabeled_context_derived_result_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["qa3_calibration_integrity_closure"]["expected_status"]


def _forbidden_change_counts() -> dict[str, int]:
    changed = _git_changed_files()
    return {
        "scoring_weight_change_count": sum(
            path.startswith("specs/phases/") for path in changed
        ),
        "transition_threshold_change_count": sum(
            path
            in {
                "specs/common/phase_state_machine.yaml",
                "src/business_cycle/phases/state_machine.py",
            }
            for path in changed
        ),
        "acceptance_window_change_count": sum(
            path == "specs/backtests/calibration_acceptance_windows.yaml"
            for path in changed
        ),
    }


def _git_changed_files() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "diff", "--name-only"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]
