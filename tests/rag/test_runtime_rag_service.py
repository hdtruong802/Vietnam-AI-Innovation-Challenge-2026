"""Tests for Phase 8-10 runtime RAG service integration."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.chunking import ChunkSourceMetadata, build_evidence_chunks
from app.config import ENV_FILES, Settings, get_settings
from app.rag.normalization import normalize_document
from app.rag.parsing import parse_sections
from app.models.rag import EvidenceHit
from app.routers.rag import search_evidence_get
from app.services.llm_service import (
    GroundedRAGAnswerService,
    LLMResult,
    OpenAILLMClient,
    _build_grounded_prompt,
)
from app.services import rag_service
from app.services.procedure_service import ProcedureService


def _sample_chunk():
    sections = parse_sections(
        normalize_document("Thanh phan ho so: giay chung sinh can cuoc cha me"),
        "runtime-source",
    )
    return build_evidence_chunks(
        sections,
        ChunkSourceMetadata(
            source_id="runtime-source",
            procedure_ids=("birth_registration",),
            jurisdiction="VN",
            source_refs=("local-k1-fixture://runtime-source",),
            review_status="approved",
        ),
    )[0]


class RuntimeRAGServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_rag_get_settings = rag_service.get_settings
        rag_service.get_settings = lambda: Settings(legacy_rag_enabled=True)

    def tearDown(self) -> None:
        rag_service.get_settings = self._original_rag_get_settings
        rag_service.RAGService.clear_cache()

    def test_legacy_rag_is_disabled_by_default(self) -> None:
        rag_service.get_settings = lambda: Settings(legacy_rag_enabled=False)

        result = rag_service.RAGService.search_evidence("giay chung sinh")

        self.assertEqual("blocked", result.status)
        self.assertEqual("legacy_rag_disabled", result.reason)
        self.assertEqual([], result.hits)
        self.assertEqual(0, result.loaded_chunks)

    def test_settings_use_repository_and_backend_env_files(self) -> None:
        self.assertEqual(REPOSITORY_ROOT / ".env", ENV_FILES[0])
        self.assertEqual(BACKEND_ROOT / ".env", ENV_FILES[1])

    def test_openai_client_reads_current_settings_when_created(self) -> None:
        original = get_settings()
        get_settings.cache_clear()
        try:
            configured = Settings(
                openai_api_key="test-runtime-key",
                openai_model="test-runtime-model",
            )
            from app.services import llm_service

            original_get_settings = llm_service.get_settings
            llm_service.get_settings = lambda: configured
            client = OpenAILLMClient()
        finally:
            llm_service.get_settings = original_get_settings
            get_settings.cache_clear()

        self.assertEqual("test-runtime-key", client.api_key)
        self.assertEqual("test-runtime-model", client.model)
        self.assertIsNotNone(original)

    def test_load_clean_chunks_from_jsonl(self) -> None:
        chunk = _sample_chunk()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chunks.jsonl"
            path.write_text(
                json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            loaded = rag_service.load_clean_chunks(path)

        self.assertEqual((chunk,), loaded)

    def test_search_evidence_maps_runtime_procedure_id(self) -> None:
        chunk = _sample_chunk()
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: (chunk,)
            result = rag_service.RAGService.search_evidence(
                "giay chung sinh", procedure_id="dang-ky-khai-sinh"
            )
        finally:
            rag_service._cached_chunks = original

        self.assertEqual("ok", result.status)
        self.assertEqual("runtime-source", result.hits[0].source_id)

    def test_search_evidence_fails_closed_for_empty_query(self) -> None:
        result = rag_service.RAGService.search_evidence("")

        self.assertEqual("blocked", result.status)
        self.assertEqual("query_required", result.reason)
        self.assertEqual([], result.hits)

    def test_get_route_helper_supports_browser_smoke(self) -> None:
        chunk = _sample_chunk()
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: (chunk,)
            result = search_evidence_get(
                query="giay chung sinh",
                procedure_id="dang-ky-khai-sinh",
                top_k=1,
            )
        finally:
            rag_service._cached_chunks = original

        self.assertEqual("ok", result.status)
        self.assertEqual(1, len(result.hits))

    def test_checklist_includes_rag_source_when_available(self) -> None:
        chunk = _sample_chunk()
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: (chunk,)
            response = ProcedureService.get_checklist("dang-ky-khai-sinh")
        finally:
            rag_service._cached_chunks = original

        self.assertTrue(
            any(source.ref_id == chunk.chunk_id for source in response.source_refs)
        )

    def test_grounded_answer_uses_llm_when_evidence_exists(self) -> None:
        class FakeLLMClient:
            def complete_grounded_answer(self, *, query, evidence):
                return LLMResult(
                    text=f"Can chuan bi giay chung sinh [{evidence[0].chunk_id}]",
                    model="gpt-4o-mini",
                )

        chunk = _sample_chunk()
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: (chunk,)
            response = GroundedRAGAnswerService.answer(
                query="toi can giay to gi",
                procedure_id="dang-ky-khai-sinh",
                top_k=1,
                llm_client=FakeLLMClient(),
            )
        finally:
            rag_service._cached_chunks = original

        self.assertEqual("ok", response.status)
        self.assertEqual("gpt-4o-mini", response.model)
        self.assertIn(chunk.chunk_id, response.citations)
        self.assertIn(chunk.chunk_id, response.answer)

    def test_grounded_prompt_uses_accented_vietnamese_and_exact_citation_rule(
        self,
    ) -> None:
        chunk = _sample_chunk()
        hit = EvidenceHit(
            chunk_id=chunk.chunk_id,
            source_id=chunk.source_id,
            procedure_ids=list(chunk.procedure_ids),
            chunk_type=chunk.chunk_type,
            text=chunk.text,
            context_prefix=chunk.context_prefix,
            score=1.0,
            source_refs=list(chunk.source_refs),
            legal_basis_refs=list(chunk.legal_basis_refs),
        )
        prompt = _build_grounded_prompt(query="can giay to gi", evidence=[hit])

        self.assertIn("CÂU HỎI NGƯỜI DÙNG", prompt)
        self.assertIn("Trả lời ngắn gọn bằng tiếng Việt có dấu.", prompt)
        self.assertIn("không dùng nhãn [chunk_id: abc123]", prompt)
        self.assertIn("biến thể đặc biệt", prompt)

    def test_grounded_answer_fails_closed_without_evidence(self) -> None:
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: ()
            response = GroundedRAGAnswerService.answer(query="ngoai pham vi")
        finally:
            rag_service._cached_chunks = original

        self.assertEqual("official_review_required", response.status)
        self.assertEqual([], response.citations)
        self.assertEqual([], response.evidence)

    def test_grounded_answer_fails_closed_without_openai_key(self) -> None:
        chunk = _sample_chunk()
        original = rag_service._cached_chunks
        try:
            rag_service._cached_chunks = lambda: (chunk,)
            response = GroundedRAGAnswerService.answer(
                query="giay chung sinh",
                procedure_id="dang-ky-khai-sinh",
                top_k=1,
                llm_client=OpenAILLMClient(api_key=""),
            )
        finally:
            rag_service._cached_chunks = original

        self.assertEqual("official_review_required", response.status)
        self.assertEqual("missing_openai_api_key", response.reason)
        self.assertIn(chunk.chunk_id, response.citations)


if __name__ == "__main__":
    unittest.main()
