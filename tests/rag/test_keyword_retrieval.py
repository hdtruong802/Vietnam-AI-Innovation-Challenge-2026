"""Tests for Phase 4 approved-only keyword retrieval."""

from __future__ import annotations

import unittest

from backend.app.rag.chunking import ChunkSourceMetadata, build_evidence_chunks
from backend.app.rag.normalization import normalize_document
from backend.app.rag.parsing import parse_sections
from backend.app.rag.retrieval import (
    ApprovedSourceRegistry,
    KeywordRetriever,
    RetrievalQuery,
    tokenize,
)


def _chunks(source_id: str, text: str, procedure_id: str, status: str = "approved"):
    sections = parse_sections(normalize_document(text), source_id)
    return build_evidence_chunks(
        sections,
        ChunkSourceMetadata(
            source_id=source_id,
            procedure_ids=(procedure_id,),
            jurisdiction="VN",
            effective_from="2024-01-01",
            effective_to=None,
            review_status=status,
            source_refs=(f"https://example.gov/{source_id}",),
        ),
    )


class KeywordRetrievalTests(unittest.TestCase):
    def test_tokenize_folds_vietnamese_accents(self) -> None:
        self.assertEqual(("dang", "ky", "khai", "sinh"), tokenize("Đăng ký khai sinh"))

    def test_needs_review_chunks_are_not_retrieved(self) -> None:
        registry = ApprovedSourceRegistry(
            _chunks(
                "source-1",
                "Thanh phan ho so: giay chung sinh",
                "birth_registration",
                status="needs_review",
            )
        )
        result = KeywordRetriever(registry).search(
            RetrievalQuery(
                text="giay chung sinh",
                procedure_id="birth_registration",
            )
        )

        self.assertEqual(0, registry.approved_count)
        self.assertEqual("blocked", result.status)
        self.assertEqual("official_review_required", result.reason)
        self.assertEqual((), result.hits)

    def test_retrieval_filters_by_procedure_and_ranks_keyword_match(self) -> None:
        registry = ApprovedSourceRegistry(
            [
                *_chunks(
                    "source-1",
                    "Thanh phan ho so: giay chung sinh giay chung sinh",
                    "birth_registration",
                ),
                *_chunks(
                    "source-2",
                    "Le phi: mien phi",
                    "birth_registration",
                ),
                *_chunks(
                    "source-3",
                    "Thanh phan ho so: so ho khau",
                    "residence_registration",
                ),
            ]
        )
        result = KeywordRetriever(registry).search(
            RetrievalQuery(
                text="giay chung sinh",
                procedure_id="birth_registration",
                top_k=2,
            )
        )

        self.assertEqual("ok", result.status)
        self.assertEqual("source-1", result.hits[0].source_id)
        self.assertTrue(
            all("birth_registration" in hit.procedure_ids for hit in result.hits)
        )

    def test_effective_date_filter_fail_closes_future_source(self) -> None:
        registry = ApprovedSourceRegistry(
            _chunks(
                "source-4",
                "Thanh phan ho so: giay chung sinh",
                "birth_registration",
            )
        )
        result = KeywordRetriever(registry).search(
            RetrievalQuery(
                text="giay chung sinh",
                procedure_id="birth_registration",
                effective_on="2023-12-31",
            )
        )

        self.assertEqual("blocked", result.status)
        self.assertEqual("official_review_required", result.reason)


if __name__ == "__main__":
    unittest.main()
