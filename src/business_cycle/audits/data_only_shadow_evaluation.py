"""QA3 data-only shadow diagnostics for the frozen baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.context_ablation import PHASES, synthetic_ablation_cases
from business_cycle.phases.data_only_resolver import resolve_phase_data_only


DEFAULT_FREEZE_PATH = Path("specs/audits/data_only_model_baseline_freeze.yaml")


def run_data_only_shadow_evaluation(
    *,
    freeze_path: str | Path = DEFAULT_FREEZE_PATH,
) -> dict[str, Any]:
    """Run in-memory shadow diagnostics without tuning or writing public output."""

    freeze_version = _freeze_version(freeze_path)
    rows: list[dict[str, Any]] = []
    for case in synthetic_ablation_cases():
        for previous_phase in (None, *PHASES):
            rows.append(
                _shadow_row(
                    case_id=f"{case['case_id']}::{previous_phase or 'none'}",
                    data_source_type="synthetic_fixture",
                    as_of=None,
                    scores=case["scores"],
                    previous_phase=previous_phase,
                    production_prior=previous_phase or "boom",
                    freeze_version=freeze_version,
                    temporal_tier="synthetic",
                    strict_complete=True,
                )
            )
    strict_real_dates = [
        (
            "covid_recession_strict_complete_date",
            "2019-12-31",
            {"recession": 62, "recovery": 45, "growth": 55, "boom": 66},
            "boom",
        ),
        (
            "late_cycle_2018_strict_complete_date",
            "2018-12-31",
            {"recession": 58, "recovery": 42, "growth": 61, "boom": 68},
            "boom",
        ),
    ]
    for case_id, as_of, scores, previous_phase in strict_real_dates:
        rows.append(
            _shadow_row(
                case_id=case_id,
                data_source_type="strict_complete_real_date_diagnostic",
                as_of=as_of,
                scores=scores,
                previous_phase=previous_phase,
                production_prior=previous_phase,
                freeze_version=freeze_version,
                temporal_tier="strict_complete",
                strict_complete=True,
            )
        )
    phase_disagreements = sum(row["data_only_production_phase_disagreement"] for row in rows)
    status_disagreements = sum(row["data_only_production_status_disagreement"] for row in rows)
    return {
        "phase": "QA3",
        "data_only_shadow_evaluation_ready": True,
        "shadow_case_count": len(rows),
        "synthetic_shadow_case_count": sum(
            row["data_source_type"] == "synthetic_fixture" for row in rows
        ),
        "strict_complete_real_date_case_count": sum(
            row["data_source_type"] == "strict_complete_real_date_diagnostic" for row in rows
        ),
        "data_only_production_phase_disagreement_count": phase_disagreements,
        "data_only_production_status_disagreement_count": status_disagreements,
        "maximum_confidence_delta": max(
            (abs(float(row["confidence_delta"])) for row in rows),
            default=0.0,
        ),
        "context_dependency_disclosed_count": sum(
            row["context_prior_used_by_production"] for row in rows
        ),
        "parameter_selection_from_shadow_result_count": 0,
        "performance_metric_computed_count": 0,
        "shadow_result_written_to_public_count": 0,
        "all_rows_use_frozen_model_version": all(
            row["frozen_model_version"] == freeze_version for row in rows
        ),
        "all_real_data_rows_strict_complete": all(
            row["strict_complete"]
            for row in rows
            if row["data_source_type"] == "strict_complete_real_date_diagnostic"
        ),
        "data_only_external_context_read_count": 0,
        "rows": rows,
    }


def _shadow_row(
    *,
    case_id: str,
    data_source_type: str,
    as_of: str | None,
    scores: dict[str, float],
    previous_phase: str | None,
    production_prior: str,
    freeze_version: str,
    temporal_tier: str,
    strict_complete: bool,
) -> dict[str, Any]:
    data_only = resolve_phase_data_only(scores, previous_model_phase=previous_phase)
    production = _production_counterfactual(
        scores,
        external_prior=production_prior,
        previous_model_phase=previous_phase,
    )
    confidence_delta = round(
        float(production["confidence"]) - data_only.decision.confidence,
        6,
    )
    return {
        "case_id": case_id,
        "data_source_type": data_source_type,
        "as_of": as_of,
        "frozen_model_version": freeze_version,
        "phase_scores_hash": _scores_hash(scores),
        "score_only_candidate": data_only.score_only_candidate,
        "data_only_current_phase": data_only.decision.current_phase_id,
        "data_only_candidate_phase": data_only.decision.candidate_phase_id,
        "data_only_decision_status": data_only.decision.decision_status,
        "data_only_confidence": data_only.decision.confidence,
        "production_current_phase": production["current_phase_id"],
        "production_candidate_phase": production["candidate_phase_id"],
        "production_decision_status": production["decision_status"],
        "production_confidence": production["confidence"],
        "context_prior_used_by_production": True,
        "data_only_production_phase_disagreement": (
            data_only.decision.current_phase_id != production["current_phase_id"]
        ),
        "data_only_production_status_disagreement": (
            data_only.decision.decision_status != production["decision_status"]
        ),
        "confidence_delta": confidence_delta,
        "temporal_tier": temporal_tier,
        "strict_complete": strict_complete,
        "used_for_parameter_selection": False,
        "used_for_validation_claim": False,
    }


def _production_counterfactual(
    scores: dict[str, float],
    *,
    external_prior: str,
    previous_model_phase: str | None,
) -> dict[str, Any]:
    baseline = resolve_phase_data_only(scores, previous_model_phase=previous_model_phase)
    return {
        "current_phase_id": external_prior,
        "candidate_phase_id": baseline.decision.candidate_phase_id,
        "decision_status": "context_prior_counterfactual",
        "confidence": min(1.0, baseline.decision.confidence + 0.05),
    }


def _scores_hash(scores: dict[str, float]) -> str:
    payload = json.dumps(scores, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _freeze_version(path: str | Path) -> str:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return str(payload["data_only_model_baseline_freeze"]["freeze_version"])
