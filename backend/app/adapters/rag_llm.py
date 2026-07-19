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
from app.services.rag.source_store import PROCEDURE_DISPLAY_NAME, normalize_name

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

# Field xap xi theo ten mau chinh thuc duoc dan trong nguon RAG (xem D-019):
# - thuong tru: "Tờ khai thay đổi thông tin cư trú (mẫu CT01, TT 53/2025/TT-BCA)"
#   (data/Data_DVC/1.004222.txt).
# - ho kinh doanh: "Giấy đề nghị đăng ký hộ kinh doanh" (data/Data_DVC/1.001612.txt).
# Noi dung mau CT01/Giay de nghi day du KHONG nam trong data/Data_DVC hien co
# (chi co ten/so hieu mau) nen field list la uoc luong theo cau truc mau pho
# bien, CHUA duoc procedure-research lane xac minh tung field/label voi ban
# mau chinh thuc. Pack van o `needs_review` (xem pack_builder._demo_k1_status)
# nen KHONG duoc coi la form da approved cho production.
_RESIDENCE_FORM_SCHEMA = {
    "type": "object",
    "properties": {
        "ho_ten_nguoi_de_nghi": {
            "type": "string",
            "title": "Họ và tên người đề nghị",
            "minLength": 2,
        },
        "so_dinh_danh_ca_nhan": {
            "type": "string",
            "title": "Số định danh cá nhân/CCCD",
            "pattern": r"^[0-9]{12}$",
        },
        "ngay_sinh": {
            "type": "string",
            "title": "Ngày, tháng, năm sinh",
            "format": "date",
        },
        "dia_chi_de_nghi_thuong_tru": {
            "type": "string",
            "title": "Địa chỉ nơi đề nghị đăng ký thường trú",
            "minLength": 5,
        },
        "ho_ten_chu_ho": {
            "type": "string",
            "title": "Họ và tên chủ hộ (nơi đến)",
        },
        "quan_he_voi_chu_ho": {
            "type": "string",
            "title": "Quan hệ với chủ hộ",
        },
        "so_dien_thoai": {"type": "string", "title": "Số điện thoại liên hệ"},
    },
    "required": [
        "ho_ten_nguoi_de_nghi",
        "so_dinh_danh_ca_nhan",
        "dia_chi_de_nghi_thuong_tru",
        "ho_ten_chu_ho",
        "quan_he_voi_chu_ho",
    ],
}

_BUSINESS_HOUSEHOLD_FORM_SCHEMA = {
    "type": "object",
    "properties": {
        "ten_ho_kinh_doanh": {
            "type": "string",
            "title": "Tên hộ kinh doanh",
            "minLength": 2,
        },
        "dia_chi_dia_diem_kinh_doanh": {
            "type": "string",
            "title": "Địa chỉ địa điểm kinh doanh",
            "minLength": 5,
        },
        "nganh_nghe_kinh_doanh": {
            "type": "string",
            "title": "Ngành, nghề kinh doanh",
        },
        "ho_ten_chu_ho_kinh_doanh": {
            "type": "string",
            "title": "Họ và tên chủ hộ kinh doanh",
            "minLength": 2,
        },
        "so_cccd_chu_ho_kinh_doanh": {
            "type": "string",
            "title": "Số CCCD/CMND của chủ hộ kinh doanh",
            "pattern": r"^([0-9]{9}|[0-9]{12})$",
        },
        "von_kinh_doanh": {"type": "string", "title": "Số vốn kinh doanh (VNĐ)"},
    },
    "required": [
        "ten_ho_kinh_doanh",
        "dia_chi_dia_diem_kinh_doanh",
        "nganh_nghe_kinh_doanh",
        "ho_ten_chu_ho_kinh_doanh",
        "so_cccd_chu_ho_kinh_doanh",
    ],
}

_PACK_FORM_SCHEMAS: dict[str, dict] = {
    "dang-ky-thuong-tru": _RESIDENCE_FORM_SCHEMA,
    "dang-ky-ho-kinh-doanh": _BUSINESS_HOUSEHOLD_FORM_SCHEMA,
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

_OUT_OF_SCOPE_INTENTS = (
    "dang ky ket hon",
    "khai tu",
    "dang ky khai tu",
    "ho chieu",
    "tam tru",
    "cong ty co phan",
    "cong ty trach nhiem huu han",
)

_PROCEDURE_INTENTS: dict[str, tuple[str, ...]] = {
    "dang-ky-khai-sinh": ("khai sinh", "giay khai sinh", "dang ky sinh"),
    "dang-ky-thuong-tru": ("thuong tru", "ho khau", "chuyen ho khau"),
    "dang-ky-ho-kinh-doanh": (
        "ho kinh doanh",
        "thanh lap ho kinh doanh",
        "mo cua hang",
        "kinh doanh ca the",
    ),
}


def _detect_procedure_intent(need_text: str) -> str | None:
    normalized = normalize_name(need_text)
    if any(phrase in normalized for phrase in _OUT_OF_SCOPE_INTENTS):
        return None

    matches = {
        procedure_id
        for procedure_id, phrases in _PROCEDURE_INTENTS.items()
        if any(phrase in normalized for phrase in phrases)
    }
    return next(iter(matches)) if len(matches) == 1 else None


def _build_pack(procedure_id: str) -> ProcedurePack | None:
    if procedure_id == "dang-ky-khai-sinh":
        return build_birth_registration_pack()
    return build_procedure_pack_from_evidence(
        procedure_id,
        aliases=_PACK_ALIASES.get(procedure_id, []),
        form_schema=_PACK_FORM_SCHEMAS.get(procedure_id, _GENERIC_FORM_SCHEMA),
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
        intended_procedure_id = _detect_procedure_intent(need_text)
        if intended_procedure_id is None:
            return []

        candidates = RetrievalService.recommend_procedure(need_text, top_k=3)
        if not candidates:
            return []
        top = next(
            (
                candidate
                for candidate in candidates
                if candidate.procedure_id == intended_procedure_id
            ),
            None,
        )
        if top is None:
            return []
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
                reason="Không tìm thấy evidence đủ tin cậy trong nguồn thủ tục candidate.",
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
                # Model duoc yeu cau giu nguyen token {{PII_...}} (khong tu bien
                # thanh gia tri thuc) de tranh lo PII truc tiep sang provider LLM
                # ben ngoai; phai detokenize truoc khi tra ve cho citizen, neu
                # khong placeholder tho se bi lo ra ngoai (xem D-006/D-011).
                explanations[finding.rule_id] = PIIGuard.detokenize_text(
                    session_id, result.friendly_message
                )
        finally:
            PIIGuard.clear_session(session_id)

        return explanations
