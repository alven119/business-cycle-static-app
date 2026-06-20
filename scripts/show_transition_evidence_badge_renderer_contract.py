"""Print a concise transition evidence badge renderer contract summary."""

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
    load_transition_evidence_badge_renderer_contract,
)

DEFAULT_CONTRACT_PATH = Path("specs/common/transition_evidence_badge_renderer_contract.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show transition evidence badge renderer contract summary.")
    parser.add_argument(
        "--contract",
        default=str(DEFAULT_CONTRACT_PATH),
        help="Transition evidence badge renderer contract YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_transition_evidence_badge_renderer_contract(args.contract)
    except TransitionEvidenceRendererContractError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    display_model = contract.safe_display_model
    forbidden = set(display_model["forbidden_display_fields"])
    zh_patterns = set(contract.prohibited_text_patterns["zh"])
    en_patterns = set(contract.prohibited_text_patterns["en"])
    direct_trade_text_blocked = {"買進", "賣出", "加碼", "減碼"}.issubset(
        zh_patterns
    ) and {"buy signal", "sell signal"}.issubset(en_patterns)
    phase_override_field_blocked = {
        "current_phase_override",
        "decision_status_override",
    }.issubset(forbidden)
    next_phase = contract.recommended_next_phase
    reason = " ".join(str(next_phase["reason_zh"]).split())

    print(f"version={contract.version}")
    print(f"status={contract.status}")
    print(f"required_display_field_count={len(display_model['required_fields'])}")
    print(f"forbidden_display_field_count={len(display_model['forbidden_display_fields'])}")
    print(f"family_mapping_count={len(contract.level_display_mapping)}")
    print(f"dashboard_integration_precondition_count={len(contract.dashboard_integration_preconditions)}")
    print(f"direct_trade_text_blocked={str(direct_trade_text_blocked).lower()}")
    print(f"phase_override_field_blocked={str(phase_override_field_blocked).lower()}")
    print("dashboard_renderer_wiring_allowed_now=false")
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
