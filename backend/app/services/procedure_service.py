"""Compatibility helpers for RAG smoke tests.

The public checklist API remains owned by ``CopilotService``.  This module
only exposes evidence assembled by the additive RAG runtime and never creates
an independent, unreviewed procedure checklist.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.common import Citation
from app.services.rag_service import RAGService


@dataclass(frozen=True)
class ChecklistEvidence:
    source_refs: list[Citation]


class ProcedureService:
    @staticmethod
    def get_checklist(procedure_id: str) -> ChecklistEvidence:
        evidence = RAGService.search_evidence(
            query="thành phần hồ sơ",
            procedure_id=procedure_id,
            top_k=3,
        )
        source_refs = [
            Citation(
                ref_id=hit.chunk_id,
                title=f"RAG evidence {hit.source_id}",
                url_or_ref=hit.source_refs[0] if hit.source_refs else None,
            )
            for hit in evidence.hits
        ]
        return ChecklistEvidence(source_refs=source_refs)
