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

PHASE1_COLUMNS = (
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
)


def _write_candidate_fixture(repository_root: Path) -> Path:
    raw_path = repository_root / "dataset_raw" / "canonical-birth.txt"
    raw_path.parent.mkdir(parents=True)
    raw_path.write_text(
        "Mã thủ tục: 1.001193\nTên thủ tục: Đăng ký khai sinh",
        encoding="utf-8",
    )
    manifest = repository_root / "phase1.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PHASE1_COLUMNS)
        writer.writeheader()
        writer.writerow(
            {
                "raw_document_id": "canonical-birth",
                "raw_path": "dataset_raw/canonical-birth.txt",
                "procedure_id": "birth_registration",
                "annotation_status": "approved",
                "expected_sections": "overview:1-2",
            }
        )
    return manifest


class ApprovedPackTests(unittest.TestCase):
    def test_template_rows_remain_candidates_until_explicit_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            phase1_manifest = _write_candidate_fixture(repository_root)
            rows = build_template_rows(phase1_manifest, repository_root)
        self.assertTrue(rows)
        self.assertTrue(all(row["review_status"] == "needs_review" for row in rows))
        self.assertTrue(all(not row["reviewed_by"] for row in rows))
        self.assertTrue(all(not row["last_verified_at"] for row in rows))
        self.assertTrue(all(row["normalized_sha256"] for row in rows))
        self.assertEqual(set(APPROVED_SOURCE_COLUMNS), set(rows[0]))

    def test_approved_manifest_requires_exact_columns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("source_id\nsource-1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_approved_manifest(path)

    def test_build_approved_pack_uses_reviewed_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository_root = Path(directory)
            phase1_manifest = _write_candidate_fixture(repository_root)
            rows = build_template_rows(phase1_manifest, repository_root)
            row = rows[0]
            row.update(
                {
                    "title": "Approved fixture source",
                    "authority": "K1 reviewed authority",
                    "jurisdiction": "VN",
                    "source_ref": f"https://example.gov/{row['raw_document_id']}",
                    "document_version": "fixture-v1",
                    "effective_from": "2024-01-01",
                    "last_verified_at": "2026-07-18",
                    "permission_status": "official_public",
                    "review_status": "approved",
                    "reviewed_by": "K1-test-reviewer",
                    "reviewed_at": "2026-07-18",
                }
            )
            manifest = repository_root / "approved.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=APPROVED_SOURCE_COLUMNS)
                writer.writeheader()
                writer.writerow(row)

            records, report = build_approved_pack(
                manifest, repository_root, "2026-07-18"
            )

        self.assertEqual(1, report["selected"])
        self.assertGreater(report["approved"], 0)
        self.assertEqual("approved", records[0]["source"]["review_status"])
        self.assertTrue(
            all(chunk["review_status"] == "approved" for chunk in records[0]["chunks"])
        )


if __name__ == "__main__":
    unittest.main()
