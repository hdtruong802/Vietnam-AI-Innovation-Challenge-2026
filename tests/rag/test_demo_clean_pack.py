"""Tests for demo clean RAG pack generation."""

from __future__ import annotations

import unittest

from scripts.data.build_demo_clean_rag_pack import main


class DemoCleanPackTests(unittest.TestCase):
    def test_demo_clean_pack_requires_explicit_approved_manifest(self) -> None:
        self.assertEqual(2, main([]))


if __name__ == "__main__":
    unittest.main()
