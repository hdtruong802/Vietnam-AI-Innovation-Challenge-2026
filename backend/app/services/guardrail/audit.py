"""Redacted audit log toi gian (xem 'LOG' trong docs/diagram_v3.mmd).

Chi luu ban da redact trong memory (vong doi process) + ghi qua logging
stdlib. Khong luu gia tri PII goc, khong luu token map. Day la advisory
log cho demo/hackathon, khong phai audit store lau dai.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.services.guardrail.pii_guard import PIIGuard

logger = logging.getLogger("vngov.audit")


@dataclass
class AuditEvent:
    event_type: str
    metadata: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class RedactedAudit:
    _events: List[AuditEvent] = []
    _max_events = 500

    @classmethod
    def log_event(cls, event_type: str, metadata: Dict[str, Any]) -> AuditEvent:
        redacted_metadata = {
            key: (PIIGuard.redact_free_text(value) if isinstance(value, str) else value)
            for key, value in metadata.items()
        }
        event = AuditEvent(event_type=event_type, metadata=redacted_metadata)
        cls._events.append(event)
        if len(cls._events) > cls._max_events:
            cls._events.pop(0)
        logger.info("audit_event type=%s metadata=%s", event_type, redacted_metadata)
        return event

    @classmethod
    def recent_events(cls, limit: int = 50) -> List[AuditEvent]:
        return cls._events[-limit:]

    @classmethod
    def clear(cls) -> None:
        """Chi dung trong test de tranh leak state giua cac test case."""
        cls._events = []
