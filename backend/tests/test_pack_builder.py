"""Unit test cho app/services/rag/pack_builder.py (xem D-019 trong DECISIONS.md).

Khong can data/Data_DVC: chi kiem tra ham deterministic tren form_schema/
settings gia lap, tach biet voi test_rag_adapter.py (can source thuc).
"""

from __future__ import annotations

from datetime import date

from app.config import get_settings
from app.models.procedure import ReviewStatus, ValidationRuleType
from app.services.rag.pack_builder import _demo_k1_status, _required_field_rules

_SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "ho_ten": {"type": "string", "title": "Họ và tên"},
        "so_cccd": {
            "type": "string",
            "title": "Số CCCD",
            "pattern": r"^[0-9]{12}$",
        },
        "ngay_sinh": {"type": "string", "title": "Ngày sinh", "format": "date"},
    },
    "required": ["ho_ten", "so_cccd"],
}


def test_required_field_rules_keeps_req_ordering_and_rule_id_format():
    rules = _required_field_rules("dang-ky-thu-nghiem", _SAMPLE_SCHEMA, "SRC-1")

    required_rules = [r for r in rules if r.type == ValidationRuleType.REQUIRED]
    assert [r.rule_id for r in required_rules] == [
        "DANG-KY-THU-NGHIEM-REQ-1",
        "DANG-KY-THU-NGHIEM-REQ-2",
    ]
    assert [r.field_id for r in required_rules] == ["ho_ten", "so_cccd"]
    assert all(r.source_ref_ids == ["SRC-1"] for r in required_rules)


def test_required_field_rules_adds_string_pattern_rule():
    rules = _required_field_rules("dang-ky-thu-nghiem", _SAMPLE_SCHEMA, "SRC-1")

    pattern_rules = [r for r in rules if r.type == ValidationRuleType.STRING_PATTERN]
    assert len(pattern_rules) == 1
    assert pattern_rules[0].field_id == "so_cccd"
    assert pattern_rules[0].params.get("pattern") == r"^[0-9]{12}$"


def test_required_field_rules_adds_date_format_rule():
    rules = _required_field_rules("dang-ky-thu-nghiem", _SAMPLE_SCHEMA, "SRC-1")

    date_rules = [r for r in rules if r.type == ValidationRuleType.DATE_FORMAT]
    assert len(date_rules) == 1
    assert date_rules[0].field_id == "ngay_sinh"


def test_demo_k1_status_defaults_to_needs_review(monkeypatch):
    """Mac dinh (flag False) phai giu dung fail-closed cua D-013."""
    original = get_settings()
    monkeypatch.setattr(
        "app.services.rag.pack_builder.get_settings",
        lambda: original.model_copy(update={"rag_demo_k1_approved": False}),
    )

    review_status, last_verified_at, version = _demo_k1_status(
        "candidate-2026-07-17", "demo-k1-simulated-2026-07-17"
    )

    assert review_status == ReviewStatus.NEEDS_REVIEW
    assert last_verified_at is None
    assert version == "candidate-2026-07-17"


def test_demo_k1_status_returns_approved_when_flag_enabled(monkeypatch):
    """Xem D-019: flag chi danh cho demo cuc bo, version phai co marker ro
    de khong nham voi K1 nguoi thuc da duyet."""
    original = get_settings()
    monkeypatch.setattr(
        "app.services.rag.pack_builder.get_settings",
        lambda: original.model_copy(update={"rag_demo_k1_approved": True}),
    )

    review_status, last_verified_at, version = _demo_k1_status(
        "candidate-2026-07-17", "demo-k1-simulated-2026-07-17"
    )

    assert review_status == ReviewStatus.APPROVED
    assert last_verified_at == date.fromisoformat(get_settings().rag_source_freeze_date)
    assert version == "demo-k1-simulated-2026-07-17"
