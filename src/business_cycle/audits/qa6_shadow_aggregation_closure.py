"""QA6 shadow aggregation closure contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.aggregation_rule_leakage import (
    summarize_aggregation_rule_leakage,
)
from business_cycle.audits.model_freeze_lineage import summarize_model_freeze_lineage
from business_cycle.audits.qa6_readiness_semantics import (
    summarize_qa6_readiness_semantics,
)
from business_cycle.audits.shadow_aggregation_diagnostics import (
    run_shadow_aggregation_diagnostics,
)
from business_cycle.audits.shadow_aggregation_fixtures import (
    validate_shadow_aggregation_structural_fixtures,
)
from business_cycle.audits.shadow_aggregation_freeze import (
    summarize_shadow_aggregation_freeze,
)
from business_cycle.audits.shadow_aggregation_production_isolation import (
    summarize_shadow_aggregation_production_isolation,
)
from business_cycle.audits.shadow_evidence_layer_routing import (
    summarize_shadow_evidence_layer_routing,
)
from business_cycle.shadow_model.aggregation_contract import (
    summarize_shadow_aggregation_rule_contract,
)
from business_cycle.shadow_model.structural_eligibility import (
    evaluate_structural_eligibility,
)
from business_cycle.shadow_model.typed_evidence import (
    summarize_typed_book_evidence_contract,
)


DEFAULT_QA6_CLOSURE_PATH = Path("specs/audits/qa6_shadow_aggregation_closure.yaml")


def summarize_qa6_shadow_aggregation_closure(
    path: str | Path = DEFAULT_QA6_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA6 hard gates."""

    expected = _load_expected(path)
    lineage = summarize_model_freeze_lineage()
    readiness = summarize_qa6_readiness_semantics()
    typed = summarize_typed_book_evidence_contract()
    routing = summarize_shadow_evidence_layer_routing()
    aggregation = summarize_shadow_aggregation_rule_contract()
    structural = evaluate_structural_eligibility([])
    fixtures = validate_shadow_aggregation_structural_fixtures()
    diagnostics = _required_diagnostics()
    leakage = summarize_aggregation_rule_leakage()
    freeze = summarize_shadow_aggregation_freeze()
    isolation = summarize_shadow_aggregation_production_isolation()
    real_ready = all(
        item["candidate_selection_enabled"] is False
        and item["candidate_phase_computed"] is False
        and item["context_prior_used"] is False
        and item["known_label_used"] is False
        and item["performance_metric_computed"] is False
        and item["strict_fallback_count"] == 0
        and item["public_output_written"] is False
        for item in diagnostics.values()
    )
    summary = {
        "phase": "QA6",
        "freeze_lineage_ready": lineage["freeze_lineage_ready"],
        "prior_freeze_artifact_preserved": lineage[
            "prior_freeze_artifact_preserved"
        ],
        "readiness_semantics_ready": readiness["readiness_semantics_ready"],
        "typed_evidence_contract_ready": typed["typed_evidence_contract_ready"],
        "layer_routing_contract_ready": routing["layer_routing_contract_ready"],
        "aggregation_schema_preregistered": aggregation[
            "aggregation_schema_preregistered"
        ],
        "structural_candidate_eligibility_ready": structural[
            "structural_candidate_eligibility_ready"
        ],
        "synthetic_structural_eligibility_validated": fixtures[
            "synthetic_structural_eligibility_validated"
        ],
        "real_data_aggregation_diagnostics_ready": real_ready,
        "aggregation_rule_leakage_guard_ready": leakage[
            "aggregation_rule_leakage_guard_ready"
        ],
        "shadow_aggregation_freeze_ready": freeze[
            "shadow_aggregation_freeze_ready"
        ],
        "production_isolation_verified": isolation[
            "production_isolation_verified"
        ],
        "structurally_mapped_role_count": readiness[
            "structurally_mapped_role_count"
        ],
        "evidence_evaluable_role_count": readiness[
            "evidence_evaluable_role_count"
        ],
        "structurally_routable_major_group_count": readiness[
            "structurally_routable_major_group_count"
        ],
        "evidence_evaluable_major_group_count": readiness[
            "evidence_evaluable_major_group_count"
        ],
        "aggregation_eligible_major_group_count": readiness[
            "aggregation_eligible_major_group_count"
        ],
        "numeric_weight_count": aggregation["numeric_weight_count"],
        "newly_defined_threshold_count": aggregation[
            "newly_defined_threshold_count"
        ],
        "historical_label_used_for_rule_selection_count": aggregation[
            "historical_label_used_for_rule_selection_count"
        ]
        + leakage["historical_result_used_for_rule_selection_count"],
        "candidate_selection_enabled": False,
        "formal_candidate_phase_computed": False,
        "formal_decision_model_ready": False,
        "data_only_model_economically_validated": False,
        "independent_validation_ready": False,
        "holdout_registered": freeze["holdout_registered"],
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "qa7_allowed": True,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa6_closure_status": expected["qa6_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "lineage": lineage,
        "readiness": readiness,
        "typed_evidence": typed,
        "routing": routing,
        "aggregation": aggregation,
        "structural": structural,
        "fixtures": fixtures,
        "diagnostics": diagnostics,
        "leakage": leakage,
        "freeze": freeze,
        "isolation": isolation,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _required_diagnostics() -> dict[str, dict[str, Any]]:
    return {
        "strict_2000": run_shadow_aggregation_diagnostics(
            as_of="2000-03-31", data_mode="vintage_as_of"
        ),
        "strict_2008": run_shadow_aggregation_diagnostics(
            as_of="2008-09-30", data_mode="vintage_as_of"
        ),
        "strict_2019": run_shadow_aggregation_diagnostics(
            as_of="2019-12-31", data_mode="vintage_as_of"
        ),
        "revised_2019": run_shadow_aggregation_diagnostics(
            as_of="2019-12-31", data_mode="revised"
        ),
    }


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != value:
            return False
    checks = (
        summary["lineage"]["silent_freeze_rewrite_count"] == 0
        and summary["readiness"]["raw_transform_only_mislabeled_evaluable_count"] == 0
        and summary["typed_evidence"]["untyped_role_count"] == 0
        and summary["routing"]["prohibited_cross_layer_route_count"] == 0
        and summary["aggregation"]["equal_weight_aggregation_count"] == 0
        and summary["fixtures"]["structural_fixture_pass_count"]
        == summary["fixtures"]["structural_fixture_count"]
        and summary["leakage"]["aggregation_rule_scenario_id_reference_count"] == 0
        and summary["freeze"]["aggregation_freeze_hash_valid"] is True
        and summary["isolation"]["production_behavior_change_count"] == 0
    )
    return checks


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "qa6_shadow_aggregation_closure"
    ]["expected_status"]
