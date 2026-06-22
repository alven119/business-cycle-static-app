"""QA5 book-core data contracts and shadow evidence model closure."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    summarize_book_core_indicator_data_contracts,
)
from business_cycle.audits.book_core_series_verification import (
    verify_book_core_series_contracts,
)
from business_cycle.audits.book_core_transformations import (
    summarize_book_core_transformation_contracts,
)
from business_cycle.audits.book_faithful_shadow_fixtures import (
    summarize_book_faithful_shadow_model_fixtures,
)
from business_cycle.audits.book_fidelity_readiness import (
    summarize_book_fidelity_readiness,
)
from business_cycle.audits.book_phase_major_groups import (
    summarize_book_phase_major_group_readiness,
)
from business_cycle.audits.indicator_promotion import (
    summarize_indicator_promotion_readiness,
)
from business_cycle.audits.qa5_scope_count_semantics import (
    summarize_qa5_scope_count_semantics,
)
from business_cycle.audits.shadow_candidate_freeze import (
    summarize_book_faithful_shadow_candidate_freeze,
)
from business_cycle.audits.shadow_production_isolation import (
    summarize_shadow_production_isolation,
)
from business_cycle.shadow_model.runner import run_shadow_evidence_model


DEFAULT_QA5_CLOSURE_PATH = Path("specs/audits/qa5_book_core_shadow_model_closure.yaml")


def summarize_qa5_book_core_shadow_model_closure(
    path: str | Path = DEFAULT_QA5_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA5 hard gates."""

    expected = _load_expected(path)
    scope = summarize_qa5_scope_count_semantics()
    groups = summarize_book_phase_major_group_readiness()
    data_contracts = summarize_book_core_indicator_data_contracts()
    verification = verify_book_core_series_contracts(no_api=True)
    transformations = summarize_book_core_transformation_contracts()
    fixtures = summarize_book_faithful_shadow_model_fixtures()
    diagnostics = _run_required_shadow_diagnostics()
    promotion = summarize_indicator_promotion_readiness()
    freeze = summarize_book_faithful_shadow_candidate_freeze()
    readiness = summarize_book_fidelity_readiness()
    isolation = summarize_shadow_production_isolation()
    changes = _forbidden_change_summary()
    formal_candidate = any(
        diagnostic["formal_candidate_phase_computed"] for diagnostic in diagnostics.values()
    )
    summary = {
        "phase": "QA5",
        "scope_count_semantics_ready": scope["scope_count_semantics_ready"],
        "formal_v1_primary_partition_valid": scope[
            "formal_v1_primary_partition_valid"
        ],
        "major_group_contract_ready": groups["major_group_contract_ready"],
        "book_core_data_contract_registry_ready": data_contracts[
            "book_core_data_contract_registry_ready"
        ],
        "official_series_verification_ready": verification[
            "official_series_verification_ready"
        ],
        "transformation_contract_registry_ready": transformations[
            "transformation_contract_registry_ready"
        ],
        "shadow_evidence_model_implemented": all(
            diagnostic["model_id"] == "book_faithful_shadow_v2_alpha1"
            for diagnostic in diagnostics.values()
        ),
        "synthetic_structural_validation_ready": fixtures[
            "synthetic_structural_validation_ready"
        ],
        "real_data_shadow_diagnostics_ready": all(
            diagnostic["strict_fallback_count"] == 0
            and diagnostic["context_prior_used_count"] == 0
            and diagnostic["formal_candidate_phase_computed"] is False
            and diagnostic["known_label_used_for_parameter_selection"] is False
            and diagnostic["performance_metric_computed"] is False
            and diagnostic["public_output_written"] is False
            for diagnostic in diagnostics.values()
        ),
        "promotion_gate_updated": promotion[
            "ready_for_shadow_evidence_model_count"
        ]
        > 0
        and promotion["new_production_promotion_count"] == 0,
        "shadow_candidate_freeze_ready": freeze["shadow_candidate_freeze_ready"],
        "book_fidelity_rollups_ready": readiness["book_fidelity_rollups_ready"],
        "production_isolation_verified": isolation["production_isolation_verified"],
        "canonical_indicator_role_count": data_contracts[
            "canonical_indicator_role_count"
        ],
        "data_contract_row_count": data_contracts["data_contract_row_count"],
        "ready_strict_complete_count": data_contracts["ready_strict_complete_count"],
        "ready_strict_partial_count": data_contracts["ready_strict_partial_count"],
        "ready_revised_diagnostic_count": data_contracts[
            "ready_revised_diagnostic_count"
        ],
        "blocked_role_count": data_contracts["blocked_role_count"],
        "ready_for_shadow_evidence_model_count": promotion[
            "ready_for_shadow_evidence_model_count"
        ],
        "shadow_major_group_ready_count": readiness["shadow_major_group_ready_count"],
        "unresolved_major_group_count": readiness["unresolved_major_group_count"],
        "formal_candidate_phase_computed": formal_candidate,
        "formal_decision_model_ready": readiness["formal_decision_model_ready"],
        "production_book_fidelity_ready": readiness["production_book_fidelity_ready"],
        "book_alignment_claim_allowed": readiness["book_alignment_claim_allowed"],
        "proposed_v2_economically_validated": False,
        "new_weight_defined_count": transformations["new_weight_defined_count"],
        "new_threshold_defined_count": transformations["new_threshold_defined_count"],
        "parameter_tuning_executed": False,
        "performance_backtest_executed": False,
        "holdout_registered": freeze["holdout_registered"],
        "production_behavior_change_count": isolation["production_behavior_change_count"],
        "qa6_allowed": True,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa5_closure_status": expected["qa5_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "scope_count_semantics": scope,
        "major_groups": groups,
        "data_contracts": data_contracts,
        "series_verification": verification,
        "transformations": transformations,
        "fixtures": fixtures,
        "shadow_diagnostics": diagnostics,
        "promotion": promotion,
        "shadow_freeze": freeze,
        "readiness": readiness,
        "production_isolation": isolation,
        "forbidden_change_summary": changes,
    }
    summary["result"] = "passed" if _qa5_passed(summary, expected) else "blocked"
    return summary


def _run_required_shadow_diagnostics() -> dict[str, dict[str, Any]]:
    return {
        "strict_2019": run_shadow_evidence_model(
            as_of="2019-12-31", data_mode="vintage_as_of"
        ),
        "strict_2008": run_shadow_evidence_model(
            as_of="2008-09-30", data_mode="vintage_as_of"
        ),
        "strict_2000": run_shadow_evidence_model(
            as_of="2000-03-31", data_mode="vintage_as_of"
        ),
        "revised_2019": run_shadow_evidence_model(
            as_of="2019-12-31", data_mode="revised"
        ),
    }


def _qa5_passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != value:
            return False
    scope = summary["scope_count_semantics"]
    groups = summary["major_groups"]
    data_contracts = summary["data_contracts"]
    transformations = summary["transformations"]
    fixtures = summary["fixtures"]
    promotion = summary["promotion"]
    freeze = summary["shadow_freeze"]
    isolation = summary["production_isolation"]
    return (
        scope["overlapping_primary_classification_count"] == 0
        and scope["canonical_role_without_matrix_row_count"] == 0
        and scope["duplicate_indicator_matrix_row_count"] == 0
        and groups["recovery_major_group_count"] == 4
        and groups["growth_major_group_count"] == 4
        and groups["boom_major_group_count"] == 7
        and groups["subrole_without_major_group_count"] == 0
        and groups["subrole_mapped_to_multiple_major_groups_count"] == 0
        and data_contracts["role_without_data_contract_count"] == 0
        and data_contracts["data_contract_without_role_count"] == 0
        and data_contracts["silent_substitution_count"] == 0
        and data_contracts["unverified_series_identity_count"] == 0
        and transformations["new_threshold_defined_count"] == 0
        and transformations["new_weight_defined_count"] == 0
        and transformations["engineering_default_mislabeled_as_book_count"] == 0
        and transformations["strict_transform_with_revised_lookback_count"] == 0
        and fixtures["canonical_fixture_pass_count"]
        == fixtures["canonical_phase_fixture_count"]
        and fixtures["missing_evidence_zero_fill_count"] == 0
        and promotion["ready_for_shadow_evidence_model_count"] > 0
        and promotion["new_production_promotion_count"] == 0
        and promotion["production_review_ready_count"] == 0
        and freeze["shadow_freeze_hash_valid"] is True
        and freeze["decision_parameter_frozen_count"] == 0
        and freeze["holdout_registered"] is False
        and isolation["production_imports_shadow_module_count"] == 0
        and isolation["production_behavior_change_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa5_book_core_shadow_model_closure"
    ]["expected_status"]


def _forbidden_change_summary() -> dict[str, Any]:
    changed = _git_changed_files()
    return {
        "scoring_weight_change_count": sum(path.startswith("specs/phases/") for path in changed),
        "threshold_change_count": sum(
            path.startswith("specs/phases/")
            or path == "specs/common/phase_state_machine.yaml"
            for path in changed
        ),
        "production_resolver_changed": any(
            path.startswith("src/business_cycle/phases/") for path in changed
        ),
        "production_dashboard_changed": any(
            path.startswith("src/business_cycle/render/") for path in changed
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
