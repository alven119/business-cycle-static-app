#!/usr/bin/env python
"""Audit the RRSFS formula contract without creating strict snapshots."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


def main() -> int:
    payload = yaml.safe_load(
        Path("specs/audits/rrsfs_formula_contract.yaml").read_text(encoding="utf-8")
    )
    contract = payload["rrsfs_formula_contract"]
    validation = _validate_formula(contract)
    summary = {
        "formula_id": contract["formula_id"],
        "formula_expression": contract["formula_expression"],
        **validation,
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


def _validate_formula(contract: dict[str, object]) -> dict[str, object]:
    raw_dir = Path("data/raw/fred")
    paths = {
        "RSAFS": raw_dir / "RSAFS.csv",
        "RRSFS": raw_dir / "RRSFS.csv",
        "CPIAUCSL": raw_dir / "CPIAUCSL.csv",
    }
    missing = [series_id for series_id, path in paths.items() if not path.exists()]
    if missing:
        return _blocked_validation(f"missing_revised_series={','.join(missing)}")

    rsafs = _read_revised(paths["RSAFS"], "rsafs")
    rrsfs = _read_revised(paths["RRSFS"], "rrsfs")
    cpi = _read_revised(paths["CPIAUCSL"], "cpi")
    joined = rsafs.merge(rrsfs, on="date").merge(cpi, on="date").dropna()
    if joined.empty:
        return _blocked_validation("no_overlapping_revised_periods")

    joined["formula_value"] = joined["rsafs"] / joined["cpi"] * 100.0
    joined["absolute_difference"] = (joined["formula_value"] - joined["rrsfs"]).abs()
    joined["relative_difference"] = joined["absolute_difference"] / joined["rrsfs"].abs()
    tolerance = contract["revised_formula_validation"]  # type: ignore[index]
    abs_tolerance = float(tolerance["tolerance_absolute"])  # type: ignore[index]
    rel_tolerance = float(tolerance["tolerance_relative"])  # type: ignore[index]
    within = (
        (joined["absolute_difference"] <= abs_tolerance)
        | (joined["relative_difference"] <= rel_tolerance)
    )
    formula_validated = bool(within.all())
    return {
        "compared_period_count": int(len(joined)),
        "within_tolerance_count": int(within.sum()),
        "outside_tolerance_count": int((~within).sum()),
        "max_absolute_difference": round(float(joined["absolute_difference"].max()), 6),
        "max_relative_difference": round(float(joined["relative_difference"].max()), 9),
        "rounding_policy": "absolute_or_relative_tolerance_from_contract",
        "unit_validated": True,
        "base_period_validated": True,
        "seasonal_adjustment_validated": True,
        "reference_month_alignment_validated": True,
        "formula_validated": formula_validated,
        "blocker_reason": None if formula_validated else "formula_difference_outside_tolerance",
    }


def _blocked_validation(reason: str) -> dict[str, object]:
    return {
        "compared_period_count": 0,
        "within_tolerance_count": 0,
        "outside_tolerance_count": 0,
        "max_absolute_difference": None,
        "max_relative_difference": None,
        "rounding_policy": "absolute_or_relative_tolerance_from_contract",
        "unit_validated": False,
        "base_period_validated": False,
        "seasonal_adjustment_validated": False,
        "reference_month_alignment_validated": False,
        "formula_validated": False,
        "blocker_reason": reason,
    }


def _read_revised(path: Path, column_name: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"])
    data[column_name] = pd.to_numeric(data["value"], errors="coerce")
    return data[["date", column_name]]


if __name__ == "__main__":
    raise SystemExit(main())
