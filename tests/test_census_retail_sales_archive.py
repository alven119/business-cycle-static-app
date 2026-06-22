from business_cycle.data_sources.census_retail_sales_archive import RetailSalesEstimate, parser_status


def test_retail_sales_contract_tracks_benchmark_revision_stage() -> None:
    estimate = RetailSalesEstimate(
        release_date="2008-09-12",
        reference_month="2008-08",
        estimate_stage="advance",
        value=380000.0,
        seasonal_adjustment="seasonally_adjusted",
        units="millions_of_dollars",
        source_artifact_id="marts_2008_09_12",
    )

    assert estimate.estimate_stage in {"advance", "revised", "benchmark_revision"}
    assert parser_status() == "implemented_partial_pdf_text_parser_full_horizon_blocked"
