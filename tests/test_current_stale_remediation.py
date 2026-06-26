from __future__ import annotations

from business_cycle.current.current_data_refresh import (
    LIVE_OPERATOR_CONFIRMATION,
    build_current_data_refresh_manifest,
)
from business_cycle.current.current_stale_remediation import (
    summarize_current_stale_remediation,
)
from business_cycle.data_sources import SeriesObservation


class FreshProvider:
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        return [SeriesObservation(series_id=series_id, date="2099-12-31", value="1.0")]


def test_stale_remediation_keeps_thresholds_registered() -> None:
    summary = summarize_current_stale_remediation()

    assert summary["stale_remediation_ready"] is True
    assert summary["unresolved_safe_fixable_stale_issue_count"] == 0
    assert summary["stale_threshold_modified_count"] == 0
    assert summary["arbitrary_stale_threshold_added_count"] == 0
    assert summary["fixture_date_mislabeled_as_live_count"] == 0


def test_stale_remediation_recognizes_live_reduction(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("FRED_API_KEY", "secret-token")
    manifest = build_current_data_refresh_manifest(
        cache_dir=tmp_path / "cache",
        provider=FreshProvider(),
        execute_live=True,
        operator_confirmation=LIVE_OPERATOR_CONFIRMATION,
    )
    summary = summarize_current_stale_remediation(refresh_manifest=manifest)

    assert manifest["live_fetch_succeeded"] is True
    assert summary["stale_count_reduced"] is True
    assert summary["safe_fixable_stale_issue_count"] == 0
    assert summary["unresolved_safe_fixable_stale_issue_count"] == 0
