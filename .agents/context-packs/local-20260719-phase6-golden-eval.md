# Context Pack - local-20260719-phase6-golden-eval

## Task Record

- Task ID: `local-20260719-phase6-golden-eval`
- Mode: `verify-demo`
- Status: `handoff`
- Owner tam thoi: Codex
- Base ref: `cao` / `f01f8f3`
- Branch/worktree: integrated into local `cao`; feature worktree retained as a recovery point
- Risk: `isolated` (evaluation assets only; no runtime/API changes)
- AI Log: chua bat; khong capture prompt trong task nay

## Goal, Success Criteria, Constraints, Stopping Conditions

- Goal: tao Phase 6 offline golden evaluation gom 60 cau cho ba procedure pack MVP.
- Success Criteria:
  - Dung 60 case, can bang 20 case cho moi suite khai sinh/thuong tru/ho kinh doanh.
  - Co happy path, khong dau, typo, mo ho, thu tuc gan nghia, greeting va ngoai pham vi.
  - Runner goi FastAPI in-process voi `procedure_data_mode=demo_pack`, RAG/LLM disabled.
  - Bao cao routing accuracy theo suite/category, false route, missed route va false verified.
  - Gate bat buoc `false_verified == 0`; runner exit non-zero neu routing/trust gate khong dat.
  - Tests corpus/schema/evaluator pass va backend regression khong bi anh huong.
- Constraints: khong API key, provider that, cloud/CI/CD, raw data hoac suy dien fact phap ly.
- Stopping Conditions: dung va bao cao neu muon dat routing gate can sua runtime/router, can them fact phap ly, hoac phat hien contract khong backward-compatible. User da chon Option 1, nen khong tu sua runtime khi evaluation fail.

## Resource Claims

- Files/areas: `scripts/evaluation/`, `tests/evaluation/`, `docs/evaluation/`, Context Pack.
- API/schema/contracts: chi doc public API hien tai; khong thay doi endpoint/model.
- Runtime/data: TestClient in-process; khong chiem port, khong doc `.env`, khong goi network.
- Decision: D-017; khong can Decision moi vi chi them evaluation isolated.

## Context Selected

- `docs/ai/PROJECT_CONTEXT.md`: ba MVP va golden cases tuong duong.
- `docs/ai/ARCHITECTURE.md`: fail-closed, deterministic rules, LLM boundary.
- `docs/ai/DECISIONS.md` D-017: demo-approved khong duoc phat verified/K1.
- `backend/app/adapters/demo_pack.py`: router can duoc evaluation.
- `backend/tests/test_demo_e2e.py`: offline TestClient/settings baseline.
- `scripts/data/evaluate_retrieval_golden.py`: CLI/report/exit-code pattern.

## Verification, Rollback, Handoff

- Planned checks: evaluator CLI, evaluation tests, backend full pytest, repo validate, diff check.
- Rollback: revert evaluation commit; runtime khong thay doi.
- Evidence:
  - Corpus: 60 unique cases, 20 per suite, all seven required categories in every suite.
  - Evaluation tests: `5 passed`.
  - Backend + evaluation regression: `69 passed`, one Starlette dependency deprecation warning.
  - Golden CLI: expected exit `1`; routing `48/60` (`0.80`), false routes `4`, missed routes `8`, false verified `0`, fail-closed trust errors `18`, demo/HTTP errors `0`.
  - Full-tree repo guard is blocked by pre-existing `.codex/hooks.json` and `.cursor/hooks.json` in base; staged guard is required for task diff.
- Resource release: released after fast-forward to local `cao`; no port/server/cloud resource was claimed.
- Publish: khong push/PR trong task nay.
