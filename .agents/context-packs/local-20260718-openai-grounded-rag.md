# Context Pack - local-20260718-openai-grounded-rag

## Identity

- Task ID: `local-20260718-openai-grounded-rag` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `implement`
- Status: `active`
- Base ref / commit: `cao` / `d1ca4f5`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Them LLM adapter OpenAI cho runtime RAG, mac dinh dung `gpt-4o-mini`.
- Success Criteria: Co endpoint tra loi grounded tren evidence RAG; khong co evidence, thieu API key hoac provider loi thi tra `official_review_required`; API key doc tu env va khong commit secret; tests pass.
- Constraints: Khong sua frontend/image changes cua user; khong commit `.env` hoac artifact/raw data; chi them route additive; giu search evidence deterministic hien co.
- Stopping Conditions: Dung neu can thay frontend breaking, can provider ngoai OpenAI, can network de test that voi API key, hoac can dua secret vao repo.
- Non-goals: Chua streaming chat, chua conversation memory, chua vector index, chua official legal URL verification.

## Scope da claim

- Files/areas: Backend config, RAG models/router/service, LLM service, tests, docs env/example, Decision Log.
- API/schema/contracts: Them `/v1/rag/answer`; khong doi contract `/v1/rag/search`.
- Runtime/data/resources: Doc `OPENAI_API_KEY` tu environment; doc ignored clean chunks artifact neu co.
- Risk: `shared`
- Decision Log: D-010 Accepted theo yeu cau truc tiep cua user.

## Kiem chung va handoff

- Checks: pending during implementation.
- Rollback/fallback: Go bo route/service LLM; runtime RAG search va checklist citations tiep tuc hoat dong.
- Evidence: pending.
- Residual risk: Test khong goi network/OpenAI that trong sandbox; can user chay smoke voi key local.
- Files/resources da cham: pending.
- Claim release: pending.
