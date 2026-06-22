from __future__ import annotations

from business_cycle.data_sources.eia_wti_observational_archive import (
    EiaWtiObservation,
    EiaWtiTemporalPolicy,
    select_eia_wti_observation_as_of,
)


def test_eia_wti_snapshot_fails_closed_without_verified_policy() -> None:
    rows = [
        EiaWtiObservation(
            observation_date="2008-09-29",
            availability_date="2008-09-30",
            value=100.0,
            unit="Dollars per Barrel",
            correction_status="official_history_candidate",
        )
    ]

    assert select_eia_wti_observation_as_of(rows, as_of="2008-09-30") is None


def test_eia_wti_snapshot_selects_latest_available_only_when_policy_verified() -> None:
    rows = [
        EiaWtiObservation(
            observation_date="2008-09-29",
            availability_date="2008-09-30",
            value=100.0,
            unit="Dollars per Barrel",
            correction_status="verified",
        ),
        EiaWtiObservation(
            observation_date="2008-09-30",
            availability_date="2008-10-01",
            value=101.0,
            unit="Dollars per Barrel",
            correction_status="verified",
        ),
    ]
    policy = EiaWtiTemporalPolicy(
        policy_id="fixture_verified",
        availability_rule_verified=True,
        revision_policy_verified=True,
        availability_precision="day",
        end_of_day_policy=True,
    )

    selected = select_eia_wti_observation_as_of(rows, as_of="2008-09-30", policy=policy)

    assert selected is not None
    assert selected.observation_date == "2008-09-29"
