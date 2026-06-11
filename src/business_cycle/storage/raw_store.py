"""Filesystem raw data cache."""

from __future__ import annotations

import csv
from pathlib import Path

from business_cycle.data_sources.base import SeriesObservation


class RawCsvStore:
    """Store raw provider observations as CSV files."""

    def __init__(self, root_dir: str | Path = "data/raw") -> None:
        self.root_dir = Path(root_dir)

    def path_for(self, provider: str, series_id: str) -> Path:
        clean_provider = provider.strip().lower()
        clean_series_id = series_id.strip().upper()
        return self.root_dir / clean_provider / f"{clean_series_id}.csv"

    def exists(self, provider: str, series_id: str) -> bool:
        return self.path_for(provider, series_id).exists()

    def write_observations(
        self,
        provider: str,
        series_id: str,
        observations: list[SeriesObservation],
    ) -> Path:
        path = self.path_for(provider, series_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=["series_id", "date", "value", "realtime_start", "realtime_end"],
            )
            writer.writeheader()
            for observation in observations:
                writer.writerow(
                    {
                        "series_id": observation.series_id,
                        "date": observation.date,
                        "value": observation.value,
                        "realtime_start": observation.realtime_start or "",
                        "realtime_end": observation.realtime_end or "",
                    }
                )
        return path

    def read_observations(self, provider: str, series_id: str) -> list[SeriesObservation]:
        path = self.path_for(provider, series_id)
        with path.open("r", newline="", encoding="utf-8") as csv_file:
            return [
                SeriesObservation(
                    series_id=row["series_id"],
                    date=row["date"],
                    value=row["value"],
                    realtime_start=row.get("realtime_start") or None,
                    realtime_end=row.get("realtime_end") or None,
                )
                for row in csv.DictReader(csv_file)
            ]

