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
    ("eligibility", "Yêu cầu, điều kiện thực hiện"),
    ("beneficiaries", "Đối tượng thực hiện"),
    ("result", "Kết quả thực hiện"),
    ("description", "Mô tả"),
]

# "Thành phần hồ sơ" va "Cách thức thực hiện" (phí/thời hạn) KHONG con trong
# _SECTIONS: source that la cac block lap lai nhieu dong (tuong duong 1 bang),
# neu chunk chung thanh 1 doan text se mat "xuong song" cua thu tuc (thieu
# phi/thoi han/dieu kien rieng tung dong) khien LLM de doan/bia khi evidence
# thieu. Build rieng tung row -> EvidenceChunk + citation rieng, xem
# build_chunks() ben duoi va docs/ai/DECISIONS.md.
_ORG_FIELDS = [
    ("implementing_org", "Cơ quan thực hiện"),
    ("authority_org", "Cơ quan có thẩm quyền"),
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

        for org_field, org_label in _ORG_FIELDS:
            text = getattr(record, org_field, "").strip()
            if not text or text == "Không có thông tin":
                continue
            chunk_id = f"{procedure_id}:{record.procedure_code or record.file_name}:{org_field}"
            chunks.append(
                EvidenceChunk(
                    chunk_id=chunk_id,
                    procedure_id=procedure_id,
                    procedure_name=procedure_name,
                    section=org_label,
                    text=f"{org_label} của thủ tục {record.name}: {text}.",
                    source_title=f"{record.name} — {source_title}",
                    source_ref=source_ref,
                    source_url=source_url,
                    last_verified_at=None,
                )
            )

        # Moi hinh thuc nop (online/direct/postal) co phi + thoi han rieng —
        # tach 1 EvidenceChunk/row de khong lam mat thong tin phi/thoi han
        # (truoc day 2 field nay bi bo hoan toan, khong vao RAG chunk nao).
        for idx, method_row in enumerate(record.submission_method_rows, start=1):
            parts = [f"Hình thức nộp: {method_row.method}."]
            if method_row.processing_time:
                parts.append(f"Thời hạn giải quyết: {method_row.processing_time}.")
            if method_row.fee:
                parts.append(f"Phí, lệ phí: {method_row.fee}.")
            if method_row.description:
                parts.append(method_row.description)
            chunk_id = (
                f"{procedure_id}:{record.procedure_code or record.file_name}:"
                f"submission_method:{idx}"
            )
            chunks.append(
                EvidenceChunk(
                    chunk_id=chunk_id,
                    procedure_id=procedure_id,
                    procedure_name=procedure_name,
                    section="Cách thức thực hiện",
                    text=" ".join(parts),
                    source_title=f"{record.name} — {source_title}",
                    source_ref=source_ref,
                    source_url=source_url,
                    last_verified_at=None,
                )
            )

        # Moi giay to trong "Thanh phan ho so" la 1 row rieng (co the thuoc
        # 1 nhom dieu kien `[ ... ]`) — tach citation/row-level thay vi
        # gop chung 1 doan text lam mat cau truc dieu kien ap dung.
        for idx, doc_row in enumerate(record.document_rows, start=1):
            text = doc_row.name
            if doc_row.original_copies or doc_row.duplicate_copies:
                text = (
                    f"{text} (Bản chính: {doc_row.original_copies or '0'}, "
                    f"Bản sao: {doc_row.duplicate_copies or '0'})"
                )
            if doc_row.group:
                text = f"[Áp dụng khi: {doc_row.group}] {text}"
            chunk_id = f"{procedure_id}:{record.procedure_code or record.file_name}:document:{idx}"
            chunks.append(
                EvidenceChunk(
                    chunk_id=chunk_id,
                    procedure_id=procedure_id,
                    procedure_name=procedure_name,
                    section="Thành phần hồ sơ",
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
