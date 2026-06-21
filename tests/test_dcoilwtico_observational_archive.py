from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_dcoilwtico_observational_archive_requires_availability_and_revision_policy() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "DCOILWTICO"
    )

    assert row["preferred_reconstruction_method"] == "official_observational_archive"
    assert row["official_source_candidates"][0]["source_domain"] == "eia.gov"
    assert "current history plus one-day lag" in row["prohibited_shortcuts"]
    assert row["final_strict_ready"] is False
