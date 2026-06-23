from __future__ import annotations

import json

from business_cycle.storage.book_core_source_cache import (
    build_cache_metadata,
    summarize_book_core_source_cache_contract,
    validate_cache_metadata,
    write_cache_metadata_atomic,
)


def test_book_core_source_cache_metadata_is_atomic_and_secret_free(tmp_path) -> None:
    payload = build_cache_metadata(
        adapter_id="phase10::fred::PSAVERT",
        role_ids=["growth_personal_saving_rate"],
        source_series_or_release_id="PSAVERT",
        row_count=1,
    )
    path = tmp_path / "cache" / "psavert.json"

    write_cache_metadata_atomic(path, payload)
    reloaded = json.loads(path.read_text(encoding="utf-8"))

    assert validate_cache_metadata(reloaded) is True
    assert summarize_book_core_source_cache_contract()["cache_contract_ready"] is True
    assert summarize_book_core_source_cache_contract()["cache_checksum_failure_count"] == 0
    reloaded["row_count"] = 2
    assert validate_cache_metadata(reloaded) is False
