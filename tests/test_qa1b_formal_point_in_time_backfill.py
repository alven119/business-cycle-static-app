from __future__ import annotations

import scripts.update_point_in_time_data as updater
from business_cycle.data_sources.alfred_provider import AlfredObservation


def test_api_key_presence_is_reported_without_secret(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("FRED_API_KEY", "very-secret-value")

    class FakeProvider:
        last_request_count = 1
        last_pagination_count = 0

        def fetch_observations(self, series_id: str, **_kwargs: object) -> list[AlfredObservation]:
            return [
                AlfredObservation(
                    series_id=series_id,
                    observation_date="2020-01-31",
                    value="1.0",
                    realtime_start="2020-02-15",
                    realtime_end="9999-12-31",
                )
            ]

    monkeypatch.setattr(updater, "AlfredProvider", FakeProvider)
    updater.main(["--series-id", "UNRATE", "--cache-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert "fred_api_key_present=true" in output
    assert "secret_logged=false" in output
    assert "very-secret-value" not in output
