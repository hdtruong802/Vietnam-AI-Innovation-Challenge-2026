# Context Pack - local-20260718-openai-grounded-rag

## Identity

- Task ID: `local-20260718-openai-grounded-rag` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `d1ca4f5`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Hoan thien luong OpenAI grounded RAG tu `.env` den frontend, mac dinh dung `gpt-4o-mini`, va loai bo hien thi tieng Viet/markdown loi trong chat.
- Success Criteria: Backend nap `.env` on dinh tu repo hoac `backend` bat ke working directory; client OpenAI khong dong bang key rong luc import; `/v1/rag/answer` goi duoc provider voi key hop le; frontend hien thi tieng Viet sach va cau tra loi co citations; tests/typecheck pass.
- Constraints: Giu nguyen bo cuc frontend cua peer; khong commit/in secret; khong doi breaking contract; giu approved-only va fail-closed.
- Stopping Conditions: Dung o loi xac thuc/quota/provider neu OpenAI tu choi key; khong hien thi hoac sua secret; khong mo rong sang redesign frontend.
- Non-goals: Chua streaming chat, chua conversation memory, chua vector index, chua official legal URL verification.

## Scope da claim

- Files/areas: Backend config, RAG models/router/service, LLM service, runtime tests, va cac chuoi chat/RAG trong `frontend/src/app/page.tsx`.
- API/schema/contracts: Them `/v1/rag/answer`; khong doi contract `/v1/rag/search`.
- Runtime/data/resources: Doc `OPENAI_API_KEY` tu environment; doc ignored clean chunks artifact neu co.
- Risk: `shared`
- Decision Log: D-010 Accepted theo yeu cau truc tiep cua user.

## Kiem chung va handoff

- Checks: `40/40` RAG unittest pass; `11/11` backend pytest pass; frontend `npm run typecheck` pass; repository guard pass; real OpenAI smoke on port 8011 returned `status=ok`, `model=gpt-4o-mini`, UTF-8 answer and citations.
- Rollback/fallback: Go bo route/service LLM; runtime RAG search va checklist citations tiep tuc hoat dong.
- Evidence: `.env` duoc nap tu repo va backend path; client runtime nhan key; temporary port 8011 da release.
- Residual risk: Clean K1 pack dang gan nham nhieu source vao `birth_registration` (co ket hon, giam ho, nguoi co cong), trong khi canonical birth source `1.001193` chua co. Prompt khong the bu duoc metadata sai; can sua manifest va rebuild pack truoc khi coi chat content la demo-ready. Browser runtime khong available nen chua visual smoke tu phien nay. Port 8000 van do process ngoai phien giu va phai restart tu terminal cua user.
- Files/resources da cham: backend config/main/RAG/LLM/procedure services, backend API contract test, runtime RAG test, frontend `page.tsx`, context pack.
- Claim release: port 8011 released; source files handoff; port 8000 khong claim duoc.
