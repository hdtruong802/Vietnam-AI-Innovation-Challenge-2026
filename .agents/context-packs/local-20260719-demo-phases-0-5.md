# Context Pack - local-20260719-demo-phases-0-5

## Identity

- Task ID: `local-20260719-demo-phases-0-5`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Base ref / commit: `cao` / `5a91f099bffe4859433be7f93d52ff834fc37c17`
- Branch / worktree: integrated into local `cao`; source worktree retained as a recovery point
- AI Log: chua bat; khong capture prompt trong task nay

## Muc tieu va ranh gioi

- Muc tieu: hoan tat Phase 0-5 cho ba pack MVP: demo-approved trust, frontend watermark, feedback API, LLM gateway kill switch va E2E local.
- Non-goals: khong K1/human legal approval, khong cloud/deploy, khong bat legacy RAG, khong goi provider bang API key that.
- Acceptance criteria:
  - Ba pack dung `review_status=demo_approved`, `demo_mode=true`, khong phat `verified_guidance`/`last_verified_at` nhu K1.
  - Intake/checklist/form/deterministic precheck van chay day du trong demo mode.
  - Frontend luon hien "Da kiem thu cho demo MVP" va "Khong phai K1"; khong hien "Da xac minh nguon" cho demo.
  - `POST /v1/feedback` strict, privacy-safe, khong persist/log note hoac session id; FE goi endpoint that.
  - LLM gateway on/off khong thay findings/verdict; missing key/disabled la kill switch an toan.
  - Backend, RAG, frontend test/typecheck va E2E local pass; false verified cho demo bang 0.
- Constraints: fast-forward ket qua ve local `cao`, khong push; khong copy `.env`; khong su dung secret.
- Stop condition: dung neu can suy dien K1/noi dung phap ly moi, can secret/provider that, cloud/deploy, hoac thay contract khong backward-compatible.

## Scope da claim

- Backend: demo pack/trust/copilot/config/dependencies, feedback model/router, tests.
- Frontend: procedure-case types/reducer/trust/checklist/precheck/feedback API va tests.
- Docs/config: D-024, `.env.example`, Context Pack.
- API: additive `demo_mode`; additive `POST /v1/feedback`; khong xoa/doi route hien co.
- Khong cham: raw `Data_DVC`, ignored artifacts, `.env`, cloud resources, deployment settings.
- Risk: `shared` (API + demo flow).
- Decision: D-013, D-014, D-023 va D-024.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Product | `docs/ai/PROJECT_CONTEXT.md` | Ba MVP va trust states. |
| Architecture | `docs/ai/ARCHITECTURE.md` sections 3-8 | Fail-closed, PII, LLM/rule boundary. |
| Data policy | `docs/ai/SECRETS_AND_DATA.md` | K1 va secret/PII boundary. |
| Claude handoff | commit `5a91f09` | A1-A5 va A6 test baseline. |
| Runtime | `backend/app/services/copilot_service.py`, `trust_policy.py` | Trust/content/verdict assembly. |
| Frontend | `frontend/src/features/procedure-case/**` | Consumer demo_mode va feedback. |

## Dependencies va resource claim

- Depends on: ba JSON demo pack trong commit `5a91f09`; existing deterministic RuleEngine va GatewayLLMProvider.
- Shared resource: public API schema va local demo flow; khong claim port/server cho den verify-demo.
- Claim owner: Codex den handoff; release sau commit/merge local.

## Kiem chung va handoff

- Commands: backend pytest, RAG pytest, frontend test/typecheck, staged repo guard, in-process E2E/kill-switch tests.
- Rollback: revert task commit; default `procedure_data_mode=fixture`, `llm_mode=disabled`, legacy RAG disabled.
- Evidence:
  - Backend target: `18 passed`.
  - Backend full regression: `64 passed`, mot Starlette deprecation warning tu dependency.
  - Frontend: `31 passed`; `tsc --noEmit` pass; ESLint `src/features/procedure-case` pass.
  - Full ESLint con mot loi co san ngoai scope tai `frontend/src/app/layout.tsx:43` (`no-sync-scripts`).
  - Next production build trong clone chinh: pass; static routes `/` va `/_not-found` generated.
  - Build trong worktree tung bi Turbopack chan do junction `node_modules` tro ra ngoai filesystem root; day la gioi han cua setup worktree, khong phai loi source.
- Claims da release: da release; khong co port/server/cloud resource.
- Viec tiep theo: Phase 6+ chi sau handoff; deploy can user xac nhan rieng.
