from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_icsa_requires_weekly_claims_release_archive_not_lag_proxy() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "ICSA"
    )

    assert row["preferred_reconstruction_method"] == "official_release_archive"
    assert "current ICSA plus Thursday lag" in row["prohibited_shortcuts"]
    assert row["revision_behavior"].startswith("advance weekly value")
    assert row["final_strict_ready"] is False
