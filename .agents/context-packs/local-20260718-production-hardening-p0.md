# Context Pack - local-20260718-production-hardening-p0

## Identity

- Task ID: `local-20260718-production-hardening-p0` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `4274bd5`
- Branch / worktree: `fix/local-20260718-production-hardening-p0` / `C:/tmp/vaic-production-hardening-p0`
- AI Log: `chua bat`

## Muc tieu va ranh gioi

- Muc tieu: Trien khai lat cat Production Hardening P0 cho chatbot local: chan verified guidance tu du lieu chua K1, khoa RAG legacy nhiem du lieu theo mac dinh, chi nap ba thu tuc canonical, cai thien abstention ngoai pham vi, va lam health/config phan anh dung readiness.
- Non-goals: Khong CI/CD, cloud, deploy, vector database, auth/account, frontend redesign, migration breaking API, goi OpenAI that, hoac cong nhan duyet phap ly.
- Acceptance criteria:
  - Pack sinh truc tiep tu `data/Data_DVC` co trang thai `needs_review`; TrustPolicy khong duoc tra `verified_guidance` hoac verdict precheck cho pack nay.
  - Allowlist chi gom thu tuc canonical `1.001193`, `1.004222`, `1.001612`; cac bien the khai sinh/thuong tru khong bi tron vao pack mac dinh.
  - `/v1/rag/search` va `/v1/rag/answer` legacy bi feature-gate tat theo mac dinh, van giu URL/response schema de rollback va compatibility.
  - Intake khong de xuat ba MVP cho greeting, nhu cau mo ho, ket hon, khai tu, ho chieu, tam tru hoac thanh lap cong ty co phan.
  - Health tra `degraded` khi runtime chi fixture, RAG/LLM tat, hoac LLM gateway chua co key; capabilities neu ro readiness.
  - Backend/RAG tests, repository guard va benchmark offline pass; khong co network/provider call.
- Constraints: Repo policy la baseline; user loai CI/CD/cloud va cho phep Codex tu review tai lieu ky thuat. Khong sua raw data/artifacts/secret va khong gan nhan human K1 cho review cua AI.
- Stop condition: Dung neu can breaking public API/schema, xoa legacy endpoint, sua raw source, dung service/dependency tra phi, doc/in secret, hoac tuyên bo duyet phap ly.

## Scope da claim

- Files/areas: `backend/app/config.py`, `backend/app/dependencies.py`, `backend/app/routers/health.py`, `backend/app/models/procedure.py`, `backend/app/services/{trust_policy,rag_service}.py`, `backend/app/services/rag/**`, `backend/app/adapters/rag_llm.py`, source-manifest/clean-pack scripts, backend/RAG tests, `.env.example`, `docs/ai/{DECISIONS,PROJECT_CONTEXT}.md`, task Context Pack.
- API/schema/contracts: Giu nguyen routes/request/response; additive enum `needs_review` va additive health capability keys.
- Khong duoc cham: `frontend/**`, `data/**`, `dataset_raw/**`, `artifacts/**`, `.github/**`, deploy/runbook cloud, `.env` va credentials.
- Risk: `shared` - thay trust/runtime behavior nhung khong breaking contract.
- Decision Log: D-013 production hardening fail-closed (ghi trong task nay; user xac nhan scope option 3, loai CI/CD/cloud).

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Product/runtime baseline | `docs/ai/PROJECT_CONTEXT.md`, `docs/ai/ARCHITECTURE.md` | Trust states, K1 boundary, ba procedure MVP. |
| Existing implementation | D-011, `backend/app/services/rag/**`, `backend/app/adapters/rag_llm.py` | RAG raw-source va diem auto-approve can harden. |
| Legacy RAG | `backend/app/services/{rag_service,llm_service}.py`, `backend/app/rag/**` | Stack doc clean pack nhiem du lieu can feature-gate. |
| Review evidence | `local-20260718-openai-grounded-rag`, benchmark offline 2026-07-18 | Xac nhan source contamination, OOS false positive va false precheck pass. |

## Dependencies va resource claim

- Depends on: Backend/RAG hien tai tren `cao`; frontend Tram dang dirty o worktree chinh nen tach khoi scope.
- Shared resource: none; tests chi dung local files va fake/offline LLM.
- Claim owner + thoi han: Codex trong task hien tai; release khi `handoff`/`done`.

## Kiem chung va handoff

- Commands: `python -m pytest backend/tests -q`; RAG unittest; benchmark OOS; repository guard; diff review.
- Rollback: tat cac mode moi/hoan tac D-013; legacy routes van ton tai va co the bat lai bang config ro rang sau khi clean pack duoc review.
- Evidence / ket qua: backend `46 passed`; RAG `41 passed`; OOS/positive smoke `23 passed`; repository guard pass; `git diff --check` pass; flake8 changed scope pass khi bo cac rule format xung dot san voi Black (`E501,E402,W503`). Khong goi network/provider.
- Files/API/resources da cham: source/trust/config/health adapters; source-manifest va clean-pack scripts; tests; `.env.example`; D-013 va Project Context. Giu nguyen public route/request/response schema; enum/capability chi additive.
- Risk / rollback / chua kiem chung: Chua co K1 human/legal approval, provider smoke that, frontend/E2E hoac production readiness. Legacy routes duoc giu nhung tat mac dinh.
- Claims da release: tat ca claims cua task release khi handoff nay duoc commit.
- Viec tiep theo: Task rieng cho K1 source review/release; sau do grounded conversation + citation validator, frontend integration va E2E. CI/CD/cloud tiep tuc nam ngoai scope theo user.
