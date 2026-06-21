from __future__ import annotations

from pathlib import Path

import scripts.update_point_in_time_data as updater
from business_cycle.data_sources.alfred_provider import AlfredObservation, AlfredProviderError
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def test_dgs10_full_range_failure_uses_segmented_modern_repair(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")

    class FakeProvider:
        def __init__(self) -> None:
            self.last_request_count = 0
            self.last_pagination_count = 0
            self.last_http_status = 200
            self.last_response_content_type = "application/json"
            self.last_response_byte_count = 100
            self.last_error_class = None

        def fetch_observations(self, series_id: str, **kwargs: object) -> list[AlfredObservation]:
            self.last_request_count = 1
            self.last_pagination_count = 0
            observation_start = str(kwargs["observation_start"])
            realtime_start = str(kwargs["realtime_start"])
            realtime_end = str(kwargs["realtime_end"])
            if realtime_start == "2005-06-28" and realtime_end == "2021-12-31":
                self.last_error_class = "Timeout"
                raise AlfredProviderError("full range too large")
            return [
                AlfredObservation(
                    series_id=series_id,
                    observation_date=observation_start,
                    value="4.0",
                    realtime_start=realtime_start,
                    realtime_end="9999-12-31",
                )
            ]

    monkeypatch.setattr(updater, "AlfredProvider", FakeProvider)

    updater.main(
        [
            "--series-id",
            "DGS10",
            "--observation-start",
            "2005-06-28",
            "--observation-end",
            "2021-12-31",
            "--as-of-start",
            "2005-06-28",
            "--as-of-end",
            "2021-12-31",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "dgs10_modern_provider_ready=true" in output
    assert "dgs10_segment_query_count=4" in output
    assert "dgs10_segment_query_failure_count=0" in output
    assert "per_as_of_network_request_count=0" in output
    assert PointInTimeCache(tmp_path).read_series("DGS10").manifest["row_count"] == 4
