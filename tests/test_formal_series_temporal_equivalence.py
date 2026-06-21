from __future__ import annotations

from business_cycle.audits.temporal_equivalence import (
    summarize_formal_series_temporal_equivalence,
)


def test_formal_series_temporal_equivalence_rejects_unapproved_substitution() -> None:
    summary = summarize_formal_series_temporal_equivalence()

    assert summary["remediation_series_count"] == 7
    assert summary["proposed_substitution_count"] == 1
    assert summary["approved_feature_gated_substitution_count"] == 0
    assert summary["silent_substitution_count"] == 0
    assert summary["rejected_substitution_count"] == 1
    assert "DGS10" in summary["unresolved_formal_series_ids"]
