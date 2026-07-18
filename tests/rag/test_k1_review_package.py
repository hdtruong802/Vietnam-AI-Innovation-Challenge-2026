"""Tests for the K1 review-ready candidate package and validation gate."""

from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

from scripts.data.k1_review_package import (
    K1PackageError,
    K1_REVIEW_COLUMNS,
    build_candidate_rows,
    load_manifest,
    validate_reviewed_rows,
    write_manifest,
)
from scripts.data.prepare_k1_review_package import main as prepare_main
from scripts.data.validate_k1_review_package import main as validate_main

CANONICAL_FIXTURES = {
    "1.001193": (
        "Thủ tục đăng ký khai sinh",
        "dang-ky-khai-sinh",
        "Hộ tịch",
    ),
    "1.004222": (
        "Đăng ký thường trú",
        "dang-ky-thuong-tru",
        "Đăng ký, quản lý cư trú",
    ),
    "1.001612": (
        "Đăng ký thành lập hộ kinh doanh",
        "dang-ky-ho-kinh-doanh",
        "Thành lập và hoạt động doanh nghiệp",
    ),
}


def _write_source(path: Path, code: str, name: str, field_area: str) -> None:
    path.write_text(
        "\n".join(
            (
                "Chi tiết thủ tục hành chính:",
                f"Mã thủ tục: {code}",
                f"Số quyết định: TEST-{code}",
                f"Tên thủ tục: {name}",
                "Cấp thực hiện: Cấp Xã",
                "Loại thủ tục: TTHC",
                f"Lĩnh vực: {field_area}",
                "Trình tự thực hiện: Nộp hồ sơ theo hướng dẫn.",
                "Cơ quan thực hiện: Cơ quan thử nghiệm",
                "Cơ quan có thẩm quyền: Cơ quan thử nghiệm",
                "Căn cứ pháp lý: * Văn bản thử nghiệm (TEST-REF)",
            )
        ),
        encoding="utf-8",
    )


def _build_repository(root: Path) -> Path:
    source_dir = root / "data" / "Data_DVC"
    source_dir.mkdir(parents=True)
    for code, (name, _, field_area) in CANONICAL_FIXTURES.items():
        _write_source(source_dir / f"{code}.txt", code, name, field_area)
    (root / "artifacts").mkdir()
    return source_dir


def _approve_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    approved: list[dict[str, str]] = []
    for row in rows:
        updated = dict(row)
        updated.update(
            {
                "authority": "Cơ quan có thẩm quyền đã được reviewer xác minh",
                "jurisdiction": "Việt Nam / cấp xã",
                "source_url": f"https://source-{row['source_id']}.gov.vn/procedure",
                "document_version": f"reviewed-{row['decision_no']}",
                "effective_from": "2024-01-01",
                "effective_to": "",
                "last_verified_at": "2026-07-18",
                "permission_status": "official_public",
                "review_status": "approved",
                "reviewed_by": "K1 synthetic test reviewer",
                "reviewed_at": "2026-07-18",
                "review_notes": "Đã đối chiếu mã, phạm vi, hiệu lực và nguồn chính thức.",
            }
        )
        approved.append(updated)
    return approved


class K1ReviewPackageTests(unittest.TestCase):
    def test_prepare_builds_exact_candidate_set_without_auto_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            rows, report = build_candidate_rows(root, source_dir)

        self.assertEqual(3, len(rows))
        self.assertEqual(set(CANONICAL_FIXTURES), {row["source_id"] for row in rows})
        self.assertTrue(all(row["review_status"] == "needs_review" for row in rows))
        self.assertTrue(all(not row["reviewed_by"] for row in rows))
        self.assertTrue(all(not row["last_verified_at"] for row in rows))
        self.assertEqual("review_ready", report["status"])
        encoded_report = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("Trình tự thực hiện", encoded_report)
        self.assertNotIn("Nộp hồ sơ theo hướng dẫn", encoded_report)

    def test_prepare_cli_writes_manifest_report_and_checklist_under_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            output_dir = root / "artifacts" / "k1-review"

            with redirect_stdout(io.StringIO()):
                result = prepare_main(
                    [
                        "--repository-root",
                        str(root),
                        "--source-dir",
                        str(source_dir),
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            self.assertEqual(0, result)
            rows = load_manifest(output_dir / "candidate-sources.csv")
            self.assertEqual(3, len(rows))
            self.assertTrue((output_dir / "provenance-report.json").is_file())
            checklist = (output_dir / "review-checklist.md").read_text(encoding="utf-8")
            self.assertIn("not evidence that K1 approval occurred", checklist)

    def test_discovery_fails_when_canonical_source_is_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            name, _, field_area = CANONICAL_FIXTURES["1.001193"]
            _write_source(source_dir / "duplicate.txt", "1.001193", name, field_area)

            with self.assertRaises(K1PackageError) as raised:
                build_candidate_rows(root, source_dir)

        self.assertIn(
            "canonical_source_duplicate",
            {issue.code for issue in raised.exception.issues},
        )

    def test_candidate_manifest_cannot_pass_review_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            rows, _ = build_candidate_rows(root, source_dir)

            with self.assertRaises(K1PackageError) as raised:
                validate_reviewed_rows(rows, root, date(2026, 7, 18))

        codes = {issue.code for issue in raised.exception.issues}
        self.assertIn("review_status_not_approved", codes)
        self.assertIn("reviewed_by_required", codes)
        self.assertIn("source_url_required", codes)

    def test_explicit_synthetic_review_passes_and_detects_checksum_tampering(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            rows, _ = build_candidate_rows(root, source_dir)
            approved_rows = _approve_rows(rows)

            report = validate_reviewed_rows(approved_rows, root, date(2026, 7, 18))
            self.assertEqual("release_ready", report["status"])
            self.assertEqual(3, report["source_count"])

            tampered_path = root / approved_rows[0]["raw_path"]
            tampered_path.write_text(
                tampered_path.read_text(encoding="utf-8") + "\nMô tả: changed",
                encoding="utf-8",
            )
            with self.assertRaises(K1PackageError) as raised:
                validate_reviewed_rows(approved_rows, root, date(2026, 7, 18))

        self.assertIn(
            "raw_checksum_mismatch",
            {issue.code for issue in raised.exception.issues},
        )

    def test_validate_cli_does_not_write_release_report_for_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            rows, _ = build_candidate_rows(root, source_dir)
            manifest = root / "artifacts" / "k1-review" / "candidate.csv"
            report = root / "artifacts" / "k1-review" / "release.json"
            write_manifest(rows, manifest)

            with redirect_stderr(io.StringIO()):
                result = validate_main(
                    [
                        "--repository-root",
                        str(root),
                        "--manifest",
                        str(manifest),
                        "--as-of",
                        "2026-07-18",
                        "--report-output",
                        str(report),
                    ]
                )

            self.assertEqual(1, result)
            self.assertFalse(report.exists())

    def test_validate_cli_writes_report_for_explicit_synthetic_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = _build_repository(root)
            rows, _ = build_candidate_rows(root, source_dir)
            manifest = root / "artifacts" / "k1-review" / "reviewed.csv"
            report = root / "artifacts" / "k1-review" / "release.json"
            write_manifest(_approve_rows(rows), manifest)

            with redirect_stdout(io.StringIO()):
                result = validate_main(
                    [
                        "--repository-root",
                        str(root),
                        "--manifest",
                        str(manifest),
                        "--as-of",
                        "2026-07-18",
                        "--report-output",
                        str(report),
                    ]
                )

            self.assertEqual(0, result)
            self.assertEqual(
                "release_ready",
                json.loads(report.read_text(encoding="utf-8"))["status"],
            )

    def test_manifest_loader_rejects_column_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "bad.csv"
            with manifest.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=K1_REVIEW_COLUMNS[:-1])
                writer.writeheader()

            with self.assertRaises(K1PackageError):
                load_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
