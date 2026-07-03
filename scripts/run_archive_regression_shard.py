#!/usr/bin/env python3
"""Run a governed archive-regression shard."""

from __future__ import annotations

from business_cycle.audits.archive_regression_shards import (
    main_run_archive_regression_shard,
)


if __name__ == "__main__":
    raise SystemExit(main_run_archive_regression_shard())
