"""Small deterministic PDF text-layer extractor for Census release PDFs.

This is not OCR and intentionally supports only embedded text streams. It
handles the simple PDF operators needed by small official-format fixtures and
many text-layer PDFs: literal strings used with ``Tj`` and arrays used with
``TJ`` inside uncompressed or FlateDecode streams.
"""

from __future__ import annotations

import re
import zlib


class CensusPdfTextError(ValueError):
    """Raised when a PDF has no supported text layer."""


def extract_pdf_text_layer(content: bytes) -> str:
    """Extract visible text from supported PDF text streams."""

    if not content.startswith(b"%PDF"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CensusPdfTextError("artifact is neither PDF nor UTF-8 text") from exc
    chunks: list[str] = []
    for stream_match in re.finditer(rb"<<(?P<dict>.*?)>>\s*stream\r?\n(?P<body>.*?)\r?\nendstream", content, re.S):
        stream_dict = stream_match.group("dict")
        body = stream_match.group("body")
        if b"FlateDecode" in stream_dict:
            try:
                body = zlib.decompress(body)
            except zlib.error:
                continue
        chunks.extend(_extract_text_operators(body))
    text = "\n".join(part for part in chunks if part.strip())
    if not text.strip():
        raise CensusPdfTextError("no supported PDF text-layer operators found")
    return _normalize_pdf_text(text)


def _extract_text_operators(stream: bytes) -> list[str]:
    text: list[str] = []
    for match in re.finditer(rb"\((?:\\.|[^\\)])*\)\s*Tj", stream, re.S):
        text.append(_decode_pdf_literal(match.group(0).rsplit(b")", 1)[0] + b")"))
    for match in re.finditer(rb"\[(?P<array>.*?)\]\s*TJ", stream, re.S):
        pieces = re.findall(rb"\((?:\\.|[^\\)])*\)", match.group("array"), re.S)
        if pieces:
            text.append("".join(_decode_pdf_literal(piece) for piece in pieces))
    return text


def _decode_pdf_literal(token: bytes) -> str:
    if token.startswith(b"(") and token.endswith(b")"):
        token = token[1:-1]
    token = (
        token.replace(rb"\(", b"(")
        .replace(rb"\)", b")")
        .replace(rb"\\", b"\\")
        .replace(rb"\n", b"\n")
        .replace(rb"\r", b"\r")
        .replace(rb"\t", b"\t")
    )
    return token.decode("latin-1", errors="ignore")


def _normalize_pdf_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
