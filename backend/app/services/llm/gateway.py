"""Provider-neutral LLM Gateway (xem docs/proposal.md muc 5, D-006).

- Dung `openai` SDK nhung tro `base_url` theo `AI_BASE_URL` de tuong thich
  bat ky provider OpenAI-compatible nao (khong lock-in mot vendor).
- Neu thieu `AI_API_KEY`/`OPENAI_API_KEY` hoac goi model loi/timeout, gateway KHONG bao gio
  bia noi dung quy pham: chuyen sang fallback templating deterministic
  dua tren evidence/finding da co, giu nguyen tinh fail-closed cua he thong.
- Khong nhan raw PII: caller (Orchestrator) phai tokenize truoc khi goi
  gateway (xem app/services/guardrail/pii_guard.py va diagram_v3.mmd).
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from app.config import get_settings
from app.services.llm.prompts import (
    CLARIFICATION_SYSTEM_PROMPT,
    EXPLANATION_SYSTEM_PROMPT,
    build_clarification_user_payload,
    build_explanation_user_payload,
)
from app.services.llm.schemas import ClarificationOutput, ExplanationOutput

logger = logging.getLogger("vngov.llm_gateway")


def _evidence_to_text(chunks) -> str:
    lines = []
    for chunk in chunks:
        lines.append(f"[{chunk.section}] {chunk.text[:600]} (Nguồn: {chunk.source_title})")
    return "\n".join(lines)


class LLMGateway:
    """Facade static; khong giu state ngoai client (khong luu chat history/PII)."""

    _client = None
    _client_initialized = False

    @classmethod
    def reset(cls) -> None:
        """Chi dung trong test: buoc khoi tao lai client theo settings moi."""
        cls._client = None
        cls._client_initialized = False

    @classmethod
    def _get_client(cls):
        if cls._client_initialized:
            return cls._client
        cls._client_initialized = True
        settings = get_settings()
        if not settings.effective_ai_api_key:
            cls._client = None
            return None
        try:
            from openai import OpenAI

            cls._client = OpenAI(
                api_key=settings.effective_ai_api_key,
                base_url=settings.effective_ai_base_url,
                timeout=settings.effective_ai_timeout_seconds,
            )
        except Exception:  # pragma: no cover - defensive, missing/broken SDK
            logger.warning("LLM Gateway: khong the khoi tao client, dung fallback offline.")
            cls._client = None
        return cls._client

    @classmethod
    def is_online(cls) -> bool:
        return cls._get_client() is not None

    @classmethod
    def _call_json(cls, system_prompt: str, user_payload: str) -> Optional[dict]:
        client = cls._get_client()
        if client is None:
            return None
        settings = get_settings()
        try:
            response = client.chat.completions.create(
                model=settings.effective_ai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_payload},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=settings.effective_ai_timeout_seconds,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as exc:  # pragma: no cover - network/provider errors
            logger.warning("LLM Gateway call failed, fallback deterministic: %s", exc)
            return None

    @classmethod
    def generate_clarification(
        cls,
        user_message: str,
        evidence_chunks: List,
        pending_questions: List[str],
        history_summary: str = "",
    ) -> ClarificationOutput:
        payload = build_clarification_user_payload(
            user_message=user_message,
            history_summary=history_summary,
            evidence_text=_evidence_to_text(evidence_chunks),
            pending_questions=pending_questions,
        )
        raw = cls._call_json(CLARIFICATION_SYSTEM_PROMPT, payload)
        if raw is not None:
            try:
                return ClarificationOutput.model_validate(raw)
            except Exception:
                logger.warning("LLM Gateway: output khong dung schema, fallback deterministic.")

        return cls._fallback_clarification(user_message, evidence_chunks, pending_questions)

    @classmethod
    def classify_procedure(cls, text: str, catalog: list) -> Optional[str]:
        """Xep mo ta tu nhien vao mot trong cac procedure_id cho phep (T1, PRD).

        Chi tra ve id nam trong catalog hoac None; khong bao gio tu tao thu tuc
        moi. Offline/loi -> None (giu nguyen hanh vi deterministic hien tai).
        """
        if not catalog:
            return None
        payload = json.dumps({"procedures": catalog, "text": text}, ensure_ascii=False)
        raw = cls._call_json(_CLASSIFY_SYSTEM_PROMPT, payload)
        if not isinstance(raw, dict):
            return None
        procedure_id = raw.get("procedure_id")
        allowed = {item.get("procedure_id") for item in catalog}
        if isinstance(procedure_id, str) and procedure_id in allowed:
            return procedure_id
        return None

    @classmethod
    def extract_form_data(cls, text: str, form_schema: dict) -> Optional[dict]:
        """De xuat gia tri nhap cho form tu mo ta tu nhien (draft-only).

        LLM CHI de xuat gia tri de nguoi dung review; khong phan quyet ho so.
        Offline/loi -> None (caller giu form trong, nguoi dung dien tay).
        """
        properties = (form_schema or {}).get("properties") or {}
        if not properties:
            return None
        field_specs = []
        for field_id, prop in properties.items():
            spec = {
                "id": field_id,
                "title": prop.get("title", field_id),
                "type": prop.get("type", "string"),
            }
            if prop.get("format"):
                spec["format"] = prop["format"]
            if prop.get("enum"):
                spec["enum"] = prop["enum"]
            field_specs.append(spec)
        payload = json.dumps({"fields": field_specs, "text": text}, ensure_ascii=False)
        raw = cls._call_json(_EXTRACTION_SYSTEM_PROMPT, payload)
        if not isinstance(raw, dict):
            return None
        cleaned: dict = {}
        for field_id, value in raw.items():
            prop = properties.get(field_id)
            if prop is None:
                continue
            expected = prop.get("type", "string")
            if expected == "boolean" and isinstance(value, bool):
                cleaned[field_id] = value
            elif (
                expected in ("number", "integer")
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            ):
                cleaned[field_id] = value
            elif expected == "string" and isinstance(value, str) and value.strip():
                text_value = value.strip()[:300]
                if prop.get("enum") and text_value not in prop["enum"]:
                    continue
                cleaned[field_id] = text_value
        return cleaned or None

    @classmethod
    def explain_finding(
        cls,
        field_label: str,
        rule_message: str,
        tokenized_context: str = "",
    ) -> ExplanationOutput:
        payload = build_explanation_user_payload(field_label, rule_message, tokenized_context)
        raw = cls._call_json(EXPLANATION_SYSTEM_PROMPT, payload)
        if raw is not None:
            try:
                return ExplanationOutput.model_validate(raw)
            except Exception:
                logger.warning(
                    "LLM Gateway: explanation output khong dung schema, fallback deterministic."
                )

        return ExplanationOutput(friendly_message=rule_message, suggested_fix=None)

    @staticmethod
    def _fallback_clarification(
        user_message: str,
        evidence_chunks: List,
        pending_questions: List[str],
    ) -> ClarificationOutput:
        if not evidence_chunks:
            return ClarificationOutput(
                intent_summary=user_message[:200],
                needs_clarification=True,
                clarifying_question="Bạn có thể mô tả rõ hơn thủ tục bạn cần thực hiện không?",
                reply_message=(
                    "Tôi chưa xác định được thủ tục phù hợp trong phạm vi hỗ trợ hiện tại "
                    "(đăng ký khai sinh, đăng ký thường trú, đăng ký thành lập hộ kinh doanh). "
                    "Bạn có thể mô tả cụ thể hơn nhu cầu của mình không?"
                ),
            )

        if pending_questions:
            question_text = _PENDING_QUESTION_TEXT.get(
                pending_questions[0],
                "Bạn có thể cung cấp thêm thông tin chi tiết cho trường hợp của mình không?",
            )
            return ClarificationOutput(
                intent_summary=user_message[:200],
                needs_clarification=True,
                clarifying_question=question_text,
                reply_message=question_text,
            )

        procedure_name = evidence_chunks[0].procedure_name if evidence_chunks else "thủ tục của bạn"
        return ClarificationOutput(
            intent_summary=user_message[:200],
            needs_clarification=False,
            clarifying_question=None,
            reply_message=(
                f"Tôi đã tìm được hướng dẫn cho thủ tục **{procedure_name}** kèm nguồn tham khảo bên dưới. "
                "Bạn có thể xem checklist giấy tờ và các bước thực hiện chi tiết."
            ),
        )


_PENDING_QUESTION_TEXT = {
    "procedure_selection": "Bạn đang cần thực hiện thủ tục nào: đăng ký khai sinh, đăng ký thường trú, hay đăng ký thành lập hộ kinh doanh?",
    "jurisdiction_detail": "Bạn dự định nộp hồ sơ tại tỉnh/thành phố hoặc xã/phường nào?",
    "relationship_to_subject": "Bạn là ai trong hồ sơ này (ví dụ: cha/mẹ của trẻ, chủ hộ, người đứng tên đăng ký)?",
}


_EXTRACTION_SYSTEM_PROMPT = (
    "Bạn là bộ trích xuất dữ liệu biểu mẫu hành chính. Người dùng cung cấp danh sách "
    "field (id, title, type, format, enum nếu có) và một đoạn mô tả tiếng Việt. "
    "Trả về DUY NHẤT một JSON object dạng {field_id: giá_trị}. QUY TẮC BẮT BUỘC: "
    "(1) chỉ đưa vào field mà giá trị xuất hiện rõ ràng trong đoạn mô tả, tuyệt đối "
    "không suy đoán hay bịa; (2) ngày tháng chuyển về định dạng YYYY-MM-DD; "
    "(3) field boolean trả true/false; field number trả số; (4) field có enum phải "
    "chọn đúng một giá trị trong enum, không khớp thì bỏ qua field đó; "
    "(5) không thêm field ngoài danh sách, không thêm văn bản ngoài JSON."
)


_CLASSIFY_SYSTEM_PROMPT = (
    "Bạn là bộ phân loại nhu cầu thủ tục hành chính. Người dùng cung cấp danh sách "
    "procedures (procedure_id, name) và một đoạn mô tả tiếng Việt. Trả về DUY NHẤT "
    'một JSON object {"procedure_id": "<id>" | null}. QUY TẮC: chỉ chọn một id có '
    "trong danh sách khi đoạn mô tả thể hiện rõ nhu cầu thuộc thủ tục đó (kể cả khi "
    "người dùng kể gián tiếp, ví dụ kể về việc con mới sinh nghĩa là cần đăng ký khai sinh); "
    "không chắc chắn hoặc ngoài danh sách thì trả null; không thêm trường hay văn bản nào khác."
)
