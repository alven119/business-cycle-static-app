from business_cycle.audits.point_in_time_coverage import discover_formal_dependencies


def test_cpiaucsl_is_formal_leaf_dependency_for_rrsfs_derivation() -> None:
    deps = discover_formal_dependencies("specs/indicator_catalog.yaml")

    assert "CPIAUCSL" in deps.direct_series_ids
    assert "RRSFS" in deps.derived_series_ids
