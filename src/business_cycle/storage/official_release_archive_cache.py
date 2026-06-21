"""Cache for official release archive artifacts and reconstruction attempts."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OfficialReleaseArchiveCacheError(ValueError):
    """Raised when official archive cache metadata is invalid."""


@dataclass(frozen=True)
class CachedOfficialArchiveArtifact:
    """Cached official archive artifact metadata and optional bytes path."""

    source_id: str
    metadata: dict[str, Any]
    content_path: Path | None


class OfficialReleaseArchiveCache:
    """Atomic metadata/content cache for official release archive reconstruction."""

    schema_version = 1

    def __init__(self, root_dir: str | Path = "data/raw/official_release_archives") -> None:
        self.root_dir = Path(root_dir)

    def metadata_path(self, source_id: str) -> Path:
        return self.root_dir / f"{_clean_source_id(source_id)}.metadata.json"

    def content_path(self, source_id: str, suffix: str = ".artifact") -> Path:
        return self.root_dir / f"{_clean_source_id(source_id)}{suffix}"

    def exists(self, source_id: str) -> bool:
        return self.metadata_path(source_id).exists()

    def write_attempt(
        self,
        *,
        source_id: str,
        source_domain: str,
        artifact_url: str,
        artifact_type: str,
        release_date: str | None,
        reference_period: str | None,
        parser_id: str,
        parser_version: str,
        parse_status: str,
        extracted_row_count: int,
        content: bytes | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Write artifact metadata atomically; content is optional for blocked attempts."""

        clean_source_id = _clean_source_id(source_id)
        if self.exists(clean_source_id) and not force:
            return self.read(clean_source_id).metadata
        self.root_dir.mkdir(parents=True, exist_ok=True)
        content_checksum = None
        content_file: str | None = None
        if content is not None:
            content_file = self.content_path(clean_source_id).name
            content_tmp = self.content_path(clean_source_id).with_suffix(".artifact.tmp")
            content_tmp.write_bytes(content)
            content_checksum = _sha256(content_tmp)
            os.replace(content_tmp, self.root_dir / content_file)
        metadata = {
            "schema_version": self.schema_version,
            "source_id": clean_source_id,
            "source_domain": source_domain,
            "artifact_url": artifact_url,
            "artifact_type": artifact_type,
            "release_date": release_date,
            "reference_period": reference_period,
            "downloaded_at": _now_iso(),
            "checksum": content_checksum or _sha256_bytes(json.dumps({
                "source_id": clean_source_id,
                "artifact_url": artifact_url,
                "parse_status": parse_status,
            }, sort_keys=True).encode("utf-8")),
            "content_file": content_file,
            "parser_id": parser_id,
            "parser_version": parser_version,
            "parse_status": parse_status,
            "extracted_row_count": extracted_row_count,
            "no_secret": True,
        }
        _assert_no_secret(metadata)
        tmp = self.metadata_path(clean_source_id).with_suffix(".metadata.json.tmp")
        tmp.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.metadata_path(clean_source_id))
        return metadata

    def read(self, source_id: str) -> CachedOfficialArchiveArtifact:
        """Read and validate official archive metadata."""

        clean_source_id = _clean_source_id(source_id)
        path = self.metadata_path(clean_source_id)
        if not path.exists():
            raise OfficialReleaseArchiveCacheError(
                f"Missing official archive metadata for {clean_source_id}"
            )
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise OfficialReleaseArchiveCacheError(
                f"Corrupt official archive metadata for {clean_source_id}"
            ) from exc
        if metadata.get("schema_version") != self.schema_version:
            raise OfficialReleaseArchiveCacheError(
                f"Unsupported official archive schema for {clean_source_id}"
            )
        _assert_no_secret(metadata)
        content_file = metadata.get("content_file")
        content_path = self.root_dir / content_file if isinstance(content_file, str) else None
        if content_path is not None and not content_path.exists():
            raise OfficialReleaseArchiveCacheError(
                f"Official archive content missing for {clean_source_id}"
            )
        return CachedOfficialArchiveArtifact(
            source_id=clean_source_id,
            metadata=metadata,
            content_path=content_path,
        )

    def cached_source_ids(self) -> set[str]:
        """Return cached official archive source IDs."""

        return {path.name.removesuffix(".metadata.json") for path in self.root_dir.glob("*.metadata.json")}


def _clean_source_id(source_id: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in source_id)
    if not cleaned:
        raise OfficialReleaseArchiveCacheError("source_id must not be empty")
    return cleaned


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _assert_no_secret(value: Any) -> None:
    text = json.dumps(value, sort_keys=True)
    if "FRED_API_KEY" in text or "api_key" in text.lower():
        raise OfficialReleaseArchiveCacheError("Official archive metadata must not contain secrets")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
