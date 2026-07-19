"""Deterministic transform tu RAG evidence sang app.models.procedure.ProcedurePack.

Day KHONG phai LLM sinh noi dung: chi la parser deterministic tren van ban
da duoc allowlist trong source_store (tuong duong buoc 'Chuan hoa / chunk'
trong RAG lifecycle). Dung cho cac pack chua duoc author cu the (thuong
tru, ho kinh doanh); pack da co checklist curate tay (khai sinh) van giu
noi dung curated, chi lam giau them source_refs tu RAG.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date
from typing import List, Optional

from app.config import get_settings
from app.models.common import Citation, ClarifyingQuestion, FindingSeverity
from app.models.procedure import (
    ChecklistItem,
    ProcedurePack,
    ProcedureStep,
    ReviewStatus,
    ValidationRule,
    ValidationRuleType,
)
from app.services.rag.retrieval import RetrievalService
from app.services.rag.source_store import (
    PROCEDURE_DISPLAY_NAME,
    SourceRecord,
    get_source_freeze_date,
    load_candidate_records,
)

_CONDITIONAL_MARKERS = ("trường hợp", "nếu có", "nếu ")


def _document_description(row) -> str:
    text = row.name
    if row.original_copies or row.duplicate_copies:
        text = (
            f"{text} (Bản chính: {row.original_copies or '0'}, "
            f"Bản sao: {row.duplicate_copies or '0'})"
        )
    if row.group:
        text = f"Áp dụng khi: {row.group}. {text}"
    return text


def _title_from_document_line(line: str) -> str:
    for sep in (":", ";"):
        if sep in line:
            candidate = line.split(sep, 1)[0].strip(" -.")
            if candidate:
                return candidate[:120]
    return line[:100].strip()


def _is_conditional(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in _CONDITIONAL_MARKERS)


def _split_steps(raw_text: str) -> List[str]:
    matches = re.split(r"(?:^|\n)\s*\*?\s*[Bb]ước\s*\d+[:.]?\s*", raw_text)
    steps = [s.strip() for s in matches if s.strip()]
    if steps:
        return steps
    bullets = [b.strip() for b in re.split(r"\n\s*\*\s*", raw_text) if b.strip()]
    if bullets:
        return bullets
    return [raw_text.strip()] if raw_text.strip() else []


def _record_checksum(record: SourceRecord) -> str:
    payload = "|".join(
        [
            record.file_name,
            record.name,
            record.documents,
            record.steps,
            record.legal_basis_raw,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _primary_citation(record: SourceRecord) -> Citation:
    if record.legal_basis:
        entry = record.legal_basis[0]
        ref_id = (entry.get("ref_code") or entry["title"])[:120]
        return Citation(
            ref_id=ref_id,
            title=entry["title"][:240],
            url_or_ref="https://dichvucong.gov.vn",
        )
    ref_id = (record.procedure_code or record.decision_no or record.file_name)[:120]
    return Citation(ref_id=ref_id, title=record.name[:240], url_or_ref="https://dichvucong.gov.vn")


def _demo_k1_status(
    default_version: str, demo_version: str
) -> tuple[ReviewStatus, date | None, str]:
    """Xem D-013/D-019: mac dinh (`rag_demo_k1_approved=False`) giu dung fail-
    closed cua D-013 - tra ve `needs_review`/khong co `last_verified_at`.
    CHI khi flag demo duoc bat tuong minh (chi danh cho demo cuc bo, KHONG
    duoc bat tren production) moi tra ve `approved` + ngay freeze, va version
    doi thanh `demo-k1-simulated-...` de khong the nham voi K1 nguoi thuc."""

    if not get_settings().rag_demo_k1_approved:
        return ReviewStatus.NEEDS_REVIEW, None, default_version
    return ReviewStatus.APPROVED, date.fromisoformat(get_source_freeze_date()), demo_version


def _required_field_rules(
    procedure_id: str, form_schema: dict, citation_ref_id: str
) -> List[ValidationRule]:
    """Sinh validation rules deterministic tu JSON Schema cua form:
    REQUIRED cho field trong `required` (giu nguyen thu tu/rule_id `REQ-N`
    de tuong thich voi rule_id da dung trong test), STRING_PATTERN neu field
    co `pattern`, DATE_FORMAT neu field co `format: date` (xem D-019: form
    schema cu the hon cho thuong tru/ho kinh doanh can validate dinh dang,
    khong chi kiem truong bat buoc)."""

    properties = form_schema.get("properties", {})
    required_field_ids = list(form_schema.get("required", []))
    rules: List[ValidationRule] = []
    for idx, field_id in enumerate(required_field_ids, start=1):
        label = properties.get(field_id, {}).get("title", field_id)
        rules.append(
            ValidationRule(
                rule_id=f"{procedure_id.upper()}-REQ-{idx}",
                type=ValidationRuleType.REQUIRED,
                field_id=field_id,
                severity=FindingSeverity.ERROR,
                message=f"{label} là bắt buộc và không được để trống.",
                fix_hint="Vui lòng nhập đầy đủ thông tin cho trường này.",
                source_ref_ids=[citation_ref_id],
            )
        )
    for idx, (field_id, field_def) in enumerate(properties.items(), start=1):
        label = field_def.get("title", field_id)
        pattern = field_def.get("pattern")
        if pattern:
            rules.append(
                ValidationRule(
                    rule_id=f"{procedure_id.upper()}-FORMAT-{idx}",
                    type=ValidationRuleType.STRING_PATTERN,
                    field_id=field_id,
                    severity=FindingSeverity.ERROR,
                    message=f"{label} chưa đúng định dạng quy định.",
                    fix_hint="Kiểm tra lại định dạng của trường này (ví dụ đủ số chữ số).",
                    params={"pattern": pattern},
                    source_ref_ids=[citation_ref_id],
                )
            )
        if field_def.get("format") == "date":
            rules.append(
                ValidationRule(
                    rule_id=f"{procedure_id.upper()}-DATE-{idx}",
                    type=ValidationRuleType.DATE_FORMAT,
                    field_id=field_id,
                    severity=FindingSeverity.ERROR,
                    message=f"{label} chưa đúng định dạng ngày (YYYY-MM-DD).",
                    fix_hint="Nhập ngày theo định dạng YYYY-MM-DD.",
                    source_ref_ids=[citation_ref_id],
                )
            )
    return rules


def build_procedure_pack_from_evidence(
    procedure_id: str,
    *,
    aliases: List[str],
    form_schema: dict,
    intake_questions: Optional[List[ClarifyingQuestion]] = None,
) -> Optional[ProcedurePack]:
    """Sinh ProcedurePack tu evidence RAG cho pack chua duoc curate tay.

    Tra ve None neu khong co source nao trong allowlist duoc nap (fail
    closed: Trust Policy se coi procedure nay la chua verified).
    """

    records_by_procedure = load_candidate_records()
    records = records_by_procedure.get(procedure_id) or []
    if not records:
        return None

    record = records[0]
    citation = _primary_citation(record)

    required_documents: List[ChecklistItem] = []
    optional_documents: List[ChecklistItem] = []
    for idx, doc_row in enumerate(record.document_rows, start=1):
        # Giay to thuoc 1 nhom dieu kien `[ Truong hop ... ]` trong nguon chi
        # ap dung cho tinh huong cu the do -> "conditional", giu nguyen dieu
        # kien trong `condition` de FE/LLM khong bia ra dieu kien khac.
        is_conditional = bool(doc_row.group) or _is_conditional(doc_row.name)
        description = _document_description(doc_row)
        item = ChecklistItem(
            id=f"{procedure_id}-doc-{idx}",
            label=_title_from_document_line(doc_row.name),
            kind="conditional" if is_conditional else "required",
            description=(description[:1000] or "Xem chi tiết trong hồ sơ nguồn."),
            source_ref_ids=[citation.ref_id],
            condition={"group": doc_row.group} if doc_row.group else None,
        )
        (optional_documents if is_conditional else required_documents).append(item)

    if not required_documents:
        required_documents = [
            ChecklistItem(
                id=f"{procedure_id}-doc-0",
                label="Tờ khai theo mẫu quy định",
                kind="required",
                description="Điền đầy đủ thông tin vào biểu mẫu do nhà nước ban hành.",
                source_ref_ids=[citation.ref_id],
            )
        ]

    step_texts = _split_steps(record.steps)
    steps = [
        ProcedureStep(order=idx, title=f"Bước {idx}", detail=text[:1000])
        for idx, text in enumerate(step_texts, start=1)
    ] or [
        ProcedureStep(
            order=1,
            title="Nộp hồ sơ",
            detail="Nộp hồ sơ theo quy định tại cơ quan có thẩm quyền.",
        )
    ]
    steps = steps[:30]

    source_refs = [citation]
    rag_citations = RetrievalService.get_citations_for_procedure(procedure_id)
    if rag_citations:
        source_refs = [
            Citation(
                ref_id=(entry.get("ref_code") or entry.get("title", "source"))[:120],
                title=(entry.get("title") or record.name)[:240],
                url_or_ref=entry.get("url") or "https://dichvucong.gov.vn",
            )
            for entry in rag_citations
        ]

    review_status, last_verified_at, version = _demo_k1_status(
        f"candidate-{get_source_freeze_date()}",
        f"demo-k1-simulated-{get_source_freeze_date()}",
    )

    return ProcedurePack(
        procedure_id=procedure_id,
        name=PROCEDURE_DISPLAY_NAME.get(procedure_id, record.name),
        jurisdiction="Theo phân cấp quy định tại nguồn thủ tục (xem source_refs).",
        authority=record.authority_org or record.implementing_org or None,
        version=version,
        review_status=review_status,
        last_verified_at=last_verified_at,
        checksum=_record_checksum(record),
        source_refs=source_refs,
        intake_questions=intake_questions or [],
        required_documents=required_documents,
        optional_documents=optional_documents,
        steps=steps,
        form_schema=form_schema,
        validation_rules=_required_field_rules(procedure_id, form_schema, citation.ref_id),
        aliases=aliases,
    )


_BIRTH_FORM_SCHEMA = {
    "type": "object",
    "properties": {
        "ho_ten_tre": {"type": "string", "title": "Họ và tên trẻ", "minLength": 2},
        "ngay_sinh_tre": {
            "type": "string",
            "title": "Ngày sinh của trẻ",
            "format": "date",
        },
        "ho_ten_cha": {"type": "string", "title": "Họ và tên cha"},
        "ho_ten_me": {"type": "string", "title": "Họ và tên mẹ"},
    },
    "required": ["ho_ten_tre", "ngay_sinh_tre", "ho_ten_me"],
}

_BIRTH_DEFAULT_CITATIONS = [
    Citation(
        ref_id="LUAT-HOTICH-2014",
        title="Luật Hộ tịch số 60/2014/QH13",
        url_or_ref="https://chinhphu.vn",
    ),
    Citation(
        ref_id="ND-123-2015",
        title="Nghị định 123/2015/NĐ-CP",
        url_or_ref="https://chinhphu.vn",
    ),
]


def build_birth_registration_pack() -> ProcedurePack:
    """Checklist da curate tay cho 'Đăng ký khai sinh' (structured procedure
    data). RAG chi lam giau them source_refs/freshness, khong tu doi noi
    dung da curated — dung cho pack co evidence pattern khac 3 loai file
    con lai trong data/Data_DVC.
    """

    rag_citations = RetrievalService.get_citations_for_procedure("dang-ky-khai-sinh")
    source_refs = (
        [
            Citation(
                ref_id=(entry.get("ref_code") or entry.get("title", "source"))[:120],
                title=(entry.get("title") or "Đăng ký khai sinh")[:240],
                url_or_ref=entry.get("url") or "https://dichvucong.gov.vn",
            )
            for entry in rag_citations
        ]
        if rag_citations
        else _BIRTH_DEFAULT_CITATIONS
    )
    primary_ref_id = source_refs[0].ref_id
    secondary_ref_id = source_refs[1].ref_id if len(source_refs) > 1 else primary_ref_id

    review_status, last_verified_at, version = _demo_k1_status(
        f"candidate-curated-{get_source_freeze_date()}",
        f"demo-k1-simulated-curated-{get_source_freeze_date()}",
    )

    return ProcedurePack(
        procedure_id="dang-ky-khai-sinh",
        name="Đăng ký khai sinh",
        jurisdiction="Cấp xã/phường/thị trấn",
        authority="Ủy ban nhân dân cấp xã",
        version=version,
        review_status=review_status,
        last_verified_at=last_verified_at,
        checksum="curated-birth-v1",
        source_refs=source_refs,
        intake_questions=[],
        required_documents=[
            ChecklistItem(
                id="giay-chung-sinh",
                label="Giấy chứng sinh",
                kind="required",
                description=(
                    "Bản chính do cơ sở y tế nơi trẻ sinh ra cấp. Nếu không có giấy "
                    "chứng sinh thì nộp văn bản xác nhận của người làm chứng."
                ),
                source_ref_ids=[secondary_ref_id],
            ),
            ChecklistItem(
                id="cccd-cha-me",
                label="Căn cước công dân của cha và mẹ",
                kind="required",
                description="Bản chụp xuất trình kèm bản chính để đối chiếu.",
                source_ref_ids=[primary_ref_id],
            ),
        ],
        optional_documents=[
            ChecklistItem(
                id="giay-dang-ky-ket-hon",
                label="Giấy chứng nhận kết hôn",
                kind="optional",
                description="Xuất trình nếu cha mẹ có đăng ký kết hôn để xác định quan hệ cha, mẹ, con.",
                source_ref_ids=[primary_ref_id],
            )
        ],
        steps=[
            ProcedureStep(
                order=1,
                title="Chuẩn bị và nộp hồ sơ",
                detail=(
                    "Người đi đăng ký chuẩn bị đầy đủ giấy tờ và nộp tại UBND cấp xã "
                    "nơi cư trú của cha hoặc mẹ. Giải quyết ngay trong ngày, miễn phí."
                ),
            )
        ],
        form_schema=_BIRTH_FORM_SCHEMA,
        validation_rules=_required_field_rules(
            "dang-ky-khai-sinh", _BIRTH_FORM_SCHEMA, primary_ref_id
        ),
        aliases=["khai sinh", "sinh con", "birth"],
    )
