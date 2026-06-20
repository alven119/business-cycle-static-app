"""Print a concise dashboard evidence integration readiness summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.render.dashboard_evidence_readiness import (  # noqa: E402
    DashboardEvidenceReadinessError,
    load_dashboard_evidence_integration_readiness,
    summarize_dashboard_evidence_integration_readiness,
)

DEFAULT_READINESS_PATH = Path("specs/common/dashboard_evidence_integration_readiness.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show dashboard evidence integration readiness summary.")
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS_PATH),
        help="Dashboard evidence integration readiness YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        readiness = load_dashboard_evidence_integration_readiness(args.readiness)
        summary = summarize_dashboard_evidence_integration_readiness(readiness)
    except DashboardEvidenceReadinessError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    print(f"version={summary['version']}")
    print(f"status={summary['status']}")
    print(f"artifact_count={summary['artifact_count']}")
    print(f"validator_count={summary['validator_count']}")
    print(f"active_blocker_count={summary['active_blocker_count']}")
    print(
        "required_before_dashboard_wiring_count="
        f"{summary['required_before_dashboard_wiring_count']}"
    )
    print(f"phase_7g_closure_status={summary['phase_7g_closure_status']}")
    print(f"dashboard_wiring_allowed_now={str(summary['dashboard_wiring_allowed_now']).lower()}")
    print(f"public_output_allowed_now={str(summary['public_output_allowed_now']).lower()}")
    print(
        "formal_decision_impact_allowed="
        f"{str(summary['formal_decision_impact_allowed']).lower()}"
    )
    print(f"recommended_next_phase={summary['recommended_next_phase']}")
    print(f"reason={summary['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
