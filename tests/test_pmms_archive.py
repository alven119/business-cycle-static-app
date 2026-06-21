from business_cycle.data_sources.pmms_archive import PmmsWeeklyRecord, parser_status


def test_pmms_contract_records_methodology_epoch() -> None:
    row = PmmsWeeklyRecord(
        release_date="2019-12-26",
        survey_window_start="2019-12-19",
        survey_window_end="2019-12-25",
        reference_week="2019-12-26",
        mortgage_rate_30y=3.74,
        methodology_epoch="legacy_survey",
        source_artifact_id="pmms_2019_12_26",
        checksum="abc",
    )

    assert row.methodology_epoch == "legacy_survey"
    assert parser_status() == "blocked_pending_pmms_methodology_and_archive_review"
