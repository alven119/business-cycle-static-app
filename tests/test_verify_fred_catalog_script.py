from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.verify_fred_catalog as verify_script
from business_cycle.indicators.series_verification import SeriesVerificationResult


def test_main_without_fred_api_key_exits_with_clear_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.setattr(verify_script, "load_dotenv", lambda: None)
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        verify_script.main(["--catalog-path", str(catalog_path)])

    assert exc_info.value.code == 1
    assert "FRED_API_KEY is not set" in capsys.readouterr().err


def test_write_results_outputs_serializable_json(tmp_path: Path) -> None:
    output_path = tmp_path / "verification.json"
    results = [
        SeriesVerificationResult(
            indicator_id="unemployment_rate",
            series_id="UNRATE",
            provider="fred",
            status="ok",
            observations_count=2,
            first_date="2020-01-01",
            last_date="2020-02-01",
            message="ok",
        )
    ]

    verify_script.write_results(output_path, results)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"] == {
        "total": 1,
        "ok": 1,
        "failed": 0,
        "missing": 0,
        "unsupported": 0,
    }
    assert payload["results"][0]["series_id"] == "UNRATE"


def test_filter_catalog_entries_by_indicator_and_series() -> None:
    entries = [
        {
            "indicator_id": "unemployment_rate",
            "provider": "fred",
            "candidate_series": [{"provider": "fred", "series_id": "UNRATE"}],
        },
        {
            "indicator_id": "real_retail_sales",
            "provider": "fred",
            "candidate_series": [
                {"provider": "fred", "series_id": "RRSFS"},
                {"provider": "fred", "series_id": "RSAFS"},
            ],
        },
    ]

    filtered = verify_script.filter_catalog_entries(
        entries,
        indicator_ids=["real_retail_sales"],
        series_ids=["RSAFS"],
    )

    assert len(filtered) == 1
    assert filtered[0]["indicator_id"] == "real_retail_sales"
    assert filtered[0]["candidate_series"] == [{"provider": "fred", "series_id": "RSAFS"}]

