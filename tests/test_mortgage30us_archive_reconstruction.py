from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_mortgage30us_requires_pmms_methodology_and_archive_review() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "MORTGAGE30US"
    )

    assert row["preferred_reconstruction_method"] == "official_observational_archive"
    assert row["official_source_candidates"][0]["source_domain"] == "freddiemac.com"
    assert "current PMMS history plus weekly lag" in row["prohibited_shortcuts"]
    assert row["final_strict_ready"] is False
