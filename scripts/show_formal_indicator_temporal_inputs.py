#!/usr/bin/env python
"""Compatibility wrapper for formal indicator temporal provenance output."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


if __name__ == "__main__":
    from explain_formal_indicator_temporal_inputs import main

    raise SystemExit(main())
