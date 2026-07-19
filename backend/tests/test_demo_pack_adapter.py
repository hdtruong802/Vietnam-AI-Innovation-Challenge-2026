from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.adapters.demo_pack import load_demo_packs
from app.config import Settings
from app.main import create_app
from app.models.procedure import ReviewStatus, ValidationRuleType

MVP_IDS = {"dang-ky-khai-sinh", "dang-ky-thuong-tru", "dang-ky-ho-kinh-doanh"}

KHAI_SINH_ANSWERS = {
    "q_hinh_thuc_nop": "Trực tiếp tại Trung tâm Phục vụ hành chính công",
    "q_ket_hon": "Đã đăng ký kết hôn",
    "q_nguoi_dang_ky": "Cha hoặc mẹ của trẻ",
}


@pytest.fixture
def client() -> TestClient:
    settings = Settings(app_env="test", procedure_data_mode="demo_pack")
    return TestClient(create_app(settings=settings))


def test_all_three_demo_packs_load_demo_approved_with_watermark() -> None:
    packs = load_demo_packs()

    assert set(packs) == MVP_IDS
    for pack in packs.values():
        assert pack.review_status == ReviewStatus.DEMO_APPROVED
        assert pack.demo_pack is True
        assert pack.checksum
        assert pack.last_verified_at is None
        assert pack.source_refs
        assert pack.intake_questions
        assert len(pack.required_documents) >= 1
        assert len(pack.required_documents) + len(pack.optional_documents) >= 3
        assert len(pack.steps) >= 3
        assert len(pack.form_schema["properties"]) >= 6
        assert len(pack.validation_rules) >= 8


def test_every_rule_type_is_exercised_in_every_pack() -> None:
    for pack in load_demo_packs().values():
        used_types = {rule.type for rule in pack.validation_rules}
        assert used_types == set(
            ValidationRuleType
        ), f"{pack.procedure_id} thiếu rule type: {set(ValidationRuleType) - used_types}"


def test_citation_coverage_is_complete() -> None:
    for pack in load_demo_packs().values():
        known_refs = {citation.ref_id for citation in pack.source_refs}
        for item in [*pack.required_documents, *pack.optional_documents]:
            assert item.source_ref_ids, f"{pack.procedure_id}/{item.id} thiếu citation"
            assert set(item.source_ref_ids) <= known_refs
        for rule in pack.validation_rules:
            assert rule.source_ref_ids, f"{pack.procedure_id}/{rule.rule_id} thiếu citation"
            assert set(rule.source_ref_ids) <= known_refs


def test_procedures_list_carries_demo_mode(client: TestClient) -> None:
    response = client.get("/v1/procedures")

    assert response.status_code == 200
    assert {item["procedure_id"] for item in response.json()} == MVP_IDS
    assert all(item["demo_mode"] is True for item in response.json())
    assert all(item["review_status"] == "demo_approved" for item in response.json())


def test_health_reports_degraded_demo_guidance(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["capabilities"]["procedure_data"] == "demo_pack"
    assert response.json()["status"] == "degraded"
    assert response.json()["capabilities"]["procedure_guidance"] == "demo_approved"


def test_recommend_supports_accented_vietnamese(client: TestClient) -> None:
    response = client.post(
        "/v1/procedures/recommend",
        json={"need_text": "Vợ tôi mới sinh, tôi muốn làm giấy khai sinh cho con"},
    )

    assert response.status_code == 200
    assert response.json()["candidates"][0]["procedure_id"] == "dang-ky-khai-sinh"
    assert response.json()["demo_mode"] is True
    assert response.json()["fixture_mode"] is False


def test_checklist_is_demo_only_after_clarifications(
    client: TestClient,
) -> None:
    response = client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist",
        json={"clarification_answers": KHAI_SINH_ANSWERS},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["trust_state"] == "official_review_required"
    assert body["demo_mode"] is True
    assert body["fixture_mode"] is False
    assert body["last_verified_at"] is None
    assert body["procedure_card"]["authority"]
    assert len(body["required_documents"]) >= 3
    assert body["form_schema"]["properties"]
    assert body["source_refs"]


def test_checklist_needs_more_information_without_answers(client: TestClient) -> None:
    response = client.post(
        "/v1/procedures/dang-ky-khai-sinh/checklist",
        json={"clarification_answers": {}},
    )

    assert response.status_code == 200
    assert response.json()["trust_state"] == "need_more_information"


def test_precheck_flags_errors_and_passes_after_fix(client: TestClient) -> None:
    bad = client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-khai-sinh",
            "form_data": {
                "ho_ten_tre": "Nguyễn Thị Demo",
                "ngay_sinh_tre": "2099-01-01",
                "noi_sinh": "Bệnh viện demo",
                "ho_ten_me": "Trần Thị Mẹ Demo",
                "cccd_me": "12345",
                "co_thong_tin_cha": True,
                "ngay_dang_ky": "2026-07-01",
            },
        },
    )
    good = client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-khai-sinh",
            "form_data": {
                "ho_ten_tre": "Nguyễn Thị Demo",
                "ngay_sinh_tre": "2026-06-01",
                "noi_sinh": "Bệnh viện demo",
                "ho_ten_me": "Trần Thị Mẹ Demo",
                "cccd_me": "012345678901",
                "co_thong_tin_cha": True,
                "ho_ten_cha": "Nguyễn Văn Cha Demo",
                "cccd_cha": "012345678902",
                "ngay_dang_ky": "2026-07-01",
            },
        },
    )

    assert bad.status_code == 200
    assert bad.json()["trust_state"] == "official_review_required"
    assert bad.json()["demo_mode"] is True
    assert bad.json()["verdict"] == "needs_fix"
    flagged_rules = {finding["rule_id"] for finding in bad.json()["findings"]}
    assert "KS-FMT-02" in flagged_rules  # ngày sinh tương lai
    assert "KS-PAT-01" in flagged_rules  # CCCD mẹ sai định dạng
    assert "KS-CON-01" in flagged_rules  # thiếu họ tên cha khi đã xác nhận có
    assert "KS-CMP-01" in flagged_rules  # ngày đăng ký trước ngày sinh
    assert all(finding["fix_hint"] for finding in bad.json()["findings"])

    assert good.status_code == 200
    assert good.json()["verdict"] == "pass_preliminary"
    assert good.json()["findings"] == []


def test_cross_field_and_conditional_rules_for_other_packs(client: TestClient) -> None:
    thuong_tru = client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-thuong-tru",
            "form_data": {
                "ho_ten": "Lê Văn Demo",
                "so_dinh_danh": "012345678903",
                "dia_chi_thuong_tru_moi": "Số 1 đường Demo, phường Demo",
                "hinh_thuc_cho_o": "Về ở với người thân (chủ hộ đồng ý)",
            },
        },
    )
    ho_kinh_doanh = client.post(
        "/v1/applications/validate",
        json={
            "procedure_id": "dang-ky-ho-kinh-doanh",
            "form_data": {
                "ten_ho_kinh_doanh": "Quán ăn Demo",
                "chu_the_dang_ky": "Các thành viên hộ gia đình",
                "ho_ten_chu_ho": "Phạm Văn Chủ Demo",
                "cccd_chu_ho": "012345678904",
                "dia_chi_tru_so": "Số 2 đường Demo",
                "nganh_nghe": "Dịch vụ ăn uống",
                "von_kinh_doanh": "năm mươi triệu",
            },
        },
    )

    tt_rules = {finding["rule_id"] for finding in thuong_tru.json()["findings"]}
    assert thuong_tru.json()["verdict"] == "needs_fix"
    assert {"TT-CON-01", "TT-CON-02"} <= tt_rules

    hkd_rules = {finding["rule_id"] for finding in ho_kinh_doanh.json()["findings"]}
    assert ho_kinh_doanh.json()["verdict"] == "needs_fix"
    assert "HKD-CON-01" in hkd_rules
    assert "HKD-TYP-01" in hkd_rules


def test_production_explicit_demo_pack_mode_stays_degraded() -> None:
    settings = Settings(
        app_env="production",
        procedure_data_mode="demo_pack",
        cors_allowed_origins="",
    )
    production_client = TestClient(create_app(settings=settings))

    health = production_client.get("/health")
    catalog = production_client.get("/v1/procedures")

    assert health.status_code == 200
    assert health.json()["status"] == "degraded"
    assert health.json()["capabilities"]["procedure_guidance"] == "demo_approved"
    assert catalog.status_code == 200
    assert len(catalog.json()) == 3


def test_demo_mode_never_emits_verified_guidance(client: TestClient) -> None:
    responses = [
        client.post(
            "/v1/procedures/recommend",
            json={"need_text": "Tôi muốn đăng ký khai sinh"},
        ),
        client.post(
            "/v1/intake/turn",
            json={
                "session_id": "demo-false-verified-gate",
                "message": "Tôi muốn đăng ký khai sinh",
            },
        ),
        client.post(
            "/v1/procedures/dang-ky-khai-sinh/checklist",
            json={"clarification_answers": KHAI_SINH_ANSWERS},
        ),
        client.post(
            "/v1/applications/validate",
            json={"procedure_id": "dang-ky-khai-sinh", "form_data": {}},
        ),
    ]

    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["demo_mode"] is True for response in responses)
    assert all(response.json()["trust_state"] != "verified_guidance" for response in responses)


def test_openapi_route_set_includes_feedback(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert set(paths) == {
        "/",
        "/health",
        "/v1/feedback",
        "/v1/applications/prefill",
        "/v1/applications/validate",
        "/v1/intake/turn",
        "/v1/procedures",
        "/v1/procedures/{procedure_id}/checklist",
        "/v1/procedures/recommend",
    }
