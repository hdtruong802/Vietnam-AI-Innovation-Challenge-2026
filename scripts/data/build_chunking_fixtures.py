"""Build diagnostic EvidenceChunk records for the Phase 1 fixture allowlist."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.chunking import (  # noqa: E402
    ChunkSourceMetadata,
    build_evidence_chunks,
    build_report,
)
from backend.app.rag.normalization import decode_utf8, normalize_document  # noqa: E402
from backend.app.rag.parsing import parse_sections  # noqa: E402


DEFAULT_MANIFEST = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "chunking_phase1_manifest.csv"
)


def _manifest_checksum(manifest_path: Path) -> str:
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def build_fixture_chunks(
    manifest_path: Path,
    repository_root: Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    records: list[dict[str, object]] = []
    chunks = []
    warnings: Counter[str] = Counter()
    for row in rows:
        raw_path = repository_root / row["raw_path"]
        payload = raw_path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["raw_sha256"]:
            raise ValueError(f"checksum mismatch for {row['raw_document_id']}")
        document = normalize_document(decode_utf8(payload))
        sections = parse_sections(document, row["raw_document_id"])
        warnings.update(document.warnings)
        for section in sections:
            warnings.update(section.parse_warnings)

        metadata = ChunkSourceMetadata(
            source_id=row["raw_document_id"],
            procedure_ids=(row["procedure_id"],),
            review_status=row["annotation_status"],
        )
        document_chunks = build_evidence_chunks(sections, metadata)
        chunks.extend(document_chunks)
        records.append(
            {
                "source_id": row["raw_document_id"],
                "procedure_id": row["procedure_id"],
                "review_status": row["annotation_status"],
                "chunks": [chunk.to_dict() for chunk in document_chunks],
            }
        )

    report = build_report(
        chunks=chunks,
        selected=len(rows),
        input_manifest_checksum=_manifest_checksum(manifest_path),
        source_snapshot_id=f"phase1-fixtures:{_manifest_checksum(manifest_path)[:16]}",
        warning_counts=warnings,
    )
    return records, report.to_dict()


def _require_artifacts_path(
    output: Path, repository_root: Path, parser: argparse.ArgumentParser
) -> Path:
    resolved = output.resolve()
    artifacts = (repository_root / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("--output and --report-output must be below ignored artifacts/")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report-output", type=Path)
    arguments = parser.parse_args(argv)

    repository_root = arguments.repository_root.resolve()
    try:
        records, report = build_fixture_chunks(
            arguments.manifest.resolve(), repository_root
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Chunk build failed: {error}", file=sys.stderr)
        return 1

    if arguments.output is not None:
        output = _require_artifacts_path(arguments.output, repository_root, parser)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    if arguments.report_output is not None:
        report_output = _require_artifacts_path(
            arguments.report_output, repository_root, parser
        )
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(
        "Chunk build valid: "
        f"documents={report['selected']} chunks={report['chunk_count']} "
        f"p95_tokens={report['token_percentiles']['p95']} "
        f"max_tokens={report['token_percentiles']['p100']} "
        f"tokenizer={report['tokenizer_id']} "
        f"approved={report['approved']} quarantined={report['quarantined']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
