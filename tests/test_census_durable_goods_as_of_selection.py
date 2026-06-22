from __future__ import annotations

from business_cycle.data_sources.census_durable_goods_archive import (
    DurableGoodsEstimate,
    select_durable_goods_estimate_as_of,
)


def test_dgorder_selector_hides_revision_before_release_date() -> None:
    estimates = [
        DurableGoodsEstimate(
            release_date="2008-09-25",
            reference_month="2008-08",
            estimate_stage="advance",
            value=210000.0,
            seasonal_adjustment="seasonally_adjusted",
            units="millions_of_dollars",
            source_artifact_id="advance",
        ),
        DurableGoodsEstimate(
            release_date="2008-10-03",
            reference_month="2008-08",
            estimate_stage="full",
            value=211000.0,
            seasonal_adjustment="seasonally_adjusted",
            units="millions_of_dollars",
            source_artifact_id="full",
        ),
    ]

    selected = select_durable_goods_estimate_as_of(
        estimates,
        as_of="2008-09-30",
        reference_month="2008-08",
    )

    assert selected is not None
    assert selected.estimate_stage == "advance"
    assert selected.value == 210000.0
