from __future__ import annotations

import yaml

from business_cycle.data_sources.census_durable_goods_archive import (
    DurableGoodsEstimate,
    parser_status,
)


def test_dgorder_policy_requires_real_parser_before_strict_ready() -> None:
    payload = yaml.safe_load(open("specs/audits/dgorder_release_archive_policy.yaml", encoding="utf-8"))
    policy = payload["dgorder_release_archive_policy"]

    assert policy["series_id"] == "DGORDER"
    assert policy["strict_ready"] is False
    assert policy["parser_status"] == parser_status()


def test_dgorder_estimate_preserves_release_stage_metadata() -> None:
    estimate = DurableGoodsEstimate(
        release_date="2008-09-25",
        reference_month="2008-08",
        estimate_stage="advance",
        value=210000.0,
        seasonal_adjustment="seasonally_adjusted",
        units="millions_of_dollars",
        source_artifact_id="fixture",
    )

    assert estimate.estimate_stage == "advance"
    assert estimate.parser_version == "0-blocked"
