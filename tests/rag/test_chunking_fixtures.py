"""Tests for the metadata-only Phase 1 chunking fixtures."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "data"
    / "validate_chunking_fixtures.py"
)
SPEC = importlib.util.spec_from_file_location("validate_chunking_fixtures", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load chunking fixture validator")
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ChunkingFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata, cls.rows = validator.load_fixtures()

    def test_checked_in_manifest_is_valid(self) -> None:
        self.assertEqual([], validator.validate_manifest(self.metadata, self.rows))

    def test_manifest_is_balanced_across_three_procedures(self) -> None:
        counts = Counter(row["procedure_id"] for row in self.rows)
        self.assertEqual(
            {
                "birth_registration": 10,
                "residence_registration": 10,
                "household_business_registration": 10,
            },
            dict(counts),
        )

    def test_annotations_use_review_lifecycle_and_do_not_embed_raw_text(self) -> None:
        self.assertTrue(
            all(
                row["annotation_status"] in validator.ALLOWED_ANNOTATION_STATUSES
                for row in self.rows
            )
        )
        self.assertFalse(self.metadata["selection"]["raw_content_committed"])
        expected_columns = set(validator.REQUIRED_COLUMNS)
        self.assertTrue(all(set(row) == expected_columns for row in self.rows))

    def test_validator_rejects_non_contiguous_boundaries(self) -> None:
        rows = copy.deepcopy(self.rows)
        first_ranges = rows[0]["expected_sections"].split("|")
        first_ranges[0] = "overview:2-3"
        rows[0]["expected_sections"] = "|".join(first_ranges)
        errors = validator.validate_manifest(self.metadata, rows)
        self.assertTrue(
            any("section ranges must be contiguous" in error for error in errors)
        )

    def test_validator_rejects_unbalanced_distribution(self) -> None:
        rows = copy.deepcopy(self.rows[:-1])
        errors = validator.validate_manifest(self.metadata, rows)
        self.assertTrue(any("fixture count" in error for error in errors))
        self.assertTrue(
            any("household_business_registration" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
