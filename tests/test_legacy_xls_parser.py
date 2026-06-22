from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.data_sources.legacy_xls import LegacyXlsError, open_legacy_workbook


def test_legacy_xls_rejects_non_biff_file(tmp_path: Path) -> None:
    path = tmp_path / "not.xls"
    path.write_text("not an xls", encoding="utf-8")

    with pytest.raises(LegacyXlsError, match="not OLE/BIFF"):
        open_legacy_workbook(path)
