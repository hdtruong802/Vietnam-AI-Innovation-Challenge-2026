"""Tests for demo clean RAG pack generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.data.build_demo_clean_rag_pack import main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class DemoCleanPackTests(unittest.TestCase):
    def test_demo_clean_pack_outputs_flat_chunks(self) -> None:
        with tempfile.TemporaryDirectory(
            dir=REPOSITORY_ROOT / "artifacts"
        ) as directory:
            root = Path(directory)
            result = main(
                [
                    "--manifest-output",
                    str(root / "sources.csv"),
                    "--grouped-output",
                    str(root / "grouped.jsonl"),
                    "--chunks-output",
                    str(root / "chunks.jsonl"),
                    "--report-output",
                    str(root / "report.json"),
                ]
            )

            self.assertEqual(0, result)
            self.assertTrue((root / "sources.csv").is_file())
            self.assertTrue((root / "grouped.jsonl").is_file())
            self.assertTrue((root / "chunks.jsonl").is_file())
            self.assertTrue((root / "report.json").is_file())
            self.assertGreater((root / "chunks.jsonl").stat().st_size, 0)
            first_chunk = json.loads(
                (root / "chunks.jsonl").read_text(encoding="utf-8").splitlines()[0]
            )
            self.assertIn("Chi tiết thủ tục hành chính", first_chunk["text"])
            self.assertNotIn("Chi tiáº¿t", first_chunk["text"])


if __name__ == "__main__":
    unittest.main()
