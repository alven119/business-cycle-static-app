"""Print a concise portfolio policy template schema summary."""

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
    load_portfolio_policy_template_schema,
)

DEFAULT_SCHEMA_PATH = Path("specs/portfolio/portfolio_policy_template_schema.yaml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show portfolio policy template schema summary.")
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Portfolio policy template schema YAML path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        schema = load_portfolio_policy_template_schema(args.schema)
    except PortfolioPolicyTemplateError as exc:
        parser.exit(status=1, message=f"error: {exc}\n")

    required_fields = schema.template_object_schema["required_fields"]
    next_phase = schema.recommended_next_phase
    print(f"version={schema.version}")
    print(f"status={schema.status}")
    print(f"allowed_template_count={len(schema.allowed_template_ids)}")
    print(f"prohibited_field_count={len(schema.prohibited_fields)}")
    print(f"required_template_field_count={len(required_fields)}")
    print("live_allocation_allowed_now=false")
    print("trade_signal_generation_allowed_now=false")
    print("public_output_allowed_now=false")
    print(f"recommended_next_phase={next_phase['phase_id']}")
    print(f"reason={' '.join(str(next_phase['reason_zh']).split())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
