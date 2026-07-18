# Context Pack - local-20260718-chunking-phase-8-10

## Identity

- Task ID: `local-20260718-chunking-phase-8-10` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `ac01284`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai loader clean RAG pack, runtime retrieval service va demo integration vao backend chatbot/checklist.
- Success Criteria: Runtime load duoc `artifacts/chatbot/clean-rag-chunks.jsonl`; search noi bo filter procedure runtime sang RAG procedure IDs; endpoint `/v1/rag/search` tra evidence; checklist them citations tu clean RAG evidence khi co; tests va staged guard pass.
- Constraints: Khong them dependency, database, vector index hay external provider; khong commit artifacts/raw data; khong sua frontend/image changes cua user; retrieval van fail-closed neu clean pack thieu/khong co hit.
- Stopping Conditions: Dung neu can public schema migration lon, can deploy config, clean chunks sai schema, hoac can overwrite frontend/image changes ngoai scope.
- Non-goals: Chua thay static checklist bang generated answer, chua LLM synthesis, chua production citation URL.

## Scope da claim

- Files/areas: Context Pack nay; `backend/app/models/rag.py`; `backend/app/services/rag_service.py`; `backend/app/routers/rag.py`; `backend/app/main.py`; `backend/app/services/procedure_service.py`; runtime RAG tests.
- API/schema/contracts: Them route demo `/v1/rag/search` va response model noi bo cho evidence search.
- Runtime/data/resources: Doc clean chunks tu ignored `artifacts/chatbot/clean-rag-chunks.jsonl`; khong commit artifact.
- Risk: `shared`
- Decision Log: D-009 Accepted; demo runtime integration khong them dependency/index.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Phase 7 handoff | `.agents/context-packs/local-20260718-chunking-phase-7.md` | Clean chatbot artifacts va source_refs local K1. |
| RAG modules | `backend/app/rag/` | EvidenceChunk, ApprovedSourceRegistry, KeywordRetriever. |
| Backend routes/services | `backend/app/main.py`, `backend/app/services/procedure_service.py` | Diem tich hop runtime thap rui ro. |

## Kiem chung va handoff

- Checks: 32 RAG unit tests pass; demo clean RAG pack rebuild pass with 30 sources / 632 approved chunks / max 450; direct RAGService smoke returns `ok`, loaded_chunks=632, hits=3 for birth registration query; staged guard pass.
- Rollback/fallback: Bo RAG route/model/service integration va citations append; clean static checklist van con fallback; artifacts khong bi commit.
- Evidence: `py -3 -m unittest discover -s tests\rag -p test_*.py`; `py -3 scripts\data\build_demo_clean_rag_pack.py`; `py -3 -c "... RAGService.search_evidence(...)"`; staged `validate_repo.py --staged`.
- Residual risk: Default repo guard hien bi frontend whitespace ngoai scope; production legal citation van la `local-k1-fixture://...` cho demo, chua official URL.
- Files/resources da cham: Context Pack nay; backend RAG model/router/service; `backend/app/main.py`; `backend/app/services/procedure_service.py`; `tests/rag/test_runtime_rag_service.py`.
- Claim release: Release khi record chuyen `handoff`.
- Viec tiep theo: Phase 11 can de frontend goi `/v1/rag/search` hoac backend synthesize answer co citations tu hits.
