"""Trust / Response Policy (xem docs/proposal.md muc 1, 6).

Day la noi duy nhat quyet dinh 1 trong 3 trust state. Fail-closed: khi
thieu evidence hoac mau thuan, khong bao gio tra "verified_guidance".
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from app.services.rag.schemas import RetrievalEvidence

VERIFIED_GUIDANCE = "verified_guidance"
NEED_MORE_INFORMATION = "need_more_information"
OFFICIAL_REVIEW_REQUIRED = "official_review_required"

_VALID_STATES = {VERIFIED_GUIDANCE, NEED_MORE_INFORMATION, OFFICIAL_REVIEW_REQUIRED}


class TrustPolicy:
    @staticmethod
    def decide(
        evidence: Optional[RetrievalEvidence],
        out_of_scope: bool = False,
        needs_clarification: bool = False,
    ) -> str:
        if out_of_scope:
            return OFFICIAL_REVIEW_REQUIRED
        if evidence is not None and evidence.conflict:
            return OFFICIAL_REVIEW_REQUIRED
        if evidence is None or not evidence.is_grounded:
            # Chua co evidence grounded: neu he thong con dang hoi lam ro (vd
            # chua xac dinh duoc thu tuc) thi khong fail-closed ngay, chi
            # fail-closed khi da het co hoi lam ro ma van khong co evidence.
            return NEED_MORE_INFORMATION if needs_clarification else OFFICIAL_REVIEW_REQUIRED
        if needs_clarification:
            return NEED_MORE_INFORMATION
        return VERIFIED_GUIDANCE

    @staticmethod
    def enforce_citations(trust_state: str, citations: Iterable) -> str:
        """Fail-closed guard: khong duoc cong bo `verified_guidance` cho
        huong dan quy pham neu thieu citation (xem 'Citation coverage 100%'
        trong docs/proposal.md muc 7).
        """

        citations_list: List = list(citations)
        if trust_state == VERIFIED_GUIDANCE and not citations_list:
            return OFFICIAL_REVIEW_REQUIRED
        return trust_state

    @staticmethod
    def is_valid_state(trust_state: str) -> bool:
        return trust_state in _VALID_STATES
