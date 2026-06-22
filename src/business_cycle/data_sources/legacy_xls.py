"""Small deterministic helpers for legacy BIFF XLS workbooks."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import xlrd


BIFF_OLE_SIGNATURE = b"\xd0\xcf\x11\xe0"
PARSER_ID = "legacy_biff_xls_xlrd"
PARSER_VERSION = "1"


class LegacyXlsError(ValueError):
    """Raised when a legacy BIFF workbook cannot be parsed deterministically."""


@dataclass(frozen=True)
class LegacyWorkbook:
    path: Path
    checksum: str
    sheet_names: tuple[str, ...]
    book: Any


def open_legacy_workbook(path: str | Path) -> LegacyWorkbook:
    """Open an OLE/BIFF XLS workbook with xlrd and verify its signature."""

    workbook_path = Path(path)
    content = workbook_path.read_bytes()
    if not content.startswith(BIFF_OLE_SIGNATURE):
        raise LegacyXlsError("workbook is not OLE/BIFF XLS")
    try:
        book = xlrd.open_workbook(file_contents=content)
    except xlrd.XLRDError as exc:
        raise LegacyXlsError(f"xlrd failed to open workbook: {exc}") from exc
    sheet_names = tuple(book.sheet_names())
    if not sheet_names:
        raise LegacyXlsError("workbook contains no sheets")
    return LegacyWorkbook(
        path=workbook_path,
        checksum=hashlib.sha256(content).hexdigest(),
        sheet_names=sheet_names,
        book=book,
    )
