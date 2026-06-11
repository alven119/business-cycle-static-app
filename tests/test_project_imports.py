"""Smoke tests for the Phase 0A package skeleton."""


def test_business_cycle_package_imports() -> None:
    import business_cycle
    from business_cycle import data_sources
    from business_cycle import indicators
    from business_cycle import phases
    from business_cycle import render
    from business_cycle import storage

    assert data_sources is not None
    assert indicators is not None
    assert phases is not None
    assert render is not None
    assert storage is not None

    assert business_cycle.__all__ == [
        "data_sources",
        "indicators",
        "phases",
        "render",
        "storage",
    ]
