from __future__ import annotations

from business_cycle.data_sources.census_retail_sales_archive import (
    RetailSalesEstimate,
    select_retail_sales_estimate_as_of,
)


def test_rsafs_selector_hides_benchmark_revision_before_release_date() -> None:
    estimates = [
        RetailSalesEstimate(
            release_date="2008-09-12",
            reference_month="2008-08",
            estimate_stage="advance",
            value=380000.0,
            seasonal_adjustment="seasonally_adjusted",
            units="millions_of_dollars",
            source_artifact_id="advance",
        ),
        RetailSalesEstimate(
            release_date="2009-04-30",
            reference_month="2008-08",
            estimate_stage="benchmark_revision",
            value=381500.0,
            seasonal_adjustment="seasonally_adjusted",
            units="millions_of_dollars",
            source_artifact_id="benchmark",
        ),
    ]

    selected = select_retail_sales_estimate_as_of(
        estimates,
        as_of="2008-09-30",
        reference_month="2008-08",
    )

    assert selected is not None
    assert selected.estimate_stage == "advance"
    assert selected.value == 380000.0
