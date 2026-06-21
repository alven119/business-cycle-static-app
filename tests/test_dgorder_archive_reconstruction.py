from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_dgorder_requires_advance_and_revision_release_archive() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "DGORDER"
    )

    assert row["preferred_reconstruction_method"] == "official_release_archive"
    assert row["official_source_candidates"][0]["source_domain"] == "census.gov"
    assert "full report revision before publication" in row["prohibited_shortcuts"]
    assert row["final_strict_ready"] is False
