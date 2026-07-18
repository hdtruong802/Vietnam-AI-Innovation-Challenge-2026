from typing import Dict, Any
from uuid import uuid4

from app.models.validation import ValidationResponse, Finding
from app.services.guardrail.audit import RedactedAudit
from app.services.guardrail.pii_guard import PIIGuard
from app.services.llm.gateway import LLMGateway
from app.services.rag.retrieval import RetrievalService


class ValidationService:
    @staticmethod
    def validate(procedure_id: str, form_data: Dict[str, Any]) -> ValidationResponse:
        findings = []
        is_valid = True

        if procedure_id == "dang-ky-khai-sinh":
            # Required checks
            if not form_data.get("ho_ten_tre"):
                findings.append(Finding(
                    field="ho_ten_tre",
                    severity="error",
                    message="Họ và tên trẻ là bắt buộc và không được để trống.",
                    fix_suggestion="Vui lòng điền họ và tên đầy đủ của trẻ.",
                    rule_id="R-BIRTH-001"
                ))
                is_valid = False

            if not form_data.get("ngay_sinh_tre"):
                findings.append(Finding(
                    field="ngay_sinh_tre",
                    severity="error",
                    message="Ngày sinh của trẻ là bắt buộc.",
                    fix_suggestion="Vui lòng chọn ngày sinh của trẻ.",
                    rule_id="R-BIRTH-002"
                ))
                is_valid = False

            # Logical / cross-field check
            ho_ten_tre = form_data.get("ho_ten_tre", "")
            if ho_ten_tre and not any(char.isalpha() for char in ho_ten_tre):
                findings.append(Finding(
                    field="ho_ten_tre",
                    severity="error",
                    message="Họ tên của trẻ chứa ký tự không hợp lệ.",
                    fix_suggestion="Vui lòng chỉ sử dụng chữ cái tiếng Việt và khoảng trắng.",
                    rule_id="R-BIRTH-003"
                ))
                is_valid = False

            # Warning checks
            if not form_data.get("ho_ten_cha"):
                findings.append(Finding(
                    field="ho_ten_cha",
                    severity="warning",
                    message="Thiếu thông tin người cha có thể ảnh hưởng nếu muốn ghi tên cha vào giấy khai sinh ngay lập tức.",
                    fix_suggestion="If there is father information, please fill it in to do identification at the same time.",
                    rule_id="R-BIRTH-004"
                ))

        else:
            # Default validator for other forms
            if not form_data.get("ho_ten_nguoi_khai"):
                findings.append(Finding(
                    field="ho_ten_nguoi_khai",
                    severity="error",
                    message="Họ và tên người khai là bắt buộc.",
                    fix_suggestion="Vui lòng điền họ tên của bạn.",
                    rule_id="R-GEN-001"
                ))
                is_valid = False

        # Gan source_ref tu RAG citations (grounding), khong doi severity/rule_id.
        citations = RetrievalService.get_citations_for_procedure(procedure_id)
        default_source_ref = citations[0]["ref_code"] if citations else None
        for finding in findings:
            if finding.source_ref is None:
                finding.source_ref = default_source_ref

        findings = ValidationService._explain_findings(procedure_id, form_data, findings)

        summary = "Hồ sơ của bạn đã đạt các kiểm tra sơ bộ." if is_valid else "Phát hiện một số lỗi cần khắc phục trước khi nộp hồ sơ."

        RedactedAudit.log_event(
            "validation_completed",
            {
                "procedure_id": procedure_id,
                "is_valid": is_valid,
                "findings_count": len(findings),
                "llm_online": LLMGateway.is_online(),
            },
        )

        return ValidationResponse(
            procedure_id=procedure_id,
            is_valid=is_valid,
            findings=findings,
            summary_message=summary
        )

    @staticmethod
    def _explain_findings(procedure_id: str, form_data: Dict[str, Any], findings):
        """LLM co the dien giai lai finding cho tu nhien hon, nhung KHONG duoc
        doi field/severity/rule_id (verdict van do rule engine quyet dinh —
        xem 'Deterministic rules' trong docs/proposal.md muc 1).

        Dung mot session PII Guard tam thoi trong pham vi request nay (khong
        can them session_id vao public schema): tokenize -> goi LLM -> detokenize
        -> huy session ngay, thay vi gui raw form data ra ngoai.
        """

        if not findings or not LLMGateway.is_online():
            return findings

        ephemeral_session = f"validate-{uuid4().hex}"
        tokenized_form, _ = PIIGuard.tokenize_fields(ephemeral_session, form_data)

        enriched = []
        for finding in findings:
            context_pairs = [
                f"{key}={value}" for key, value in tokenized_form.items() if key != finding.field
            ]
            tokenized_context = ", ".join(context_pairs)[:400]

            explanation = LLMGateway.explain_finding(
                field_label=finding.field or "",
                rule_message=finding.message,
                tokenized_context=tokenized_context,
            )

            friendly_message = PIIGuard.detokenize_text(ephemeral_session, explanation.friendly_message)
            suggested_fix = (
                PIIGuard.detokenize_text(ephemeral_session, explanation.suggested_fix)
                if explanation.suggested_fix
                else finding.fix_suggestion
            )

            enriched.append(
                finding.model_copy(update={"message": friendly_message or finding.message, "fix_suggestion": suggested_fix})
            )

        PIIGuard.clear_session(ephemeral_session)
        return enriched
