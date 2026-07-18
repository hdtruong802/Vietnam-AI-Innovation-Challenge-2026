"""RAG/LLM/Guardrail adapters implement cac Protocol trong app/ports.py.

Day la lop "adapter" trong kien truc hexagonal cua backend (xem
app/dependencies.py va app/adapters/dev_fixture.py): logic RAG/LLM thuc
nam trong app/services/{rag,llm,guardrail}/*, adapter o day chi chuyen
doi sang contract ma CopilotService/AppContainer da dinh nghia san.

Bat/tat qua Settings: procedure_data_mode=rag, rag_mode=rag,
llm_mode=gateway (xem D-011 trong docs/ai/DECISIONS.md).
"""

from __future__ import annotations

from typing import Any, Sequence

from app.config import get_settings
from app.catalog import CANONICAL_PROCEDURES
from app.models.common import SessionContext
from app.models.procedure import ProcedureCandidate, ProcedurePack, ProcedureSummary
from app.models.validation import Finding
from app.ports import RetrievalEvidence, RetrievalQuery
from app.services.guardrail.pii_guard import PIIGuard
from app.services.llm.gateway import LLMGateway
from app.services.rag.pack_builder import (
    build_birth_registration_pack,
    build_procedure_pack_from_evidence,
)
from app.services.rag.retrieval import RetrievalService
from app.services.rag.schemas import RetrievalQuery as RagRetrievalQuery
from app.services.rag.source_store import PROCEDURE_DISPLAY_NAME

_GENERIC_FORM_SCHEMA = {
    "type": "object",
    "properties": {
        "ho_ten_nguoi_khai": {
            "type": "string",
            "title": "Họ và tên người khai",
            "minLength": 2,
        },
        "so_dien_thoai": {"type": "string", "title": "Số điện thoại"},
    },
    "required": ["ho_ten_nguoi_khai"],
}

_PACK_ALIASES: dict[str, list[str]] = {
    "dang-ky-thuong-tru": ["thuong tru", "ho khau", "residence", "chuyen ho khau"],
    "dang-ky-ho-kinh-doanh": [
        "ho kinh doanh",
        "mo cua hang",
        "business",
        "thanh lap ho kinh doanh",
    ],
}


def _build_pack(procedure_id: str) -> ProcedurePack | None:
    if procedure_id == "dang-ky-khai-sinh":
        return build_birth_registration_pack()
    return build_procedure_pack_from_evidence(
        procedure_id,
        aliases=_PACK_ALIASES.get(procedure_id, []),
        form_schema=_GENERIC_FORM_SCHEMA,
    )


class RagProcedureRepository:
    """ProcedureRepository backed boi RAG source (data/Data_DVC).

    Cache trong instance vi pack duoc build tu source tinh (freeze date);
    khong rebuild moi request. Neu source cho mot procedure MVP chua nap
    duoc (thieu file allowlist), pack tuong ung la None -> Trust Policy se
    tra `official_review_required` cho dung procedure do, khong fail toan
    bo repository.
    """

    def __init__(self) -> None:
        self._packs: dict[str, ProcedurePack] | None = None

    def _all_packs(self) -> dict[str, ProcedurePack]:
        if self._packs is None:
            self._packs = {}
            for summary in CANONICAL_PROCEDURES:
                pack = _build_pack(summary.procedure_id)
                if pack is not None:
                    self._packs[summary.procedure_id] = pack
        return self._packs

    async def list_procedures(self) -> list[ProcedureSummary]:
        packs = self._all_packs()
        summaries: list[ProcedureSummary] = []
        for canonical in CANONICAL_PROCEDURES:
            pack = packs.get(canonical.procedure_id)
            if pack is None:
                summaries.append(canonical)
                continue
            summaries.append(
                ProcedureSummary(
                    procedure_id=pack.procedure_id,
                    name=pack.name,
                    version=pack.version,
                    review_status=pack.review_status,
                )
            )
        return summaries

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None:
        return self._all_packs().get(procedure_id)


class RagRecommendationProvider:
    """RecommendationProvider dung lexical retrieval tren evidence RAG."""

    async def recommend(
        self, need_text: str, session_context: SessionContext
    ) -> list[ProcedureCandidate]:
        candidates = RetrievalService.recommend_procedure(need_text, top_k=1)
        if not candidates:
            return []
        top = candidates[0]
        if top.score < get_settings().rag_min_confidence:
            return []
        return [
            ProcedureCandidate(
                procedure_id=top.procedure_id,
                name=PROCEDURE_DISPLAY_NAME.get(top.procedure_id, top.procedure_name),
                reason=f"Khớp nội dung nguồn thủ tục với độ tin cậy {top.score:.2f}.",
            )
        ]


class RagRetrievalProvider:
    """RetrievalProvider dung lexical similarity tren cac chunk da allowlist."""

    async def retrieve(self, query: RetrievalQuery) -> RetrievalEvidence:
        evidence = RetrievalService.retrieve(
            RagRetrievalQuery(text=query.query, procedure_id=query.procedure_id)
        )
        if not evidence.is_grounded:
            return RetrievalEvidence(
                available=False,
                reason="Không tìm thấy evidence đủ tin cậy trong nguồn thủ tục đã duyệt.",
            )
        references = tuple(
            citation.get("ref_code") or citation.get("title", "")
            for citation in evidence.citations
            if citation.get("ref_code") or citation.get("title")
        )
        return RetrievalEvidence(available=True, references=references)


class GatewayLLMProvider:
    """LLMProvider provider-neutral (OpenAI-compatible) voi PII Guard truoc khi goi model.

    `explain_findings` chi diễn giải finding đã có (message do RuleEngine
    quyết định), KHÔNG tạo/đổi finding hay verdict — đúng nguyên tắc trong
    docs/proposal.md muc 5/6. Khi thiếu `AI_API_KEY` hoặc model lỗi,
    LLMGateway tự fallback deterministic nên hàm này luôn trả về giá trị
    an toàn (đồng nghĩa fail-closed cho phần diễn giải, không ảnh hưởng
    verdict/findings gốc).
    """

    async def is_available(self) -> bool:
        return LLMGateway.is_online()

    async def explain_findings(
        self, session_id: str, form_data: dict[str, Any], findings: Sequence[Finding]
    ) -> dict[str, str]:
        if not findings:
            return {}

        tokenized, _ = PIIGuard.tokenize_fields(session_id, form_data)
        explanations: dict[str, str] = {}
        try:
            for finding in findings:
                field_id = finding.field_id or "thông tin đã nộp"
                token_value = tokenized.get(finding.field_id) if finding.field_id else None
                tokenized_context = (
                    f"{finding.field_id}={token_value}" if token_value is not None else ""
                )
                result = LLMGateway.explain_finding(
                    field_label=field_id,
                    rule_message=finding.message,
                    tokenized_context=tokenized_context,
                )
                explanations[finding.rule_id] = result.friendly_message
        finally:
            PIIGuard.clear_session(session_id)

        return explanations
