from __future__ import annotations

from pydantic import Field, model_validator

from app.models.common import (
    ClarificationAnswer,
    ClarifyingQuestion,
    ConfirmedFact,
    IntakeTurnType,
    JourneyProgress,
    NextAction,
    RegulatoryResponse,
    ReviewGate,
    SessionContext,
    StrictRequestModel,
)
from app.models.procedure import ProcedureCandidate, ProcedureCard


class RecommendationRequest(StrictRequestModel):
    need_text: str = Field(min_length=1, max_length=500)
    session_context: SessionContext = Field(default_factory=SessionContext)


class RecommendationResponse(RegulatoryResponse):
    candidates: list[ProcedureCandidate] = Field(default_factory=list, max_length=3)
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    message_plain: str = Field(min_length=1, max_length=1_000)


class IntakeRequest(StrictRequestModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=500)
    session_context: SessionContext = Field(default_factory=SessionContext)
    turn_type: IntakeTurnType = IntakeTurnType.FREE_TEXT
    selected_procedure_id: str | None = Field(default=None, max_length=120)
    clarification_answer: ClarificationAnswer | None = None
    review_gate_acknowledgement: ReviewGate | None = None

    @model_validator(mode="after")
    def validate_turn_payload(self) -> "IntakeRequest":
        if self.turn_type == IntakeTurnType.PROCEDURE_SELECT and not self.selected_procedure_id:
            raise ValueError("selected_procedure_id is required for procedure_select")
        if self.turn_type == IntakeTurnType.CLARIFICATION_ANSWER and not self.clarification_answer:
            raise ValueError("clarification_answer is required for clarification_answer")
        if (
            self.turn_type == IntakeTurnType.REVIEW_ACKNOWLEDGEMENT
            and not self.review_gate_acknowledgement
        ):
            raise ValueError("review_gate_acknowledgement is required for review_acknowledgement")
        return self


class IntakeResponse(RegulatoryResponse):
    session_id: str
    detected_procedure_id: str | None = None
    procedure: ProcedureCandidate | None = None
    message_plain: str = Field(min_length=1, max_length=1_000)
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    proposed_session_context: SessionContext = Field(default_factory=SessionContext)
    journey: JourneyProgress | None = None
    procedure_card: ProcedureCard | None = None
    confirmed_facts: list[ConfirmedFact] = Field(default_factory=list)
    next_action: NextAction | None = None
