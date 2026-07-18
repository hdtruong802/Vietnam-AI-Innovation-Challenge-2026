"""Session-scoped PII Guard (xem docs/proposal.md muc 5, 6 va D-006).

Tokenize truc tiep direct identifier truoc khi payload roi khoi trusted
boundary (vd. truoc khi goi LLM Gateway ben ngoai). Token map CHI ton tai
in-memory theo session, co TTL, KHONG duoc ghi vao log/DB/vector/CaseSnapshot
(xem "Memory va resume" trong proposal).

Thiet ke: tokenize theo TEN TRUONG (field-level) cho du lieu form co cau
truc — day la cach an toan va xac dinh (deterministic) hon regex tren free
text, va giu nguyen cac truong khong dinh danh (ngay sinh, dien tich, loai
hinh...) de rule engine / LLM van kiem tra logic/conflict duoc.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from app.config import PII_TOKEN_TTL_SECONDS

_FIELD_TYPE_PATTERNS = [
    (re.compile(r"(ho_?ten|ten_)", re.IGNORECASE), "NAME"),
    (re.compile(r"(cccd|cmnd|ho_?chieu|so_?can_?cuoc)", re.IGNORECASE), "ID"),
    (re.compile(r"(dien_?thoai|sdt|phone)", re.IGNORECASE), "PHONE"),
    (re.compile(r"(dia_?chi|address)", re.IGNORECASE), "ADDR"),
    (re.compile(r"(email)", re.IGNORECASE), "EMAIL"),
]

_FREE_TEXT_PATTERNS = [
    (re.compile(r"\b0\d{9,10}\b"), "[PHONE_REDACTED]"),
    (re.compile(r"\b\d{9}\b|\b\d{12}\b"), "[ID_REDACTED]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL_REDACTED]"),
]


def _field_type(field_name: str) -> str | None:
    for pattern, type_name in _FIELD_TYPE_PATTERNS:
        if pattern.search(field_name):
            return type_name
    return None


@dataclass
class _SessionTokenMap:
    tokens: Dict[str, Any] = field(default_factory=dict)
    expires_at: float = 0.0


class PIIGuard:
    """In-memory, session-scoped. Khong co persistence layer nao duoc dung."""

    _sessions: Dict[str, _SessionTokenMap] = {}

    @classmethod
    def _purge_expired(cls) -> None:
        now = time.monotonic()
        expired = [sid for sid, m in cls._sessions.items() if m.expires_at < now]
        for sid in expired:
            cls._sessions.pop(sid, None)

    @classmethod
    def _get_or_create_session(cls, session_id: str) -> _SessionTokenMap:
        cls._purge_expired()
        session = cls._sessions.get(session_id)
        if session is None:
            session = _SessionTokenMap()
            cls._sessions[session_id] = session
        session.expires_at = time.monotonic() + PII_TOKEN_TTL_SECONDS
        return session

    @classmethod
    def tokenize_fields(cls, session_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Tra ve (payload_da_tokenize, so_field_da_tokenize). Token map luu
        noi bo trong session, khong tra ve cho caller de tranh vo tinh log ra.
        """

        session = cls._get_or_create_session(session_id)
        tokenized: Dict[str, Any] = {}
        count = 0
        # Salt ngan tu session_id de token khong the vo tinh trung giua hai
        # session khac nhau (tranh detokenize sai session neu code goi nham).
        salt = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:6]
        prefix = f"{{{{PII_"

        for key, value in data.items():
            type_name = _field_type(key)
            if type_name is None or value in (None, ""):
                tokenized[key] = value
                continue
            count += 1
            token_index = sum(1 for t in session.tokens if t.startswith(f"{prefix}{type_name}_{salt}_")) + 1
            token = f"{{{{PII_{type_name}_{salt}_{token_index}}}}}"
            session.tokens[token] = value
            tokenized[key] = token

        return tokenized, count

    @classmethod
    def detokenize_fields(cls, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        session = cls._sessions.get(session_id)
        if session is None:
            return data
        restored: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str) and value in session.tokens:
                restored[key] = session.tokens[value]
            else:
                restored[key] = value
        return restored

    @classmethod
    def detokenize_text(cls, session_id: str, text: str) -> str:
        session = cls._sessions.get(session_id)
        if session is None or not text:
            return text
        for token, real_value in session.tokens.items():
            text = text.replace(token, str(real_value))
        return text

    @classmethod
    def clear_session(cls, session_id: str) -> None:
        cls._sessions.pop(session_id, None)

    @staticmethod
    def redact_free_text(text: str) -> str:
        """Best-effort regex mask cho free text truoc khi ghi log (khong bat
        buoc tokenize truoc khi gui LLM cho free text — xem Note trong
        docs/diagram_v3.mmd, day la stretch goal ngoai pham vi bat buoc).
        """

        redacted = text
        for pattern, replacement in _FREE_TEXT_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted
