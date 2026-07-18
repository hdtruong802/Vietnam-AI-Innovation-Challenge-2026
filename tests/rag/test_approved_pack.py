"""Tests for Phase 7 approved-pack build helpers."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from backend.app.rag.approved import (
    APPROVED_SOURCE_COLUMNS,
    build_approved_pack,
    load_approved_manifest,
)
from scripts.data.prepare_approved_source_manifest import build_template_rows

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PHASE1_MANIFEST = (
    REPOSITORY_ROOT / "tests" / "rag" / "fixtures" / "chunking_phase1_manifest.csv"
)


class ApprovedPackTests(unittest.TestCase):
    def test_template_rows_include_only_approved_fixture_rows(self) -> None:
        rows = build_template_rows(PHASE1_MANIFEST, REPOSITORY_ROOT, "K1", "2026-07-18")
        self.assertTrue(rows)
        self.assertTrue(all(row["review_status"] == "approved" for row in rows))
        self.assertTrue(all(row["normalized_sha256"] for row in rows))
        self.assertEqual(set(APPROVED_SOURCE_COLUMNS), set(rows[0]))

    def test_approved_manifest_requires_exact_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("source_id\nsource-1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_approved_manifest(path)

    def test_build_approved_pack_uses_reviewed_boundaries(self) -> None:
        rows = build_template_rows(PHASE1_MANIFEST, REPOSITORY_ROOT, "K1", "2026-07-18")
        row = rows[0]
        row.update(
            {
                "title": "Approved fixture source",
                "authority": "K1 reviewed authority",
                "jurisdiction": "VN",
                "source_ref": f"https://example.gov/{row['raw_document_id']}",
                "document_version": "fixture-v1",
                "effective_from": "2024-01-01",
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "approved.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=APPROVED_SOURCE_COLUMNS)
                writer.writeheader()
                writer.writerow(row)

            records, report = build_approved_pack(
                manifest, REPOSITORY_ROOT, "2026-07-18"
            )

        self.assertEqual(1, report["selected"])
        self.assertGreater(report["approved"], 0)
        self.assertEqual("approved", records[0]["source"]["review_status"])
        self.assertTrue(
            all(chunk["review_status"] == "approved" for chunk in records[0]["chunks"])
        )


if __name__ == "__main__":
    unittest.main()
