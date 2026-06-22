from __future__ import annotations

from scripts.reconstruct_formal_official_archives import _summary


def test_artifact_integrity_counts_do_not_treat_landing_page_as_release() -> None:
    summary = _summary(
        rows=[],
        attempts=[],
        source_candidate_count=0,
        strict_ready=0,
        blocked_series=[],
        cache_dir="data/raw/official_release_archives",
        reuse_existing=True,
    )

    assert summary["landing_page_counted_as_release_artifact_count"] == 0
    assert summary["strict_artifact_with_zero_rows_count"] == 0
