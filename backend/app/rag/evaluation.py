"""Deterministic retrieval evaluation helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .retrieval import KeywordRetriever, RetrievalQuery

EVALUATOR_VERSION = "vaic-retrieval-evaluator-v1"


@dataclass(frozen=True, slots=True)
class GoldenQuery:
    query_id: str
    text: str
    procedure_id: str
    expected_source_ids: tuple[str, ...] = ()
    expected_chunk_ids: tuple[str, ...] = ()
    effective_on: str | None = None

    def __post_init__(self) -> None:
        if not self.query_id.strip():
            raise ValueError("query_id is required")
        if not self.text.strip():
            raise ValueError("query text is required")
        if not self.procedure_id.strip():
            raise ValueError("procedure_id is required")
        if not self.expected_source_ids and not self.expected_chunk_ids:
            raise ValueError("at least one expected source or chunk is required")


@dataclass(frozen=True, slots=True)
class GoldenQueryResult:
    query_id: str
    status: str
    hit_count: int
    matched: bool
    expected_source_ids: tuple[str, ...]
    expected_chunk_ids: tuple[str, ...]
    returned_source_ids: tuple[str, ...]
    returned_chunk_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationReport:
    evaluator_version: str
    query_count: int
    matched_count: int
    blocked_count: int
    recall_at_k: float
    top_k: int
    results: tuple[GoldenQueryResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_recall_at_k(
    retriever: KeywordRetriever,
    queries: Iterable[GoldenQuery],
    top_k: int = 5,
) -> RetrievalEvaluationReport:
    if top_k < 1:
        raise ValueError("top_k must be positive")

    results: list[GoldenQueryResult] = []
    for query in queries:
        retrieval = retriever.search(
            RetrievalQuery(
                text=query.text,
                procedure_id=query.procedure_id,
                effective_on=query.effective_on,
                top_k=top_k,
            )
        )
        returned_sources = tuple(hit.source_id for hit in retrieval.hits)
        returned_chunks = tuple(hit.chunk_id for hit in retrieval.hits)
        matched = bool(set(query.expected_source_ids) & set(returned_sources)) or bool(
            set(query.expected_chunk_ids) & set(returned_chunks)
        )
        results.append(
            GoldenQueryResult(
                query_id=query.query_id,
                status=retrieval.status,
                hit_count=len(retrieval.hits),
                matched=matched,
                expected_source_ids=query.expected_source_ids,
                expected_chunk_ids=query.expected_chunk_ids,
                returned_source_ids=returned_sources,
                returned_chunk_ids=returned_chunks,
            )
        )

    query_count = len(results)
    matched_count = sum(result.matched for result in results)
    blocked_count = sum(result.status == "blocked" for result in results)
    recall = matched_count / query_count if query_count else 1.0
    return RetrievalEvaluationReport(
        evaluator_version=EVALUATOR_VERSION,
        query_count=query_count,
        matched_count=matched_count,
        blocked_count=blocked_count,
        recall_at_k=recall,
        top_k=top_k,
        results=tuple(results),
    )
