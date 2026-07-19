from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import build_container
from app.main import create_app


class RecordingAuditSink:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, str | int | float | bool | None]]] = []

    async def emit(
        self,
        event: str,
        fields: dict[str, str | int | float | bool | None],
    ) -> None:
        self.events.append((event, fields))


def feedback_payload() -> dict:
    return {
        "context": "precheck",
        "session_id": "session-private-123",
        "procedure_id": "dang-ky-khai-sinh",
        "procedure_version": "2026-demo-v1",
        "trust_state": "official_review_required",
        "verdict": "needs_fix",
        "vote": "down",
        "reason": "kho_hieu",
        "note": "Nội dung tự do không được đưa vào audit.",
        "created_at": "2026-07-19T10:00:00+07:00",
    }


def test_feedback_accepts_request_and_audits_metadata_only() -> None:
    settings = Settings(app_env="test", procedure_data_mode="demo_pack")
    container = build_container(settings)
    audit_sink = RecordingAuditSink()
    container.audit_sink = audit_sink
    client = TestClient(create_app(settings=settings, container=container))

    response = client.post("/v1/feedback", json=feedback_payload())

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    event, fields = audit_sink.events[0]
    assert event == "feedback_received"
    assert fields["has_note"] is True
    assert "session_id" not in fields
    assert "note" not in fields
    assert "private" not in repr(fields)


def test_feedback_rejects_unknown_fields_and_oversized_notes() -> None:
    client = TestClient(create_app(Settings(app_env="test", procedure_data_mode="demo_pack")))
    unknown = client.post(
        "/v1/feedback",
        json={**feedback_payload(), "unexpected": "value"},
    )
    oversized = client.post(
        "/v1/feedback",
        json={**feedback_payload(), "note": "x" * 201},
    )

    assert unknown.status_code == 422
    assert oversized.status_code == 422
