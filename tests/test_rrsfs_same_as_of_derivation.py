from pathlib import Path

import scripts.derive_point_in_time_series as derive_script
from business_cycle.storage.point_in_time_cache import PointInTimeCache


def _write(cache: PointInTimeCache, series_id: str, value: str) -> None:
    cache.write_series(
        series_id,
        [
            {
                "series_id": series_id,
                "observation_date": "2020-02-01",
                "value": value,
                "realtime_start": "2020-03-15",
                "realtime_end": "9999-12-31",
            }
        ],
        query_mode="vintage_as_of",
        observation_start=None,
        observation_end=None,
        as_of_start=None,
        as_of_end=None,
    )


def test_rrsfs_derivation_cli_uses_same_as_of_inputs(tmp_path: Path, capsys) -> None:
    cache = PointInTimeCache(tmp_path)
    _write(cache, "RSAFS", "500000")
    _write(cache, "CPIAUCSL", "250")

    derive_script.main(
        [
            "--series-id",
            "RRSFS",
            "--as-of",
            "2020-03-31",
            "--no-write",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "rrsfs_provisional_snapshot_count=1" in output
    assert "rrsfs_strict_derived_snapshot_count=0" in output
    assert "temporal_evidence_class=derived_point_in_time" in output
    assert "revised_fallback=false" in output


def test_rrsfs_derivation_fails_closed_when_cpi_missing(tmp_path: Path, capsys) -> None:
    cache = PointInTimeCache(tmp_path)
    _write(cache, "RSAFS", "500000")

    derive_script.main(
        [
            "--series-id",
            "RRSFS",
            "--as-of",
            "2020-03-31",
            "--no-write",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "rrsfs_provisional_snapshot_count=0" in output
    assert "rrsfs_strict_derived_snapshot_count=0" in output
    assert "rrsfs_missing_pair_count=1" in output
