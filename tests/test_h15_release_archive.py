from business_cycle.data_sources.h15_release_archive import H15ReleaseObservation, parser_status


def test_h15_contract_requires_release_date_and_artifact_provenance() -> None:
    row = H15ReleaseObservation(
        release_date="2004-01-02",
        observation_date="2003-12-31",
        dgs10_value=4.25,
        source_artifact_id="h15_2004_01_02",
        source_checksum="abc",
    )

    assert row.release_date < "2004-01-31"
    assert row.source_artifact_id
    assert parser_status() == "blocked_pending_stable_h15_release_table_parser"
