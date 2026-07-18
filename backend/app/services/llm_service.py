from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI, OpenAIError

from app.config import get_settings
from app.models.rag import EvidenceHit, GroundedAnswerResponse
from app.services.rag_service import RAGService

OFFICIAL_REVIEW_REQUIRED = "official_review_required"


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str


class LLMClient(Protocol):
    def complete_grounded_answer(
        self,
        *,
        query: str,
        evidence: list[EvidenceHit],
    ) -> LLMResult: ...


class OpenAILLMClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.api_key = settings.openai_api_key if api_key is None else api_key
        self.model = settings.openai_model if model is None else model
        self.base_url = settings.openai_base_url if base_url is None else base_url
        self.timeout_seconds = (
            settings.openai_timeout_seconds
            if timeout_seconds is None
            else timeout_seconds
        )

    def complete_grounded_answer(
        self,
        *,
        query: str,
        evidence: list[EvidenceHit],
    ) -> LLMResult:
        if not self.api_key:
            raise RuntimeError("missing_openai_api_key")

        client_kwargs = {
            "api_key": self.api_key,
            "timeout": self.timeout_seconds,
        }
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý thủ tục hành chính. Chỉ trả lời dựa trên "
                        "EVIDENCE được cung cấp. Nếu evidence không đủ để kết luận, "
                        "hãy nói cần chuyển cán bộ hoặc nguồn chính thức xem lại. "
                        "Không thêm căn cứ ngoài evidence. Mỗi ý quan trọng phải gắn "
                        "mã nguồn đúng dạng [ma_chunk], ví dụ [abc123]. Không viết "
                        "[chunk_id: abc123]. Không tự suy ra rằng người dùng thuộc "
                        "trường hợp lưu động, đăng ký lại, có yếu tố nước ngoài hoặc "
                        "một trường hợp đặc biệt khác khi câu hỏi chưa nêu rõ."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_grounded_prompt(query=query, evidence=evidence),
                },
            ],
        )
        content = response.choices[0].message.content or ""
        return LLMResult(text=content.strip(), model=self.model)


def _build_grounded_prompt(*, query: str, evidence: list[EvidenceHit]) -> str:
    evidence_blocks = []
    for index, hit in enumerate(evidence, start=1):
        source_ref = hit.source_refs[0] if hit.source_refs else hit.source_id
        evidence_blocks.append(
            "\n".join(
                [
                    f"EVIDENCE {index}",
                    f"chunk_id: {hit.chunk_id}",
                    f"source_ref: {source_ref}",
                    f"score: {hit.score:.4f}",
                    f"context: {hit.context_prefix}",
                    f"text: {hit.text}",
                ]
            )
        )
    return (
        f"CÂU HỎI NGƯỜI DÙNG:\n{query}\n\n"
        "EVIDENCE ĐÃ DUYỆT:\n" + "\n\n".join(evidence_blocks) + "\n\nYÊU CẦU TRẢ LỜI:\n"
        "- Trả lời ngắn gọn bằng tiếng Việt có dấu.\n"
        "- Chỉ sử dụng thông tin trong EVIDENCE.\n"
        "- Chỉ trả lời đúng nội dung được hỏi; không thêm cảnh báo hoặc trường hợp ngoại lệ không liên quan.\n"
        "- Nếu evidence chỉ nói về một biến thể đặc biệt mà câu hỏi chưa xác định, hãy hỏi lại để làm rõ thay vì áp dụng biến thể đó.\n"
        "- Nếu có cảnh báo hoặc ràng buộc quan trọng, nêu rõ và dẫn [ma_chunk].\n"
        "- Citation phải dùng đúng mã chunk thực tế, ví dụ [abc123], không dùng nhãn [chunk_id: abc123].\n"
        "- Không khẳng định điều không có trong EVIDENCE.\n"
    )


def _citations_from_hits(hits: list[EvidenceHit]) -> list[str]:
    citations: list[str] = []
    for hit in hits:
        if hit.chunk_id not in citations:
            citations.append(hit.chunk_id)
    return citations


class GroundedRAGAnswerService:
    @staticmethod
    def answer(
        *,
        query: str,
        procedure_id: str | None = None,
        top_k: int = 5,
        llm_client: LLMClient | None = None,
    ) -> GroundedAnswerResponse:
        configured_model = get_settings().openai_model
        evidence_result = RAGService.search_evidence(
            query=query,
            procedure_id=procedure_id,
            top_k=top_k,
        )
        if evidence_result.status != "ok" or not evidence_result.hits:
            return GroundedAnswerResponse(
                status=OFFICIAL_REVIEW_REQUIRED,
                reason=evidence_result.reason or "no_evidence",
                model=configured_model,
                citations=[],
                evidence=evidence_result.hits,
                store_path=evidence_result.store_path,
                loaded_chunks=evidence_result.loaded_chunks,
            )

        client = llm_client or OpenAILLMClient()
        try:
            llm_result = client.complete_grounded_answer(
                query=query,
                evidence=evidence_result.hits,
            )
        except (OpenAIError, RuntimeError) as exc:
            return GroundedAnswerResponse(
                status=OFFICIAL_REVIEW_REQUIRED,
                reason=str(exc) or "llm_provider_error",
                model=configured_model,
                citations=_citations_from_hits(evidence_result.hits),
                evidence=evidence_result.hits,
                store_path=evidence_result.store_path,
                loaded_chunks=evidence_result.loaded_chunks,
            )

        return GroundedAnswerResponse(
            status="ok",
            reason=None,
            answer=llm_result.text,
            model=llm_result.model,
            citations=_citations_from_hits(evidence_result.hits),
            evidence=evidence_result.hits,
            store_path=evidence_result.store_path,
            loaded_chunks=evidence_result.loaded_chunks,
        )
