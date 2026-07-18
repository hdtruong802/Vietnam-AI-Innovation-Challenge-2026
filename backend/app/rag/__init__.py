"""Deterministic ingestion primitives for approved RAG sources."""

from .normalization import NormalizedDocument, normalize_document
from .parsing import ParsedSection, parse_sections

__all__ = ["NormalizedDocument", "ParsedSection", "normalize_document", "parse_sections"]
