from __future__ import annotations

from pathlib import Path

import yaml


def test_all_discovered_series_have_availability_status() -> None:
    payload = yaml.safe_load(Path("specs/common/series_release_lag_registry.yaml").read_text())
    rows = payload["series_release_lag_registry"]["series"]

    assert len(rows) == 38
    assert all(row.get("temporal_status") for row in rows)
    assert all("point_in_time_eligible" in row for row in rows)
    assert payload["series_release_lag_registry"]["summary"][
        "series_missing_availability_metadata_count"
    ] == 0


def test_derived_series_requires_input_strictness() -> None:
    payload = yaml.safe_load(Path("specs/common/series_release_lag_registry.yaml").read_text())
    derived = [
        row
        for row in payload["series_release_lag_registry"]["series"]
        if str(row["series_id"]).startswith("derived:")
    ]

    assert derived
    assert all(row["availability_rule"] == "max_input_availability" for row in derived)
    assert all(row["vintage_rule"] == "all_inputs_same_as_of_snapshot" for row in derived)
