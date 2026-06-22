from __future__ import annotations

from pathlib import Path

import yaml

import scripts.audit_rrsfs_formula as audit_formula


def test_rrsfs_formula_contract_requires_same_as_of_and_fail_closed() -> None:
    payload = yaml.safe_load(open("specs/audits/rrsfs_formula_contract.yaml", encoding="utf-8"))
    contract = payload["rrsfs_formula_contract"]

    assert contract["formula_expression"] == "RRSFS = RSAFS / CPIAUCSL * 100"
    assert contract["strict_snapshot_policy"]["same_as_of_required"] is True
    assert contract["strict_snapshot_policy"]["lagged_cpi_handling"] == "fail_closed"
    assert contract["strict_snapshot_policy"]["revised_fallback_allowed"] is False
    assert contract["validation_status"]["formula_validated"] is True


def test_rrsfs_formula_audit_validates_revised_fixture(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "data/raw/fred"
    raw_dir.mkdir(parents=True)
    (raw_dir / "RSAFS.csv").write_text("date,value\n2020-01-01,200\n", encoding="utf-8")
    (raw_dir / "CPIAUCSL.csv").write_text("date,value\n2020-01-01,100\n", encoding="utf-8")
    (raw_dir / "RRSFS.csv").write_text("date,value\n2020-01-01,200\n", encoding="utf-8")
    specs = tmp_path / "specs/audits"
    specs.mkdir(parents=True)
    specs.joinpath("rrsfs_formula_contract.yaml").write_text(
        """
rrsfs_formula_contract:
  formula_id: fixture
  formula_expression: "RRSFS = RSAFS / CPIAUCSL * 100"
  revised_formula_validation:
    tolerance_absolute: 0.01
    tolerance_relative: 0.0001
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert audit_formula.main() == 0
