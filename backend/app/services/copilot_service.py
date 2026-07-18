from __future__ import annotations

import uuid

from app.catalog import CANONICAL_PROCEDURES, is_known_procedure
from app.models.checklist import ChecklistRequest, ChecklistResponse
from app.models.common import ReviewGate, TrustState
from app.models.errors import AppError
from app.models.intake import (
    IntakeRequest,
    IntakeResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.models.procedure import ProcedurePack
from app.models.validation import ValidationRequest, ValidationResponse
from app.ports import (
    AuditSink,
    LLMProvider,
    ProcedureRepository,
    RecommendationProvider,
    RetrievalProvider,
)
from app.services.rule_engine import RuleEngine
from app.services.trust_policy import TrustPolicy


class CopilotService:
    def __init__(
        self,
        procedure_repository: ProcedureRepository,
        recommendation_provider: RecommendationProvider,
        retrieval_provider: RetrievalProvider,
        audit_sink: AuditSink,
        rule_engine: RuleEngine,
        trust_policy: TrustPolicy,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._procedure_repository = procedure_repository
        self._recommendation_provider = recommendation_provider
        self._retrieval_provider = retrieval_provider
        self._audit_sink = audit_sink
        self._rule_engine = rule_engine
        self._trust_policy = trust_policy
        self._llm_provider = llm_provider

    async def list_procedures(self):
        return await self._procedure_repository.list_procedures()

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        candidates = await self._recommendation_provider.recommend(
            request.need_text, request.session_context
        )
        if not candidates:
            metadata = self._trust_policy.needs_more_information(
                ReviewGate.U1_PROCEDURE_CONFIRMATION
            )
            return RecommendationResponse(
                **metadata.model_dump(),
                candidates=[],
                clarifying_questions=[],
                message_plain="Bạn hãy chọn một trong ba thủ tục MVP hoặc mô tả rõ hơn nhu cầu của mình.",
            )

        pack = await self._procedure_repository.get_procedure(candidates[0].procedure_id)
        metadata = self._trust_policy.metadata_for(
            pack, ReviewGate.U1_PROCEDURE_CONFIRMATION, TrustState.NEED_MORE_INFORMATION
        )
        message = (
            "Đã nhận diện thủ tục trong dữ liệu thử nghiệm. Hãy kết nối Procedure Pack đã review "
            "trước khi dùng kết quả này để chuẩn bị hồ sơ thực tế."
            if metadata.fixture_mode
            else "Hãy xác nhận thủ tục và trả lời các câu hỏi làm rõ để nhận checklist phù hợp."
        )
        return RecommendationResponse(
            **metadata.model_dump(),
            candidates=candidates,
            clarifying_questions=pack.intake_questions if pack else [],
            message_plain=message,
        )

    async def intake(self, request: IntakeRequest) -> IntakeResponse:
        recommendation = await self.recommend(
            RecommendationRequest(
                need_text=request.message, session_context=request.session_context
            )
        )
        candidate = recommendation.candidates[0] if recommendation.candidates else None
        proposed_context = request.session_context.model_copy(
            update={
                "procedure_id": (
                    candidate.procedure_id if candidate else request.session_context.procedure_id
                ),
                "procedure_version": recommendation.procedure_version,
                "pending_question_ids": [
                    question.id for question in recommendation.clarifying_questions
                ],
            }
        )
        await self._audit_sink.emit(
            "intake_turn",
            {
                "trust_state": recommendation.trust_state.value,
                "procedure_id": candidate.procedure_id if candidate else None,
            },
        )
        return IntakeResponse(
            **recommendation.model_dump(
                exclude={"candidates", "clarifying_questions", "message_plain"}
            ),
            session_id=request.session_id,
            detected_procedure_id=candidate.procedure_id if candidate else None,
            procedure=candidate,
            message_plain=recommendation.message_plain,
            clarifying_questions=recommendation.clarifying_questions,
            proposed_session_context=proposed_context,
        )

    async def checklist(self, procedure_id: str, request: ChecklistRequest) -> ChecklistResponse:
        self._require_known_procedure(procedure_id)
        pack = await self._procedure_repository.get_procedure(procedure_id)
        self._ensure_version(pack, request.procedure_version)
        metadata = self._trust_policy.metadata_for(
            pack, ReviewGate.U2_CHECKLIST_REVIEW, TrustState.VERIFIED_GUIDANCE
        )

        if pack is None:
            return ChecklistResponse(
                **metadata.model_dump(),
                procedure_id=procedure_id,
                procedure_name=self._procedure_name(procedure_id),
                message_plain="Procedure Pack chưa sẵn sàng hoặc chưa được duyệt. Vui lòng dùng kênh chính thức.",
            )

        missing_questions = [
            question.id
            for question in pack.intake_questions
            if question.required and question.id not in request.clarification_answers
        ]
        if metadata.trust_state == TrustState.VERIFIED_GUIDANCE and missing_questions:
            metadata = self._trust_policy.metadata_for(
                pack, ReviewGate.U1_PROCEDURE_CONFIRMATION, TrustState.NEED_MORE_INFORMATION
            )

        message = (
            "Đây là checklist fixture để tích hợp API, không phải yêu cầu hồ sơ thật."
            if metadata.fixture_mode
            else "Hãy review checklist, nguồn và ngày xác minh trước khi tiếp tục."
        )
        await self._audit_sink.emit(
            "checklist_generate",
            {"trust_state": metadata.trust_state.value, "procedure_id": procedure_id},
        )
        return ChecklistResponse(
            **metadata.model_dump(),
            procedure_id=pack.procedure_id,
            procedure_name=pack.name,
            required_documents=pack.required_documents,
            optional_documents=pack.optional_documents,
            steps=pack.steps,
            form_schema=pack.form_schema,
            message_plain=message,
        )

    async def validate(self, request: ValidationRequest) -> ValidationResponse:
        self._require_known_procedure(request.procedure_id)
        pack = await self._procedure_repository.get_procedure(request.procedure_id)
        self._ensure_version(pack, request.procedure_version)
        metadata = self._trust_policy.metadata_for(
            pack, ReviewGate.U3_PRECHECK_REVIEW, TrustState.VERIFIED_GUIDANCE
        )

        if pack is None or metadata.trust_state != TrustState.VERIFIED_GUIDANCE:
            return ValidationResponse(
                **metadata.model_dump(),
                procedure_id=request.procedure_id,
                verdict=None,
                summary_message=(
                    "Không thể thực hiện kiểm tra sơ bộ trên dữ liệu chưa được duyệt. "
                    "Vui lòng dùng kênh chính thức."
                ),
            )

        findings = self._rule_engine.validate(pack, request.form_data)
        verdict = "needs_fix" if self._rule_engine.has_errors(findings) else "pass_preliminary"
        explanations = await self._explain_findings_if_available(findings, request.form_data)
        await self._audit_sink.emit(
            "application_validate",
            {
                "procedure_id": request.procedure_id,
                "finding_count": len(findings),
                "trust_state": metadata.trust_state.value,
            },
        )
        return ValidationResponse(
            **metadata.model_dump(),
            procedure_id=request.procedure_id,
            verdict=verdict,
            findings=findings,
            explanations=explanations,
            summary_message=(
                "Hồ sơ đạt kiểm tra sơ bộ theo các quy tắc đã duyệt."
                if verdict == "pass_preliminary"
                else "Phát hiện thông tin cần sửa trước khi kiểm tra lại."
            ),
        )

    async def _explain_findings_if_available(
        self, findings: list, form_data: dict
    ) -> dict[str, str]:
        """Best-effort: LLM chỉ diễn giải finding đã có, không đổi verdict.

        Dùng session_id tạm/độc lập cho mỗi lần gọi vì ValidationRequest
        không có session_id công khai; PII Guard tokenize form_data trước
        khi rời trusted boundary và session bị hủy ngay sau khi dùng.
        """
        if not findings or self._llm_provider is None:
            return {}
        if not await self._llm_provider.is_available():
            return {}
        ephemeral_session_id = f"validate-{uuid.uuid4().hex}"
        return await self._llm_provider.explain_findings(ephemeral_session_id, form_data, findings)

    @staticmethod
    def _ensure_version(pack: ProcedurePack | None, requested_version: str | None) -> None:
        if pack and requested_version and requested_version != pack.version:
            raise AppError(
                409,
                "procedure_version_conflict",
                "Phiên bản thủ tục đã thay đổi. Hãy tải lại checklist trước khi tiếp tục.",
            )

    @staticmethod
    def _require_known_procedure(procedure_id: str) -> None:
        if not is_known_procedure(procedure_id):
            raise AppError(404, "procedure_not_found", "Thủ tục này chưa thuộc phạm vi MVP.")

    @staticmethod
    def _procedure_name(procedure_id: str) -> str:
        return next(item.name for item in CANONICAL_PROCEDURES if item.procedure_id == procedure_id)
