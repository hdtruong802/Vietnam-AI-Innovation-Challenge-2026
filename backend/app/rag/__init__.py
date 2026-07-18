"""Deterministic ingestion primitives for approved RAG sources."""

from .chunking import (
    ChunkBuildReport,
    ChunkSourceMetadata,
    EvidenceChunk,
    build_evidence_chunks,
    build_report,
)
from .normalization import NormalizedDocument, normalize_document
from .parsing import ParsedSection, parse_sections
from .retrieval import (
    ApprovedSourceRegistry,
    KeywordRetriever,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
)

__all__ = [
    "ApprovedSourceRegistry",
    "ChunkBuildReport",
    "ChunkSourceMetadata",
    "EvidenceChunk",
    "KeywordRetriever",
    "NormalizedDocument",
    "ParsedSection",
    "RetrievalHit",
    "RetrievalQuery",
    "RetrievalResult",
    "build_evidence_chunks",
    "build_report",
    "normalize_document",
    "parse_sections",
]
