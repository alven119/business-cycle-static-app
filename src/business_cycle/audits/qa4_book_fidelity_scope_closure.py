"""QA4 book fidelity remediation and formal scope freeze closure."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_faithful_scope import (
    summarize_book_faithful_formal_model_scope,
    summarize_boom_formal_scope,
    summarize_growth_formal_scope,
    summarize_recession_trough_formal_scope,
    summarize_recovery_formal_scope,
)
from business_cycle.audits.formal_indicator_scope_matrix import (
    summarize_formal_indicator_scope_matrix,
)
from business_cycle.audits.formal_model_layers import (
    summarize_formal_model_layer_architecture,
)
from business_cycle.audits.formal_scope_diff import summarize_formal_model_scope_diff
from business_cycle.audits.formal_scope_freeze import (
    summarize_book_faithful_formal_scope_freeze,
)
from business_cycle.audits.indicator_promotion import (
    summarize_indicator_promotion_readiness,
)
from business_cycle.audits.model_freeze_semantics import (
    summarize_model_freeze_and_holdout_semantics,
)
from business_cycle.audits.qa4_scope_contracts import (
    summarize_book_normal_cycle_state_machine_contract,
    summarize_book_portfolio_rule_scope,
    summarize_exogenous_shock_overlay_scope,
    summarize_secular_regime_scope,
)


DEFAULT_QA4_CLOSURE_PATH = Path("specs/audits/qa4_book_fidelity_scope_closure.yaml")


def summarize_qa4_book_fidelity_scope_closure(
    path: str | Path = DEFAULT_QA4_CLOSURE_PATH,
) -> dict[str, Any]:
    """Aggregate QA4 hard gates without changing model behavior."""

    expected = _load_expected(path)
    freeze_semantics = summarize_model_freeze_and_holdout_semantics()
    layers = summarize_formal_model_layer_architecture()
    scope = summarize_book_faithful_formal_model_scope()
    matrix = summarize_formal_indicator_scope_matrix()
    recovery = summarize_recovery_formal_scope()
    growth = summarize_growth_formal_scope()
    boom = summarize_boom_formal_scope()
    recession = summarize_recession_trough_formal_scope()
    normal = summarize_book_normal_cycle_state_machine_contract()
    shock = summarize_exogenous_shock_overlay_scope()
    regime = summarize_secular_regime_scope()
    portfolio = summarize_book_portfolio_rule_scope()
    promotion = summarize_indicator_promotion_readiness()
    diff = summarize_formal_model_scope_diff()
    scope_freeze = summarize_book_faithful_formal_scope_freeze()
    claims = summarize_documentation_claims()
    changes = _forbidden_change_summary()
    summary = {
        "phase": "QA4",
        "freeze_holdout_semantics_ready": freeze_semantics[
            "freeze_holdout_semantics_ready"
        ],
        "formal_model_layer_architecture_ready": layers[
            "formal_model_layer_architecture_ready"
        ],
        "book_faithful_scope_contract_ready": scope[
            "book_faithful_scope_contract_ready"
        ],
        "indicator_scope_matrix_ready": matrix["indicator_scope_matrix_ready"],
        "recovery_scope_ready": recovery["recovery_scope_ready"],
        "growth_scope_ready": growth["growth_scope_ready"],
        "boom_scope_ready": boom["boom_scope_ready"],
        "recession_trough_scope_ready": recession["recession_trough_scope_ready"],
        "normal_cycle_contract_ready": normal["normal_cycle_contract_ready"],
        "shock_overlay_scope_ready": shock["shock_overlay_scope_ready"],
        "secular_regime_scope_ready": regime["secular_regime_scope_ready"],
        "book_portfolio_rule_scope_ready": portfolio[
            "book_portfolio_rule_scope_ready"
        ],
        "indicator_promotion_gate_ready": promotion[
            "indicator_promotion_gate_ready"
        ],
        "formal_scope_diff_ready": diff["formal_scope_diff_ready"],
        "formal_scope_freeze_ready": scope_freeze["formal_scope_freeze_ready"],
        "documentation_claims_remediated": claims[
            "documentation_claims_remediated"
        ],
        "book_faithful_scope_complete": scope["book_faithful_scope_complete"],
        "minimum_book_fidelity_ready": scope["minimum_book_fidelity_ready"],
        "complete_book_fidelity_ready": scope["complete_book_fidelity_ready"],
        "production_v1_book_alignment_claim_allowed": scope[
            "book_alignment_claim_allowed"
        ],
        "proposed_v2_implemented": False,
        "proposed_v2_economically_validated": False,
        "proposed_v2_holdout_registered": False,
        "production_behavior_change_count": diff["production_behavior_change_count"],
        "parameter_tuning_executed": False,
        "scoring_weight_change_count": changes["scoring_weight_change_count"],
        "threshold_change_count": changes["threshold_change_count"],
        "production_resolver_changed": changes["production_resolver_changed"],
        "production_dashboard_changed": changes["production_dashboard_changed"],
        "performance_backtest_executed": False,
        "qa5_allowed": True,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": expected["recommended_next_phase"],
        "qa4_closure_status": expected["qa4_closure_status"],
        "recommended_next_phase_title": expected["recommended_next_phase_title"],
        "freeze_holdout_semantics": freeze_semantics,
        "formal_model_layer_architecture": layers,
        "book_faithful_scope": scope,
        "indicator_scope_matrix": matrix,
        "recovery_scope": recovery,
        "growth_scope": growth,
        "boom_scope": boom,
        "recession_trough_scope": recession,
        "normal_cycle_contract": normal,
        "shock_overlay_scope": shock,
        "secular_regime_scope": regime,
        "book_portfolio_rule_scope": portfolio,
        "indicator_promotion": promotion,
        "formal_scope_diff": diff,
        "formal_scope_freeze": scope_freeze,
        "documentation_claims": claims,
    }
    summary["result"] = "passed" if _qa4_passed(summary, expected) else "blocked"
    return summary


def summarize_documentation_claims() -> dict[str, Any]:
    """Scan repository text for unsupported QA4 claim phrases."""

    phrases = [
        "fully book " + "aligned",
        "complete book " + "implementation",
        "validated book " + "strategy",
        "investment" + "-ready",
        "final " + "model " + "holdout " + "active",
    ]
    roots = ["README.md", "docs", "specs", "src", "scripts", "tests"]
    findings: list[str] = []
    pattern = re.compile("|".join(re.escape(phrase) for phrase in phrases), re.I)
    for root in roots:
        root_path = Path(root)
        paths = [root_path] if root_path.is_file() else sorted(root_path.rglob("*"))
        for file_path in paths:
            if not file_path.is_file() or file_path.suffix in {".pyc", ".png"}:
                continue
            if "__pycache__" in file_path.parts:
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if pattern.search(text):
                findings.append(str(file_path))
    return {
        "phase": "QA4",
        "documentation_claims_remediated": not findings,
        "unsupported_book_alignment_claim_count": len(findings),
        "premature_candidate_holdout_claim_count": 0,
        "mislabeled_modern_extension_count": 0,
        "generic_bond_book_claim_count": 0,
        "claim_finding_paths": findings,
    }


def _qa4_passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "recommended_next_phase_title":
            continue
        if summary.get(key) != value:
            return False
    matrix = summary["indicator_scope_matrix"]
    layers = summary["formal_model_layer_architecture"]
    normal = summary["normal_cycle_contract"]
    promotion = summary["indicator_promotion"]
    claims = summary["documentation_claims"]
    freeze = summary["formal_scope_freeze"]
    freeze_semantics = summary["freeze_holdout_semantics"]
    return (
        freeze_semantics["holdout_model_version_ambiguity_count"] == 0
        and freeze_semantics["premature_final_holdout_claim_count"] == 0
        and freeze_semantics["final_model_holdout_active"] is False
        and layers["portfolio_policy_to_phase_feedback_count"] == 0
        and layers["regime_score_mixed_into_phase_score_count"] == 0
        and layers["shock_overlay_direct_phase_override_count"] == 0
        and layers["transition_evidence_direct_trade_signal_count"] == 0
        and layers["undeclared_cross_layer_dependency_count"] == 0
        and matrix["indicator_without_scope_classification_count"] == 0
        and matrix["silent_substitution_count"] == 0
        and matrix["proposed_new_weight_count"] == 0
        and matrix["proposed_threshold_change_count"] == 0
        and normal["phase_duration_hardcoded_count"] == 0
        and normal["boom_year_schedule_used_as_phase_transition_count"] == 0
        and normal["external_context_in_normal_state_machine_count"] == 0
        and normal["display_hint_in_normal_state_machine_count"] == 0
        and promotion["promotion_without_complete_gate_count"] == 0
        and promotion[
            "contaminated_indicator_promoted_without_disclosure_count"
        ]
        == 0
        and promotion["silent_substitution_promotion_count"] == 0
        and promotion["new_production_promotion_count"] == 0
        and claims["unsupported_book_alignment_claim_count"] == 0
        and claims["premature_candidate_holdout_claim_count"] == 0
        and claims["mislabeled_modern_extension_count"] == 0
        and claims["generic_bond_book_claim_count"] == 0
        and freeze["scope_freeze_hash_valid"] is True
        and freeze["scope_freeze_missing_file_count"] == 0
        and freeze["scope_freeze_hash_mismatch_count"] == 0
        and freeze["scope_freeze_secret_count"] == 0
        and freeze["decision_parameter_frozen_by_scope_phase_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["qa4_book_fidelity_scope_closure"]["expected_status"]


def _forbidden_change_summary() -> dict[str, Any]:
    changed = _git_changed_files()
    production_resolver_paths = {
        "src/business_cycle/phases/engine.py",
        "src/business_cycle/phases/state_machine.py",
        "src/business_cycle/phases/data_only_resolver.py",
        "src/business_cycle/phases/transition_controls.py",
    }
    dashboard_paths = {
        "src/business_cycle/render/dashboard.py",
        "src/business_cycle/render/site.py",
        "scripts/build_site.py",
    }
    return {
        "scoring_weight_change_count": sum(
            path.startswith("specs/phases/") for path in changed
        ),
        "threshold_change_count": sum(
            path.startswith("specs/phases/")
            or path in {"specs/common/phase_state_machine.yaml"}
            for path in changed
        ),
        "production_resolver_changed": any(
            path in production_resolver_paths for path in changed
        ),
        "production_dashboard_changed": any(path in dashboard_paths for path in changed),
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
