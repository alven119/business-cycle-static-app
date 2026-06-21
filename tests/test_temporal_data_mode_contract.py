from __future__ import annotations

from pathlib import Path

import yaml


def test_temporal_modes_keep_proxy_out_of_point_in_time() -> None:
    payload = yaml.safe_load(Path("specs/audits/temporal_data_mode_contract.yaml").read_text())
    modes = {
        mode["mode_id"]: mode
        for mode in payload["temporal_data_mode_contract"]["modes"]
    }

    assert set(modes) == {
        "revised",
        "release_lag_adjusted_revised_proxy",
        "initial_release_only",
        "vintage_as_of",
    }
    assert modes["release_lag_adjusted_revised_proxy"]["point_in_time"] is False
    assert modes["initial_release_only"]["point_in_time_first_release"] is True
    assert modes["initial_release_only"]["as_of_latest_vintage"] is False
    assert modes["vintage_as_of"]["point_in_time"] is True
    assert payload["temporal_data_mode_contract"]["as_of_policy"] == "end_of_day_date_precision"
