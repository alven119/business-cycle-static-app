"""Smoke tests for the Phase 0A package skeleton."""


def test_business_cycle_package_imports() -> None:
    import business_cycle
    import business_cycle.data_source
    import business_cycle.data_sources
    import business_cycle.indicators
    import business_cycle.phases
    import business_cycle.render
    import business_cycle.storage

    assert business_cycle.__all__ == [
        "data_source",
        "data_sources",
        "indicators",
        "phases",
        "render",
        "storage",
    ]
