"""Print a concise candidate recession integration design summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.backtests import (  # noqa: E402
    CandidateRecessionIntegrationDesignError,
    integration_mode_allowed,
    load_candidate_recession_integration_design,
)

DEFAULT_DESIGN_PATH = Path("specs/backtests/candidate_recession_integration_design.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show candidate recession integration design summary."
    )
    parser.add_argument(
        "--design",
        default=str(DEFAULT_DESIGN_PATH),
        help="Candidate recession integration design YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        design = load_candidate_recession_integration_design(args.design)
    except CandidateRecessionIntegrationDesignError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    hard_gate_allowed = integration_mode_allowed(design, "hard_confirmation_gate")
    soft_filter_allowed = bool(
        design.design_conclusion["soft_filter_with_watch_persistence"].get("allowed", False)
    )
    diagnostic_only_allowed = bool(
        design.design_conclusion["diagnostic_layer_only"].get("allowed", False)
    )
    next_phase = design.recommended_next_phase
    reason = " ".join(str(next_phase["reason_zh"]).split())

    print(f"version={design.version}")
    print(f"status={design.status}")
    print(f"hard_gate_allowed={str(hard_gate_allowed).lower()}")
    print(f"soft_filter_allowed={str(soft_filter_allowed).lower()}")
    print(f"diagnostic_only_allowed={str(diagnostic_only_allowed).lower()}")
    print(
        "required_acceptance_count="
        f"{len(design.required_acceptance_before_live_integration)}"
    )
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
