from app.services.guardrail.trust_policy import (
    NEED_MORE_INFORMATION,
    OFFICIAL_REVIEW_REQUIRED,
    VERIFIED_GUIDANCE,
    TrustPolicy,
)
from app.services.rag.schemas import RetrievalEvidence


def _grounded_evidence(with_citations=True):
    return RetrievalEvidence(
        procedure_id="dang-ky-khai-sinh",
        chunks=[],
        citations=[{"title": "t", "url": "u", "ref_code": "r"}] if with_citations else [],
        confidence=0.5,
        is_grounded=True,
        conflict=False,
    )


def test_out_of_scope_is_always_official_review_required():
    assert TrustPolicy.decide(_grounded_evidence(), out_of_scope=True) == OFFICIAL_REVIEW_REQUIRED


def test_no_evidence_but_still_clarifying_is_need_more_information():
    assert TrustPolicy.decide(None, needs_clarification=True) == NEED_MORE_INFORMATION


def test_no_evidence_and_no_more_clarification_fails_closed():
    assert TrustPolicy.decide(None, needs_clarification=False) == OFFICIAL_REVIEW_REQUIRED


def test_conflicting_evidence_fails_closed():
    evidence = _grounded_evidence()
    evidence.conflict = True
    assert TrustPolicy.decide(evidence) == OFFICIAL_REVIEW_REQUIRED


def test_grounded_evidence_without_pending_questions_is_verified():
    assert TrustPolicy.decide(_grounded_evidence(), needs_clarification=False) == VERIFIED_GUIDANCE


def test_grounded_evidence_with_pending_questions_is_need_more_information():
    assert TrustPolicy.decide(_grounded_evidence(), needs_clarification=True) == NEED_MORE_INFORMATION


def test_enforce_citations_downgrades_verified_without_citations():
    result = TrustPolicy.enforce_citations(VERIFIED_GUIDANCE, [])
    assert result == OFFICIAL_REVIEW_REQUIRED


def test_enforce_citations_keeps_verified_with_citations():
    result = TrustPolicy.enforce_citations(VERIFIED_GUIDANCE, [{"ref_code": "r"}])
    assert result == VERIFIED_GUIDANCE
