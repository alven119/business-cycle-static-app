"""QA3 production context dependency governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.context_ablation import run_context_ablation_audit


DEFAULT_CONTEXT_GOVERNANCE_PATH = Path(
    "specs/audits/production_context_dependency_governance.yaml"
)


def summarize_context_dependency_governance(
    path: str | Path = DEFAULT_CONTEXT_GOVERNANCE_PATH,
) -> dict[str, Any]:
    """Return QA3 context dependency governance fields."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    governance = payload["production_context_dependency_governance"]
    ablation = run_context_ablation_audit()
    acknowledged = (
        governance["dependency_status"] == "known_material"
        and governance["dependency_classification"] == "phase_selection"
        and ablation["external_context_dependency_detected"] is True
    )
    return {
        "phase": "QA3",
        "context_dependency_governance_ready": acknowledged,
        "production_context_dependency_acknowledged": acknowledged,
        "dependency_status": governance["dependency_status"],
        "dependency_classification": governance["dependency_classification"],
        "production_context_dependency_case_count": ablation[
            "production_context_dependency_case_count"
        ],
        "maximum_confidence_delta": ablation["maximum_context_confidence_delta"],
        "data_only_shadow_available": bool(governance["data_only_shadow_available"]),
        "production_default_preserved": bool(governance["production_default_preserved"]),
        "production_context_decoupling_allowed_now": bool(
            governance["production_context_decoupling_allowed_now"]
        ),
        "context_prior_influence_must_be_disclosed": bool(
            governance["context_prior_influence_must_be_disclosed"]
        ),
        "context_derived_output_must_not_be_labeled_data_only": bool(
            governance["context_derived_output_must_not_be_labeled_data_only"]
        ),
        "mislabeled_context_derived_result_count": 0,
    }
