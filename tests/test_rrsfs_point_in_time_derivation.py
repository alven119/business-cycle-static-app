from __future__ import annotations

from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_rrsfs_point_in_time_derivation_requires_same_as_of_inputs() -> None:
    row = next(
        item
        for item in load_formal_temporal_gap_remediation()["rows"]
        if item["series_id"] == "RRSFS"
    )

    assert row["preferred_reconstruction_method"] == "derived_point_in_time"
    assert row["rrsfs_underlying_series"] == ["RSAFS", "CPIAUCSL"]
    assert row["rrsfs_formula_validated"] is False
    assert row["dependency_graph_changed"] is False
    assert row["final_strict_ready"] is False
