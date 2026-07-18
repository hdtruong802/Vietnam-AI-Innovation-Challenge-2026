"""Deterministic ingestion primitives for approved RAG sources."""

from .chunking import (
    ChunkBuildReport,
    ChunkSourceMetadata,
    EvidenceChunk,
    build_evidence_chunks,
    build_report,
)
from .approved import build_approved_pack
from .normalization import NormalizedDocument, normalize_document
from .parsing import ParsedSection, parse_sections
from .retrieval import (
    ApprovedSourceRegistry,
    KeywordRetriever,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
)
from .sources import SourceDocument, SourceDocumentRegistry, SourceValidationIssue
from .evaluation import (
    GoldenQuery,
    GoldenQueryResult,
    RetrievalEvaluationReport,
    evaluate_recall_at_k,
)

__all__ = [
    "ApprovedSourceRegistry",
    "ChunkBuildReport",
    "ChunkSourceMetadata",
    "EvidenceChunk",
    "GoldenQuery",
    "GoldenQueryResult",
    "KeywordRetriever",
    "NormalizedDocument",
    "ParsedSection",
    "RetrievalEvaluationReport",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "SourceDocument",
    "SourceDocumentRegistry",
    "SourceValidationIssue",
    "build_approved_pack",
    "build_evidence_chunks",
    "build_report",
    "evaluate_recall_at_k",
    "normalize_document",
    "parse_sections",
]
