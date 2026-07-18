from __future__ import annotations

from app.models.common import (
    ConfirmedFact,
    JourneyProgress,
    JourneyStep,
    JourneyStepStatus,
    ReviewGate,
    SessionContext,
)
from app.models.procedure import JourneyStageDefinition, ProcedureCard, ProcedurePack


def build_confirmed_facts(pack: ProcedurePack, context: SessionContext) -> list[ConfirmedFact]:
    """Echo only declared clarification answers; persistence stays with the client."""

    labels = {question.id: question.prompt for question in pack.intake_questions}
    return [
        ConfirmedFact(key=key, label=labels[key], value=value)
        for key, value in context.clarification_answers.items()
        if key in labels
    ]


def build_procedure_card(pack: ProcedurePack) -> ProcedureCard:
    return ProcedureCard(
        procedure_id=pack.procedure_id,
        name=pack.name,
        authority=pack.authority,
        processing_time=pack.processing_time,
        fee=pack.fee,
    )


def build_journey(pack: ProcedurePack, context: SessionContext) -> JourneyProgress:
    stages = pack.journey_stages if len(pack.journey_stages) == 5 else _default_stages(pack)
    completed = 0
    steps: list[JourneyStep] = []
    is_current_available = True

    for index, stage in enumerate(stages):
        stage_complete = _is_complete(index, stage, pack, context)
        if stage_complete:
            status = JourneyStepStatus.COMPLETE
            completed += 1
        elif is_current_available:
            status = JourneyStepStatus.CURRENT
            is_current_available = False
        else:
            status = JourneyStepStatus.UPCOMING
        steps.append(
            JourneyStep(
                id=stage.id,
                title=stage.title,
                description=stage.description,
                status=status,
            )
        )

    return JourneyProgress(completed_steps=completed, steps=steps)


def _is_complete(
    index: int,
    stage: JourneyStageDefinition,
    pack: ProcedurePack,
    context: SessionContext,
) -> bool:
    if index == 0:
        return context.procedure_id == pack.procedure_id
    if stage.requires_document_review:
        document_ids = {item.id for item in pack.required_documents}
        return bool(document_ids) and document_ids.issubset(context.reviewed_document_ids)
    if stage.question_ids:
        return all(
            question_id in context.clarification_answers for question_id in stage.question_ids
        )
    if stage.id == "precheck":
        return ReviewGate.U3_PRECHECK_REVIEW in context.acknowledged_review_gates
    return False


def _default_stages(pack: ProcedurePack) -> list[JourneyStageDefinition]:
    question_ids = [question.id for question in pack.intake_questions]
    return [
        JourneyStageDefinition(
            id="procedure",
            title="Xác định thủ tục",
            description="Xác nhận thủ tục phù hợp.",
        ),
        JourneyStageDefinition(
            id="personal-information",
            title="Thông tin người yêu cầu",
            description="Bổ sung thông tin cần làm rõ cho tình huống.",
            question_ids=question_ids,
        ),
        JourneyStageDefinition(
            id="case-information",
            title="Thông tin theo trường hợp",
            description="Hoàn thiện các dữ kiện theo biểu mẫu được duyệt.",
        ),
        JourneyStageDefinition(
            id="documents",
            title="Giấy tờ đính kèm",
            description="Rà soát checklist trước khi nộp.",
            requires_document_review=True,
        ),
        JourneyStageDefinition(
            id="precheck",
            title="Kiểm tra trước khi nộp",
            description="Xem lại kết quả kiểm tra sơ bộ.",
        ),
    ]
