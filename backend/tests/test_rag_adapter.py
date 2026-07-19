"""Tich hop RAG/LLM/Guardrail adapter voi khung CopilotService/AppContainer.

Bo sung cho test_api_contract.py (fixture mode) va test_retrieval.py/
test_pii_guard.py/test_llm_gateway.py (unit tren tang service): kiem tra
adapter moi (`app/adapters/rag_llm.py`) tra dung du lieu that tu
data/Data_DVC qua CopilotService, giu nguyen contract/trust state cua
D-006 va khong doi verdict khi LLM explain duoc them vao.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.adapters.rag_llm import (
    GatewayLLMProvider,
    RagProcedureRepository,
    RagRecommendationProvider,
)
from app.config import Settings, get_settings
from app.main import create_app
from app.models.common import SessionContext
from app.models.procedure import ReviewStatus
from app.models.validation import Finding


def _has_source_data() -> bool:
    source_path = get_settings().rag_source_path
    return source_path.exists() and any(source_path.glob("*.txt"))


requires_source_data = pytest.mark.skipif(
    not _has_source_data(), reason="data/Data_DVC khong ton tai trong moi truong nay"
)


@pytest.fixture
def rag_client() -> TestClient:
    settings = Settings(
        app_env="test",
        procedure_data_mode="rag",
        rag_mode="rag",
        llm_mode="gateway",
        openai_api_key="",
        **{"AI_API_KEY": ""},
    )
    return TestClient(create_app(settings=settings))


@requires_source_data
@pytest.mark.anyio
async def test_repository_lists_three_mvp_procedures_as_needing_review():
    repository = RagProcedureRepository()
    summaries = await repository.list_procedures()

    assert {item.procedure_id for item in summaries} == {
        "dang-ky-khai-sinh",
        "dang-ky-thuong-tru",
        "dang-ky-ho-kinh-doanh",
    }
    assert all(item.review_status == ReviewStatus.NEEDS_REVIEW for item in summaries)


@requires_source_data
@pytest.mark.anyio
async def test_repository_pack_has_grounded_source_refs_and_checksum():
    repository = RagProcedureRepository()
    pack = await repository.get_procedure("dang-ky-thuong-tru")

    assert pack is not None
    assert pack.review_status == ReviewStatus.NEEDS_REVIEW
    assert pack.checksum
    assert pack.source_refs
    assert pack.required_documents
    assert pack.last_verified_at is None


@requires_source_data
@pytest.mark.anyio
async def test_repository_pack_is_approved_when_demo_k1_flag_enabled(monkeypatch):
    """Xem D-019: flag chi anh huong khi bat tuong minh; version phai co
    marker 'demo-k1-simulated' de khong nham voi K1 nguoi thuc."""
    original = get_settings()
    monkeypatch.setattr(
        "app.services.rag.pack_builder.get_settings",
        lambda: original.model_copy(update={"rag_demo_k1_approved": True}),
    )

    repository = RagProcedureRepository()
    pack = await repository.get_procedure("dang-ky-thuong-tru")

    assert pack is not None
    assert pack.review_status == ReviewStatus.APPROVED
    assert pack.last_verified_at is not None
    assert "demo-k1-simulated" in pack.version
    assert pack.form_schema.get("properties", {}).get("so_dinh_danh_ca_nhan")


@requires_source_data
@pytest.mark.anyio
async def test_recommendation_provider_matches_accented_vietnamese():
    provider = RagRecommendationProvider()
    candidates = await provider.recommend(
        "Tôi muốn đăng ký thành lập hộ kinh doanh", SessionContext()
    )

    assert candidates
    assert candidates[0].procedure_id == "dang-ky-ho-kinh-doanh"


@requires_source_data
@pytest.mark.anyio
@pytest.mark.parametrize(
    "need_text",
    [
        "xin chào",
        "tôi muốn đăng ký",
        "tôi muốn đăng ký kết hôn",
        "tôi cần khai tử",
        "tôi muốn làm hộ chiếu",
        "đăng ký tạm trú",
        "thành lập công ty cổ phần",
    ],
)
async def test_recommendation_provider_abstains_out_of_scope(need_text: str):
    provider = RagRecommendationProvider()

    assert await provider.recommend(need_text, SessionContext()) == []


@requires_source_data
def test_health_reports_rag_capability(rag_client: TestClient):
    response = rag_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["capabilities"] == {
        "procedure_data": "rag",
        "procedure_guidance": "needs_review",
        "rag": "rag",
        "rag_ready": "true",
        "llm": "gateway",
        "llm_ready": "false",
        "legacy_rag": "disabled",
    }


@requires_source_data
def test_checklist_endpoint_requires_official_review_for_candidate_sources(
    rag_client: TestClient,
):
    response = rag_client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist", json={"clarification_answers": {}}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trust_state"] == "official_review_required"
    assert body["fixture_mode"] is False
    assert body["source_refs"]
    # D-016 (web-to-API): candidate NEEDS_REVIEW packs may expose their cited
    # document checklist for review, but steps/form/precheck stay locked.
    assert body["required_documents"]
    assert all(item["source_ref_ids"] for item in body["required_documents"])
    assert body["steps"] == []
    assert body["form_schema"] == {}
    assert body["procedure_card"] is None


@requires_source_data
def test_recommend_endpoint_uses_real_evidence(rag_client: TestClient):
    response = rag_client.post(
        "/v1/procedures/recommend", json={"need_text": "Tôi muốn đăng ký thường trú"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["candidates"][0]["procedure_id"] == "dang-ky-thuong-tru"
    assert body["trust_state"] == "official_review_required"


@requires_source_data
def test_validate_endpoint_does_not_issue_verdict_for_candidate_sources(
    rag_client: TestClient,
):
    response = rag_client.post(
        "/v1/applications/validate",
        json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trust_state"] == "official_review_required"
    assert body["verdict"] is None
    assert body["findings"] == []
    assert body["explanations"] == {}


@requires_source_data
def test_validate_endpoint_unlocks_full_flow_when_demo_k1_approved(
    rag_client: TestClient, monkeypatch
):
    """Xem D-019: bat RAG_DEMO_K1_APPROVED phai mo full flow (verified_guidance
    + findings that tu form_schema cu the) tren du lieu RAG thuc, khac voi
    hanh vi mac dinh (official_review_required) o test tren."""
    original = get_settings()
    monkeypatch.setattr(
        "app.services.rag.pack_builder.get_settings",
        lambda: original.model_copy(update={"rag_demo_k1_approved": True}),
    )

    response = rag_client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-thuong-tru",
            "form_data": {
                "ho_ten_nguoi_de_nghi": "Nguyen Van A",
                "so_dinh_danh_ca_nhan": "khong-phai-so",
                "dia_chi_de_nghi_thuong_tru": "So 1 Hang Bai, Ha Noi",
                "ho_ten_chu_ho": "Nguyen Van B",
                "quan_he_voi_chu_ho": "Con",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trust_state"] == "verified_guidance"
    assert "demo-k1-simulated" in body["procedure_version"]
    field_ids = {finding["field_id"] for finding in body["findings"]}
    assert "so_dinh_danh_ca_nhan" in field_ids


@pytest.mark.anyio
async def test_gateway_llm_provider_never_changes_finding_and_clears_session(
    monkeypatch,
):
    provider = GatewayLLMProvider()
    monkeypatch.setattr("app.adapters.rag_llm.LLMGateway.is_online", classmethod(lambda cls: True))

    finding = Finding(
        field_id="ho_ten_tre",
        severity="error",
        rule_id="DANG-KY-KHAI-SINH-REQ-1",
        message="Họ và tên trẻ là bắt buộc và không được để trống.",
    )
    explanations = await provider.explain_findings(
        "test-session-explain", {"ho_ten_tre": "Nguyễn Văn A"}, [finding]
    )

    assert explanations[finding.rule_id] == finding.message
    from app.services.guardrail.pii_guard import PIIGuard

    assert PIIGuard._sessions.get("test-session-explain") is None


@pytest.fixture
def anyio_backend():
    return "asyncio"
