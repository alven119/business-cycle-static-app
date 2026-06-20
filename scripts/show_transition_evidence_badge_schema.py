"""Print a concise transition evidence badge schema summary."""

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
    load_transition_evidence_badge_schema,
)

DEFAULT_SCHEMA_PATH = Path("specs/common/transition_evidence_badge_schema.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show transition evidence badge schema summary.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Transition evidence badge schema YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        schema = load_transition_evidence_badge_schema(args.schema)
    except TransitionEvidenceBadgeSchemaError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    required_fields = schema.badge_object_schema["required_fields"]
    constraints = schema.badge_object_schema["constraints"]
    formal_decision_impact_allowed = not bool(
        constraints["formal_decision_impact_must_be_none"]
    ) or any(
        str(family["formal_decision_impact"]) != "none"
        for family in schema.badge_families.values()
    )
    direct_trade_signal_allowed = not {
        "action",
        "buy_signal",
        "sell_signal",
        "allocation",
        "target_weight",
    }.issubset(set(schema.prohibited_fields))
    next_phase = schema.recommended_next_phase
    reason = " ".join(str(next_phase["reason_zh"]).split())

    print(f"version={schema.version}")
    print(f"status={schema.status}")
    print(f"badge_family_count={len(schema.badge_families)}")
    print(
        "dashboard_contract_allowed_now="
        f"{str(schema.allowed_dashboard_contract['allowed_now']).lower()}"
    )
    print(f"formal_decision_impact_allowed={str(formal_decision_impact_allowed).lower()}")
    print(f"direct_trade_signal_allowed={str(direct_trade_signal_allowed).lower()}")
    print(f"prohibited_field_count={len(schema.prohibited_fields)}")
    print(f"required_badge_field_count={len(required_fields)}")
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
