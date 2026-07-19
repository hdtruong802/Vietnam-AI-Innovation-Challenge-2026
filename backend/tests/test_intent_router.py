from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import build_container
from app.main import create_app
from app.services.intent_router import (
    IntakeDisposition,
    classify_intake_text,
    normalize_intent_text,
)


class ExplodingRecommendationProvider:
    async def recommend(self, need_text, session_context):
        raise AssertionError("guarded intent must not call recommendation provider")


def _client() -> TestClient:
    settings = Settings(
        app_env="test",
        procedure_data_mode="demo_pack",
        rag_mode="disabled",
        llm_mode="disabled",
        ai_api_key="",
        openai_api_key="",
    )
    return TestClient(create_app(settings=settings))


def test_normalization_handles_accents_punctuation_and_spacing() -> None:
    assert normalize_intent_text("  Đăng ký, THƯỜNG trú! ") == "dang ky thuong tru"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("Xin chào trợ lý", IntakeDisposition.GREETING),
        ("Hello, tôi cần hỗ trợ", IntakeDisposition.GREETING),
        ("Tôi muốn đổi giấy phép lái xe", IntakeDisposition.OUT_OF_SCOPE),
        ("Cấp hộ chiếu lần đầu", IntakeDisposition.OUT_OF_SCOPE),
        ("Xin cấp lại bản sao giấy khai sinh", IntakeDisposition.UNSUPPORTED_NEAR_INTENT),
        ("Đăng ký tạm trú", IntakeDisposition.UNSUPPORTED_NEAR_INTENT),
        ("Thay đổi địa chỉ hộ kinh doanh", IntakeDisposition.UNSUPPORTED_NEAR_INTENT),
        ("Tôi cần làm giấy tờ cho con", IntakeDisposition.CONTINUE),
        ("Tôi muốn đăng ký khai sinh", IntakeDisposition.CONTINUE),
    ],
)
def test_classify_intake_text(query: str, expected: IntakeDisposition) -> None:
    assert classify_intake_text(query) == expected


@pytest.mark.parametrize(
    ("query", "expected_trust_state"),
    [
        ("Xin chào trợ lý", "need_more_information"),
        ("Tôi muốn đổi giấy phép lái xe", "official_review_required"),
        ("Xin cấp lại bản sao giấy khai sinh", "official_review_required"),
    ],
)
def test_guard_short_circuits_recommendation_provider(
    query: str,
    expected_trust_state: str,
) -> None:
    settings = Settings(app_env="test", procedure_data_mode="demo_pack")
    container = build_container(settings)
    container.recommendation_provider = ExplodingRecommendationProvider()
    client = TestClient(create_app(settings=settings, container=container))

    response = client.post(
        "/v1/intake/turn",
        json={"session_id": "guard-test", "message": query, "session_context": {}},
    )

    assert response.status_code == 200
    assert response.json()["detected_procedure_id"] is None
    assert response.json()["trust_state"] == expected_trust_state
    assert response.json()["last_verified_at"] is None


def test_ambiguous_intent_requests_more_information() -> None:
    response = _client().post(
        "/v1/intake/turn",
        json={
            "session_id": "ambiguous-test",
            "message": "Tôi mới chuyển nhà cần làm giấy tờ gì",
            "session_context": {},
        },
    )

    assert response.status_code == 200
    assert response.json()["detected_procedure_id"] is None
    assert response.json()["trust_state"] == "need_more_information"


def test_document_word_does_not_trigger_out_of_scope_guard() -> None:
    response = _client().post(
        "/v1/intake/turn",
        json={
            "session_id": "document-context-test",
            "message": "Đăng ký khai sinh có cần căn cước của cha mẹ không",
            "session_context": {},
        },
    )

    assert response.status_code == 200
    assert response.json()["detected_procedure_id"] == "dang-ky-khai-sinh"
    assert response.json()["trust_state"] == "need_more_information"


@pytest.mark.parametrize(
    ("query", "expected_procedure_id"),
    [
        ("Tôi muốn đăng ký khai sihn cho con", "dang-ky-khai-sinh"),
        ("Tôi muốn đăng ký thườn trú", "dang-ky-thuong-tru"),
        ("Đăng ký hộ kinh doah", "dang-ky-ho-kinh-doanh"),
    ],
)
def test_conservative_typo_matching_routes_supported_intents(
    query: str,
    expected_procedure_id: str,
) -> None:
    response = _client().post(
        "/v1/intake/turn",
        json={"session_id": "typo-test", "message": query, "session_context": {}},
    )

    assert response.status_code == 200
    assert response.json()["detected_procedure_id"] == expected_procedure_id
    assert response.json()["trust_state"] == "need_more_information"
    assert response.json()["demo_mode"] is True
