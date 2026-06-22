"""QA extraction prerequisite diagnostics."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractionPrerequisiteSummary:
    xlrd_available: bool
    xlrd_version: str | None
    tesseract_available: bool
    tesseract_version: str | None
    pdftoppm_available: bool
    pdftoppm_version: str | None
    controlled_ocr_available: bool
    english_ocr_model_available: bool
    result: str


def summarize_extraction_prerequisites() -> ExtractionPrerequisiteSummary:
    """Return deterministic local extraction prerequisite status."""

    xlrd_available = importlib.util.find_spec("xlrd") is not None
    xlrd_version = _package_version("xlrd") if xlrd_available else None
    tesseract_version = _executable_version("tesseract", ["tesseract", "--version"])
    pdftoppm_version = _executable_version("pdftoppm", ["pdftoppm", "-v"])
    tesseract_available = tesseract_version is not None
    pdftoppm_available = pdftoppm_version is not None
    english = _english_ocr_model_available() if tesseract_available else False
    controlled = (
        xlrd_available
        and importlib.util.find_spec("pytesseract") is not None
        and importlib.util.find_spec("pdf2image") is not None
        and importlib.util.find_spec("PIL") is not None
        and tesseract_available
        and pdftoppm_available
        and english
    )
    return ExtractionPrerequisiteSummary(
        xlrd_available=xlrd_available,
        xlrd_version=xlrd_version,
        tesseract_available=tesseract_available,
        tesseract_version=tesseract_version,
        pdftoppm_available=pdftoppm_available,
        pdftoppm_version=pdftoppm_version,
        controlled_ocr_available=controlled,
        english_ocr_model_available=english,
        result="passed" if controlled else "blocked",
    )


def _package_version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def _executable_version(name: str, args: list[str]) -> str | None:
    if shutil.which(name) is None:
        return None
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = completed.stdout or completed.stderr
    return text.splitlines()[0] if text.splitlines() else None


def _english_ocr_model_available() -> bool:
    try:
        completed = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return "eng" in {line.strip() for line in completed.stdout.splitlines()}
