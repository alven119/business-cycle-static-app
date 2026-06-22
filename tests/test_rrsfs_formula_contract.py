from __future__ import annotations

import yaml


def test_rrsfs_formula_contract_requires_same_as_of_and_fail_closed() -> None:
    payload = yaml.safe_load(open("specs/audits/rrsfs_formula_contract.yaml", encoding="utf-8"))
    contract = payload["rrsfs_formula_contract"]

    assert contract["formula_expression"] == "RRSFS = RSAFS / CPIAUCSL * 100"
    assert contract["strict_snapshot_policy"]["same_as_of_required"] is True
    assert contract["strict_snapshot_policy"]["lagged_cpi_handling"] == "fail_closed"
    assert contract["strict_snapshot_policy"]["revised_fallback_allowed"] is False
    assert contract["validation_status"]["formula_validated"] is False
