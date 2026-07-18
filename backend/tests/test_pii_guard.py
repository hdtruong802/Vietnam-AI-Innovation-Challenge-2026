from app.services.guardrail.pii_guard import PIIGuard


def test_tokenize_direct_identifiers_only():
    session_id = "test-session-1"
    form_data = {
        "ho_ten_tre": "Nguyễn Văn A",
        "so_cccd": "079123456789",
        "so_dien_thoai": "0912345678",
        "ngay_sinh_tre": "2024-01-01",
        "dien_tich": "50m2",
    }

    tokenized, count = PIIGuard.tokenize_fields(session_id, form_data)

    assert count == 3
    assert tokenized["ho_ten_tre"].startswith("{{PII_NAME_")
    assert tokenized["so_cccd"].startswith("{{PII_ID_")
    assert tokenized["so_dien_thoai"].startswith("{{PII_PHONE_")
    # Truong khong dinh danh phai giu nguyen de AI van check logic duoc.
    assert tokenized["ngay_sinh_tre"] == "2024-01-01"
    assert tokenized["dien_tich"] == "50m2"

    PIIGuard.clear_session(session_id)


def test_detokenize_restores_original_values():
    session_id = "test-session-2"
    form_data = {"ho_ten_cha": "Trần Văn B"}

    tokenized, _ = PIIGuard.tokenize_fields(session_id, form_data)
    restored = PIIGuard.detokenize_fields(session_id, tokenized)

    assert restored["ho_ten_cha"] == "Trần Văn B"

    PIIGuard.clear_session(session_id)


def test_detokenize_text_replaces_tokens_in_free_text():
    session_id = "test-session-3"
    form_data = {"ho_ten_nguoi_khai": "Lê Thị C"}
    tokenized, _ = PIIGuard.tokenize_fields(session_id, form_data)
    token = tokenized["ho_ten_nguoi_khai"]

    text_with_token = f"Người khai {token} cần bổ sung giấy tờ."
    restored_text = PIIGuard.detokenize_text(session_id, text_with_token)

    assert "Lê Thị C" in restored_text
    assert token not in restored_text

    PIIGuard.clear_session(session_id)


def test_sessions_are_isolated():
    PIIGuard.tokenize_fields("session-a", {"ho_ten_tre": "A"})
    tokenized_b, _ = PIIGuard.tokenize_fields("session-b", {"ho_ten_tre": "B"})

    # Token cua session-b khong duoc detokenize duoc boi session-a.
    restored_wrong_session = PIIGuard.detokenize_fields("session-a", tokenized_b)
    assert restored_wrong_session["ho_ten_tre"] == tokenized_b["ho_ten_tre"]

    PIIGuard.clear_session("session-a")
    PIIGuard.clear_session("session-b")


def test_redact_free_text_masks_phone_and_email():
    text = "Liên hệ 0912345678 hoặc email a@b.com để biết thêm."
    redacted = PIIGuard.redact_free_text(text)

    assert "0912345678" not in redacted
    assert "a@b.com" not in redacted
    assert "[PHONE_REDACTED]" in redacted
    assert "[EMAIL_REDACTED]" in redacted
