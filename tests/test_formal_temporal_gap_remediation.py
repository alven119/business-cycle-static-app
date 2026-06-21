from __future__ import annotations

from business_cycle.audits.temporal_equivalence import (
    load_formal_temporal_gap_remediation,
)


def test_seven_formal_temporal_gap_rows_are_explicit_and_blocked() -> None:
    matrix = load_formal_temporal_gap_remediation()
    rows = matrix["rows"]

    assert {row["series_id"] for row in rows} == {
        "DCOILWTICO",
        "DGORDER",
        "DGS10",
        "ICSA",
        "MORTGAGE30US",
        "RRSFS",
        "RSAFS",
    }
    assert all(row["official_source_candidates"] for row in rows)
    assert all(row["point_in_time_evidence_class"] != "release_lag_revised_proxy" for row in rows)
    assert all(row["final_strict_ready"] is False for row in rows)
    assert all("current revised history plus arbitrary lag" in matrix["prohibited_shortcuts"] for _ in [0])


def test_rrsfs_derivation_is_proposed_but_not_silent_dependency_change() -> None:
    rows = load_formal_temporal_gap_remediation()["rows"]
    rrsfs = next(row for row in rows if row["series_id"] == "RRSFS")

    assert rrsfs["rrsfs_current_dependency_class"] == "direct"
    assert rrsfs["rrsfs_proposed_dependency_class"] == "derived"
    assert rrsfs["rrsfs_underlying_series"] == ["RSAFS", "CPIAUCSL"]
    assert rrsfs["dependency_graph_changed"] is False
    assert rrsfs["revised_default_unchanged"] is True
