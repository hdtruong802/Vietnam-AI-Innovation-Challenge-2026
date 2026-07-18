"""Deterministic transform tu RAG evidence sang cau truc checklist/step.

Day KHONG phai LLM sinh noi dung: chi la parser deterministic tren van ban
da duoc allowlist trong source_store (tuong duong buoc 'Chuan hoa / chunk'
trong RAG lifecycle). Dung cho cac pack chua duoc author cu the (thuong
tru, ho kinh doanh); pack da co checklist tu tay (khai sinh) van giu
nguyen structured data curated, chi lam giau them citations tu RAG.
"""

from __future__ import annotations

import re
from typing import List, Optional

from app.models.checklist import ChecklistItem, ChecklistResponse, Step
from app.models.common import Citation
from app.services.rag.retrieval import RetrievalService
from app.services.rag.source_store import (
    PROCEDURE_DISPLAY_NAME,
    SourceRecord,
    get_source_freeze_date,
    load_approved_records,
)

_CONDITIONAL_MARKERS = ("trường hợp", "nếu có", "nếu ")


def _split_documents(raw_text: str) -> List[str]:
    items: List[str] = []
    buffer: List[str] = []
    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if buffer:
                items.append(" ".join(buffer))
            buffer = [stripped[2:].strip()]
        elif stripped.startswith("["):
            continue
        elif buffer:
            buffer.append(stripped)
    if buffer:
        items.append(" ".join(buffer))
    return items


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


def _extract_field(raw_text: str, label: str, default: str) -> str:
    match = re.search(rf"{label}:\s*([^\n]+)", raw_text)
    return match.group(1).strip() if match else default


def _primary_citation(record: SourceRecord) -> Citation:
    if record.legal_basis:
        entry = record.legal_basis[0]
        return Citation(title=entry["title"], url="https://dichvucong.gov.vn", ref_code=entry["ref_code"])
    return Citation(
        title=record.name,
        url="https://dichvucong.gov.vn",
        ref_code=record.procedure_code or record.decision_no or "N/A",
    )


def build_checklist_from_evidence(
    procedure_id: str,
    form_schema: dict,
) -> Optional[ChecklistResponse]:
    records_by_procedure = load_approved_records()
    records = records_by_procedure.get(procedure_id) or []
    if not records:
        return None

    record = records[0]
    citation = _primary_citation(record)

    required_documents: List[ChecklistItem] = []
    optional_documents: List[ChecklistItem] = []
    for idx, line in enumerate(_split_documents(record.documents), start=1):
        item = ChecklistItem(
            id=f"{procedure_id}-doc-{idx}",
            title=_title_from_document_line(line),
            required=not _is_conditional(line),
            description=line[:500],
            citations=[citation],
        )
        (optional_documents if _is_conditional(line) else required_documents).append(item)

    if not required_documents:
        required_documents = [
            ChecklistItem(
                id=f"{procedure_id}-doc-0",
                title="Tờ khai theo mẫu quy định",
                required=True,
                description="Điền đầy đủ thông tin vào biểu mẫu do nhà nước ban hành.",
                citations=[citation],
            )
        ]

    processing_time = _extract_field(record.submission_methods, "Thời hạn giải quyết", "Theo quy định")
    fees = _extract_field(record.submission_methods, "Phí, lệ phí", "Theo quy định")

    step_texts = _split_steps(record.steps)
    steps = [
        Step(
            step_number=idx,
            title=f"Bước {idx}",
            description=text[:600],
            processing_time=processing_time,
            fees=fees,
        )
        for idx, text in enumerate(step_texts, start=1)
    ] or [
        Step(
            step_number=1,
            title="Nộp hồ sơ",
            description="Nộp hồ sơ theo quy định tại cơ quan có thẩm quyền.",
            processing_time=processing_time,
            fees=fees,
        )
    ]

    rag_citations = RetrievalService.get_citations_for_procedure(procedure_id)
    sources = [Citation(**c) for c in rag_citations] if rag_citations else [citation]

    return ChecklistResponse(
        procedure_id=procedure_id,
        procedure_name=PROCEDURE_DISPLAY_NAME.get(procedure_id, record.name),
        required_documents=required_documents,
        optional_documents=optional_documents,
        steps=steps,
        form_schema=form_schema,
        effective_date=get_source_freeze_date(),
        sources=sources,
    )
