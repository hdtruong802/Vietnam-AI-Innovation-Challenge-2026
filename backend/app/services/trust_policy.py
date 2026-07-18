from __future__ import annotations

from datetime import date

from app.models.common import RegulatoryResponse, ReviewGate, TrustMetadata, TrustState
from app.models.procedure import ProcedurePack, ReviewStatus


class TrustPolicy:
    def metadata_for(
        self,
        pack: ProcedurePack | None,
        review_gate: ReviewGate | None,
        requested_state: TrustState = TrustState.VERIFIED_GUIDANCE,
    ) -> TrustMetadata:
        if pack is None:
            return TrustMetadata(
                trust_state=TrustState.OFFICIAL_REVIEW_REQUIRED,
                review_gate=review_gate,
            )

        is_current = (pack.effective_from is None or pack.effective_from <= date.today()) and (
            pack.effective_to is None or pack.effective_to >= date.today()
        )
        can_verify = (
            pack.review_status == ReviewStatus.APPROVED
            and bool(pack.source_refs)
            and bool(pack.last_verified_at)
            and bool(pack.checksum)
            and is_current
        )
        trust_state = requested_state if can_verify else TrustState.OFFICIAL_REVIEW_REQUIRED

        return TrustMetadata(
            trust_state=trust_state,
            procedure_version=pack.version,
            source_refs=pack.source_refs,
            last_verified_at=pack.last_verified_at,
            review_gate=review_gate,
            fixture_mode=pack.review_status == ReviewStatus.FIXTURE,
        )

    def needs_more_information(self, review_gate: ReviewGate | None = None) -> TrustMetadata:
        return TrustMetadata(
            trust_state=TrustState.NEED_MORE_INFORMATION,
            review_gate=review_gate,
        )

    @staticmethod
    def is_verified(response: RegulatoryResponse) -> bool:
        return response.trust_state == TrustState.VERIFIED_GUIDANCE
