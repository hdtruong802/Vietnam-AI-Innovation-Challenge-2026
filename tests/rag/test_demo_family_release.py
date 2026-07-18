"""Tests for the explicitly synthetic-approved local family demo release."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from backend.app.rag.chunking import EvidenceChunk
from scripts.data.demo_family_release import (
    DEMO_APPROVAL_MODE,
    DEMO_DOCUMENT_VERSION,
    DEMO_RELEASE_VERSION,
    DEMO_REVIEW_DATE,
    DEMO_REVIEWER,
    DEMO_SOURCE_URL,
    apply_synthetic_demo_approval,
    build_demo_family_release,
    write_demo_family_release,
)
from scripts.data.procedure_family_registry import (
    FAMILY_MANIFEST_COLUMNS,
    build_family_candidate_rows,
    load_family_registry,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRACKED_REGISTRY = (
    REPOSITORY_ROOT / "data" / "registry" / "procedure-family-registry.csv"
)


def _write_source(path: Path, code: str, name: str) -> None:
    path.write_text(
        "\n".join(
            (
                "Chi tiết thủ tục hành chính:",
                f"Mã thủ tục: {code}",
                f"Số quyết định: TEST-{code}",
                f"Tên thủ tục: {name}",
                "Cấp thực hiện: Cấp Xã",
                "Loại thủ tục: TTHC",
                "Lĩnh vực: Synthetic demo family release test",
                "Trình tự thực hiện: Nội dung synthetic dùng cho kiểm thử.",
                "Thành phần hồ sơ: Giấy tờ synthetic.",
                "Cơ quan thực hiện: Cơ quan synthetic",
                "Cơ quan có thẩm quyền: Cơ quan synthetic",
                "Căn cứ pháp lý: Quyết định số TEST-REF",
            )
        ),
        encoding="utf-8",
    )


def _build_fixture(root: Path) -> tuple[Path, Path]:
    data_dvc_dir = root / "data" / "Data_DVC"
    dataset_raw_dir = root / "external" / "dataset_raw"
    data_dvc_dir.mkdir(parents=True)
    dataset_raw_dir.mkdir(parents=True)
    for source in load_family_registry(TRACKED_REGISTRY).values():
        target = (
            data_dvc_dir if source.source_collection == "Data_DVC" else dataset_raw_dir
        )
        _write_source(
            target / f"{source.procedure_code}.txt",
            source.procedure_code,
            source.procedure_name,
        )
    (root / "artifacts").mkdir()
    return data_dvc_dir, dataset_raw_dir


class DemoFamilyReleaseTests(unittest.TestCase):
    def test_approval_fills_exact_user_selected_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_fixture(root)
            candidates, _ = build_family_candidate_rows(
                TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
            )

            rows = apply_synthetic_demo_approval(candidates)

        self.assertEqual(25, len(rows))
        self.assertTrue(
            all(row["manifest_version"] == DEMO_RELEASE_VERSION for row in rows)
        )
        self.assertTrue(all(row["review_status"] == "approved" for row in rows))
        self.assertTrue(all(row["source_url"] == DEMO_SOURCE_URL for row in rows))
        self.assertTrue(
            all(row["document_version"] == DEMO_DOCUMENT_VERSION for row in rows)
        )
        self.assertTrue(all(row["reviewed_by"] == DEMO_REVIEWER for row in rows))
        self.assertTrue(all(row["reviewed_at"] == DEMO_REVIEW_DATE for row in rows))
        self.assertTrue(
            all("Synthetic approval" in row["review_notes"] for row in rows)
        )

    def test_build_keeps_bundled_source_in_two_runtime_families(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_fixture(root)

            rows, records, report = build_demo_family_release(
                TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
            )

        self.assertEqual(25, len(rows))
        self.assertEqual(25, len(records))
        self.assertEqual(26, report["relationship_count"])
        self.assertEqual(DEMO_RELEASE_VERSION, report["release_version"])
        self.assertEqual(DEMO_APPROVAL_MODE, report["approval_mode"])
        self.assertTrue(report["not_for_production"])
        self.assertGreater(report["chunk_count"], 25)
        bundled = next(
            record for record in records if record["source"]["source_id"] == "2.000986"
        )
        self.assertEqual(
            {"birth_registration", "residence_registration"},
            set(bundled["source"]["procedure_ids"]),
        )
        self.assertTrue(
            all(
                chunk["review_status"] == "approved"
                for record in records
                for chunk in record["chunks"]
            )
        )

    def test_written_flat_chunks_match_runtime_dataclass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_fixture(root)
            rows, records, report = build_demo_family_release(
                TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
            )
            manifest = root / "artifacts" / "demo" / "reviewed.csv"
            grouped = root / "artifacts" / "chatbot" / "pack.jsonl"
            chunks = root / "artifacts" / "chatbot" / "chunks.jsonl"
            report_path = root / "artifacts" / "chatbot" / "report.json"

            write_demo_family_release(
                rows,
                records,
                report,
                manifest,
                grouped,
                chunks,
                report_path,
                root,
            )

            with manifest.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                written_rows = list(reader)
                self.assertEqual(
                    FAMILY_MANIFEST_COLUMNS, tuple(reader.fieldnames or ())
                )
            first_chunk = json.loads(chunks.read_text(encoding="utf-8").splitlines()[0])
            for field in (
                "section_ids",
                "procedure_ids",
                "section_path",
                "source_refs",
                "legal_basis_refs",
            ):
                first_chunk[field] = tuple(first_chunk[field])
            written_report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(25, len(written_rows))
        self.assertEqual("approved", EvidenceChunk(**first_chunk).review_status)
        self.assertTrue(written_report["not_for_production"])

    def test_outputs_outside_artifacts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_fixture(root)
            rows, records, report = build_demo_family_release(
                TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
            )

            with self.assertRaises(ValueError):
                write_demo_family_release(
                    rows,
                    records,
                    report,
                    root / "tracked-reviewed.csv",
                    root / "artifacts" / "pack.jsonl",
                    root / "artifacts" / "chunks.jsonl",
                    root / "artifacts" / "report.json",
                    root,
                )


if __name__ == "__main__":
    unittest.main()
