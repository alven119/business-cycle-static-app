from __future__ import annotations

import os

import pytest
import requests

from business_cycle.data_sources.alfred_provider import AlfredProvider, AlfredProviderError


class FakeResponse:
    def __init__(self, payload: object, *, status_error: Exception | None = None) -> None:
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self) -> None:
        if self.status_error:
            raise self.status_error

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_fetch_observations_parses_output_type_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    session = FakeSession(
        [
            FakeResponse(
                {
                    "observations": [
                        {
                            "date": "2020-01-31",
                            "value": "1.0",
                            "realtime_start": "2020-02-15",
                            "realtime_end": "9999-12-31",
                        }
                    ]
                }
            )
        ]
    )

    provider = AlfredProvider(session=session)  # type: ignore[arg-type]
    rows = provider.fetch_observations("UNRATE", output_type=1)

    assert rows[0].realtime_start == "2020-02-15"
    assert session.calls[0]["params"]["units"] == "lin"  # type: ignore[index]


def test_retry_timeout_and_secret_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    session = FakeSession([requests.Timeout("timeout"), requests.Timeout("timeout")])
    provider = AlfredProvider(
        session=session,  # type: ignore[arg-type]
        max_retries=1,
        retry_sleep_seconds=0,
    )

    with pytest.raises(AlfredProviderError) as excinfo:
        provider.fetch_observations("UNRATE")

    assert "secret" not in str(excinfo.value)
    assert "api_key" not in str(excinfo.value)
    assert len(session.calls) == 2


def test_malformed_response_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret")
    provider = AlfredProvider(session=FakeSession([FakeResponse({"observations": [{}]})]))  # type: ignore[arg-type]

    with pytest.raises(AlfredProviderError):
        provider.fetch_observations("UNRATE")


def test_no_real_api_key_is_required_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    assert os.getenv("FRED_API_KEY") is None
