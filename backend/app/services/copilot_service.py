from __future__ import annotations

import uuid

from app.catalog import CANONICAL_PROCEDURES, is_known_procedure
from app.models.checklist import ChecklistRequest, ChecklistResponse
from app.models.common import (
    IntakeTurnType,
    NextAction,
    ReviewGate,
    SessionContext,
    TrustState,
)
from app.models.errors import AppError
from app.models.intake import (
    IntakeRequest,
    IntakeResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.models.procedure import ProcedureCandidate, ProcedurePack
from app.models.validation import ValidationRequest, ValidationResponse
from app.ports import (
    AuditSink,
    LLMProvider,
    ProcedureRepository,
    RecommendationProvider,
    RetrievalProvider,
)
from app.services.journey import (
    build_confirmed_facts,
    build_journey,
    build_procedure_card,
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
                message_plain="Hãy chọn một trong ba thủ tục MVP hoặc mô tả rõ hơn nhu cầu của mình.",
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
        if request.turn_type == IntakeTurnType.FREE_TEXT:
            return await self._intake_free_text(request)
        if request.turn_type == IntakeTurnType.PROCEDURE_SELECT:
            return await self._intake_selection(request)
        if request.turn_type == IntakeTurnType.CLARIFICATION_ANSWER:
            return await self._intake_answer(request)
        return await self._intake_review_acknowledgement(request)

    async def checklist(self, procedure_id: str, request: ChecklistRequest) -> ChecklistResponse:
        self._require_known_procedure(procedure_id)
        pack = await self._procedure_repository.get_procedure(procedure_id)
        self._ensure_version(pack, request.procedure_version)
        context = self._context_for_procedure(
            request.session_context, procedure_id, pack, request.clarification_answers
        )
        metadata = self._trust_policy.metadata_for(
            pack, ReviewGate.U2_CHECKLIST_REVIEW, TrustState.VERIFIED_GUIDANCE
        )

        if pack is None:
            return ChecklistResponse(
                **metadata.model_dump(),
                procedure_id=procedure_id,
                procedure_name=self._procedure_name(procedure_id),
                message_plain="Procedure Pack chưa sẵn sàng hoặc chưa được duyệt. Vui lòng dùng kênh chính thức.",
                next_action=self._official_review_action(),
            )

        missing_questions = [
            question.id
            for question in pack.intake_questions
            if question.required and question.id not in context.clarification_answers
        ]
        if metadata.trust_state == TrustState.VERIFIED_GUIDANCE and missing_questions:
            metadata = self._trust_policy.metadata_for(
                pack,
                ReviewGate.U1_PROCEDURE_CONFIRMATION,
                TrustState.NEED_MORE_INFORMATION,
            )

        verified = metadata.trust_state == TrustState.VERIFIED_GUIDANCE
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
            required_documents=pack.required_documents if verified else [],
            optional_documents=pack.optional_documents if verified else [],
            steps=pack.steps if verified else [],
            form_schema=pack.form_schema if verified else {},
            form_sections=pack.form_sections if verified else [],
            procedure_card=build_procedure_card(pack) if verified else None,
            journey=build_journey(pack, context),
            next_action=(
                self._answer_questions_action()
                if missing_questions
                else self._checklist_review_action()
            ),
            message_plain=message,
        )

    async def validate(self, request: ValidationRequest) -> ValidationResponse:
        self._require_known_procedure(request.procedure_id)
        pack = await self._procedure_repository.get_procedure(request.procedure_id)
        self._ensure_version(pack, request.procedure_version)
        context = self._context_for_procedure(request.session_context, request.procedure_id, pack)
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
                journey=build_journey(pack, context) if pack else None,
                next_action=self._official_review_action(),
                proposed_session_context=context,
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
            journey=build_journey(pack, context),
            next_action=NextAction(
                code="review_precheck",
                label="Review kết quả kiểm tra sơ bộ trước khi nộp.",
                review_gate=ReviewGate.U3_PRECHECK_REVIEW,
            ),
            proposed_session_context=context,
        )

    async def _intake_free_text(self, request: IntakeRequest) -> IntakeResponse:
        recommendation = await self.recommend(
            RecommendationRequest(
                need_text=request.message, session_context=request.session_context
            )
        )
        candidate = recommendation.candidates[0] if recommendation.candidates else None
        pack = (
            await self._procedure_repository.get_procedure(candidate.procedure_id)
            if candidate
            else None
        )
        context = self._context_for_procedure(
            request.session_context, candidate.procedure_id if candidate else None, pack
        )
        return await self._build_intake_response(
            request,
            recommendation,
            candidate,
            pack,
            context,
            recommendation.clarifying_questions,
        )

    async def _intake_selection(self, request: IntakeRequest) -> IntakeResponse:
        assert request.selected_procedure_id is not None
        self._require_known_procedure(request.selected_procedure_id)
        pack = await self._procedure_repository.get_procedure(request.selected_procedure_id)
        candidate = (
            ProcedureCandidate(
                procedure_id=pack.procedure_id,
                name=pack.name,
                reason="Người dùng đã chọn thủ tục từ danh sách MVP.",
            )
            if pack
            else None
        )
        context = self._context_for_procedure(
            request.session_context, request.selected_procedure_id, pack
        )
        metadata = self._metadata_for_intake(pack, context)
        recommendation = RecommendationResponse(
            **metadata.model_dump(),
            candidates=[candidate] if candidate else [],
            clarifying_questions=pack.intake_questions if pack else [],
            message_plain=(
                "Hãy trả lời các câu hỏi làm rõ trước khi xem checklist."
                if pack
                else "Procedure Pack chưa sẵn sàng. Vui lòng dùng kênh chính thức."
            ),
        )
        return await self._build_intake_response(
            request,
            recommendation,
            candidate,
            pack,
            context,
            recommendation.clarifying_questions,
        )

    async def _intake_answer(self, request: IntakeRequest) -> IntakeResponse:
        assert request.clarification_answer is not None
        procedure_id = request.session_context.procedure_id
        if not procedure_id:
            raise AppError(422, "procedure_not_selected", "Hãy xác định thủ tục trước khi trả lời.")
        self._require_known_procedure(procedure_id)
        if (
            request.clarification_answer.question_id
            not in request.session_context.pending_question_ids
        ):
            raise AppError(
                422,
                "clarification_question_not_pending",
                "Câu trả lời không thuộc câu hỏi đang chờ xác nhận.",
            )
        pack = await self._procedure_repository.get_procedure(procedure_id)
        answers = {
            **request.session_context.clarification_answers,
            request.clarification_answer.question_id: request.clarification_answer.value,
        }
        context = self._context_for_procedure(request.session_context, procedure_id, pack, answers)
        metadata = self._metadata_for_intake(pack, context)
        candidate = self._candidate_for_pack(pack)
        pending_questions = self._pending_questions(pack, context)
        recommendation = RecommendationResponse(
            **metadata.model_dump(),
            candidates=[candidate] if candidate else [],
            clarifying_questions=pending_questions,
            message_plain=(
                "Cảm ơn bạn. Hãy tiếp tục trả lời các câu hỏi còn lại."
                if pending_questions
                else "Thông tin làm rõ đã đủ để bạn review thủ tục và checklist."
            ),
        )
        return await self._build_intake_response(
            request, recommendation, candidate, pack, context, pending_questions
        )

    async def _intake_review_acknowledgement(self, request: IntakeRequest) -> IntakeResponse:
        assert request.review_gate_acknowledgement is not None
        procedure_id = request.session_context.procedure_id
        pack = (
            await self._procedure_repository.get_procedure(procedure_id) if procedure_id else None
        )
        acknowledged = list(request.session_context.acknowledged_review_gates)
        if request.review_gate_acknowledgement not in acknowledged:
            acknowledged.append(request.review_gate_acknowledgement)
        context = request.session_context.model_copy(
            update={"acknowledged_review_gates": acknowledged}
        )
        metadata = self._metadata_for_intake(pack, context)
        candidate = self._candidate_for_pack(pack)
        pending_questions = self._pending_questions(pack, context)
        recommendation = RecommendationResponse(
            **metadata.model_dump(),
            candidates=[candidate] if candidate else [],
            clarifying_questions=pending_questions,
            message_plain="Đã ghi nhận xác nhận trong phiên hiện tại của trình duyệt.",
        )
        return await self._build_intake_response(
            request, recommendation, candidate, pack, context, pending_questions
        )

    async def _build_intake_response(
        self,
        request: IntakeRequest,
        recommendation: RecommendationResponse,
        candidate: ProcedureCandidate | None,
        pack: ProcedurePack | None,
        context: SessionContext,
        questions: list,
    ) -> IntakeResponse:
        await self._audit_sink.emit(
            "intake_turn",
            {
                "trust_state": recommendation.trust_state.value,
                "procedure_id": candidate.procedure_id if candidate else None,
                "turn_type": request.turn_type.value,
            },
        )
        verified = recommendation.trust_state == TrustState.VERIFIED_GUIDANCE
        return IntakeResponse(
            **recommendation.model_dump(
                exclude={"candidates", "clarifying_questions", "message_plain"}
            ),
            session_id=request.session_id,
            detected_procedure_id=candidate.procedure_id if candidate else None,
            procedure=candidate,
            message_plain=recommendation.message_plain,
            clarifying_questions=questions,
            proposed_session_context=context,
            journey=build_journey(pack, context) if pack else None,
            procedure_card=build_procedure_card(pack) if pack and verified else None,
            confirmed_facts=build_confirmed_facts(pack, context) if pack else [],
            next_action=self._next_intake_action(pack, context, questions),
        )

    def _metadata_for_intake(self, pack: ProcedurePack | None, context: SessionContext):
        state = (
            TrustState.NEED_MORE_INFORMATION
            if self._pending_questions(pack, context)
            else TrustState.VERIFIED_GUIDANCE
        )
        return self._trust_policy.metadata_for(pack, ReviewGate.U1_PROCEDURE_CONFIRMATION, state)

    @staticmethod
    def _candidate_for_pack(pack: ProcedurePack | None) -> ProcedureCandidate | None:
        if pack is None:
            return None
        return ProcedureCandidate(
            procedure_id=pack.procedure_id,
            name=pack.name,
            reason="Thủ tục đang được xử lý trong phiên hiện tại.",
        )

    @staticmethod
    def _pending_questions(pack: ProcedurePack | None, context: SessionContext) -> list:
        if pack is None:
            return []
        return [
            question
            for question in pack.intake_questions
            if question.id not in context.clarification_answers
        ]

    @staticmethod
    def _context_for_procedure(
        context: SessionContext,
        procedure_id: str | None,
        pack: ProcedurePack | None,
        answers: dict[str, str] | None = None,
    ) -> SessionContext:
        merged_answers = answers if answers is not None else context.clarification_answers
        pending = (
            [question.id for question in pack.intake_questions if question.id not in merged_answers]
            if pack
            else []
        )
        return context.model_copy(
            update={
                "procedure_id": procedure_id,
                "procedure_version": (pack.version if pack else context.procedure_version),
                "clarification_answers": merged_answers,
                "pending_question_ids": pending,
            }
        )

    @staticmethod
    def _answer_questions_action() -> NextAction:
        return NextAction(
            code="answer_clarifications",
            label="Trả lời các câu hỏi làm rõ còn lại.",
            review_gate=ReviewGate.U1_PROCEDURE_CONFIRMATION,
        )

    @staticmethod
    def _checklist_review_action() -> NextAction:
        return NextAction(
            code="review_checklist",
            label="Review checklist, nguồn và ngày xác minh trước khi tiếp tục.",
            review_gate=ReviewGate.U2_CHECKLIST_REVIEW,
        )

    @staticmethod
    def _official_review_action() -> NextAction:
        return NextAction(
            code="official_review_required",
            label="Dùng kênh chính thức để được hỗ trợ và xác nhận.",
        )

    def _next_intake_action(
        self, pack: ProcedurePack | None, context: SessionContext, questions: list
    ) -> NextAction:
        if pack is None:
            return self._official_review_action()
        if questions:
            return self._answer_questions_action()
        if ReviewGate.U1_PROCEDURE_CONFIRMATION not in context.acknowledged_review_gates:
            return NextAction(
                code="confirm_procedure",
                label="Xác nhận thủ tục trước khi chuyển sang checklist.",
                review_gate=ReviewGate.U1_PROCEDURE_CONFIRMATION,
            )
        return self._checklist_review_action()

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
