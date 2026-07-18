"""Validate metadata-only fixtures for the Phase 1 chunking dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_DIR = REPOSITORY_ROOT / "tests" / "rag" / "fixtures"
META_PATH = DEFAULT_FIXTURE_DIR / "chunking_phase1.meta.json"
MANIFEST_PATH = DEFAULT_FIXTURE_DIR / "chunking_phase1_manifest.csv"
REQUIRED_COLUMNS = {
    "raw_document_id",
    "raw_path",
    "procedure_id",
    "annotation_status",
    "raw_sha256",
    "byte_count",
    "line_count",
    "nonempty_line_count",
    "max_line_chars",
    "edge_case_tags",
    "expected_sections",
}
DOCUMENT_ID_PATTERN = re.compile(r"^[1-3]\.\d{6}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SECTION_PATTERN = re.compile(r"^([a-z_]+):(\d+)-(\d+)$")


def load_fixtures(
    meta_path: Path = META_PATH, manifest_path: Path = MANIFEST_PATH
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = set(reader.fieldnames or [])
    if columns != REQUIRED_COLUMNS:
        missing = sorted(REQUIRED_COLUMNS - columns)
        extra = sorted(columns - REQUIRED_COLUMNS)
        raise ValueError(f"Invalid manifest columns; missing={missing}, extra={extra}")
    return metadata, rows


def parse_sections(value: str) -> list[tuple[str, int, int]]:
    sections: list[tuple[str, int, int]] = []
    for encoded in value.split("|"):
        match = SECTION_PATTERN.fullmatch(encoded)
        if match is None:
            raise ValueError(f"Invalid section range: {encoded}")
        section_type, start, end = match.groups()
        sections.append((section_type, int(start), int(end)))
    return sections


def validate_manifest(
    metadata: dict[str, Any], rows: list[dict[str, str]]
) -> list[str]:
    errors: list[str] = []
    procedures = set(metadata.get("procedure_ids", []))
    taxonomy = set(metadata.get("taxonomy", []))
    selection = metadata.get("selection", {})
    expected_per_procedure = selection.get("target_per_procedure")

    if metadata.get("schema_version") != 1:
        errors.append("metadata.schema_version must be 1")
    if selection.get("raw_content_committed") is not False:
        errors.append("selection.raw_content_committed must be false")
    if selection.get("scanned_documents", 0) >= selection.get("corpus_documents", 0):
        errors.append("selection must remain bounded below the full corpus")
    if len(rows) != expected_per_procedure * len(procedures):
        errors.append("fixture count does not match procedure distribution")

    counts: Counter[str] = Counter()
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        prefix = f"manifest row {row_number}"
        document_id = row["raw_document_id"]
        procedure_id = row["procedure_id"]
        counts[procedure_id] += 1

        if document_id in seen_ids:
            errors.append(f"{prefix}: duplicate raw_document_id")
        seen_ids.add(document_id)
        if DOCUMENT_ID_PATTERN.fullmatch(document_id) is None:
            errors.append(f"{prefix}: invalid raw_document_id")
        if row["raw_path"] != f"dataset_raw/{document_id}.txt":
            errors.append(f"{prefix}: raw_path must match raw_document_id")
        if procedure_id not in procedures:
            errors.append(f"{prefix}: unknown procedure_id")
        if row["annotation_status"] != metadata.get("annotation_status"):
            errors.append(f"{prefix}: invalid annotation_status")
        if SHA256_PATTERN.fullmatch(row["raw_sha256"]) is None:
            errors.append(f"{prefix}: invalid raw_sha256")

        try:
            line_count = int(row["line_count"])
            byte_count = int(row["byte_count"])
            nonempty_count = int(row["nonempty_line_count"])
            max_line_chars = int(row["max_line_chars"])
        except ValueError:
            errors.append(f"{prefix}: structural metrics must be integers")
            continue
        if min(line_count, byte_count, nonempty_count, max_line_chars) <= 0:
            errors.append(f"{prefix}: structural metrics must be positive")

        try:
            sections = parse_sections(row["expected_sections"])
        except ValueError as error:
            errors.append(f"{prefix}: {error}")
            continue
        expected_start = 1
        for section_type, start, end in sections:
            if section_type not in taxonomy:
                errors.append(f"{prefix}: unknown section type {section_type}")
            if start != expected_start or end < start:
                errors.append(f"{prefix}: section ranges must be contiguous")
            expected_start = end + 1
        if expected_start != line_count + 1:
            errors.append(f"{prefix}: section ranges must end at line_count")

    for procedure_id in procedures:
        if counts[procedure_id] != expected_per_procedure:
            errors.append(
                f"procedure {procedure_id} has {counts[procedure_id]} fixtures; "
                f"expected {expected_per_procedure}"
            )
    return errors


def validate_raw(rows: list[dict[str, str]], repository_root: Path) -> list[str]:
    errors: list[str] = []
    for row in rows:
        document_id = row["raw_document_id"]
        raw_path = repository_root / row["raw_path"]
        prefix = f"raw fixture {document_id}"
        if not raw_path.is_file():
            errors.append(f"{prefix}: file is missing")
            continue
        payload = raw_path.read_bytes()
        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            errors.append(f"{prefix}: file is not valid UTF-8")
            continue
        lines = re.split(r"\r?\n", text)
        actual = {
            "raw_sha256": hashlib.sha256(payload).hexdigest(),
            "byte_count": len(payload),
            "line_count": len(lines),
            "nonempty_line_count": sum(bool(line.strip()) for line in lines),
            "max_line_chars": max(len(line) for line in lines),
        }
        for field, value in actual.items():
            expected: str | int = row[field]
            if field != "raw_sha256":
                expected = int(expected)
            if value != expected:
                errors.append(f"{prefix}: {field} does not match manifest")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-raw",
        action="store_true",
        help="Verify ignored raw files and checksums without printing their content.",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="Repository root containing dataset_raw for strict verification.",
    )
    arguments = parser.parse_args(argv)

    try:
        metadata, rows = load_fixtures()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Fixture validation failed: {error}", file=sys.stderr)
        return 1
    errors = validate_manifest(metadata, rows)
    if arguments.verify_raw:
        errors.extend(validate_raw(rows, arguments.repository_root.resolve()))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    procedures = Counter(row["procedure_id"] for row in rows)
    mode = "manifest+raw" if arguments.verify_raw else "manifest"
    print(f"Chunking fixtures valid ({mode}): {len(rows)} documents; {dict(procedures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
