import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.config as config

client = TestClient(app)


def _has_source_data() -> bool:
    return config.RAG_SOURCE_DIR.exists() and any(config.RAG_SOURCE_DIR.glob("*.txt"))


requires_source_data = pytest.mark.skipif(
    not _has_source_data(), reason="data/Data_DVC khong ton tai trong moi truong nay"
)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_intake_turn_asks_for_procedure_when_unclear():
    response = client.post(
        "/v1/intake/turn",
        json={"session_id": "s1", "messages": [{"role": "user", "content": "xin chào"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["detected_procedure_id"] is None
    assert body["trust_state"] == "need_more_information"
    assert "procedure_selection" in body["required_clarifications"]


@requires_source_data
def test_intake_turn_detects_khai_sinh_and_returns_citations():
    response = client.post(
        "/v1/intake/turn",
        json={
            "session_id": "s2",
            "messages": [{"role": "user", "content": "tôi muốn làm khai sinh cho con"}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["detected_procedure_id"] == "dang-ky-khai-sinh"
    assert body["trust_state"] in {"need_more_information", "verified_guidance"}


@requires_source_data
def test_checklist_endpoint_returns_grounded_sources():
    response = client.post("/v1/procedures/dang-ky-thuong-tru/checklist", json={"procedure_id": "dang-ky-thuong-tru"})
    assert response.status_code == 200
    body = response.json()
    assert body["procedure_id"] == "dang-ky-thuong-tru"
    assert len(body["sources"]) > 0
    assert len(body["required_documents"]) > 0


def test_validate_application_keeps_deterministic_verdict():
    response = client.post(
        "/v1/applications/validate",
        json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_valid"] is False
    assert any(f["rule_id"] == "R-BIRTH-001" for f in body["findings"])
