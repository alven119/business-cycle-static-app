"""Formal series temporal/economic equivalence audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TemporalEquivalenceAuditError(ValueError):
    """Raised when the formal temporal remediation matrix is invalid."""


def load_formal_temporal_gap_remediation(
    path: str | Path = "specs/audits/formal_temporal_gap_remediation.yaml",
) -> dict[str, Any]:
    """Load QA1C formal temporal gap remediation matrix."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(
        payload.get("formal_temporal_gap_remediation"), dict
    ):
        raise TemporalEquivalenceAuditError("formal_temporal_gap_remediation root is required")
    matrix = payload["formal_temporal_gap_remediation"]
    rows = matrix.get("rows")
    if not isinstance(rows, list) or not rows:
        raise TemporalEquivalenceAuditError("formal_temporal_gap_remediation.rows is required")
    ids = [str(row.get("series_id")) for row in rows if isinstance(row, dict)]
    if len(ids) != len(set(ids)):
        raise TemporalEquivalenceAuditError("series_id values must be unique")
    return matrix


def summarize_formal_series_temporal_equivalence(
    path: str | Path = "specs/audits/formal_temporal_gap_remediation.yaml",
) -> dict[str, Any]:
    """Summarize explicit substitution/equivalence decisions."""

    matrix = load_formal_temporal_gap_remediation(path)
    rows = matrix["rows"]
    proposed = [row for row in rows if row.get("proposed_substitute_series")]
    temporal_equivalent = [
        row for row in proposed if row.get("temporal_equivalence_status") is True
    ]
    economic_equivalent = [
        row for row in proposed if row.get("economic_equivalence_status") is True
    ]
    signal_equivalent = [row for row in proposed if row.get("signal_equivalence_status") is True]
    approved = [
        row
        for row in proposed
        if row.get("temporal_equivalence_status") is True
        and row.get("economic_equivalence_status") is True
        and row.get("signal_equivalence_status") is True
        and row.get("approved_feature_gated_substitution") is True
    ]
    silent = [
        row
        for row in rows
        if row.get("proposed_substitute_series")
        and not row.get("temporal_equivalence_status")
        and row.get("approved_feature_gated_substitution") is True
    ]
    rejected = [row for row in proposed if row not in approved]
    return {
        "remediation_series_count": len(rows),
        "proposed_substitution_count": len(proposed),
        "temporally_equivalent_substitution_count": len(temporal_equivalent),
        "economically_equivalent_substitution_count": len(economic_equivalent),
        "signal_equivalent_substitution_count": len(signal_equivalent),
        "approved_feature_gated_substitution_count": len(approved),
        "silent_substitution_count": len(silent),
        "rejected_substitution_count": len(rejected),
        "unresolved_formal_series_ids": [
            str(row["series_id"]) for row in rows if not row.get("final_strict_ready")
        ],
        "result": "passed" if not silent else "failed",
    }
