from __future__ import annotations

from pathlib import Path

import scripts.reconstruct_formal_official_archives as reconstruct


def test_reconstruct_cli_accepts_all_unresolved_alias(tmp_path: Path, capsys) -> None:
    reconstruct.main(
        [
            "--all-unresolved-formal",
            "--no-network",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert "requested_series_count=7" in output
    assert "official_archive_source_candidate_count=11" in output
    assert "result=blocked" in output
