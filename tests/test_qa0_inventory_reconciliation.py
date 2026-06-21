from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from business_cycle.audits.inventory_reconciliation import run_qa0_inventory_reconciliation


def test_qa0_inventory_reconciliation_is_complete_for_current_repo() -> None:
    summary = run_qa0_inventory_reconciliation()

    assert summary["canonical_requirement_count"] > 22
    assert summary["traceability_row_count"] == summary["canonical_requirement_count"]
    assert summary["missing_traceability_requirement_count"] == 0
    assert summary["duplicate_traceability_requirement_count"] == 0
    assert summary["unknown_traceability_requirement_count"] == 0
    assert summary["discovered_formal_indicator_count"] >= 13
    assert summary["mapped_indicator_count"] == summary["discovered_unique_indicator_count"]
    assert summary["unmapped_indicator_count"] == 0
    assert summary["audited_series_count"] == summary["discovered_unique_series_count"]
    assert summary["unaudited_series_count"] == 0
    assert summary["series_without_temporal_status_count"] == 0
    assert summary["provenance_unmapped_indicator_count"] == 0
    assert summary["orphaned_implementation_path_count"] == 0
    assert summary["missing_book_indicator_coverage_row_count"] == 0
    assert summary["qa0_inventory_complete"] is True


def test_repository_new_indicator_without_mapping_is_detected(tmp_path: Path) -> None:
    repo = _copy_audit_repo(tmp_path)
    catalog_path = repo / "specs/indicator_catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog["indicators"].append(
        {
            "indicator_id": "temporary_unmapped_indicator",
            "provider": "fred",
            "candidate_fred_series": ["TEMPQA0"],
            "source_priority": [{"fred": "TEMPQA0"}],
            "direction": "higher_is_better",
            "score_method": "level_percentile_score",
        }
    )
    catalog_path.write_text(yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8")

    summary = run_qa0_inventory_reconciliation(repo)

    assert summary["unmapped_indicator_count"] == 1
    assert summary["provenance_unmapped_indicator_count"] == 1


def test_repository_new_series_without_registry_is_detected(tmp_path: Path) -> None:
    repo = _copy_audit_repo(tmp_path)
    catalog_path = repo / "specs/indicator_catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog["indicators"][0]["candidate_fred_series"].append({"series_id": "TEMPQA1"})
    catalog_path.write_text(yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8")

    summary = run_qa0_inventory_reconciliation(repo)

    assert summary["series_without_release_lag_registry_count"] == 1
    assert summary["unaudited_series_count"] == 1


def test_traceability_missing_and_duplicate_rows_are_detected(tmp_path: Path) -> None:
    repo = _copy_audit_repo(tmp_path)
    path = repo / "specs/audits/book_method_traceability.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = payload["book_method_traceability"]["rows"]
    payload["book_method_traceability"]["rows"] = rows[1:] + [rows[1]]
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")

    summary = run_qa0_inventory_reconciliation(repo)

    assert summary["missing_traceability_requirement_count"] == 1
    assert summary["duplicate_traceability_requirement_count"] == 1


def test_orphaned_implementation_path_is_detected(tmp_path: Path) -> None:
    repo = _copy_audit_repo(tmp_path)
    path = repo / "specs/audits/book_method_traceability.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["book_method_traceability"]["rows"][0]["implementation_paths"] = [
        "src/business_cycle/does_not_exist.py"
    ]
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")

    summary = run_qa0_inventory_reconciliation(repo)

    assert summary["orphaned_implementation_path_count"] == 1


def _copy_audit_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    for name in ("specs", "src", "tests"):
        shutil.copytree(name, repo / name)
    return repo
