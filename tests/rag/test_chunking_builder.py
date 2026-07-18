"""Tests for deterministic Phase 3 evidence chunk building."""

from __future__ import annotations

import unittest

from backend.app.rag.chunking import (
    ChunkSourceMetadata,
    build_evidence_chunks,
    build_report,
)
from backend.app.rag.normalization import normalize_document
from backend.app.rag.parsing import parse_sections


class ChunkBuilderTests(unittest.TestCase):
    def test_chunks_are_deterministic_and_keep_provenance(self) -> None:
        sections = parse_sections(
            normalize_document(
                "Ten thu tuc: Demo\n" "Thanh phan ho so: First paper\n" "Le phi: none"
            ),
            "source-1",
        )
        metadata = ChunkSourceMetadata(
            source_id="source-1",
            procedure_ids=("birth_registration",),
            jurisdiction="VN",
            review_status="needs_review",
        )

        first = build_evidence_chunks(sections, metadata)
        second = build_evidence_chunks(sections, metadata)

        self.assertEqual(first, second)
        self.assertTrue(all(chunk.chunk_id for chunk in first))
        self.assertTrue(all(chunk.source_id == "source-1" for chunk in first))
        self.assertTrue(all(chunk.section_ids for chunk in first))
        self.assertTrue(
            all(chunk.procedure_ids == ("birth_registration",) for chunk in first)
        )
        self.assertTrue(all(chunk.review_status == "needs_review" for chunk in first))

    def test_short_compatible_sibling_sections_are_merged(self) -> None:
        sections = parse_sections(
            normalize_document(
                "Co quan thuc hien: Ward committee\n"
                "Co quan co tham quyen: District committee"
            ),
            "source-2",
        )
        chunks = build_evidence_chunks(
            sections,
            ChunkSourceMetadata(
                source_id="source-2",
                procedure_ids=("residence_registration",),
            ),
        )

        self.assertEqual(1, len(chunks))
        self.assertEqual(2, len(chunks[0].section_ids))
        self.assertEqual("authority", chunks[0].chunk_type)

    def test_long_section_is_split_under_hard_budget(self) -> None:
        text = "Thanh phan ho so: " + " ".join(f"paper{i}" for i in range(1200))
        sections = parse_sections(normalize_document(text), "source-3")
        chunks = build_evidence_chunks(
            sections,
            ChunkSourceMetadata(
                source_id="source-3",
                procedure_ids=("household_business_registration",),
            ),
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.token_count <= 450 for chunk in chunks))
        self.assertTrue(
            all(
                any(part.startswith("part-") for part in chunk.section_path)
                for chunk in chunks
            )
        )

    def test_report_is_stable_and_counts_needs_review_as_quarantined(self) -> None:
        sections = parse_sections(normalize_document("Le phi: none"), "source-4")
        chunks = build_evidence_chunks(
            sections,
            ChunkSourceMetadata(
                source_id="source-4", procedure_ids=("birth_registration",)
            ),
        )
        first = build_report(
            chunks, selected=1, input_manifest_checksum="abc", source_snapshot_id="snap"
        )
        second = build_report(
            chunks, selected=1, input_manifest_checksum="abc", source_snapshot_id="snap"
        )

        self.assertEqual(first, second)
        self.assertEqual(0, first.approved)
        self.assertEqual(len(chunks), first.quarantined)
        self.assertEqual(len(chunks), first.chunk_count)


if __name__ == "__main__":
    unittest.main()
