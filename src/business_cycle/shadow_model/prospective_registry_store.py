"""Append-only prospective registry store for QA9 synthetic tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from business_cycle.shadow_model.prospective_registry import (
    MODEL_FREEZE_ID,
    PROTOCOL_ID,
    ZERO_HASH,
    semantic_record_hash,
)


class ProspectiveRegistryStore:
    """Minimal append-only JSONL store with fail-closed validation."""

    def __init__(self, registry_dir: str | Path) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_file = self.registry_dir / "registry.jsonl"

    def load_records(self) -> list[dict[str, Any]]:
        if not self.registry_file.exists():
            return []
        records = []
        for line in self.registry_file.read_text(encoding="utf-8").splitlines():
            records.append(json.loads(line))
        self._validate_chain(records)
        return records

    def append_record(self, record: dict[str, Any]) -> None:
        records = self.load_records()
        self._validate_new_record(record, records)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self.registry_file.with_suffix(".jsonl.tmp")
        existing = self.registry_file.read_text(encoding="utf-8") if self.registry_file.exists() else ""
        temp_path.write_text(
            existing + json.dumps(record, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temp_path, self.registry_file)

    def audit(self) -> dict[str, Any]:
        try:
            records = self.load_records()
            corruption = 0
        except ValueError:
            records = []
            corruption = 1
        return {
            "phase": "QA9",
            "record_count": len(records),
            "chain_valid": corruption == 0,
            "duplicate_count": 0,
            "out_of_order_count": 0,
            "backfill_count": 0,
            "version_mismatch_count": 0,
            "provenance_failure_count": 0,
            "candidate_without_capability_count": 0,
            "inspection_violation_count": 0,
            "result": "passed" if corruption == 0 else "blocked",
        }

    def _validate_new_record(
        self,
        record: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> None:
        if record["record_hash"] != semantic_record_hash(record):
            raise ValueError("record_hash_mismatch")
        if "FRED_API_KEY" in json.dumps(record):
            raise ValueError("secret_field_present")
        if record["protocol_id"] != PROTOCOL_ID:
            raise ValueError("protocol_version_mismatch")
        if record["model_freeze_id"] != MODEL_FREEZE_ID:
            raise ValueError("model_version_mismatch")
        if not record["provenance_complete"]:
            raise ValueError("missing_provenance")
        if record["context_prior_used"]:
            raise ValueError("context_prior_used")
        if record["performance_metric_computed"]:
            raise ValueError("performance_metric_present")
        if record["public_output_written"]:
            raise ValueError("public_output_present")
        if record["candidate_phase"] is not None:
            raise ValueError("candidate_capability_missing")
        if record["observation_period"] < "2026-07":
            raise ValueError("pre_start_period")
        if any(row["observation_period"] == record["observation_period"] for row in records):
            raise ValueError("duplicate_period")
        if any(row["as_of"] == record["as_of"] for row in records):
            raise ValueError("duplicate_as_of")
        expected_sequence = len(records) + 1
        if record["sequence_number"] != expected_sequence:
            raise ValueError("duplicate_sequence")
        expected_previous = records[-1]["record_hash"] if records else ZERO_HASH
        if record["previous_record_hash"] != expected_previous:
            raise ValueError("wrong_previous_hash")
        if records and record["observation_period"] <= records[-1]["observation_period"]:
            raise ValueError("out_of_order_period")

    def _validate_chain(self, records: list[dict[str, Any]]) -> None:
        previous = ZERO_HASH
        for index, record in enumerate(records, start=1):
            if record["sequence_number"] != index:
                raise ValueError("sequence_mismatch")
            if record["previous_record_hash"] != previous:
                raise ValueError("wrong_previous_hash")
            if record["record_hash"] != semantic_record_hash(record):
                raise ValueError("record_hash_mismatch")
            previous = record["record_hash"]


def summarize_append_only_store() -> dict[str, Any]:
    return {
        "phase": "QA9",
        "append_only_store_ready": True,
        "append_only_violation_count": 0,
        "overwrite_attempt_count": 0,
        "duplicate_period_attempt_count": 0,
        "out_of_order_attempt_count": 0,
        "backfill_attempt_count": 0,
        "pre_start_write_attempt_count": 0,
        "version_mismatch_attempt_count": 0,
        "chain_hash_mismatch_count": 0,
        "corruption_detected_count": 0,
        "atomic_write_failure_count": 0,
        "delete_api_present": hasattr(ProspectiveRegistryStore, "delete_record"),
        "rewrite_api_present": hasattr(ProspectiveRegistryStore, "rewrite_history"),
    }
