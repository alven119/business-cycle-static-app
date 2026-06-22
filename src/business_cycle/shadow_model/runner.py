"""Runner for the QA5 shadow evidence model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.shadow_model.contracts import load_shadow_model_spec
from business_cycle.shadow_model.phase_profiles import build_phase_profiles
from business_cycle.shadow_model.role_evidence import build_role_evidence


def run_shadow_evidence_model(
    *,
    as_of: str,
    data_mode: str,
    output: str | Path | None = None,
    context_prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the shadow-only evidence model and optionally write JSON outside repo output paths."""

    if context_prior:
        raise ValueError("context prior is prohibited for the shadow evidence model")
    spec = load_shadow_model_spec()
    role_evidence = build_role_evidence(as_of=as_of, data_mode=data_mode)
    phase_profiles = build_phase_profiles(role_evidence)
    summary = _summary(spec, as_of, data_mode, role_evidence, phase_profiles)
    result = {
        **summary,
        "role_evidence": role_evidence,
        "phase_profiles": phase_profiles,
    }
    if output is not None:
        output_path = Path(output)
        if _is_prohibited_output_path(output_path):
            raise ValueError("shadow diagnostics may not write data/backtests or public")
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    return result


def _summary(
    spec: dict[str, Any],
    as_of: str,
    data_mode: str,
    role_evidence: list[dict[str, Any]],
    phase_profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    role_counts = _count_statuses(role_evidence)
    profile_counts = _count_profiles(phase_profiles)
    return {
        "model_id": spec["model_id"],
        "as_of": as_of,
        "data_mode": data_mode,
        "role_evidence_count": len(role_evidence),
        "phase_profile_count": len(phase_profiles),
        "complete_role_count": role_counts["complete"],
        "partial_role_count": role_counts["partial"],
        "unavailable_role_count": role_counts["unavailable"],
        "invalid_role_count": role_counts["invalid"],
        "raw_transform_only_count": role_counts["raw_transform_only"],
        "complete_phase_profile_count": profile_counts["complete"],
        "partial_phase_profile_count": profile_counts["partial"],
        "strict_fallback_count": 0,
        "context_prior_used_count": 0,
        "formal_candidate_phase_computed": False,
        "known_label_used_for_parameter_selection": False,
        "performance_metric_computed": False,
        "public_output_written": False,
        "production_behavior_changed": False,
    }


def _count_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "complete": sum(
            row["evidence_status"] in {"supportive", "contradictory", "neutral"}
            for row in rows
        ),
        "partial": sum(row["evidence_status"] == "raw_transform_only" for row in rows),
        "unavailable": sum(row["evidence_status"] == "unavailable" for row in rows),
        "invalid": sum(row["evidence_status"] == "invalid" for row in rows),
        "raw_transform_only": sum(
            row["evidence_status"] == "raw_transform_only" for row in rows
        ),
    }


def _count_profiles(profiles: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "complete": sum(
            profile["shadow_profile_status"] == "complete_evidence_profile"
            for profile in profiles
        ),
        "partial": sum(
            profile["shadow_profile_status"] == "partial_evidence_profile"
            for profile in profiles
        ),
    }


def _is_prohibited_output_path(path: Path) -> bool:
    normalized = path.as_posix()
    return normalized.startswith("data/backtests") or normalized.startswith("public")

