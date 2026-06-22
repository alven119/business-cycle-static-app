from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies


def test_rrsfs_derived_output_is_not_counted_as_leaf_dependency() -> None:
    deps = discover_formal_dependencies("specs/indicator_catalog.yaml")

    assert "RRSFS" not in deps.direct_series_ids
    assert "RSAFS" in deps.direct_series_ids
    assert "CPIAUCSL" in deps.direct_series_ids
    assert "RRSFS" in deps.derived_series_ids
    assert len(deps.direct_series_ids) == 15
