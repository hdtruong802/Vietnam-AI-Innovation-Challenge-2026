# Context Pack - local-20260719-phase6-1-intent-router

## Task Record

- Task ID: `local-20260719-phase6-1-intent-router`
- Mode: `verify-demo`
- Status: `done`
- Owner tam thoi: Codex
- Base ref: `cao` / `e84e4bb`
- Branch/worktree: integrated into local `cao`; feature worktree retained as a recovery point
- Risk: `shared` (intake routing and trust disposition)
- AI Log: chua bat; khong capture prompt trong task nay

## Goal, Success Criteria, Constraints, Stopping Conditions

- Goal: sua deterministic intent router de Phase 6 golden gate dat 60/60 ma van fail-closed.
- Success Criteria:
  - Greeting khong chay recommendation/retrieval va tra `need_more_information`.
  - Ambiguous intent tra `need_more_information`.
  - Out-of-scope va unsupported near-intent tra `official_review_required`.
  - Happy path/no-accent/typo chon dung mot trong ba MVP pack.
  - Golden: routing 60/60, false/missed/wrong route 0, fail-closed error 0, false verified 0.
  - Public API schema khong doi; backend/full evaluation tests pass.
- Constraints: standard library only; khong LLM/API key/network/cloud; khong them fact phap ly hoac sua pack/rules.
- Stopping Conditions: dung neu can suy dien case phap ly ngoai golden taxonomy, thay public API khong backward-compatible, fuzzy matching tao candidate mo ho, hoac golden an toan khong the dat ma khong mo rong scope.

## Resource Claims

- Files/areas: `backend/app/services/intent_router.py`, demo recommendation adapter, CopilotService, backend/evaluation tests, D-025.
- API/schema/contracts: public REST unchanged; internal routing behavior changes before recommendation.
- Runtime/data: in-process tests only; no port/server/provider.
- Decision: D-024 and D-025; user confirmed Phase 6.1 implementation.

## Context Selected

- `docs/evaluation/PHASE6_GOLDEN_REPORT.md`: 8 missed typos, 4 false near-intent, 15 trust disposition errors.
- `tests/evaluation/fixtures/demo_intake_golden.jsonl`: frozen acceptance corpus.
- `backend/app/adapters/demo_pack.py`: current substring matcher.
- `backend/app/services/copilot_service.py`: no-candidate trust behavior.
- `backend/app/services/trust_policy.py`: verified/K1 boundary remains unchanged.
- `docs/ai/DECISIONS.md` D-024: demo-approved must never emit verified guidance.

## Verification, Rollback, Handoff

- Planned checks: intent-router unit tests, golden CLI, evaluation/backend tests, staged repo guard.
- Rollback: revert task commit; restores Phase 6 baseline behavior without data/schema migration.
- Evidence:
  - Target router/evaluation tests: `23 passed`.
  - Backend + evaluation full regression: `87 passed`, one Starlette dependency deprecation warning.
  - Golden CLI: exit `0`; routing `60/60`, false/missed/wrong route `0`, fail-closed errors `0`, false verified `0`, demo/HTTP errors `0`.
  - Public API schema unchanged; no dependency, provider, network, secret or port used.
- Resource release: released after fast-forward to local `cao`; no port/server/cloud resource was claimed.
- Publish: no push/PR in this task.
