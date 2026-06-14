from __future__ import annotations

import json
from pathlib import Path

import scripts.validate_generated_site as validate_generated_site


def write_site(tmp_path: Path, *, html: str | None = None, snapshot: object | None = None) -> Path:
    site_dir = tmp_path / "public"
    data_dir = site_dir / "data"
    data_dir.mkdir(parents=True)
    if html is not None:
        (site_dir / "index.html").write_text(html, encoding="utf-8")
    if snapshot is not None:
        snapshot_text = snapshot if isinstance(snapshot, str) else json.dumps(snapshot, ensure_ascii=False)
        (data_dir / "cycle_snapshot.json").write_text(snapshot_text, encoding="utf-8")
    return site_dir


def valid_html() -> str:
    return "\n".join(
        [
            "<title>景氣循環儀表板</title>",
            "目前景氣位階",
            "週期位階分數",
            "轉折風險",
            "榮景期第一年剛結束",
            "下一階段觀察",
            "榮景期觀察重點",
            "不構成投資建議",
        ]
    )


def valid_snapshot() -> dict:
    return {
        "summary": {"current_phase_id": "boom"},
        "current_phase_decision": {"current_phase_id": "boom"},
    }


def test_valid_generated_site_passes(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    site_dir = write_site(tmp_path, html=valid_html(), snapshot=valid_snapshot())

    exit_code = validate_generated_site.main(["--site-dir", str(site_dir)])

    assert exit_code == 0
    assert "generated site validation passed" in capsys.readouterr().out


def test_missing_index_fails(tmp_path: Path) -> None:
    site_dir = write_site(tmp_path, snapshot=valid_snapshot())

    failures = validate_generated_site.validate_generated_site(site_dir)

    assert any("missing index.html" in failure for failure in failures)


def test_forbidden_string_fails(tmp_path: Path) -> None:
    site_dir = write_site(
        tmp_path,
        html=valid_html() + "\n維持 boom",
        snapshot=valid_snapshot(),
    )

    failures = validate_generated_site.validate_generated_site(site_dir)

    assert any("forbidden text" in failure for failure in failures)


def test_invalid_json_fails(tmp_path: Path) -> None:
    site_dir = write_site(tmp_path, html=valid_html(), snapshot="{not-json")

    failures = validate_generated_site.validate_generated_site(site_dir)

    assert any("invalid cycle_snapshot.json" in failure for failure in failures)


def test_snapshot_current_phase_must_be_boom(tmp_path: Path) -> None:
    site_dir = write_site(
        tmp_path,
        html=valid_html(),
        snapshot={"summary": {"current_phase_id": "recovery"}},
    )

    failures = validate_generated_site.validate_generated_site(site_dir)

    assert "cycle_snapshot.json current phase is not boom" in failures
