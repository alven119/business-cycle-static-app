#!/usr/bin/env python
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.host == "0.0.0.0":
        parser.exit(status=2, message="error: host 0.0.0.0 is not allowed\n")
    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        parser.exit(status=1, message=f"error: directory not found: {directory}\n")
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as exc:
        parser.exit(status=1, message=f"error: cannot bind {args.host}:{args.port}: {exc}\n")
    print(f"serving=http://{args.host}:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
