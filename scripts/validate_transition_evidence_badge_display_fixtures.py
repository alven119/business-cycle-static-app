"""Validate transition evidence badge renderer display model fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.render.transition_evidence_renderer_contract import (  # noqa: E402
    TransitionEvidenceRendererContractError,
    load_transition_evidence_badge_display_fixtures,
    load_transition_evidence_badge_renderer_contract,
    validate_transition_evidence_badge_display_fixtures,
)

DEFAULT_CONTRACT_PATH = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")
DEFAULT_FIXTURES_PATH = Path("specs/common/transition_evidence_badge_display_fixtures.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate transition evidence badge display fixtures.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Transition evidence badge renderer contract YAML path.",
    )
    parser.add_argument(
        "--fixtures",
        default=str(DEFAULT_FIXTURES_PATH),
        help="Transition evidence badge display fixtures YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_transition_evidence_badge_renderer_contract(args.contract)
        fixtures = load_transition_evidence_badge_display_fixtures(args.fixtures)
        summary = validate_transition_evidence_badge_display_fixtures(fixtures, contract)
    except TransitionEvidenceRendererContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"contract_version={contract.version}")
    print(f"fixtures_version={fixtures.version}")
    print(f"valid_display_fixture_count={summary.valid_display_fixture_count}")
    print(f"invalid_display_fixture_count={summary.invalid_display_fixture_count}")
    print(f"valid_display_pass_count={summary.valid_display_pass_count}")
    print(f"invalid_display_rejected_count={summary.invalid_display_rejected_count}")
    print(f"unexpected_valid_display_failures={len(summary.unexpected_valid_display_failures)}")
    print(f"unexpected_invalid_display_passes={len(summary.unexpected_invalid_display_passes)}")
    print(f"expected_display_error_mismatches={len(summary.expected_display_error_mismatches)}")
    if summary.unexpected_valid_display_failures:
        print(f"unexpected_valid_display_failure_details={summary.unexpected_valid_display_failures}")
    if summary.unexpected_invalid_display_passes:
        print(f"unexpected_invalid_display_pass_details={summary.unexpected_invalid_display_passes}")
    if summary.expected_display_error_mismatches:
        print(f"expected_display_error_mismatch_details={summary.expected_display_error_mismatches}")
    print(f"result={'passed' if summary.passed else 'failed'}")
    return 0 if summary.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
