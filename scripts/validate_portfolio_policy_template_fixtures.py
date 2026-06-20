"""Validate portfolio policy template fixtures against the schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.portfolio import (  # noqa: E402
    PortfolioPolicyTemplateError,
    load_portfolio_policy_template_fixtures,
    load_portfolio_policy_template_schema,
    validate_portfolio_policy_template_fixtures,
)

DEFAULT_SCHEMA_PATH = Path("specs/portfolio/portfolio_policy_template_schema.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/portfolio/portfolio_policy_template_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate portfolio policy template fixtures.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Portfolio policy template schema YAML path.",
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Portfolio policy template fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        schema = load_portfolio_policy_template_schema(args.schema)
        fixtures = load_portfolio_policy_template_fixtures(args.fixtures)
        summary = validate_portfolio_policy_template_fixtures(fixtures, schema)
    except PortfolioPolicyTemplateError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"schema_version={summary.schema_version}")
    print(f"fixtures_version={summary.fixtures_version}")
    print(f"valid_template_count={summary.valid_template_count}")
    print(f"invalid_template_count={summary.invalid_template_count}")
    print(f"valid_pass_count={summary.valid_pass_count}")
    print(f"invalid_rejected_count={summary.invalid_rejected_count}")
    print(f"unexpected_valid_failures={len(summary.unexpected_valid_failures)}")
    print(f"unexpected_invalid_passes={len(summary.unexpected_invalid_passes)}")
    print(f"expected_error_mismatches={len(summary.expected_error_mismatches)}")
    print(f"result={'passed' if summary.passed else 'failed'}")
    if summary.passed:
        return 0
    for failure in summary.unexpected_valid_failures:
        print(f"unexpected_valid_failure={failure['fixture_id']}: {failure['error']}")
    for fixture_id in summary.unexpected_invalid_passes:
        print(f"unexpected_invalid_pass={fixture_id}")
    for mismatch in summary.expected_error_mismatches:
        print(
            "expected_error_mismatch="
            f"{mismatch['fixture_id']}: expected {mismatch['expected']} got {mismatch['error']}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
