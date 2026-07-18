"""Tests for procedure-family registry and dual-source K1 candidate packaging."""

from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.data.k1_review_package import K1PackageError
from scripts.data.prepare_family_k1_review_package import main as prepare_main
from scripts.data.procedure_family_registry import (
    EXPECTED_ANCHORS,
    EXPECTED_PROCEDURE_CODES,
    FAMILY_MANIFEST_COLUMNS,
    REGISTRY_COLUMNS,
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
                "Lĩnh vực: Synthetic family registry test",
                "Trình tự thực hiện: Nội dung synthetic dùng cho kiểm thử.",
                "Cơ quan thực hiện: Cơ quan synthetic",
                "Cơ quan có thẩm quyền: Cơ quan synthetic",
                "Căn cứ pháp lý: * Văn bản synthetic (TEST-REF)",
            )
        ),
        encoding="utf-8",
    )


def _build_dual_source_fixture(root: Path) -> tuple[Path, Path]:
    data_dvc_dir = root / "data" / "Data_DVC"
    dataset_raw_dir = root / "external" / "dataset_raw"
    data_dvc_dir.mkdir(parents=True)
    dataset_raw_dir.mkdir(parents=True)
    sources = load_family_registry(TRACKED_REGISTRY)
    for source in sources.values():
        target_dir = (
            data_dvc_dir if source.source_collection == "Data_DVC" else dataset_raw_dir
        )
        _write_source(
            target_dir / f"{source.procedure_code}.txt",
            source.procedure_code,
            source.procedure_name,
        )
    (root / "artifacts").mkdir()
    return data_dvc_dir, dataset_raw_dir


class ProcedureFamilyRegistryTests(unittest.TestCase):
    def test_tracked_registry_has_exact_scope_and_anchor_invariants(self) -> None:
        sources = load_family_registry(TRACKED_REGISTRY)

        self.assertEqual(EXPECTED_PROCEDURE_CODES, set(sources))
        self.assertEqual(25, len(sources))
        self.assertEqual(
            26, sum(len(source.relationships) for source in sources.values())
        )
        for family_id, anchor_code in EXPECTED_ANCHORS.items():
            anchor = sources[anchor_code]
            self.assertTrue(
                any(
                    relationship.family_id == family_id
                    and relationship.relation_type == "anchor"
                    for relationship in anchor.relationships
                )
            )

    def test_bundled_2000986_is_one_source_with_two_family_relationships(self) -> None:
        source = load_family_registry(TRACKED_REGISTRY)["2.000986"]

        self.assertEqual("dataset_raw", source.source_collection)
        self.assertEqual(
            {"dang-ky-khai-sinh", "dang-ky-thuong-tru"},
            {relationship.family_id for relationship in source.relationships},
        )
        self.assertTrue(
            all(
                relationship.relation_type == "bundled_workflow"
                for relationship in source.relationships
            )
        )

    def test_dual_source_builder_outputs_unique_needs_review_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_dual_source_fixture(root)

            rows, report = build_family_candidate_rows(
                TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
            )

        self.assertEqual(25, len(rows))
        self.assertEqual(25, len({row["source_id"] for row in rows}))
        self.assertEqual(26, report["relationship_count"])
        self.assertTrue(all(row["review_status"] == "needs_review" for row in rows))
        self.assertTrue(all(not row["reviewed_by"] for row in rows))
        bundled = next(row for row in rows if row["source_id"] == "2.000986")
        self.assertEqual("dang-ky-khai-sinh|dang-ky-thuong-tru", bundled["family_ids"])
        self.assertEqual("dataset_raw/2.000986.txt", bundled["raw_path"])
        encoded_report = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("Nội dung synthetic dùng cho kiểm thử", encoded_report)
        self.assertNotIn(str(dataset_raw_dir), encoded_report)

    def test_builder_fails_when_external_dataset_raw_source_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_dual_source_fixture(root)
            (dataset_raw_dir / "2.000575.txt").unlink()

            with self.assertRaises(K1PackageError) as raised:
                build_family_candidate_rows(
                    TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
                )

        self.assertIn(
            "family_source_missing",
            {issue.code for issue in raised.exception.issues},
        )

    def test_builder_fails_when_source_title_differs_from_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_dual_source_fixture(root)
            _write_source(
                dataset_raw_dir / "2.000720.txt",
                "2.000720",
                "Tên thủ tục không đúng registry",
            )

            with self.assertRaises(K1PackageError) as raised:
                build_family_candidate_rows(
                    TRACKED_REGISTRY, data_dvc_dir, dataset_raw_dir
                )

        self.assertIn(
            "family_source_name_mismatch",
            {issue.code for issue in raised.exception.issues},
        )

    def test_prepare_cli_writes_family_package_below_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dvc_dir, dataset_raw_dir = _build_dual_source_fixture(root)
            output_dir = root / "artifacts" / "family-k1-review"

            with redirect_stdout(io.StringIO()):
                result = prepare_main(
                    [
                        "--repository-root",
                        str(root),
                        "--registry",
                        str(TRACKED_REGISTRY),
                        "--data-dvc-dir",
                        str(data_dvc_dir),
                        "--dataset-raw-dir",
                        str(dataset_raw_dir),
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            self.assertEqual(0, result)
            manifest = output_dir / "candidate-family-sources.csv"
            with manifest.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                self.assertEqual(
                    FAMILY_MANIFEST_COLUMNS, tuple(reader.fieldnames or ())
                )
            self.assertEqual(25, len(rows))
            self.assertTrue((output_dir / "family-provenance-report.json").is_file())
            self.assertTrue((output_dir / "family-review-checklist.md").is_file())

    def test_registry_loader_rejects_code_set_drift(self) -> None:
        with TRACKED_REGISTRY.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "drift.csv"
            with registry.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLUMNS)
                writer.writeheader()
                writer.writerows(
                    row for row in rows if row["procedure_code"] != "2.000575"
                )

            with self.assertRaises(K1PackageError) as raised:
                load_family_registry(registry)

        self.assertIn(
            "registry_code_set_mismatch",
            {issue.code for issue in raised.exception.issues},
        )


if __name__ == "__main__":
    unittest.main()
