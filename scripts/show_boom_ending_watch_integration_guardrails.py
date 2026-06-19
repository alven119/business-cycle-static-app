"""Print a concise boom-ending watch integration guardrails summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    BoomEndingWatchIntegrationGuardrailsError,
    load_boom_ending_watch_integration_guardrails,
)

DEFAULT_GUARDRAILS_PATH = Path("specs/backtests/boom_ending_watch_integration_guardrails.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show boom-ending watch integration guardrails summary."
    )
    parser.add_argument(
        "--guardrails",
        default=str(DEFAULT_GUARDRAILS_PATH),
        help="Boom-ending watch integration guardrails YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        guardrails = load_boom_ending_watch_integration_guardrails(args.guardrails)
    except BoomEndingWatchIntegrationGuardrailsError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    conclusion = guardrails.design_conclusion
    next_phase = guardrails.recommended_next_phase
    reason = " ".join(str(next_phase["reason_zh"]).split())

    print(f"version={guardrails.version}")
    print(f"status={guardrails.status}")
    print(f"diagnostic_only_allowed={str(conclusion['diagnostic_only']['allowed']).lower()}")
    print(
        "transition_risk_boost_allowed="
        f"{str(conclusion['transition_risk_boost']['allowed']).lower()}"
    )
    print(
        "direct_recession_confirmation_allowed="
        f"{str(conclusion['direct_recession_confirmation']['allowed']).lower()}"
    )
    print(
        "direct_portfolio_action_allowed="
        f"{str(conclusion['direct_portfolio_action']['allowed']).lower()}"
    )
    print(
        "required_acceptance_count="
        f"{len(guardrails.required_acceptance_before_live_integration)}"
    )
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
