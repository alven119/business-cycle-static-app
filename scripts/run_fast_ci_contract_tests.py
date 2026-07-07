#!/usr/bin/env python3
"""Run the contract-defined fast-ci critical pytest subset."""

from __future__ import annotations

from business_cycle.audits.fast_ci_contract_tests import run_fast_ci_contract_tests


if __name__ == "__main__":
    raise SystemExit(run_fast_ci_contract_tests())
