from business_cycle.data_sources.census_durable_goods_archive import DurableGoodsEstimate, parser_status


def test_durable_goods_contract_tracks_advance_and_revised_stage() -> None:
    estimate = DurableGoodsEstimate(
        release_date="2008-09-25",
        reference_month="2008-08",
        estimate_stage="advance",
        value=210000.0,
        seasonal_adjustment="seasonally_adjusted",
        units="millions_of_dollars",
        source_artifact_id="m3_2008_09_25",
    )

    assert estimate.estimate_stage == "advance"
    assert parser_status() == "blocked_pending_census_m3_release_parser"
