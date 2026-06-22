from __future__ import annotations

import pytest

from business_cycle.shadow_model.prospective_registry import (
    ZERO_HASH,
    build_prospective_record,
    semantic_record_hash,
)
from business_cycle.shadow_model.prospective_registry_store import (
    ProspectiveRegistryStore,
    summarize_append_only_store,
)


def test_prospective_registry_store_appends_chain(tmp_path) -> None:
    store = ProspectiveRegistryStore(tmp_path)
    first = build_prospective_record(
        sequence_number=1,
        previous_record_hash=ZERO_HASH,
        observation_period="2026-07",
        as_of="2026-08-31",
        input_snapshot_manifest_hash="hash1",
    )
    second = build_prospective_record(
        sequence_number=2,
        previous_record_hash=first["record_hash"],
        observation_period="2026-08",
        as_of="2026-09-30",
        input_snapshot_manifest_hash="hash2",
    )

    store.append_record(first)
    store.append_record(second)

    assert [row["sequence_number"] for row in store.load_records()] == [1, 2]
    assert store.audit()["chain_valid"] is True


@pytest.mark.parametrize(
    ("mutator", "error"),
    [
        (
            lambda record: record.update({"observation_period": "2026-06"}),
            "pre_start_period",
        ),
        (
            lambda record: record.update({"model_freeze_id": "wrong"}),
            "model_version_mismatch",
        ),
        (
            lambda record: record.update({"provenance_complete": False}),
            "missing_provenance",
        ),
        (
            lambda record: record.update({"candidate_phase": "recovery"}),
            "candidate_capability_missing",
        ),
    ],
)
def test_prospective_registry_store_rejects_invalid_records(
    tmp_path,
    mutator,
    error: str,
) -> None:
    record = build_prospective_record(
        sequence_number=1,
        previous_record_hash=ZERO_HASH,
        observation_period="2026-07",
        as_of="2026-08-31",
        input_snapshot_manifest_hash="hash1",
    )
    mutator(record)
    record["record_hash"] = semantic_record_hash(record)

    with pytest.raises(ValueError, match=error):
        ProspectiveRegistryStore(tmp_path).append_record(record)


def test_prospective_registry_store_has_no_rewrite_api() -> None:
    summary = summarize_append_only_store()

    assert summary["append_only_store_ready"] is True
    assert summary["delete_api_present"] is False
    assert summary["rewrite_api_present"] is False
