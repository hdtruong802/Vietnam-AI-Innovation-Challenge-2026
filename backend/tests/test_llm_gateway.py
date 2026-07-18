from app.services.llm.gateway import LLMGateway
from app.services.llm.schemas import ClarificationOutput, ExplanationOutput
from app.services.rag.schemas import EvidenceChunk


def _sample_chunk():
    return EvidenceChunk(
        chunk_id="c1",
        procedure_id="dang-ky-khai-sinh",
        procedure_name="Đăng ký khai sinh",
        section="steps",
        text="Nộp hồ sơ tại UBND cấp xã.",
        source_title="Luật Hộ tịch",
        source_ref="60/2014/QH13",
        last_verified_at="2026-07-17",
    )


def test_gateway_is_offline_without_api_key(monkeypatch):
    monkeypatch.setattr("app.config.AI_API_KEY", "", raising=False)
    LLMGateway._client_initialized = False
    LLMGateway._client = None

    assert LLMGateway.is_online() is False


def test_fallback_clarification_asks_for_procedure_when_no_evidence(monkeypatch):
    monkeypatch.setattr("app.config.AI_API_KEY", "", raising=False)
    LLMGateway._client_initialized = False
    LLMGateway._client = None

    result = LLMGateway.generate_clarification(
        user_message="tôi cần giúp đỡ",
        evidence_chunks=[],
        pending_questions=[],
    )

    assert isinstance(result, ClarificationOutput)
    assert result.needs_clarification is True
    assert "phạm vi hỗ trợ" in result.reply_message or "mô tả" in result.reply_message.lower()


def test_fallback_clarification_asks_pending_question(monkeypatch):
    monkeypatch.setattr("app.config.AI_API_KEY", "", raising=False)
    LLMGateway._client_initialized = False
    LLMGateway._client = None

    result = LLMGateway.generate_clarification(
        user_message="tôi muốn khai sinh cho con",
        evidence_chunks=[_sample_chunk()],
        pending_questions=["jurisdiction_detail"],
    )

    assert result.needs_clarification is True
    assert result.clarifying_question is not None


def test_fallback_clarification_grounded_message(monkeypatch):
    monkeypatch.setattr("app.config.AI_API_KEY", "", raising=False)
    LLMGateway._client_initialized = False
    LLMGateway._client = None

    result = LLMGateway.generate_clarification(
        user_message="tôi muốn khai sinh cho con",
        evidence_chunks=[_sample_chunk()],
        pending_questions=[],
    )

    assert result.needs_clarification is False
    assert "Đăng ký khai sinh" in result.reply_message


def test_fallback_explanation_never_changes_severity_field(monkeypatch):
    monkeypatch.setattr("app.config.AI_API_KEY", "", raising=False)
    LLMGateway._client_initialized = False
    LLMGateway._client = None

    result = LLMGateway.explain_finding(
        field_label="ho_ten_tre",
        rule_message="Họ và tên trẻ là bắt buộc và không được để trống.",
        tokenized_context="ngay_sinh_tre=2024-01-01",
    )

    assert isinstance(result, ExplanationOutput)
    assert result.friendly_message == "Họ và tên trẻ là bắt buộc và không được để trống."
