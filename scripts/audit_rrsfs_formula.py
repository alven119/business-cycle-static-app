#!/usr/bin/env python
"""Audit the RRSFS formula contract without creating strict snapshots."""

from __future__ import annotations

from pathlib import Path

import yaml


def main() -> int:
    payload = yaml.safe_load(Path("specs/audits/rrsfs_formula_contract.yaml").read_text(encoding="utf-8"))
    contract = payload["rrsfs_formula_contract"]
    validation = contract.get("validation_status", {})
    summary = {
        "formula_id": contract["formula_id"],
        "formula_expression": contract["formula_expression"],
        "compared_period_count": 0,
        "within_tolerance_count": 0,
        "outside_tolerance_count": 0,
        "max_absolute_difference": None,
        "max_relative_difference": None,
        "rounding_policy": "millions_tolerance_pending_revised_series_reconciliation",
        "unit_validated": bool(validation.get("unit_validated")),
        "base_period_validated": bool(validation.get("base_period_validated")),
        "seasonal_adjustment_validated": bool(validation.get("seasonal_adjustment_validated")),
        "formula_validated": bool(validation.get("formula_validated")),
        "result": "passed" if validation.get("formula_validated") else "blocked",
    }
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
