from __future__ import annotations

from business_cycle.shadow_model.evidence_evaluators import (
    summarize_book_core_role_evaluation_rules,
)


def main() -> None:
    summary = summarize_book_core_role_evaluation_rules()
    for key in (
        "phase",
        "role_evaluation_contract_registry_ready",
        "canonical_role_count",
        "evaluation_contract_count",
        "role_without_evaluation_contract_count",
        "duplicate_role_evaluation_contract_count",
        "preregistered_evaluable_role_count",
        "raw_transform_only_role_count",
        "blocked_rule_count",
        "blocked_threshold_count",
        "blocked_data_count",
        "blocked_equivalence_count",
        "evaluator_with_historical_label_input_count",
        "evaluator_with_external_context_input_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
