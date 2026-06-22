from __future__ import annotations

import yaml


def test_rrsfs_formula_contract_validated_but_strict_derivation_stays_blocked() -> None:
    payload = yaml.safe_load(
        open("specs/audits/rrsfs_point_in_time_derivation.yaml", encoding="utf-8")
    )
    contract = payload["rrsfs_point_in_time_derivation"]

    assert contract["same_as_of_rule_required"] is True
    assert contract["rrsfs_formula_validated"] is True
    assert contract["rrsfs_unit_validated"] is True
    assert contract["rrsfs_base_period_validated"] is True
    assert contract["strict_ready"] is False
