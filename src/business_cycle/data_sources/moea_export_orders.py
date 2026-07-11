"""Official Taiwan MOEA export-order CSV adapter for research-only use."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import csv
import io
from typing import Protocol

import requests

from business_cycle.data_sources import SeriesObservation


class HttpResponse(Protocol):
    content: bytes

    def raise_for_status(self) -> None: ...


@dataclass(frozen=True)
class MoeaExportOrderSeries:
    series_id: str
    product_name_zh: str
    source_url: str


SERIES = {
    "TW_MOEA_ICT_EXPORT_ORDERS": MoeaExportOrderSeries(
        series_id="TW_MOEA_ICT_EXPORT_ORDERS",
        product_name_zh="資訊與通信產品",
        source_url=(
            "https://service.moea.gov.tw/EE520/opendata/"
            "經濟部統計處_外銷訂單_資訊通訊產品.csv"
        ),
    ),
    "TW_MOEA_ELECTRONICS_EXPORT_ORDERS": MoeaExportOrderSeries(
        series_id="TW_MOEA_ELECTRONICS_EXPORT_ORDERS",
        product_name_zh="電子產品",
        source_url=(
            "https://service.moea.gov.tw/EE520/opendata/"
            "經濟部統計處_外銷訂單_電子產品.csv"
        ),
    ),
}


class MoeaExportOrdersProvider:
    """Fetch and validate licensed official CSV resources without credentials."""

    def __init__(self, *, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_series_observations(self, series_id: str) -> list[SeriesObservation]:
        definition = SERIES.get(series_id)
        if definition is None:
            raise ValueError(f"unsupported MOEA export-order series: {series_id}")
        response = requests.get(definition.source_url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return parse_moea_export_orders_csv(response.content, definition=definition)


def parse_moea_export_orders_csv(
    content: bytes,
    *,
    definition: MoeaExportOrderSeries,
) -> list[SeriesObservation]:
    """Parse a BOM-aware MOEA CSV and convert ROC YYYYMM to ISO month dates."""

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    expected = {"統計項目", "貨品別", "資料期(民國年)", "統計值(金額)", "計量單位"}
    if not reader.fieldnames or not expected <= set(reader.fieldnames):
        raise ValueError("MOEA export-order CSV schema mismatch")
    rows: dict[str, SeriesObservation] = {}
    for row in reader:
        if row["貨品別"].strip() != definition.product_name_zh:
            raise ValueError("MOEA export-order product identity mismatch")
        if row["統計項目"].strip() != "外銷訂單金額_美元":
            raise ValueError("MOEA export-order measure identity mismatch")
        if row["計量單位"].strip() != "百萬美元":
            raise ValueError("MOEA export-order unit mismatch")
        period = row["資料期(民國年)"].strip()
        if len(period) != 5 or not period.isdigit():
            raise ValueError("MOEA export-order period must be ROC YYYMM")
        year = int(period[:3]) + 1911
        month = int(period[3:])
        observation_date = date(year, month, 1).isoformat()
        value = row["統計值(金額)"].strip().replace(",", "")
        if not value or not value.replace(".", "", 1).isdigit():
            raise ValueError("MOEA export-order value is not numeric")
        rows[observation_date] = SeriesObservation(
            series_id=definition.series_id,
            date=observation_date,
            value=value,
        )
    if len(rows) < 24:
        raise ValueError("MOEA export-order history is unexpectedly short")
    return [rows[key] for key in sorted(rows)]
