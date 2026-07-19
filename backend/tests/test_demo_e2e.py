from __future__ import annotations

from fastapi.testclient import TestClient

from app.adapters.demo_pack import load_demo_packs
from app.config import Settings
from app.dependencies import build_container
from app.main import create_app


class FakeExplanationProvider:
    async def is_available(self) -> bool:
        return True

    async def explain_findings(self, session_id, form_data, findings):
        assert session_id.startswith("validate-")
        return {finding.rule_id: f"Demo explanation for {finding.rule_id}" for finding in findings}


def _settings() -> Settings:
    return Settings(
        app_env="test",
        procedure_data_mode="demo_pack",
        rag_mode="disabled",
        llm_mode="disabled",
        ai_api_key="",
        openai_api_key="",
    )


def _answers_for(procedure_id: str) -> dict[str, str]:
    pack = load_demo_packs()[procedure_id]
    return {
        question.id: question.options[0] if question.options else "Thông tin demo"
        for question in pack.intake_questions
    }


def test_all_three_demo_packs_complete_structured_flow_without_verified_guidance() -> None:
    client = TestClient(create_app(_settings()))

    for procedure_id, pack in load_demo_packs().items():
        intake = client.post(
            "/v1/intake/turn",
            json={
                "session_id": f"demo-{procedure_id}",
                "message": pack.aliases[0],
                "session_context": {},
            },
        )
        assert intake.status_code == 200
        assert intake.json()["detected_procedure_id"] == procedure_id
        assert intake.json()["demo_mode"] is True
        assert intake.json()["trust_state"] != "verified_guidance"
        assert intake.json()["last_verified_at"] is None

        checklist = client.post(
            f"/v1/procedures/{procedure_id}/checklist",
            json={"clarification_answers": _answers_for(procedure_id)},
        )
        assert checklist.status_code == 200
        assert checklist.json()["required_documents"]
        assert checklist.json()["form_schema"]["properties"]
        assert checklist.json()["demo_mode"] is True
        assert checklist.json()["trust_state"] == "official_review_required"
        assert checklist.json()["last_verified_at"] is None

        validation = client.post(
            "/v1/applications/validate",
            json={"procedure_id": procedure_id, "form_data": {}},
        )
        assert validation.status_code == 200
        assert validation.json()["verdict"] == "needs_fix"
        assert validation.json()["findings"]
        assert validation.json()["demo_mode"] is True
        assert validation.json()["trust_state"] == "official_review_required"
        assert validation.json()["last_verified_at"] is None


def test_llm_kill_switch_changes_only_explanations_not_rules_or_verdict() -> None:
    settings = _settings()
    disabled_container = build_container(settings)
    disabled_client = TestClient(create_app(settings=settings, container=disabled_container))

    enabled_container = build_container(settings)
    enabled_container.llm_provider = FakeExplanationProvider()
    enabled_client = TestClient(create_app(settings=settings, container=enabled_container))
    payload = {"procedure_id": "dang-ky-khai-sinh", "form_data": {}}

    disabled = disabled_client.post("/v1/applications/validate", json=payload).json()
    enabled = enabled_client.post("/v1/applications/validate", json=payload).json()

    assert disabled["explanations"] == {}
    assert enabled["explanations"]
    assert disabled["verdict"] == enabled["verdict"] == "needs_fix"
    assert disabled["findings"] == enabled["findings"]
    assert disabled["trust_state"] == enabled["trust_state"] == "official_review_required"
    assert disabled["demo_mode"] is enabled["demo_mode"] is True


def test_demo_health_reports_llm_kill_switch_offline() -> None:
    response = TestClient(create_app(_settings())).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["capabilities"]["llm"] == "disabled"
    assert response.json()["capabilities"]["llm_ready"] == "false"
