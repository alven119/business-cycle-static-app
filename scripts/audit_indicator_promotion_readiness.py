from __future__ import annotations

from business_cycle.audits.indicator_promotion import (
    summarize_indicator_promotion_readiness,
)


def main() -> None:
    summary = summarize_indicator_promotion_readiness()
    for key in (
        "phase",
        "indicator_promotion_gate_ready",
        "promotion_candidate_count",
        "shadow_model_ready_count",
        "production_review_ready_count",
        "promotion_without_complete_gate_count",
        "contaminated_indicator_promoted_without_disclosure_count",
        "silent_substitution_promotion_count",
        "new_production_promotion_count",
    ):
        print(f"{key}={str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}")


if __name__ == "__main__":
    main()

