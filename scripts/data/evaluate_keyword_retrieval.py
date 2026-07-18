"""Smoke-test approved-only keyword retrieval against Phase 3 fixture chunks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.app.rag.retrieval import (  # noqa: E402
    ApprovedSourceRegistry,
    KeywordRetriever,
    RetrievalQuery,
)
from scripts.data.build_chunking_fixtures import build_fixture_chunks  # noqa: E402


DEFAULT_MANIFEST = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "chunking_phase1_manifest.csv"
)


def _chunks_from_records(records: list[dict[str, object]]) -> list[object]:
    # The CLI is diagnostic-only, so reuse chunk dicts via the builder's object path
    # by requesting no JSON serialization from the retrieval module.
    from backend.app.rag.chunking import EvidenceChunk

    chunks: list[EvidenceChunk] = []
    for record in records:
        for encoded in record["chunks"]:  # type: ignore[index]
            chunks.append(EvidenceChunk(**encoded))  # type: ignore[arg-type]
    return chunks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--query", default="thanh phan ho so")
    parser.add_argument("--procedure-id", default="birth_registration")
    arguments = parser.parse_args(argv)

    try:
        records, _report = build_fixture_chunks(
            arguments.manifest.resolve(), arguments.repository_root.resolve()
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Keyword retrieval evaluation failed: {error}", file=sys.stderr)
        return 1

    registry = ApprovedSourceRegistry(_chunks_from_records(records))
    retriever = KeywordRetriever(registry)
    result = retriever.search(
        RetrievalQuery(
            text=arguments.query,
            procedure_id=arguments.procedure_id,
        )
    )
    print(
        "Keyword retrieval smoke: "
        f"selected={registry.selected_count} approved={registry.approved_count} "
        f"quarantined={registry.quarantined_count} status={result.status} "
        f"reason={result.reason or 'none'} hits={len(result.hits)}"
    )
    return 0 if result.status == "blocked" and result.reason == "official_review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
