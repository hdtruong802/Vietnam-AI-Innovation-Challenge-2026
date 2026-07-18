"""Tests for Phase 6 retrieval Recall@K evaluation."""

from __future__ import annotations

import unittest

from backend.app.rag.evaluation import GoldenQuery, evaluate_recall_at_k
from backend.app.rag.retrieval import ApprovedSourceRegistry, KeywordRetriever
from scripts.data.evaluate_retrieval_golden import sample_chunks


class RetrievalEvaluationTests(unittest.TestCase):
    def test_recall_at_k_counts_expected_sources(self) -> None:
        report = evaluate_recall_at_k(
            KeywordRetriever(ApprovedSourceRegistry(sample_chunks())),
            (
                GoldenQuery(
                    query_id="birth-docs",
                    text="giay chung sinh can cuoc cha me",
                    procedure_id="birth_registration",
                    expected_source_ids=("sample-birth",),
                    effective_on="2026-07-18",
                ),
                GoldenQuery(
                    query_id="missing",
                    text="khong co ket qua",
                    procedure_id="birth_registration",
                    expected_source_ids=("missing-source",),
                    effective_on="2026-07-18",
                ),
            ),
            top_k=5,
        )

        self.assertEqual(2, report.query_count)
        self.assertEqual(1, report.matched_count)
        self.assertEqual(0.5, report.recall_at_k)
        self.assertFalse(report.results[1].matched)

    def test_golden_query_requires_expected_target(self) -> None:
        with self.assertRaises(ValueError):
            GoldenQuery(
                query_id="bad",
                text="query",
                procedure_id="birth_registration",
            )


if __name__ == "__main__":
    unittest.main()
