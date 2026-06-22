from __future__ import annotations

import yaml


def test_rrsfs_reference_month_alignment_fails_closed_without_same_month_cpi() -> None:
    payload = yaml.safe_load(open("specs/audits/rrsfs_formula_contract.yaml", encoding="utf-8"))
    policy = payload["rrsfs_formula_contract"]["strict_snapshot_policy"]

    assert policy["reference_month_alignment_rule"] == (
        "same_reference_month_when_cpi_available_else_fail_closed"
    )
    assert policy["missing_same_month_cpi_policy"] == "fail_closed"
    assert policy["lagged_cpi_handling"] == "fail_closed"
