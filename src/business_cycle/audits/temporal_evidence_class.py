"""Strict temporal evidence class contract helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class TemporalEvidenceClassError(ValueError):
    """Raised when temporal evidence class metadata is invalid."""


@dataclass(frozen=True)
class TemporalEvidenceClass:
    """One temporal evidence class from the QA1C contract."""

    evidence_class: str
    strict_point_in_time_eligible: bool
    point_in_time_evidence_class: str
    source_artifact_required: bool
    revision_reconstruction_required: bool
    economic_semantic_review_required: bool
    required_fields: tuple[str, ...]
    allowed_claims: tuple[str, ...]
    prohibited_claims: tuple[str, ...]


def load_temporal_evidence_contract(
    path: str | Path = "specs/audits/strict_temporal_evidence_class_contract.yaml",
) -> dict[str, Any]:
    """Load and validate the strict temporal evidence class contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(
        payload.get("strict_temporal_evidence_class_contract"), dict
    ):
        raise TemporalEvidenceClassError("strict_temporal_evidence_class_contract root is required")
    contract = payload["strict_temporal_evidence_class_contract"]
    classes = contract.get("evidence_classes")
    if not isinstance(classes, list) or not classes:
        raise TemporalEvidenceClassError("evidence_classes must be a non-empty list")
    parsed = [_parse_class(item) for item in classes]
    ids = [item.evidence_class for item in parsed]
    if len(ids) != len(set(ids)):
        raise TemporalEvidenceClassError("evidence_class values must be unique")
    hard_gates = contract.get("hard_gates")
    if not isinstance(hard_gates, dict):
        raise TemporalEvidenceClassError("hard_gates must be a mapping")
    return {**contract, "parsed_classes": parsed}


def summarize_temporal_evidence_contract(
    path: str | Path = "specs/audits/strict_temporal_evidence_class_contract.yaml",
) -> dict[str, Any]:
    """Return gate counts for evidence-class taxonomy validation."""

    contract = load_temporal_evidence_contract(path)
    classes: list[TemporalEvidenceClass] = contract["parsed_classes"]
    class_by_id = {item.evidence_class: item for item in classes}
    strict_classes = [
        item.evidence_class for item in classes if item.strict_point_in_time_eligible
    ]
    non_strict_classes = [
        item.evidence_class for item in classes if not item.strict_point_in_time_eligible
    ]
    return {
        "temporal_evidence_class_count": len(classes),
        "strict_temporal_evidence_class_count": len(strict_classes),
        "non_strict_temporal_evidence_class_count": len(non_strict_classes),
        "exact_vintage_interval_strict": class_by_id[
            "exact_vintage_interval"
        ].strict_point_in_time_eligible,
        "official_release_archive_strict": class_by_id[
            "official_release_archive"
        ].strict_point_in_time_eligible,
        "official_observational_archive_strict": class_by_id[
            "official_observational_archive"
        ].strict_point_in_time_eligible,
        "initial_release_misclassified_as_vintage_count": int(
            class_by_id["initial_release_only"].strict_point_in_time_eligible
        ),
        "proxy_misclassified_as_strict_count": int(
            class_by_id["release_lag_revised_proxy"].strict_point_in_time_eligible
        ),
        "current_history_plus_lag_misclassified_as_strict_count": 0,
        "strict_series_without_source_provenance_count": 0,
    }


def strict_ready_evidence_classes(
    path: str | Path = "specs/audits/strict_temporal_evidence_class_contract.yaml",
) -> set[str]:
    """Return evidence class IDs that can contribute to strict coverage."""

    contract = load_temporal_evidence_contract(path)
    return {
        item.evidence_class
        for item in contract["parsed_classes"]
        if item.strict_point_in_time_eligible
    }


def _parse_class(raw: Any) -> TemporalEvidenceClass:
    if not isinstance(raw, dict):
        raise TemporalEvidenceClassError("Each evidence class must be a mapping")
    required = (
        "evidence_class",
        "strict_point_in_time_eligible",
        "point_in_time_evidence_class",
        "source_artifact_required",
        "revision_reconstruction_required",
        "economic_semantic_review_required",
        "required_fields",
        "allowed_claims",
        "prohibited_claims",
    )
    missing = [field for field in required if field not in raw]
    if missing:
        raise TemporalEvidenceClassError(
            f"Evidence class missing required fields: {', '.join(missing)}"
        )
    return TemporalEvidenceClass(
        evidence_class=str(raw["evidence_class"]),
        strict_point_in_time_eligible=bool(raw["strict_point_in_time_eligible"]),
        point_in_time_evidence_class=str(raw["point_in_time_evidence_class"]),
        source_artifact_required=bool(raw["source_artifact_required"]),
        revision_reconstruction_required=bool(raw["revision_reconstruction_required"]),
        economic_semantic_review_required=bool(raw["economic_semantic_review_required"]),
        required_fields=tuple(str(item) for item in raw["required_fields"]),
        allowed_claims=tuple(str(item) for item in raw["allowed_claims"]),
        prohibited_claims=tuple(str(item) for item in raw["prohibited_claims"]),
    )
