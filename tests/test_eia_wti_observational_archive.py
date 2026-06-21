from __future__ import annotations

from business_cycle.data_sources.eia_wti_observational_archive import (
    fetch_eia_wti_history,
    parse_eia_wti_history_html,
)


EIA_HTML = b"""
<html><body>
Cushing, OK WTI Spot Price FOB (Dollars per Barrel)
1986 Jan- 6 to Jan-10 26.53 25.85 25.87 26.03 25.65
1986 Jan-13 to Jan-17 25.08 24.97 25.18 23.98 23.63
Release Date: 6/17/2026
</body></html>
"""


def test_eia_wti_history_parser_extracts_dated_observations() -> None:
    observations, release_date = parse_eia_wti_history_html(EIA_HTML)

    assert release_date == "2026-06-17"
    assert len(observations) == 10
    assert observations[0].observation_date == "1986-01-06"
    assert observations[0].availability_date == "1986-01-07"
    assert observations[0].value == 26.53
    assert observations[0].correction_status == "official_history_candidate"


def test_eia_wti_fetch_uses_injected_official_response() -> None:
    def fake_opener(url: str, timeout_seconds: float) -> tuple[int, str, bytes]:
        assert "eia.gov" in url
        assert timeout_seconds > 0
        return 200, "text/html", EIA_HTML

    result = fetch_eia_wti_history(opener=fake_opener)

    assert result.status_code == 200
    assert result.parse_status == "parsed"
    assert len(result.observations) == 10
