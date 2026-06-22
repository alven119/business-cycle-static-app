"""QA6 freeze lineage and immutability audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_LINEAGE_PATH = Path("specs/audits/model_freeze_lineage.yaml")
CURRENT_QA4_FREEZE_PATH = Path("specs/audits/book_faithful_formal_scope_freeze.yaml")
PRIOR_QA4_FREEZE_PATH = Path(
    "specs/audits/book_faithful_formal_scope_freeze_v1_original_qa4.yaml"
)


def summarize_model_freeze_lineage(
    path: str | Path = DEFAULT_LINEAGE_PATH,
) -> dict[str, Any]:
    """Return freeze lineage hard-gate counts."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "model_freeze_lineage"
    ]
    versions = payload["freeze_versions"]
    ids = {row["freeze_id"] for row in versions}
    edges = [row for row in versions if row["parent_freeze_id"]]
    parent_missing = [
        row for row in edges if row["parent_freeze_id"] not in ids
    ]
    prior_preserved = _prior_freeze_preserved()
    changed_without_lineage = [
        row
        for row in versions
        if row["changed_component_ids"]
        and not row["old_component_hashes"]
        and row["parent_freeze_id"]
    ]
    decision_active_without_model = [
        row
        for row in versions
        if row["decision_behavior_changed"]
        and "model_version" not in row["changed_component_ids"]
    ]
    silent_rewrites = 0 if prior_preserved and not changed_without_lineage else 1
    return {
        "phase": "QA6",
        "freeze_lineage_ready": prior_preserved
        and not parent_missing
        and not changed_without_lineage
        and not decision_active_without_model
        and silent_rewrites == 0,
        "freeze_artifact_count": int(CURRENT_QA4_FREEZE_PATH.exists())
        + int(PRIOR_QA4_FREEZE_PATH.exists()),
        "freeze_lineage_edge_count": len(edges),
        "prior_freeze_artifact_preserved": prior_preserved,
        "silent_freeze_rewrite_count": silent_rewrites,
        "freeze_without_parent_count": sum(
            row["parent_freeze_id"] is None for row in versions
        ),
        "changed_hash_without_lineage_count": len(changed_without_lineage),
        "decision_active_change_without_new_model_version_count": len(
            decision_active_without_model
        ),
        "holdout_reset_required_count": sum(
            row["holdout_reset_required"] for row in versions
        ),
        "lineage_versions": versions,
    }


def _prior_freeze_preserved() -> bool:
    if not PRIOR_QA4_FREEZE_PATH.exists() or not CURRENT_QA4_FREEZE_PATH.exists():
        return False
    prior = yaml.safe_load(PRIOR_QA4_FREEZE_PATH.read_text(encoding="utf-8"))[
        "book_faithful_formal_scope_freeze"
    ]
    current = yaml.safe_load(CURRENT_QA4_FREEZE_PATH.read_text(encoding="utf-8"))[
        "book_faithful_formal_scope_freeze"
    ]
    return (
        prior["promotion_gate_hash"]
        == "b956a1d111f5e058cddbf8d57229ff678b3956967701ad9ab68734a5d0328259"
        and current["promotion_gate_hash"]
        == "35fba08429d1ca36e87bacf374f28a9d21a8e3806d3060502cc2cfbbccb62108"
    )
