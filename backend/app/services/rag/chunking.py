"""Chuan hoa / chunk / metadata cho RAG lifecycle (xem docs/proposal.md muc 5)."""

from __future__ import annotations

from typing import List

from app.services.rag.schemas import EvidenceChunk
from app.services.rag.source_store import (
    PROCEDURE_DISPLAY_NAME,
    SourceRecord,
)

_SECTIONS = [
    ("steps", "Trình tự thực hiện"),
    ("documents", "Thành phần hồ sơ"),
    ("eligibility", "Yêu cầu, điều kiện thực hiện"),
    ("beneficiaries", "Đối tượng thực hiện"),
    ("result", "Kết quả thực hiện"),
    ("description", "Mô tả"),
]


def _primary_citation(record: SourceRecord) -> tuple[str, str]:
    if record.legal_basis:
        entry = record.legal_basis[0]
        return entry["title"], entry["ref_code"]
    if record.decision_no:
        return f"Quyết định công bố thủ tục {record.decision_no}", record.decision_no
    return "Cổng Dịch vụ công Quốc gia", record.procedure_code or record.file_name


def build_chunks(procedure_id: str, records: List[SourceRecord]) -> List[EvidenceChunk]:
    chunks: List[EvidenceChunk] = []
    procedure_name = PROCEDURE_DISPLAY_NAME.get(procedure_id, procedure_id)

    for record in records:
        source_title, source_ref = _primary_citation(record)
        source_url = "https://dichvucong.gov.vn"

        for section_key, section_label in _SECTIONS:
            text = getattr(record, section_key, "").strip()
            if not text or text == "Không có thông tin":
                continue
            chunk_id = f"{procedure_id}:{record.procedure_code or record.file_name}:{section_key}"
            chunks.append(
                EvidenceChunk(
                    chunk_id=chunk_id,
                    procedure_id=procedure_id,
                    procedure_name=procedure_name,
                    section=section_label,
                    text=text,
                    source_title=f"{record.name} — {source_title}",
                    source_ref=source_ref,
                    source_url=source_url,
                    last_verified_at=None,
                )
            )

        # Rieng cac muc phap ly duoc tach tung dieu luat de citation cu the hon.
        for entry in record.legal_basis:
            chunk_id = f"{procedure_id}:{record.procedure_code or record.file_name}:legal:{entry['ref_code']}"
            chunks.append(
                EvidenceChunk(
                    chunk_id=chunk_id,
                    procedure_id=procedure_id,
                    procedure_name=procedure_name,
                    section="Căn cứ pháp lý",
                    text=f"{record.name} áp dụng căn cứ pháp lý: {entry['title']}",
                    source_title=entry["title"],
                    source_ref=entry["ref_code"],
                    source_url=source_url,
                    last_verified_at=None,
                )
            )

    return chunks
