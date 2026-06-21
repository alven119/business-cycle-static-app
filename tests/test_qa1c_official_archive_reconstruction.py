from __future__ import annotations

from pathlib import Path

import scripts.reconstruct_formal_official_archives as reconstruct


def test_archive_reconstruction_records_blocked_attempts_without_network(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = reconstruct.main(
        [
            "--all-blocked-formal",
            "--reuse-existing",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "requested_series_count=7" in output
    assert "network_request_count=0" in output
    assert "strict_ready_series_count=0" in output
    assert "blocked_series_count=7" in output
    assert "result=blocked" in output
    assert len(list(tmp_path.glob("*.metadata.json"))) > 0


def test_archive_reconstruction_reuses_existing_attempts(
    tmp_path: Path,
    capsys,
) -> None:
    args = ["--series-id", "DGS10", "--reuse-existing", "--cache-dir", str(tmp_path)]
    reconstruct.main(args)
    capsys.readouterr()

    reconstruct.main(args)

    output = capsys.readouterr().out
    assert "archive_artifact_reused_count=3" in output
    assert "archive_artifact_written_count=0" in output
