"""Deterministic section parser for Vietnamese procedure documents."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any

from .normalization import NormalizedDocument

PARSER_VERSION = "vaic-structure-parser-v1"
SECTION_TYPES = frozenset(
    {
        "overview",
        "authority",
        "eligibility",
        "documents",
        "steps",
        "processing_time",
        "fees",
        "forms",
        "legal_basis",
        "effective_date",
        "exceptions",
        "other",
    }
)

_FIELD_TYPES: dict[str, str] = {
    "ma thu tuc": "overview",
    "so quyet dinh": "overview",
    "ten thu tuc": "overview",
    "cap thuc hien": "overview",
    "loai thu tuc": "overview",
    "linh vuc": "overview",
    "trinh tu thuc hien": "steps",
    "cach thuc thuc hien": "steps",
    "thanh phan ho so": "documents",
    "ho so bao gom": "documents",
    "thoi han giai quyet": "processing_time",
    "thoi gian giai quyet": "processing_time",
    "phi, le phi": "fees",
    "phi le phi": "fees",
    "le phi": "fees",
    "mau don, to khai": "forms",
    "bieu mau": "forms",
    "doi tuong thuc hien": "eligibility",
    "yeu cau, dieu kien thuc hien": "eligibility",
    "yeu cau dieu kien thuc hien": "eligibility",
    "co quan thuc hien": "authority",
    "co quan co tham quyen": "authority",
    "co quan duoc uy quyen": "authority",
    "co quan phoi hop": "authority",
    "dia chi tiep nhan hs": "authority",
    "ket qua thuc hien": "authority",
    "can cu phap ly": "legal_basis",
    "co so phap ly": "legal_basis",
    "ngay co hieu luc": "effective_date",
    "hieu luc thi hanh": "effective_date",
}
_INHERITED_FIELD_BOUNDARIES = frozenset({"mo ta"})
_HEADING_PREFIX = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?|[ivxlcdm]+[.)]|[a-z][.)])\s+", re.I)


@dataclass(frozen=True, slots=True)
class ParsedSection:
    section_id: str
    source_id: str
    section_path: tuple[str, ...]
    parent_section_id: str | None
    ordinal: int
    section_type: str
    text: str
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    legal_basis_refs: tuple[str, ...]
    parse_warnings: tuple[str, ...]
    parser_version: str = PARSER_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(
        character for character in decomposed if unicodedata.category(character) != "Mn"
    )
    return without_accents.replace("đ", "d")


def _classify_line(line: str, previous_type: str) -> tuple[str, bool]:
    if not line:
        return previous_type, False
    folded = _fold(line).strip()
    field = folded.split(":", maxsplit=1)[0]
    field = _HEADING_PREFIX.sub("", field).strip("[]*+- ")
    if field in _FIELD_TYPES:
        return _FIELD_TYPES[field], True
    if field in _INHERITED_FIELD_BOUNDARIES:
        return previous_type, True
    return previous_type, False


def _legal_refs(text: str) -> tuple[str, ...]:
    pattern = re.compile(
        r"\b(?:Luật|Nghị định|Thông tư|Quyết định)\s+(?:số\s+)?[\w./-]+",
        re.IGNORECASE,
    )
    return tuple(dict.fromkeys(match.group(0).strip() for match in pattern.finditer(text)))


def parse_sections(document: NormalizedDocument, source_id: str) -> list[ParsedSection]:
    """Parse normalized lines without consulting fixture labels or source paths."""

    if not source_id.strip():
        raise ValueError("source_id is required")
    if not document.lines:
        return []

    line_types: list[str] = []
    field_boundaries: list[bool] = []
    previous = "overview"
    for line in document.lines:
        current, starts_field = _classify_line(line, previous)
        line_types.append(current)
        field_boundaries.append(starts_field)
        if line:
            previous = current

    ranges: list[tuple[str, int, int]] = []
    start = 1
    current = line_types[0]
    for line_number, section_type in enumerate(line_types[1:], start=2):
        if section_type != current or field_boundaries[line_number - 1]:
            ranges.append((current, start, line_number - 1))
            current = section_type
            start = line_number
    ranges.append((current, start, len(line_types)))

    sections: list[ParsedSection] = []
    type_ordinals: dict[str, int] = {}
    for ordinal, (section_type, start_line, end_line) in enumerate(ranges, start=1):
        type_ordinals[section_type] = type_ordinals.get(section_type, 0) + 1
        text = "\n".join(document.lines[start_line - 1 : end_line]).strip()
        start_char, end_char = document.line_span(start_line, end_line)
        identity = "|".join(
            (
                PARSER_VERSION,
                source_id,
                section_type,
                str(type_ordinals[section_type]),
                str(start_line),
                str(end_line),
                hashlib.sha256(text.encode("utf-8")).hexdigest(),
            )
        )
        warnings = set(document.warnings)
        if section_type == "other":
            warnings.add("unclassified_content")
        sections.append(
            ParsedSection(
                section_id=hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24],
                source_id=source_id,
                section_path=(section_type, str(type_ordinals[section_type])),
                parent_section_id=None,
                ordinal=ordinal,
                section_type=section_type,
                text=text,
                start_line=start_line,
                end_line=end_line,
                start_char=start_char,
                end_char=end_char,
                legal_basis_refs=_legal_refs(text),
                parse_warnings=tuple(sorted(warnings)),
            )
        )
    return sections
