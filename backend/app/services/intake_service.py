"""Orchestration cho Guided Intake (capability 1, xem docs/diagram_v3.mmd).

Thu tu goi: RAG retrieve -> (neu can) LLM Gateway sinh clarification/giai
thich -> Trust Policy quyet dinh trust_state -> Redacted Audit ghi log.
Khong goi PII Guard tokenize cho free text (xem Note trong diagram_v3.mmd:
day la stretch goal ngoai pham vi bat buoc cho intake); van redact truoc
khi ghi audit log.
"""

from __future__ import annotations

from typing import List, Optional

from app.models.common import Message
from app.models.intake import IntakeRequest, IntakeResponse
from app.services.guardrail.audit import RedactedAudit
from app.services.guardrail.pii_guard import PIIGuard
from app.services.guardrail.trust_policy import TrustPolicy
from app.services.llm.gateway import LLMGateway
from app.services.rag.retrieval import RetrievalService
from app.services.rag.schemas import RetrievalEvidence, RetrievalQuery
from app.services.rag.source_store import PROCEDURE_DISPLAY_NAME

_CLARIFICATION_SEQUENCE = ["jurisdiction_detail", "relationship_to_subject"]
_RECOMMEND_MIN_SCORE = 0.03


class IntakeService:
    @staticmethod
    def _last_user_message(messages: List[Message]) -> str:
        for message in reversed(messages):
            if message.role == "user":
                return message.content
        return messages[-1].content if messages else ""

    @staticmethod
    def _history_summary(messages: List[Message]) -> str:
        turns = [f"{m.role}: {m.content}" for m in messages[-6:-1]]
        return " | ".join(turns)

    @staticmethod
    def _resolve_procedure_id(request: IntakeRequest, last_message: str) -> Optional[str]:
        if request.current_procedure_id in PROCEDURE_DISPLAY_NAME:
            return request.current_procedure_id

        candidates = RetrievalService.recommend_procedure(last_message, top_k=1)
        if candidates and candidates[0].score >= _RECOMMEND_MIN_SCORE:
            return candidates[0].procedure_id
        return None

    @staticmethod
    def handle_turn(request: IntakeRequest) -> IntakeResponse:
        last_message = IntakeService._last_user_message(request.messages)
        user_turns = sum(1 for m in request.messages if m.role == "user")

        RedactedAudit.log_event(
            "intake_turn_received",
            {
                "session_id": request.session_id,
                "message_preview": PIIGuard.redact_free_text(last_message[:120]),
                "current_procedure_id": request.current_procedure_id,
            },
        )

        detected_id = IntakeService._resolve_procedure_id(request, last_message)

        evidence: Optional[RetrievalEvidence] = None
        pending_questions: List[str] = []

        if detected_id is None:
            pending_questions = ["procedure_selection"]
        else:
            evidence = RetrievalService.retrieve(RetrievalQuery(text=last_message, procedure_id=detected_id))
            already_asked = max(user_turns - 1, 0)
            pending_questions = _CLARIFICATION_SEQUENCE[already_asked:]

        needs_clarification = bool(pending_questions)
        trust_state = TrustPolicy.decide(evidence, out_of_scope=False, needs_clarification=needs_clarification)
        citations = evidence.citations if evidence else []
        trust_state = TrustPolicy.enforce_citations(trust_state, citations)

        clarification = LLMGateway.generate_clarification(
            user_message=last_message,
            evidence_chunks=evidence.chunks if evidence else [],
            pending_questions=pending_questions,
            history_summary=IntakeService._history_summary(request.messages),
        )

        RedactedAudit.log_event(
            "intake_turn_completed",
            {
                "session_id": request.session_id,
                "detected_procedure_id": detected_id,
                "trust_state": trust_state,
                "llm_online": LLMGateway.is_online(),
            },
        )

        return IntakeResponse(
            detected_procedure_id=detected_id,
            message=clarification.reply_message,
            trust_state=trust_state,
            required_clarifications=pending_questions,
            sources=[
                {"title": c.get("title", ""), "url": c.get("url", ""), "ref_code": c.get("ref_code", "")}
                for c in citations
            ],
        )
