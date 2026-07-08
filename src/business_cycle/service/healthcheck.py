"""Healthcheck helper for the private NAS app container."""

from __future__ import annotations

from argparse import ArgumentParser
import json
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from business_cycle.service.nas_private_asgi_app import create_app


def build_healthcheck_summary(
    *,
    url: str | None = None,
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    """Return a side-effect-light healthcheck summary."""

    target_url = url if url is not None else os.environ.get(
        "BUSINESS_CYCLE_HEALTHCHECK_URL",
    )
    if not target_url:
        app = create_app()
        return {
            "healthcheck_ready": callable(app),
            "mode": "import_only",
            "status": "ok" if callable(app) else "blocked",
        }

    request = Request(target_url, headers=_headers())
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            status_code = int(response.status)
            body = response.read().decode("utf-8")
    except URLError as exc:
        return {
            "healthcheck_ready": False,
            "mode": "http",
            "status": "blocked",
            "error": exc.__class__.__name__,
        }
    return {
        "healthcheck_ready": 200 <= status_code < 300,
        "mode": "http",
        "status": "ok" if 200 <= status_code < 300 else "blocked",
        "status_code": status_code,
        "body_preview": body[:200],
    }


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser()
    parser.add_argument("--url", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=2.0)
    args = parser.parse_args(argv)

    summary = build_healthcheck_summary(
        url=args.url,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["healthcheck_ready"] else 1


def _headers() -> dict[str, str]:
    secret = os.environ.get("BUSINESS_CYCLE_APP_SESSION_SECRET")
    if not secret:
        return {}
    header_name = os.environ.get(
        "BUSINESS_CYCLE_APP_SESSION_HEADER",
        "X-Business-Cycle-Session",
    )
    return {header_name: secret}


if __name__ == "__main__":
    raise SystemExit(main())
