from __future__ import annotations

import yaml

from business_cycle.data_sources.eia_wti_observational_archive import (
    EiaWtiTemporalPolicy,
    default_eia_wti_temporal_policy,
)


def test_eia_wti_policy_contract_blocks_until_revision_policy_verified() -> None:
    payload = yaml.safe_load(open("specs/audits/eia_wti_temporal_policy.yaml", encoding="utf-8"))
    policy = payload["eia_wti_temporal_policy"]

    assert policy["series_id"] == "DCOILWTICO"
    assert policy["availability_rule_verified"] is False
    assert policy["revision_policy_verified"] is False
    assert policy["strict_ready"] is False


def test_eia_wti_default_policy_is_not_strict_ready() -> None:
    policy = default_eia_wti_temporal_policy()

    assert isinstance(policy, EiaWtiTemporalPolicy)
    assert policy.strict_ready is False
    assert policy.blocker_reason
