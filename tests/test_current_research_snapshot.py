from __future__ import annotations

import json
import subprocess
import sys

from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    summarize_current_research_snapshot_from_manifest,
    summarize_current_research_snapshot,
    write_current_research_snapshot,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
    write_current_data_refresh_manifest,
)


def test_current_research_snapshot_is_non_emitting_research_only() -> None:
    summary = summarize_current_research_snapshot()

    assert summary["current_research_snapshot_runtime_ready"] is True
    assert summary["current_snapshot_artifact_count"] == 1
    assert summary["snapshot_as_of_present"] is True
    assert summary["source_availability_summary_present"] is True
    assert summary["phase_evidence_summary_present"] is True
    assert summary["current_freshness_summary_present"] is True
    assert summary["current_evidence_readiness_present"] is True
    assert summary["phase_profile_count"] == 4
    assert summary["major_group_evidence_summary_present"] is True
    assert summary["decision_readiness_summary_present"] is True
    assert summary["blocker_summary_present"] is True
    assert summary["lineage_present"] is True
    assert summary["candidate_selection_enabled"] is False
    assert summary["candidate_phase_emitted"] is False
    assert summary["current_phase_emitted"] is False
    assert summary["predicted_current_phase_output_count"] == 0
    assert summary["selected_phase_output_count"] == 0
    assert summary["phase_rank_output_count"] == 0
    assert summary["numeric_phase_score_output_count"] == 0
    assert summary["prohibited_action_field_count"] == 0
    assert summary["economic_performance_metric_count"] == 0


def test_current_research_snapshot_write_requires_tmp(tmp_path) -> None:
    output = tmp_path / "phase39_current_snapshot.json"
    write = write_current_research_snapshot(
        build_current_research_snapshot(),
        output=output,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert write["current_research_snapshot_written"] is True
    assert payload["output_mode"] == "research_only"
    assert payload["candidate_phase_emitted"] is False
    assert payload["current_phase_emitted"] is False


def test_generate_current_research_snapshot_script(tmp_path) -> None:
    output = tmp_path / "phase39_current_snapshot.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_current_research_snapshot.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.is_file()
    assert "current_research_snapshot_runtime_ready=true" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout
    assert "current_phase_emitted=false" in result.stdout
    assert "result=passed" in result.stdout


def test_current_research_snapshot_uses_phase40_refresh_manifest(tmp_path) -> None:
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    manifest_path = tmp_path / "phase40_refresh_manifest.json"
    write_current_data_refresh_manifest(manifest, output=manifest_path)

    snapshot = build_current_research_snapshot(refresh_manifest_path=manifest_path)
    summary = summarize_current_research_snapshot_from_manifest(manifest_path)

    assert snapshot["artifact_schema_version"] == "phase40_current_research_snapshot_v1"
    assert snapshot["freeze_id"] == "book_faithful_shadow_v2_alpha37"
    assert snapshot["parent_freeze_id"] == "book_faithful_shadow_v2_alpha36"
    assert snapshot["refresh_metadata"]["refresh_manifest_hash"] == manifest["manifest_hash"]
    assert snapshot["current_freshness_summary"]["freshness_semantics_ready"] is True
    assert snapshot["current_evidence_readiness"]["phase_profile_count"] == 4
    assert snapshot["candidate_phase_emitted"] is False
    assert snapshot["current_phase_emitted"] is False
    assert summary["phase"] == "40"
    assert summary["refresh_metadata_in_snapshot"] is True
    assert summary["source_mode_visible_in_snapshot"] is True
    assert summary["fixture_fallback_explicit"] is True


def test_generate_current_research_snapshot_script_with_refresh_manifest(tmp_path) -> None:
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    manifest_path = tmp_path / "phase40_refresh_manifest.json"
    write_current_data_refresh_manifest(manifest, output=manifest_path)
    output = tmp_path / "phase40_current_snapshot.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_current_research_snapshot.py",
            "--refresh-manifest",
            str(manifest_path),
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.is_file()
    assert "phase=40" in result.stdout
    assert "refresh_mode=fixture" in result.stdout
    assert "candidate_phase_emitted=false" in result.stdout
    assert "current_phase_emitted=false" in result.stdout
