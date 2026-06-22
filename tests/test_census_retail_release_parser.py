from __future__ import annotations

import yaml

from business_cycle.data_sources.census_retail_sales_archive import (
    RetailSalesEstimate,
    parser_status,
)


def test_rsafs_policy_requires_real_parser_before_strict_ready() -> None:
    payload = yaml.safe_load(open("specs/audits/rsafs_release_archive_policy.yaml", encoding="utf-8"))
    policy = payload["rsafs_release_archive_policy"]

    assert policy["series_id"] == "RSAFS"
    assert policy["strict_ready"] is False
    assert parser_status() == "implemented_partial_pdf_text_parser_full_horizon_blocked"
    assert policy["strict_ready"] is False


def test_rsafs_estimate_preserves_benchmark_revision_stage() -> None:
    estimate = RetailSalesEstimate(
        release_date="2008-09-12",
        reference_month="2008-08",
        estimate_stage="benchmark_revision",
        value=380000.0,
        seasonal_adjustment="seasonally_adjusted",
        units="millions_of_dollars",
        source_artifact_id="fixture",
    )

    assert estimate.estimate_stage == "benchmark_revision"
    assert estimate.parser_version == "1"
