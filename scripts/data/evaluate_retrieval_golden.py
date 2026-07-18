"""Evaluate Recall@K for approved keyword retrieval."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.chunking import EvidenceChunk  # noqa: E402
from backend.app.rag.evaluation import GoldenQuery, evaluate_recall_at_k  # noqa: E402
from backend.app.rag.normalization import normalize_document  # noqa: E402
from backend.app.rag.parsing import parse_sections  # noqa: E402
from backend.app.rag.retrieval import ApprovedSourceRegistry, KeywordRetriever  # noqa: E402
from backend.app.rag.sources import SourceDocument  # noqa: E402


DEFAULT_GOLDEN = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "retrieval_golden_queries.csv"
)


def _split_ids(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split("|") if item.strip())


def load_golden_queries(path: Path) -> tuple[GoldenQuery, ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return tuple(
        GoldenQuery(
            query_id=row["query_id"],
            text=row["query"],
            procedure_id=row["procedure_id"],
            expected_source_ids=_split_ids(row.get("expected_source_ids", "")),
            expected_chunk_ids=_split_ids(row.get("expected_chunk_ids", "")),
            effective_on=row.get("effective_on") or None,
        )
        for row in rows
    )


def _chunk_from_dict(value: dict[str, object]) -> EvidenceChunk:
    tuple_fields = {
        "section_ids",
        "procedure_ids",
        "section_path",
        "source_refs",
        "legal_basis_refs",
    }
    normalized = {
        key: tuple(item) if key in tuple_fields and isinstance(item, list) else item
        for key, item in value.items()
    }
    return EvidenceChunk(**normalized)  # type: ignore[arg-type]


def load_chunks(path: Path) -> tuple[EvidenceChunk, ...]:
    chunks: list[EvidenceChunk] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            decoded = json.loads(line)
            if "chunks" in decoded:
                chunks.extend(_chunk_from_dict(chunk) for chunk in decoded["chunks"])
            else:
                chunks.append(_chunk_from_dict(decoded))
    return tuple(chunks)


def sample_chunks() -> tuple[EvidenceChunk, ...]:
    from backend.app.rag.chunking import build_evidence_chunks

    specs = (
        (
            SourceDocument(
                source_id="sample-birth",
                raw_document_id="sample-birth",
                procedure_ids=("birth_registration",),
                title="Sample birth registration guidance",
                authority="Sample authority",
                jurisdiction="VN",
                source_ref="https://example.gov/sample-birth",
                document_version="sample-v1",
                document_type="official_guidance",
                effective_from="2024-01-01",
                effective_to=None,
                last_verified_at="2026-07-18",
                permission_status="official_public",
                review_status="approved",
                reviewed_by="K1",
                reviewed_at="2026-07-18",
                raw_checksum="0" * 64,
                normalized_checksum="1" * 64,
            ),
            "Thanh phan ho so: giay chung sinh va can cuoc cong dan cua cha me",
        ),
        (
            SourceDocument(
                source_id="sample-residence",
                raw_document_id="sample-residence",
                procedure_ids=("residence_registration",),
                title="Sample residence registration guidance",
                authority="Sample authority",
                jurisdiction="VN",
                source_ref="https://example.gov/sample-residence",
                document_version="sample-v1",
                document_type="official_guidance",
                effective_from="2024-01-01",
                effective_to=None,
                last_verified_at="2026-07-18",
                permission_status="official_public",
                review_status="approved",
                reviewed_by="K1",
                reviewed_at="2026-07-18",
                raw_checksum="2" * 64,
                normalized_checksum="3" * 64,
            ),
            "Thanh phan ho so: to khai thay doi thong tin cu tru va giay to cho o hop phap",
        ),
        (
            SourceDocument(
                source_id="sample-business",
                raw_document_id="sample-business",
                procedure_ids=("household_business_registration",),
                title="Sample household business guidance",
                authority="Sample authority",
                jurisdiction="VN",
                source_ref="https://example.gov/sample-business",
                document_version="sample-v1",
                document_type="official_guidance",
                effective_from="2024-01-01",
                effective_to=None,
                last_verified_at="2026-07-18",
                permission_status="official_public",
                review_status="approved",
                reviewed_by="K1",
                reviewed_at="2026-07-18",
                raw_checksum="4" * 64,
                normalized_checksum="5" * 64,
            ),
            "Thanh phan ho so: giay de nghi dang ky ho kinh doanh va giay to phap ly ca nhan",
        ),
    )
    chunks: list[EvidenceChunk] = []
    for source, text in specs:
        sections = parse_sections(normalize_document(text), source.source_id)
        chunks.extend(build_evidence_chunks(sections, source.chunk_metadata(as_of="2026-07-18")))
    return tuple(chunks)


def _require_artifacts_path(path: Path, parser: argparse.ArgumentParser) -> Path:
    resolved = path.resolve()
    artifacts = (REPOSITORY_ROOT / "artifacts").resolve()
    if artifacts not in resolved.parents:
        parser.error("--chunks must be below ignored artifacts/ unless --sample is used")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--chunks", type=Path)
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--minimum-recall-at-k", type=float, default=0.95)
    arguments = parser.parse_args(argv)

    if arguments.sample:
        chunks = sample_chunks()
    elif arguments.chunks is not None:
        chunks = load_chunks(_require_artifacts_path(arguments.chunks, parser))
    else:
        parser.error("provide --sample or --chunks artifacts/...jsonl")

    try:
        queries = load_golden_queries(arguments.golden.resolve())
        report = evaluate_recall_at_k(
            KeywordRetriever(ApprovedSourceRegistry(chunks)),
            queries,
            top_k=arguments.top_k,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Retrieval golden evaluation failed: {error}", file=sys.stderr)
        return 1

    print(
        "Retrieval golden evaluation: "
        f"queries={report.query_count} matched={report.matched_count} "
        f"blocked={report.blocked_count} recall_at_{report.top_k}={report.recall_at_k:.4f}"
    )
    return 0 if report.recall_at_k >= arguments.minimum_recall_at_k else 1


if __name__ == "__main__":
    raise SystemExit(main())
