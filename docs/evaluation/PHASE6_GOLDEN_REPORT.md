# Phase 6 - Demo Golden Evaluation

- Task Record: `local-20260719-phase6-golden-eval`
- Base: `cao@f01f8f3`
- Runtime: FastAPI `TestClient`, `procedure_data_mode=demo_pack`, RAG/LLM/legacy RAG disabled
- Corpus: 60 synthetic, non-PII queries; 20 cases per MVP procedure suite
- Gate: routing accuracy `1.0`, `false_verified == 0`, no fail-closed/demo-mode/HTTP errors

## Result

The safety gate passed, but the complete Phase 6 release gate failed.

| Metric | Result | Target | Status |
| --- | ---: | ---: | --- |
| Cases | 60 | 60 | Pass |
| Routing accuracy | 0.8000 (48/60) | 1.0000 | Fail |
| False routes | 4 | 0 | Fail |
| Missed routes | 8 | 0 | Fail |
| Wrong cross-procedure routes | 0 | 0 | Pass |
| False verified surfaces | 0 | 0 | Pass |
| Demo-mode errors on correctly routed flows | 0 | 0 | Pass |
| HTTP errors | 0 | 0 | Pass |
| Fail-closed trust-state errors | 15 | 0 | Fail |

## Coverage

| Suite | Correct / total | Accuracy |
| --- | ---: | ---: |
| Birth registration | 15 / 20 | 0.75 |
| Permanent residence registration | 17 / 20 | 0.85 |
| Household business registration | 16 / 20 | 0.80 |

| Category | Correct / total | Accuracy |
| --- | ---: | ---: |
| Happy path | 15 / 15 | 1.00 |
| No accent | 9 / 9 | 1.00 |
| Ambiguous | 9 / 9 | 1.00 |
| Greeting | 3 / 3 | 1.00 |
| Out of scope | 6 / 6 | 1.00 |
| Typo | 1 / 9 | 0.11 |
| Near intent | 5 / 9 | 0.56 |

## Findings

1. Eight typo queries were not routed. The current adapter requires an alias substring after accent normalization and has no conservative typo tolerance.
2. Four near-intent queries were routed too broadly: reissue/correction of a birth certificate, deletion of permanent residence, and change of household-business address.
3. Every near-intent and out-of-scope query returned `need_more_information` instead of `official_review_required`. Greeting and genuinely ambiguous queries correctly remain conversational with `need_more_information`. This accounts for 15 trust-state errors.
4. No evaluated intake/checklist/validation response emitted `verified_guidance` or a K1-style `last_verified_at`. The most important safety target, `false_verified == 0`, passed.

## Reproduction

```powershell
python scripts/evaluation/evaluate_demo_golden.py
python -m pytest tests/evaluation/test_demo_golden.py -q
```

The evaluator intentionally exits with code `1` while any release gate fails. Option 1 freezes runtime changes in this task, so router/guard remediation is deferred to a separate implementation task.

Phase 6.1 subsequently resolved this baseline without changing the corpus. See `docs/evaluation/PHASE6_1_ROUTER_REPORT.md`.

## Recommended Follow-up

- Add a deterministic intent guard that classifies greeting, ambiguity, unsupported near-intent and out-of-scope before alias routing.
- Replace broad substring matching with exact case/alias scoring and conservative typo handling.
- Re-run this unchanged corpus until routing accuracy is `1.0`, fail-closed errors are `0`, and `false_verified` remains `0`.
