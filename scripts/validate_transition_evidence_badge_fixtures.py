"""Validate transition evidence badge fixtures against the badge schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.render.transition_evidence_badges import (  # noqa: E402
    TransitionEvidenceBadgeSchemaError,
    load_transition_evidence_badge_fixtures,
    load_transition_evidence_badge_schema,
    validate_transition_evidence_badge_fixtures,
)

DEFAULT_SCHEMA_PATH = Path("specs/common/transition_evidence_badge_schema.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/common/transition_evidence_badge_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate transition evidence badge fixtures.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Transition evidence badge schema YAML path.",
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Transition evidence badge fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        schema = load_transition_evidence_badge_schema(args.schema)
        fixtures = load_transition_evidence_badge_fixtures(args.fixtures)
        summary = validate_transition_evidence_badge_fixtures(fixtures, schema)
    except TransitionEvidenceBadgeSchemaError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"schema_version={schema.version}")
    print(f"fixtures_version={fixtures.version}")
    print(f"valid_fixture_count={summary.valid_fixture_count}")
    print(f"invalid_fixture_count={summary.invalid_fixture_count}")
    print(f"valid_pass_count={summary.valid_pass_count}")
    print(f"invalid_rejected_count={summary.invalid_rejected_count}")
    print(f"unexpected_valid_failures={len(summary.unexpected_valid_failures)}")
    print(f"unexpected_invalid_passes={len(summary.unexpected_invalid_passes)}")
    print(f"expected_error_mismatches={len(summary.expected_error_mismatches)}")
    if summary.unexpected_valid_failures:
        print(f"unexpected_valid_failure_details={summary.unexpected_valid_failures}")
    if summary.unexpected_invalid_passes:
        print(f"unexpected_invalid_pass_details={summary.unexpected_invalid_passes}")
    if summary.expected_error_mismatches:
        print(f"expected_error_mismatch_details={summary.expected_error_mismatches}")
    print(f"result={'passed' if summary.passed else 'failed'}")
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
