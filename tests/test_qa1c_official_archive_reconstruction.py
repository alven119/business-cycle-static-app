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
            "--no-network",
            "--cache-dir",
            str(tmp_path),
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "requested_series_count=7" in output
    assert "official_archive_network_attempted_count=0" in output
    assert "strict_ready_series_count=0" in output
    assert "blocked_series_count=7" in output
    assert "result=blocked" in output
    assert "placeholder_only_archive_entry_count=0" in output
    assert not list(tmp_path.glob("*.metadata.json"))


def test_archive_reconstruction_reuses_existing_attempts(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    args = ["--series-id", "DGS10", "--reuse-existing", "--cache-dir", str(tmp_path)]
    monkeypatch.setattr(
        reconstruct,
        "_download_url",
        lambda *_args, **_kwargs: (200, "text/html", b"<html>official</html>"),
    )
    reconstruct.main(args)
    capsys.readouterr()

    reconstruct.main(args)

    output = capsys.readouterr().out
    assert "cache_reused_artifact_count=3" in output
    assert "cache_written_artifact_count=0" in output
