from business_cycle.audits.temporal_equivalence import load_formal_temporal_gap_remediation


def test_rrsfs_derivation_remains_blocked_until_same_as_of_inputs_are_strict() -> None:
    rows = load_formal_temporal_gap_remediation()["rows"]
    row = next(item for item in rows if item["series_id"] == "RRSFS")

    assert row["rrsfs_proposed_dependency_class"] == "derived"
    assert row["rrsfs_underlying_series"] == ["RSAFS", "CPIAUCSL"]
    assert row["rrsfs_point_in_time_reconstruction_ready"] is False
    assert row["final_strict_ready"] is False
