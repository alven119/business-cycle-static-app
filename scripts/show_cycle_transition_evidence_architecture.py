"""Print a concise cycle transition evidence architecture summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CycleTransitionEvidenceArchitectureError,
    load_cycle_transition_evidence_architecture,
)

DEFAULT_ARCHITECTURE_PATH = Path("specs/common/cycle_transition_evidence_architecture.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show cycle transition evidence architecture summary.")
    parser.add_argument(
        "--architecture",
        default=str(DEFAULT_ARCHITECTURE_PATH),
        help="Cycle transition evidence architecture YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        architecture = load_cycle_transition_evidence_architecture(args.architecture)
    except CycleTransitionEvidenceArchitectureError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    outputs = architecture.unified_evidence_outputs
    next_phase = architecture.recommended_next_phase
    reason = " ".join(str(next_phase["reason_zh"]).split())
    print(f"version={architecture.version}")
    print(f"status={architecture.status}")
    print(f"evidence_family_count={len(architecture.evidence_families)}")
    print(
        "dashboard_diagnostics_allowed_now="
        f"{str(architecture.dashboard_diagnostics_contract['allowed_now']).lower()}"
    )
    print(
        "transition_risk_allowed_now="
        f"{str(outputs['transition_risk_research']['allowed_now']).lower()}"
    )
    print(
        "portfolio_policy_allowed_now="
        f"{str(outputs['portfolio_policy_research']['allowed_now']).lower()}"
    )
    print(
        "formal_phase_change_allowed_now="
        f"{str(outputs['formal_phase_change']['allowed_now']).lower()}"
    )
    print(
        "direct_trade_signal_allowed_now="
        f"{str(outputs['direct_trade_signal']['allowed_now']).lower()}"
    )
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
