from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.adapters.dev_fixture import FIXTURE_PACKS, FixtureRecommendationProvider
from app.config import Settings
from app.dependencies import build_container
from app.main import create_app
from app.models.common import Citation
from app.models.procedure import ProcedurePack, ProcedureSummary, ReviewStatus


class ApprovedProcedureRepository:
    def __init__(self, pack: ProcedurePack) -> None:
        self.pack = pack

    async def list_procedures(self) -> list[ProcedureSummary]:
        return [
            ProcedureSummary(
                procedure_id=self.pack.procedure_id,
                name=self.pack.name,
                version=self.pack.version,
                review_status=self.pack.review_status,
            )
        ]

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None:
        return self.pack if procedure_id == self.pack.procedure_id else None


def approved_birth_pack() -> ProcedurePack:
    fixture = FIXTURE_PACKS["dang-ky-khai-sinh"].model_copy(deep=True)
    official_source = Citation(
        ref_id="test-approved-source",
        title="Nguồn approved giả lập cho contract test",
        url_or_ref="https://example.invalid/approved-source",
    )
    rules = [
        rule.model_copy(update={"source_ref_ids": [official_source.ref_id]})
        for rule in fixture.validation_rules
    ]
    return fixture.model_copy(
        update={
            "version": "approved-test-v1",
            "review_status": ReviewStatus.APPROVED,
            "checksum": "test-checksum",
            "source_refs": [official_source],
            "last_verified_at": date.today(),
            "validation_rules": rules,
        }
    )


@pytest.fixture
def client() -> TestClient:
    settings = Settings(app_env="test", procedure_data_mode="fixture")
    return TestClient(create_app(settings=settings))


def test_health_reports_fixture_capability(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["capabilities"]["procedure_data"] == "fixture"


def test_procedures_list_only_the_three_mvp_ids(client: TestClient) -> None:
    response = client.get("/v1/procedures")

    assert response.status_code == 200
    assert {item["procedure_id"] for item in response.json()} == {
        "dang-ky-khai-sinh",
        "dang-ky-thuong-tru",
        "dang-ky-ho-kinh-doanh",
    }
    assert all(item["fixture_mode"] for item in response.json())


def test_recommend_and_intake_support_accented_vietnamese(client: TestClient) -> None:
    recommend = client.post(
        "/v1/procedures/recommend",
        json={"need_text": "Tôi muốn đăng ký thường trú"},
    )
    intake = client.post(
        "/v1/intake/turn",
        json={"session_id": "synthetic-session", "message": "Tôi muốn đăng ký thường trú"},
    )

    assert recommend.status_code == 200
    assert recommend.json()["candidates"][0]["procedure_id"] == "dang-ky-thuong-tru"
    assert recommend.json()["trust_state"] == "official_review_required"
    assert intake.status_code == 200
    assert intake.json()["detected_procedure_id"] == "dang-ky-thuong-tru"
    assert intake.json()["proposed_session_context"]["procedure_id"] == "dang-ky-thuong-tru"


def test_fixture_checklist_and_precheck_fail_closed(client: TestClient) -> None:
    checklist = client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist",
        json={"clarification_answers": {}},
    )
    validation = client.post(
        "/v1/applications/validate",
        json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
    )

    assert checklist.status_code == 200
    assert checklist.json()["fixture_mode"] is True
    assert checklist.json()["trust_state"] == "official_review_required"
    assert validation.status_code == 200
    assert validation.json()["verdict"] is None
    assert validation.json()["trust_state"] == "official_review_required"


def test_unknown_procedure_and_invalid_body_use_safe_error_envelope(client: TestClient) -> None:
    unknown = client.post(
        "/v1/applications/validate",
        json={"procedure_id": "unknown", "form_data": {}},
    )
    old_contract = client.post(
        "/v1/intake/turn",
        json={
            "session_id": "synthetic-session",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )

    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "procedure_not_found"
    assert unknown.headers["X-Request-ID"]
    assert old_contract.status_code == 422
    assert old_contract.json()["error"]["code"] == "request_validation_failed"


def test_version_conflict_is_explicit(client: TestClient) -> None:
    response = client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist",
        json={"procedure_version": "stale-version"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "procedure_version_conflict"


def test_approved_adapter_enables_deterministic_precheck() -> None:
    settings = Settings(app_env="test", procedure_data_mode="fixture")
    container = build_container(settings)
    container.procedure_repository = ApprovedProcedureRepository(approved_birth_pack())
    container.recommendation_provider = FixtureRecommendationProvider()
    client = TestClient(create_app(settings=settings, container=container))

    invalid = client.post(
        "/v1/applications/validate",
        json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
    )
    valid = client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-khai-sinh",
            "procedure_version": "approved-test-v1",
            "form_data": {"fixture_child_name": "Nguyen An"},
        },
    )

    assert invalid.status_code == 200
    assert invalid.json()["trust_state"] == "verified_guidance"
    assert invalid.json()["verdict"] == "needs_fix"
    assert valid.status_code == 200
    assert valid.json()["verdict"] == "pass_preliminary"
    assert valid.json()["findings"] == []


def test_openapi_exposes_exactly_six_public_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert set(paths) == {
        "/health",
        "/v1/procedures",
        "/v1/procedures/{procedure_id}/checklist",
        "/v1/procedures/recommend",
        "/v1/intake/turn",
        "/v1/applications/validate",
    }


def test_production_rejects_dev_fixture() -> None:
    with pytest.raises(RuntimeError, match="fixture"):
        create_app(Settings(app_env="production", procedure_data_mode="fixture"))


def test_production_disabled_is_degraded_and_never_exposes_fixture_data() -> None:
    settings = Settings(
        app_env="production",
        procedure_data_mode="disabled",
        rag_mode="disabled",
        llm_mode="disabled",
        cors_allowed_origins="",
        rate_limit_enabled=True,
    )
    production_client = TestClient(create_app(settings=settings))

    health = production_client.get("/health")
    catalog = production_client.get("/v1/procedures")
    recommendation = production_client.post(
        "/v1/procedures/recommend", json={"need_text": "Tôi muốn đăng ký khai sinh"}
    )
    intake = production_client.post(
        "/v1/intake/turn",
        json={"session_id": "production-disabled-test", "message": "Tôi muốn đăng ký khai sinh"},
    )
    checklist = production_client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist",
        json={"clarification_answers": {}},
    )
    validation = production_client.post(
        "/v1/applications/validate",
        json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
    )

    assert health.status_code == 200
    assert health.json()["status"] == "degraded"
    assert health.json()["environment"] == "production"
    assert health.json()["capabilities"] == {
        "procedure_data": "disabled",
        "rag": "disabled",
        "llm": "disabled",
    }
    assert catalog.status_code == 200
    assert len(catalog.json()) == 3
    assert all(item["review_status"] == "unavailable" for item in catalog.json())
    assert all(item["fixture_mode"] is False for item in catalog.json())
    assert recommendation.json()["candidates"] == []
    assert recommendation.json()["trust_state"] == "need_more_information"
    assert intake.json()["trust_state"] == "need_more_information"
    assert intake.json()["fixture_mode"] is False
    assert intake.json()["detected_procedure_id"] is None
    assert intake.json()["procedure"] is None
    assert intake.json()["clarifying_questions"] == []
    assert checklist.json()["trust_state"] == "official_review_required"
    assert checklist.json()["fixture_mode"] is False
    assert checklist.json()["required_documents"] == []
    assert checklist.json()["steps"] == []
    assert validation.json()["trust_state"] == "official_review_required"
    assert validation.json()["verdict"] is None


def test_request_limit_and_rate_limit_have_safe_errors(client: TestClient) -> None:
    too_large = client.post("/v1/procedures/recommend", json={"need_text": "a" * 70_000})
    assert too_large.status_code == 422
    assert too_large.json()["error"]["code"] == "request_too_large"

    settings = Settings(
        app_env="test",
        procedure_data_mode="fixture",
        rate_limit_enabled=True,
        rate_limit_requests=1,
    )
    limited_client = TestClient(create_app(settings=settings))
    first = limited_client.post("/v1/procedures/recommend", json={"need_text": "khai sinh"})
    second = limited_client.post("/v1/procedures/recommend", json={"need_text": "khai sinh"})

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "rate_limit_exceeded"
