"""Build approved RAG chunks from K1-reviewed source manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .chunking import EvidenceChunk, build_evidence_chunks, build_report
from .normalization import decode_utf8, normalize_document
from .parsing import PARSER_VERSION, ParsedSection
from .sources import SourceDocument, SourceDocumentRegistry

APPROVED_SOURCE_COLUMNS = (
    "source_id",
    "raw_document_id",
    "raw_path",
    "procedure_ids",
    "title",
    "authority",
    "jurisdiction",
    "source_ref",
    "document_version",
    "document_type",
    "effective_from",
    "effective_to",
    "last_verified_at",
    "permission_status",
    "review_status",
    "reviewed_by",
    "reviewed_at",
    "raw_sha256",
    "normalized_sha256",
    "expected_sections",
)

_SECTION_RANGE = re.compile(r"^([a-z_]+):(\d+)-(\d+)$")
_LEGAL_REF = re.compile(
    r"\b(?:Luật|Nghị định|Thông tư|Quyết định)\s+(?:số\s+)?[\w./-]+",
    re.IGNORECASE,
)


def split_pipe(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


def parse_expected_sections(value: str) -> tuple[tuple[str, int, int], ...]:
    ranges: list[tuple[str, int, int]] = []
    for encoded in value.split("|"):
        match = _SECTION_RANGE.fullmatch(encoded)
        if match is None:
            raise ValueError(f"invalid section range: {encoded}")
        section_type, start, end = match.groups()
        ranges.append((section_type, int(start), int(end)))
    return tuple(ranges)


def legal_refs(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(match.group(0).strip() for match in _LEGAL_REF.finditer(text)))


def source_from_manifest_row(row: dict[str, str]) -> SourceDocument:
    return SourceDocument(
        source_id=row["source_id"],
        raw_document_id=row["raw_document_id"],
        procedure_ids=split_pipe(row["procedure_ids"]),
        title=row["title"],
        authority=row["authority"],
        jurisdiction=row["jurisdiction"],
        source_ref=row["source_ref"],
        document_version=row["document_version"],
        document_type=row["document_type"],
        effective_from=row["effective_from"] or None,
        effective_to=row["effective_to"] or None,
        last_verified_at=row["last_verified_at"],
        permission_status=row["permission_status"],
        review_status=row["review_status"],
        reviewed_by=row["reviewed_by"] or None,
        reviewed_at=row["reviewed_at"] or None,
        raw_checksum=row["raw_sha256"],
        normalized_checksum=row["normalized_sha256"],
        parser_version=PARSER_VERSION,
    )


def reviewed_sections(
    ranges: tuple[tuple[str, int, int], ...],
    document_text_lines: tuple[str, ...],
    source_id: str,
    line_span,
    parse_warnings: tuple[str, ...],
) -> list[ParsedSection]:
    sections: list[ParsedSection] = []
    type_ordinals: Counter[str] = Counter()
    expected_start = 1
    for ordinal, (section_type, start_line, end_line) in enumerate(ranges, start=1):
        if start_line != expected_start or end_line < start_line:
            raise ValueError("section ranges must be contiguous")
        if end_line > len(document_text_lines):
            raise ValueError("section range exceeds normalized document")
        expected_start = end_line + 1
        type_ordinals[section_type] += 1
        text = "\n".join(document_text_lines[start_line - 1 : end_line]).strip()
        start_char, end_char = line_span(start_line, end_line)
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
                legal_basis_refs=legal_refs(text),
                parse_warnings=parse_warnings,
            )
        )
    if expected_start != len(document_text_lines) + 1:
        raise ValueError("section ranges must cover normalized document")
    return sections


def load_approved_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = tuple(reader.fieldnames or ())
    if columns != APPROVED_SOURCE_COLUMNS:
        raise ValueError(
            "invalid approved source manifest columns; "
            f"expected={APPROVED_SOURCE_COLUMNS} actual={columns}"
        )
    return rows


def build_approved_pack(
    manifest_path: Path,
    repository_root: Path,
    as_of: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = load_approved_manifest(manifest_path)
    sources = tuple(source_from_manifest_row(row) for row in rows)
    registry = SourceDocumentRegistry(sources)
    issues = registry.release_issues(as_of=as_of)
    if issues:
        encoded = "; ".join(
            f"{source_id}={','.join(issue.field + ':' + issue.reason for issue in source_issues)}"
            for source_id, source_issues in sorted(issues.items())
        )
        raise ValueError(f"approved source validation failed: {encoded}")

    records: list[dict[str, Any]] = []
    chunks: list[EvidenceChunk] = []
    warnings: Counter[str] = Counter()
    for row, source in zip(rows, sources, strict=True):
        raw_path = repository_root / row["raw_path"]
        payload = raw_path.read_bytes()
        raw_sha256 = hashlib.sha256(payload).hexdigest()
        if raw_sha256 != row["raw_sha256"]:
            raise ValueError(f"checksum mismatch for {row['raw_document_id']}")

        document = normalize_document(decode_utf8(payload))
        normalized_sha256 = hashlib.sha256(document.text.encode("utf-8")).hexdigest()
        if normalized_sha256 != row["normalized_sha256"]:
            raise ValueError(f"normalized checksum mismatch for {row['raw_document_id']}")
        warnings.update(document.warnings)
        sections = reviewed_sections(
            parse_expected_sections(row["expected_sections"]),
            document.lines,
            source.source_id,
            document.line_span,
            document.warnings,
        )
        for section in sections:
            warnings.update(section.parse_warnings)
        document_chunks = build_evidence_chunks(
            sections,
            source.chunk_metadata(as_of=as_of),
        )
        chunks.extend(document_chunks)
        records.append(
            {
                "source": source.to_dict(),
                "chunks": [chunk.to_dict() for chunk in document_chunks],
            }
        )

    input_manifest_checksum = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    report = build_report(
        chunks=chunks,
        selected=len(rows),
        input_manifest_checksum=input_manifest_checksum,
        source_snapshot_id=f"approved-sources:{input_manifest_checksum[:16]}",
        warning_counts=warnings,
    )
    return records, report.to_dict()


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
