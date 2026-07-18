"""Build a clearly watermarked synthetic-approved procedure-family demo release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.app.rag.chunking import EvidenceChunk, build_evidence_chunks, build_report
from backend.app.rag.normalization import decode_utf8, normalize_document
from backend.app.rag.parsing import parse_sections
from backend.app.rag.sources import SourceDocument
from scripts.data.k1_review_package import require_artifacts_output
from scripts.data.procedure_family_registry import (
    FAMILY_MANIFEST_COLUMNS,
    build_family_candidate_rows,
    write_family_manifest,
)

DEMO_RELEASE_VERSION = "vaic-family-demo-release-v1"
DEMO_APPROVAL_MODE = "synthetic_demo"
DEMO_SOURCE_URL = "https://dichvucong.gov.vn/"
DEMO_DOCUMENT_VERSION = "2026"
DEMO_EFFECTIVE_FROM = "2026-01-01"
DEMO_REVIEW_DATE = "2026-07-18"
DEMO_REVIEWER = "Cao"
DEMO_PERMISSION_STATUS = "official_public"
DEMO_REVIEW_NOTES = (
    "Synthetic approval chỉ phục vụ demo local; không phải K1 hoặc xác minh pháp lý."
)
DEMO_AUTHORITY_FALLBACK = "Cơ quan có thẩm quyền theo nguồn thủ tục"

RUNTIME_PROCEDURE_IDS = {
    "dang-ky-khai-sinh": "birth_registration",
    "dang-ky-thuong-tru": "residence_registration",
    "dang-ky-ho-kinh-doanh": "household_business_registration",
}


def apply_synthetic_demo_approval(
    candidate_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Fill the exact local-demo metadata explicitly approved by the user."""

    approved_rows: list[dict[str, str]] = []
    for candidate in candidate_rows:
        row = {column: candidate.get(column, "") for column in FAMILY_MANIFEST_COLUMNS}
        row.update(
            {
                "manifest_version": DEMO_RELEASE_VERSION,
                "source_url": DEMO_SOURCE_URL,
                "document_version": DEMO_DOCUMENT_VERSION,
                "effective_from": DEMO_EFFECTIVE_FROM,
                "effective_to": "",
                "last_verified_at": DEMO_REVIEW_DATE,
                "permission_status": DEMO_PERMISSION_STATUS,
                "review_status": "approved",
                "reviewed_by": DEMO_REVIEWER,
                "reviewed_at": DEMO_REVIEW_DATE,
                "review_notes": DEMO_REVIEW_NOTES,
            }
        )
        approved_rows.append(row)
    return approved_rows


def _source_path(
    row: dict[str, str], data_dvc_dir: Path, dataset_raw_dir: Path
) -> Path:
    roots = {
        "Data_DVC": data_dvc_dir.resolve(),
        "dataset_raw": dataset_raw_dir.resolve(),
    }
    try:
        root = roots[row["source_collection"]]
    except KeyError as error:
        raise ValueError(
            f"unsupported source collection for {row['source_id']}"
        ) from error
    return root / f"{row['source_id']}.txt"


def _runtime_procedure_ids(row: dict[str, str]) -> tuple[str, ...]:
    family_ids = tuple(item for item in row["family_ids"].split("|") if item)
    try:
        return tuple(RUNTIME_PROCEDURE_IDS[family_id] for family_id in family_ids)
    except KeyError as error:
        raise ValueError(f"unsupported family id: {error.args[0]}") from error


def _validate_demo_metadata(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("demo release requires at least one source")
    expected = {
        "manifest_version": DEMO_RELEASE_VERSION,
        "source_url": DEMO_SOURCE_URL,
        "document_version": DEMO_DOCUMENT_VERSION,
        "effective_from": DEMO_EFFECTIVE_FROM,
        "last_verified_at": DEMO_REVIEW_DATE,
        "permission_status": DEMO_PERMISSION_STATUS,
        "review_status": "approved",
        "reviewed_by": DEMO_REVIEWER,
        "reviewed_at": DEMO_REVIEW_DATE,
        "review_notes": DEMO_REVIEW_NOTES,
    }
    for row in rows:
        for field, value in expected.items():
            if row.get(field) != value:
                raise ValueError(
                    f"synthetic demo metadata mismatch for {row.get('source_id')}: {field}"
                )


def build_demo_family_release(
    registry_path: Path,
    data_dvc_dir: Path,
    dataset_raw_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], dict[str, Any]]:
    """Build manifest, grouped records and report without writing artifacts."""

    candidates, candidate_report = build_family_candidate_rows(
        registry_path.resolve(), data_dvc_dir.resolve(), dataset_raw_dir.resolve()
    )
    approved_rows = apply_synthetic_demo_approval(candidates)
    _validate_demo_metadata(approved_rows)

    chunks: list[EvidenceChunk] = []
    records: list[dict[str, Any]] = []
    warnings: Counter[str] = Counter()
    for row in approved_rows:
        path = _source_path(row, data_dvc_dir, dataset_raw_dir)
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["raw_sha256"]:
            raise ValueError(
                f"raw checksum changed during build for {row['source_id']}"
            )

        document = normalize_document(decode_utf8(payload))
        normalized_checksum = hashlib.sha256(document.text.encode("utf-8")).hexdigest()
        if normalized_checksum != row["normalized_sha256"]:
            raise ValueError(
                f"normalized checksum changed during build for {row['source_id']}"
            )
        sections = parse_sections(document, row["source_id"])
        warnings.update(document.warnings)
        for section in sections:
            warnings.update(section.parse_warnings)

        source = SourceDocument(
            source_id=row["source_id"],
            raw_document_id=row["source_id"],
            procedure_ids=_runtime_procedure_ids(row),
            title=row["procedure_name"],
            authority=row["authority"] or DEMO_AUTHORITY_FALLBACK,
            jurisdiction=row["level"] or "Không có thông tin",
            source_ref=DEMO_SOURCE_URL,
            document_version=DEMO_DOCUMENT_VERSION,
            document_type="official_guidance_demo",
            effective_from=DEMO_EFFECTIVE_FROM,
            effective_to=None,
            last_verified_at=DEMO_REVIEW_DATE,
            permission_status=DEMO_PERMISSION_STATUS,
            review_status="approved",
            reviewed_by=DEMO_REVIEWER,
            reviewed_at=DEMO_REVIEW_DATE,
            raw_checksum=row["raw_sha256"],
            normalized_checksum=row["normalized_sha256"],
        )
        source_issues = source.validation_issues(as_of=DEMO_REVIEW_DATE)
        if source_issues:
            encoded = ",".join(
                f"{issue.field}:{issue.reason}" for issue in source_issues
            )
            raise ValueError(
                f"demo source validation failed for {row['source_id']}: {encoded}"
            )

        source_chunks = build_evidence_chunks(
            sections, source.chunk_metadata(as_of=DEMO_REVIEW_DATE)
        )
        chunks.extend(source_chunks)
        records.append(
            {
                "release": {
                    "release_version": DEMO_RELEASE_VERSION,
                    "approval_mode": DEMO_APPROVAL_MODE,
                    "not_for_production": True,
                    "review_notes": DEMO_REVIEW_NOTES,
                },
                "source": source.to_dict(),
                "family_ids": row["family_ids"].split("|"),
                "family_relations": row["family_relations"].split("|"),
                "release_tiers": row["release_tiers"].split("|"),
                "chunks": [chunk.to_dict() for chunk in source_chunks],
            }
        )

    manifest_payload = json.dumps(
        approved_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    manifest_checksum = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()
    chunk_report = build_report(
        chunks=chunks,
        selected=len(approved_rows),
        input_manifest_checksum=manifest_checksum,
        source_snapshot_id=candidate_report["source_snapshot_id"],
        warning_counts=warnings,
    ).to_dict()
    report = {
        **chunk_report,
        "release_version": DEMO_RELEASE_VERSION,
        "approval_mode": DEMO_APPROVAL_MODE,
        "not_for_production": True,
        "reviewer": DEMO_REVIEWER,
        "reviewed_at": DEMO_REVIEW_DATE,
        "source_url": DEMO_SOURCE_URL,
        "document_version": DEMO_DOCUMENT_VERSION,
        "unique_source_count": candidate_report["unique_source_count"],
        "relationship_count": candidate_report["relationship_count"],
    }
    return approved_rows, records, report


def write_demo_family_release(
    approved_rows: list[dict[str, str]],
    records: list[dict[str, Any]],
    report: dict[str, Any],
    manifest_output: Path,
    grouped_output: Path,
    chunks_output: Path,
    report_output: Path,
    repository_root: Path,
) -> None:
    outputs = tuple(
        require_artifacts_output(path, repository_root)
        for path in (manifest_output, grouped_output, chunks_output, report_output)
    )
    manifest_path, grouped_path, chunks_path, report_path = outputs

    write_family_manifest(approved_rows, manifest_path)
    grouped_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    with grouped_path.open("w", encoding="utf-8", newline="\n") as grouped_handle:
        for record in records:
            grouped_handle.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            )
    with chunks_path.open("w", encoding="utf-8", newline="\n") as chunks_handle:
        for record in records:
            for chunk in record["chunks"]:
                chunks_handle.write(
                    json.dumps(chunk, ensure_ascii=False, sort_keys=True) + "\n"
                )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_family_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if tuple(reader.fieldnames or ()) != FAMILY_MANIFEST_COLUMNS:
            raise ValueError("invalid family manifest columns")
    return rows
