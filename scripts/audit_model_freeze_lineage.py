from __future__ import annotations

from business_cycle.audits.model_freeze_lineage import summarize_model_freeze_lineage


def main() -> None:
    summary = summarize_model_freeze_lineage()
    for key in (
        "phase",
        "freeze_lineage_ready",
        "freeze_artifact_count",
        "freeze_lineage_edge_count",
        "prior_freeze_artifact_preserved",
        "silent_freeze_rewrite_count",
        "freeze_without_parent_count",
        "changed_hash_without_lineage_count",
        "decision_active_change_without_new_model_version_count",
        "holdout_reset_required_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()
