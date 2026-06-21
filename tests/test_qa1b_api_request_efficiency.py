from __future__ import annotations

import pytest

from business_cycle.data_sources.alfred_provider import AlfredProvider


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.headers: dict[str, str] = {}
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self.payload


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def get(self, _url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        self.calls.append(dict(params))
        offset = int(params["offset"])
        observations = [
            {
                "date": f"2020-0{offset + 1}-01",
                "value": "1.0",
                "realtime_start": "2020-02-01",
                "realtime_end": "9999-12-31",
            }
        ]
        return FakeResponse(
            {
                "count": 3,
                "limit": 1,
                "offset": offset,
                "observations": observations,
            }
        )


def test_pagination_is_series_bulk_not_per_as_of(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    session = FakeSession()
    provider = AlfredProvider(session=session, page_limit=1)  # type: ignore[arg-type]

    rows = provider.fetch_observations(
        "UNRATE",
        observation_start="2020-01-01",
        observation_end="2020-12-31",
        realtime_start="1776-07-04",
        realtime_end="2020-12-31",
    )

    assert len(rows) == 3
    assert provider.last_request_count == 3
    assert provider.last_pagination_count == 2
    assert {call["series_id"] for call in session.calls} == {"UNRATE"}
