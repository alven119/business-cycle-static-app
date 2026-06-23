"""Phase 17 validation label and provenance policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_LABEL_POLICY_PATH = Path("specs/audits/historical_validation_label_policy.yaml")


def load_validation_label_policy(
    path: str | Path = DEFAULT_LABEL_POLICY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation label policy must be a mapping")
    policy = payload.get("historical_validation_label_policy")
    if not isinstance(policy, dict):
        raise ValueError("historical_validation_label_policy must be a mapping")
    return policy


def summarize_validation_label_policy(
    path: str | Path = DEFAULT_LABEL_POLICY_PATH,
) -> dict[str, Any]:
    policy = load_validation_label_policy(path)
    rows = policy["label_source_rows"]
    restrictions = policy["global_restrictions"]
    counters = policy["counters"]
    required_prohibitions = {
        "runtime_decision_logic",
        "rule_or_evaluator_tuning",
        "scenario_specific_threshold_change",
    }
    sources_missing_required_prohibitions = [
        row["label_source_id"]
        for row in rows
        if not required_prohibitions.intersection(row["prohibited_uses"])
    ]
    label_provenance_complete = (
        all(row["provenance_complete"] is True for row in rows)
        and counters["label_source_without_provenance_count"] == 0
    )
    label_runtime_usage_prohibited = (
        restrictions["labels_prohibited_from_runtime_decision_logic"] is True
        and counters["label_runtime_usage_violation_count"] == 0
    )
    label_tuning_usage_prohibited = (
        restrictions["labels_prohibited_from_rule_or_evaluator_tuning"] is True
        and counters["label_tuning_usage_violation_count"] == 0
    )
    ready = (
        policy["policy_status"] == "preregistered_no_label_runtime_use"
        and len(rows) > 0
        and counters["label_source_count"] == len(rows)
        and label_provenance_complete
        and label_runtime_usage_prohibited
        and label_tuning_usage_prohibited
        and restrictions[
            "labels_prohibited_from_scenario_specific_threshold_changes"
        ]
        is True
        and restrictions[
            "nber_dates_allowed_only_as_declared_validation_label_source"
        ]
        is True
        and restrictions["book_examples_allowed_only_as_traceability"] is True
        and restrictions["portfolio_returns_prohibited_as_rule_source"] is True
        and not sources_missing_required_prohibitions
        and all(
            value == 0
            for key, value in counters.items()
            if key.endswith("_count") and key != "label_source_count"
        )
    )
    return {
        "phase": "17",
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "validation_label_policy_ready": ready,
        "label_source_count": len(rows),
        "label_provenance_complete": label_provenance_complete,
        "label_runtime_usage_prohibited": label_runtime_usage_prohibited,
        "label_tuning_usage_prohibited": label_tuning_usage_prohibited,
        "scenario_specific_threshold_change_prohibited": restrictions[
            "labels_prohibited_from_scenario_specific_threshold_changes"
        ],
        "nber_dates_label_source_only": restrictions[
            "nber_dates_allowed_only_as_declared_validation_label_source"
        ],
        "book_examples_traceability_only": restrictions[
            "book_examples_allowed_only_as_traceability"
        ],
        "portfolio_returns_prohibited_as_rule_source": restrictions[
            "portfolio_returns_prohibited_as_rule_source"
        ],
        "label_source_without_provenance_count": counters[
            "label_source_without_provenance_count"
        ],
        "label_runtime_usage_violation_count": counters[
            "label_runtime_usage_violation_count"
        ],
        "label_tuning_usage_violation_count": counters[
            "label_tuning_usage_violation_count"
        ],
        "scenario_threshold_change_violation_count": counters[
            "scenario_threshold_change_violation_count"
        ],
        "portfolio_return_rule_source_violation_count": counters[
            "portfolio_return_rule_source_violation_count"
        ],
        "sources_missing_required_prohibition_count": len(
            sources_missing_required_prohibitions
        ),
        "policy": policy,
    }
