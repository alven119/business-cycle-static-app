from __future__ import annotations

from pathlib import Path

from business_cycle.audits import data_only_model_freeze


def test_data_only_model_baseline_freeze_is_valid() -> None:
    summary = data_only_model_freeze.summarize_data_only_model_baseline_freeze()

    assert summary["data_only_baseline_freeze_ready"] is True
    assert summary["freeze_hash_valid"] is True
    assert summary["frozen_file_missing_count"] == 0
    assert summary["frozen_file_hash_mismatch_count"] == 0
    assert summary["parameter_manifest_hash_mismatch_count"] >= 0
    assert summary["unfrozen_decision_file_count"] == 0
    assert summary["secret_in_freeze_manifest_count"] == 0
    assert summary["economic_validation_status"] == "not_validated"
    assert summary["independent_validation_status"] == "not_started"
    assert summary["holdout_status"] == "not_started"


def test_decision_source_change_invalidates_freeze(monkeypatch) -> None:
    original = data_only_model_freeze._file_sha256

    def changed_hash(path: Path) -> str:
        if path == Path("specs/indicator_catalog.yaml"):
            return "changed"
        return original(path)

    monkeypatch.setattr(data_only_model_freeze, "_file_sha256", changed_hash)

    summary = data_only_model_freeze.summarize_data_only_model_baseline_freeze()

    assert summary["freeze_hash_valid"] is False
    assert summary["frozen_file_hash_mismatch_count"] > 0


def test_unfrozen_decision_source_is_detected(monkeypatch) -> None:
    original = data_only_model_freeze._decision_source_files

    def with_extra_source() -> list[Path]:
        return [*original(), Path("src/business_cycle/pipeline/runner.py")]

    monkeypatch.setattr(data_only_model_freeze, "_decision_source_files", with_extra_source)

    summary = data_only_model_freeze.summarize_data_only_model_baseline_freeze()

    assert summary["unfrozen_decision_file_count"] == 1
