from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_rsafs_requires_census_advance_release_archive() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "RSAFS"
    )

    assert row["preferred_reconstruction_method"] == "official_release_archive"
    assert row["official_source_candidates"][0]["source_domain"] == "census.gov"
    assert "current revised RSAFS plus fixed lag" in row["prohibited_shortcuts"]
    assert row["final_strict_ready"] is False
