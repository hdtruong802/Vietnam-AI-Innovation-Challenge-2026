# Phase 6.1 - Intent Router Remediation

- Task Record: `local-20260719-phase6-1-intent-router`
- Base: `cao@e84e4bb`
- Decision: D-025
- Runtime: deterministic guard and demo-pack alias scorer; no LLM, retrieval, network or new dependency

## Result

| Metric | Phase 6 baseline | Phase 6.1 | Gate |
| --- | ---: | ---: | ---: |
| Routing accuracy | 48/60 (0.80) | 60/60 (1.00) | 1.00 |
| False routes | 4 | 0 | 0 |
| Missed routes | 8 | 0 | 0 |
| Wrong cross-procedure routes | 0 | 0 | 0 |
| Fail-closed trust errors | 15 | 0 | 0 |
| False verified surfaces | 0 | 0 | 0 |
| Demo-mode errors | 0 | 0 | 0 |
| HTTP errors | 0 | 0 | 0 |

## Implementation

1. A deterministic guard handles greeting, explicit out-of-scope requests and unsupported near-intents before recommendation, without calling retrieval or LLM.
2. Greeting and unclear requests remain conversational with `need_more_information`; out-of-scope and unsupported near-intents return `official_review_required`.
3. Demo routing uses phrase-boundary exact matching first, followed by standard-library similarity for multi-word aliases only.
4. Fuzzy selection requires both a minimum score and a margin over the second candidate. Single-word aliases are never fuzzy matched.
5. TrustPolicy, pack content, checklist, validation rules and the public API schema are unchanged.

## Verification

```powershell
python scripts/evaluation/evaluate_demo_golden.py
python -m pytest backend/tests/test_intent_router.py tests/evaluation/test_demo_golden.py -q
```

The frozen 60-case corpus now passes the full release gate. Unit coverage also verifies that guarded intents short-circuit the recommendation provider and that document words such as `căn cước` do not incorrectly block a supported birth-registration query.
