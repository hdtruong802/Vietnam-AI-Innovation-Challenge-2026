from __future__ import annotations

import re
import unicodedata
from datetime import date

from app.catalog import CANONICAL_PROCEDURES
from app.models.common import Citation, ClarifyingQuestion, FindingSeverity, SessionContext
from app.models.procedure import (
    ChecklistItem,
    ProcedureCandidate,
    ProcedurePack,
    ProcedureStep,
    ProcedureSummary,
    ReviewStatus,
    ValidationRule,
    ValidationRuleType,
)
from app.ports import RetrievalEvidence, RetrievalQuery

FIXTURE_SOURCE = Citation(
    ref_id="fixture-not-legal",
    title="Dữ liệu thử nghiệm nội bộ — không phải hướng dẫn thủ tục",
    url_or_ref="fixture://backend-api-foundation",
)


def _fixture_pack(
    procedure_id: str,
    name: str,
    aliases: list[str],
    field_id: str,
    field_label: str,
) -> ProcedurePack:
    return ProcedurePack(
        procedure_id=procedure_id,
        name=name,
        jurisdiction="Mô phỏng phát triển",
        authority="Không áp dụng cho thủ tục thật",
        version="fixture-20260718",
        review_status=ReviewStatus.FIXTURE,
        last_verified_at=date(2026, 7, 18),
        checksum="fixture-only",
        source_refs=[FIXTURE_SOURCE],
        aliases=aliases,
        intake_questions=[
            ClarifyingQuestion(
                id="fixture-confirm-scenario",
                prompt="Bạn xác nhận đang chạy luồng thử nghiệm của backend chứ?",
                options=["Xác nhận", "Chọn thủ tục khác"],
                why="Dữ liệu hiện tại chỉ phục vụ kiểm thử tích hợp.",
            )
        ],
        required_documents=[
            ChecklistItem(
                id="fixture-required-item",
                label="Mục checklist minh họa",
                kind="required",
                description="Chỉ dùng để kiểm thử UI/API; không phải yêu cầu hồ sơ thật.",
                source_ref_ids=[FIXTURE_SOURCE.ref_id],
            )
        ],
        optional_documents=[],
        steps=[
            ProcedureStep(
                order=1,
                title="Chạy thử luồng API",
                detail="Kết nối adapter dữ liệu đã review trước khi dùng cho hướng dẫn thực tế.",
            )
        ],
        form_schema={
            "type": "object",
            "properties": {
                field_id: {"type": "string", "title": field_label, "minLength": 2},
            },
            "required": [field_id],
        },
        validation_rules=[
            ValidationRule(
                rule_id=f"FIXTURE-{procedure_id}-001",
                type=ValidationRuleType.REQUIRED,
                field_id=field_id,
                severity=FindingSeverity.ERROR,
                message=f"{field_label} là bắt buộc trong dữ liệu thử nghiệm.",
                fix_hint="Nhập ít nhất một giá trị mô phỏng để tiếp tục kiểm thử.",
                source_ref_ids=[FIXTURE_SOURCE.ref_id],
            ),
            ValidationRule(
                rule_id=f"FIXTURE-{procedure_id}-002",
                type=ValidationRuleType.STRING_PATTERN,
                field_id=field_id,
                severity=FindingSeverity.WARNING,
                message=f"{field_label} nên chỉ gồm chữ cái và khoảng trắng trong fixture.",
                fix_hint="Dùng chuỗi mô phỏng gồm chữ cái và khoảng trắng.",
                params={"pattern": r"^[A-Za-zÀ-ỹà-ỹ ]+$"},
                source_ref_ids=[FIXTURE_SOURCE.ref_id],
            ),
        ],
    )


FIXTURE_PACKS: dict[str, ProcedurePack] = {
    "dang-ky-khai-sinh": _fixture_pack(
        "dang-ky-khai-sinh",
        "Đăng ký khai sinh",
        ["khai sinh", "sinh con", "birth"],
        "fixture_child_name",
        "Tên trẻ (minh họa)",
    ),
    "dang-ky-thuong-tru": _fixture_pack(
        "dang-ky-thuong-tru",
        "Đăng ký thường trú",
        ["thuong tru", "ho khau", "residence"],
        "fixture_resident_name",
        "Tên người đăng ký (minh họa)",
    ),
    "dang-ky-ho-kinh-doanh": _fixture_pack(
        "dang-ky-ho-kinh-doanh",
        "Đăng ký thành lập hộ kinh doanh",
        ["ho kinh doanh", "mo cua hang", "business"],
        "fixture_business_name",
        "Tên hộ kinh doanh (minh họa)",
    ),
}


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", without_marks.replace("đ", "d")).strip()


class FixtureProcedureRepository:
    async def list_procedures(self) -> list[ProcedureSummary]:
        return [
            ProcedureSummary(
                procedure_id=pack.procedure_id,
                name=pack.name,
                version=pack.version,
                review_status=pack.review_status,
                fixture_mode=True,
            )
            for pack in FIXTURE_PACKS.values()
        ]

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None:
        return FIXTURE_PACKS.get(procedure_id)


class DisabledProcedureRepository:
    async def list_procedures(self) -> list[ProcedureSummary]:
        return list(CANONICAL_PROCEDURES)

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None:
        return None


class FixtureRecommendationProvider:
    async def recommend(
        self, need_text: str, session_context: SessionContext
    ) -> list[ProcedureCandidate]:
        normalized_need = normalize_text(need_text)
        for pack in FIXTURE_PACKS.values():
            if any(normalize_text(alias) in normalized_need for alias in pack.aliases):
                return [
                    ProcedureCandidate(
                        procedure_id=pack.procedure_id,
                        name=pack.name,
                        reason="Khớp từ khóa trong adapter dữ liệu thử nghiệm.",
                    )
                ]
        return []


class DisabledRecommendationProvider:
    async def recommend(
        self, need_text: str, session_context: SessionContext
    ) -> list[ProcedureCandidate]:
        return []


class DisabledRetrievalProvider:
    async def retrieve(self, query: RetrievalQuery) -> RetrievalEvidence:
        return RetrievalEvidence(available=False, reason="Retrieval adapter chưa được cấu hình.")


class InMemoryAuditSink:
    """Receives metadata only; it intentionally does not persist request payloads."""

    async def emit(self, event: str, fields: dict[str, str | int | float | bool | None]) -> None:
        _ = (event, fields)


class DisabledLLMProvider:
    async def is_available(self) -> bool:
        return False
