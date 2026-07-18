"""Provider-neutral LLM Gateway (xem docs/proposal.md muc 5, D-006).

- Dung `openai` SDK nhung tro `base_url` theo `AI_BASE_URL` de tuong thich
  bat ky provider OpenAI-compatible nao (khong lock-in mot vendor).
- Neu thieu `AI_API_KEY` hoac goi model loi/timeout, gateway KHONG bao gio
  bia noi dung quy pham: chuyen sang fallback templating deterministic
  dua tren evidence/finding da co, giu nguyen tinh fail-closed cua he thong.
- Khong nhan raw PII: caller (Orchestrator) phai tokenize truoc khi goi
  gateway (xem app/services/guardrail/pii_guard.py va diagram_v3.mmd).
"""

from __future__ import annotations

import json
import logging
import time
from typing import List, Optional

import app.config as app_config
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
    def _get_client(cls):
        if cls._client_initialized:
            return cls._client
        cls._client_initialized = True
        if not app_config.AI_API_KEY:
            cls._client = None
            return None
        try:
            from openai import OpenAI

            cls._client = OpenAI(
                api_key=app_config.AI_API_KEY,
                base_url=app_config.AI_BASE_URL,
                timeout=app_config.AI_TIMEOUT_SECONDS,
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
        try:
            response = client.chat.completions.create(
                model=app_config.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_payload},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=app_config.AI_TIMEOUT_SECONDS,
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
        start = time.monotonic()
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
                logger.warning("LLM Gateway: explanation output khong dung schema, fallback deterministic.")

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
                pending_questions[0], "Bạn có thể cung cấp thêm thông tin chi tiết cho trường hợp của mình không?"
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
