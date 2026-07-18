"""Loss-aware text normalization with stable line provenance."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

NORMALIZER_VERSION = "vaic-normalizer-v1"
_HORIZONTAL_SPACE = re.compile(r"[\t\v\f \u00a0\u2007\u202f]+")
_MOJIBAKE_MARKERS = ("Ã", "Â", "Ä", "Æ", "á»", "áº")
_NAVIGATION_MARKERS = ("trang chủ", "đăng nhập", "dịch vụ công", "chuyển đến nội dung", "menu")


@dataclass(frozen=True, slots=True)
class NormalizedDocument:
    """Normalized text and offsets into that normalized representation."""

    text: str
    lines: tuple[str, ...]
    line_start_chars: tuple[int, ...]
    warnings: tuple[str, ...]
    normalizer_version: str = NORMALIZER_VERSION

    def line_span(self, start_line: int, end_line: int) -> tuple[int, int]:
        """Return an exclusive character span for a one-based inclusive line range."""

        if start_line < 1 or end_line < start_line or end_line > len(self.lines):
            raise ValueError("invalid normalized line range")
        start_char = self.line_start_chars[start_line - 1]
        end_char = self.line_start_chars[end_line - 1] + len(self.lines[end_line - 1])
        return start_char, end_char


def decode_utf8(payload: bytes) -> str:
    """Decode strictly; callers must quarantine invalid input."""

    return payload.decode("utf-8", errors="strict")


def normalize_document(text: str) -> NormalizedDocument:
    """Normalize Unicode and spacing while preserving source line count."""

    warnings: set[str] = set()
    if text.startswith("\ufeff"):
        text = text[1:]
        warnings.add("byte_order_mark_removed")
    if "\r" in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        warnings.add("line_endings_normalized")

    normalized_lines: list[str] = []
    for raw_line in text.split("\n"):
        normalized = unicodedata.normalize("NFC", raw_line)
        if normalized != raw_line:
            warnings.add("unicode_nfc_normalized")
        compact = _HORIZONTAL_SPACE.sub(" ", normalized).strip()
        if compact != normalized:
            warnings.add("horizontal_whitespace_normalized")
        normalized_lines.append(compact)

    normalized_text = "\n".join(normalized_lines)
    folded = normalized_text.casefold()
    if any(marker.casefold() in folded for marker in _MOJIBAKE_MARKERS):
        warnings.add("possible_mojibake")
    if any(marker in folded for marker in _NAVIGATION_MARKERS):
        warnings.add("navigation_noise")

    starts: list[int] = []
    cursor = 0
    for line in normalized_lines:
        starts.append(cursor)
        cursor += len(line) + 1

    return NormalizedDocument(
        text=normalized_text,
        lines=tuple(normalized_lines),
        line_start_chars=tuple(starts),
        warnings=tuple(sorted(warnings)),
    )
