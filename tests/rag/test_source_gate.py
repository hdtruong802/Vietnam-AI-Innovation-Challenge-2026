"""Tests for Phase 5 source approval gate."""

from __future__ import annotations

import unittest

from backend.app.rag.sources import SourceDocument, SourceDocumentRegistry


def _source(**overrides):
    values = {
        "source_id": "source-1",
        "raw_document_id": "1.000001",
        "procedure_ids": ("birth_registration",),
        "title": "Approved guidance",
        "authority": "Official authority",
        "jurisdiction": "VN",
        "source_ref": "https://example.gov/source-1",
        "document_version": "v1",
        "document_type": "official_guidance",
        "effective_from": "2024-01-01",
        "effective_to": None,
        "last_verified_at": "2026-07-18",
        "permission_status": "official_public",
        "review_status": "approved",
        "reviewed_by": "K1",
        "reviewed_at": "2026-07-18",
        "raw_checksum": "a" * 64,
        "normalized_checksum": "b" * 64,
    }
    values.update(overrides)
    return SourceDocument(**values)


class SourceGateTests(unittest.TestCase):
    def test_approved_source_builds_chunk_metadata(self) -> None:
        source = _source()
        metadata = source.chunk_metadata(as_of="2026-07-18")

        self.assertEqual("source-1", metadata.source_id)
        self.assertEqual(("birth_registration",), metadata.procedure_ids)
        self.assertEqual("approved", metadata.review_status)
        self.assertEqual(("https://example.gov/source-1",), metadata.source_refs)

    def test_needs_review_source_is_not_release_eligible(self) -> None:
        source = _source(
            review_status="needs_review", reviewed_by=None, reviewed_at=None
        )
        issues = source.validation_issues(as_of="2026-07-18")

        self.assertFalse(source.is_release_eligible(as_of="2026-07-18"))
        self.assertTrue(any(issue.field == "review_status" for issue in issues))
        with self.assertRaises(ValueError):
            source.chunk_metadata(as_of="2026-07-18")

    def test_future_or_stale_source_is_blocked(self) -> None:
        future = _source(effective_from="2027-01-01")
        stale = _source(source_id="source-2", effective_to="2025-01-01")

        self.assertFalse(future.is_release_eligible(as_of="2026-07-18"))
        self.assertFalse(stale.is_release_eligible(as_of="2026-07-18"))

    def test_registry_filters_approved_sources(self) -> None:
        approved = _source()
        blocked = _source(source_id="source-2", review_status="rejected")
        registry = SourceDocumentRegistry((approved, blocked))

        self.assertEqual((approved,), registry.approved_sources(as_of="2026-07-18"))
        self.assertIn("source-2", registry.release_issues(as_of="2026-07-18"))


if __name__ == "__main__":
    unittest.main()
