from __future__ import annotations

from typing import Any

from app.models.checklist import ChecklistResponse
from app.models.common import Citation, ReviewGate, TrustState
from app.models.procedure import ChecklistItem, ProcedureStep
from app.services.rag_service import RAGService


PROCEDURES_DB = {
    "dang-ky-khai-sinh": {
        "id": "dang-ky-khai-sinh",
        "name": "Dang ky khai sinh",
        "jurisdiction": "Cap xa/phuong/thi tran",
        "authority": "Uy ban nhan dan cap xa",
        "effective_from": "2024-01-01",
        "effective_to": None,
        "last_verified_at": "2026-07-17",
        "trust_state": "verified_guidance",
    },
    "dang-ky-thuong-tru": {
        "id": "dang-ky-thuong-tru",
        "name": "Dang ky thuong tru",
        "jurisdiction": "Cap xa/phuong/thi tran",
        "authority": "Cong an cap xa",
        "effective_from": "2024-01-01",
        "effective_to": None,
        "last_verified_at": "2026-07-17",
        "trust_state": "verified_guidance",
    },
    "dang-ky-ho-kinh-doanh": {
        "id": "dang-ky-ho-kinh-doanh",
        "name": "Dang ky thanh lap ho kinh doanh",
        "jurisdiction": "Cap huyen/quan/thi xa",
        "authority": "Phong Tai chinh - Ke hoach cap huyen",
        "effective_from": "2024-01-01",
        "effective_to": None,
        "last_verified_at": "2026-07-17",
        "trust_state": "verified_guidance",
    },
}

from __future__ import annotations

def _rag_citations(procedure_id: str, top_k: int = 3) -> list[Citation]:
    evidence = RAGService.search_evidence(
        query=f"{PROCEDURES_DB[procedure_id]['name']} thanh phan ho so",
        procedure_id=procedure_id,
        top_k=top_k,
    )
    return [
        Citation(
            ref_id=hit.chunk_id,
            title=f"Clean RAG evidence {hit.source_id}",
            url_or_ref=hit.source_refs[0] if hit.source_refs else None,
        )
        for hit in evidence.hits
    ]


def _base_citations() -> list[Citation]:
    return [
        Citation(
            ref_id="LUAT-HOTICH-2014",
            title="Luat Ho tich so 60/2014/QH13",
            url_or_ref="https://chinhphu.vn",
        ),
        Citation(
            ref_id="ND-123-2015",
            title="Nghi dinh 123/2015/ND-CP",
            url_or_ref="https://chinhphu.vn",
        ),
    ]


class ProcedureService:
    @staticmethod
    def list_procedures() -> list[dict[str, Any]]:
        return list(PROCEDURES_DB.values())

    @staticmethod
    def get_procedure(procedure_id: str) -> dict[str, Any] | None:
        return PROCEDURES_DB.get(procedure_id)

    @staticmethod
    def get_checklist(procedure_id: str) -> ChecklistResponse:
        citations = _base_citations()
        sources = [*citations, *_rag_citations(procedure_id)]

        if procedure_id == "dang-ky-khai-sinh":
            required_documents = [
                ChecklistItem(
                    id="giay-chung-sinh",
                    label="Giay chung sinh",
                    kind="required",
                    description="Ban chinh do co so y te noi tre sinh ra cap.",
                    source_ref_ids=[citations[1].ref_id],
                ),
                ChecklistItem(
                    id="cccd-cha-me",
                    label="Can cuoc cong dan cua cha va me",
                    kind="required",
                    description="Xuat trinh giay to tuy than de doi chieu.",
                    source_ref_ids=[citations[0].ref_id],
                ),
            ]
            optional_documents = [
                ChecklistItem(
                    id="giay-dang-ky-ket-hon",
                    label="Giay chung nhan ket hon",
                    kind="optional",
                    description="Xuat trinh neu cha me co dang ky ket hon.",
                    source_ref_ids=[citations[0].ref_id],
                )
            ]
            steps = [
                ProcedureStep(
                    order=1,
                    title="Chuan bi va nop ho so",
                    detail="Chuan bi day du giay to va nop tai co quan co tham quyen.",
                )
            ]
            form_schema = {
                "type": "object",
                "properties": {
                    "ho_ten_tre": {
                        "type": "string",
                        "title": "Ho va ten tre",
                        "minLength": 2,
                    },
                    "ngay_sinh_tre": {
                        "type": "string",
                        "title": "Ngay sinh cua tre",
                        "format": "date",
                    },
                    "ho_ten_cha": {"type": "string", "title": "Ho va ten cha"},
                    "ho_ten_me": {"type": "string", "title": "Ho va ten me"},
                },
                "required": ["ho_ten_tre", "ngay_sinh_tre", "ho_ten_me"],
            }
            message = "Checklist dang ky khai sinh da san sang."
        else:
            required_documents = [
                ChecklistItem(
                    id="doc-required-1",
                    label="To khai theo mau quy dinh",
                    kind="required",
                    description="Dien day du thong tin vao bieu mau do nha nuoc ban hanh.",
                    source_ref_ids=[citations[0].ref_id],
                )
            ]
            optional_documents = []
            steps = [
                ProcedureStep(
                    order=1,
                    title="Nop ho so truc tuyen hoac truc tiep",
                    detail="Nop ho so qua Cong dich vu cong hoac tai bo phan Mot cua.",
                )
            ]
            form_schema = {
                "type": "object",
                "properties": {
                    "ho_ten_nguoi_khai": {
                        "type": "string",
                        "title": "Ho va ten nguoi khai",
                        "minLength": 2,
                    },
                    "so_dien_thoai": {"type": "string", "title": "So dien thoai"},
                },
                "required": ["ho_ten_nguoi_khai"],
            }
            message = "Checklist thu tuc da san sang."

        return ChecklistResponse(
            procedure_id=procedure_id,
            procedure_name=PROCEDURES_DB[procedure_id]["name"],
            required_documents=required_documents,
            optional_documents=optional_documents,
            steps=steps,
            form_schema=form_schema,
            message_plain=message,
            trust_state=TrustState.VERIFIED_GUIDANCE,
            source_refs=sources,
            review_gate=ReviewGate.U2_CHECKLIST_REVIEW,
            fixture_mode=True,
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
