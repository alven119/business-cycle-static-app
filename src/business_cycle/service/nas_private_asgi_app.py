"""ASGI app factory for private NAS service startup previews.

The factory is intentionally side-effect free at import time. Phase 101 validates
that a future local runner can import this factory, but it does not run uvicorn,
bind a port, start a live server, or connect to Postgres.
"""

from __future__ import annotations

from business_cycle.service.nas_asgi_adapter import NasAsgiAdapter


def create_app() -> NasAsgiAdapter:
    """Return the research-only NAS ASGI adapter for a private local runner."""

    return NasAsgiAdapter()
