from business_cycle.data_sources.ui_claims_release_archive import UiClaimsReleaseRecord, parser_status


def test_ui_claims_contract_separates_advance_and_revision_timing() -> None:
    row = UiClaimsReleaseRecord(
        release_date="2008-09-25",
        week_ending="2008-09-20",
        advance_seasonally_adjusted_initial_claims=493000,
        previous_week_revised_initial_claims=461000,
        revision_amount=6000,
        seasonal_adjustment_status="seasonally_adjusted",
        source_artifact_id="dol_2008_09_25",
        checksum="abc",
    )

    assert row.advance_seasonally_adjusted_initial_claims != row.previous_week_revised_initial_claims
    assert parser_status() == "blocked_pending_weekly_claims_release_parser"
