# Context Pack - local-20260718-chunking-phase-4

## Identity

- Task ID: `local-20260718-chunking-phase-4` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `db41c4b`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai approved-source registry va keyword retrieval baseline noi bo tren EvidenceChunk.
- Success Criteria: Retrieval chi tra ve chunk `approved`; structured filter theo procedure/jurisdiction/effective date hoat dong; khi khong co approved evidence thi fail-closed bang `official_review_required`; scorer deterministic; unit tests va staged guard pass.
- Constraints: Chi standard library; khong them dependency, database/index, embedding, public REST API, frontend hay raw corpus artifact; Phase 1 fixtures van `needs_review`.
- Stopping Conditions: Dung neu can doi public API/schema, can approved legal provenance that, can sua frontend/docs ngoai scope, hoac can index/database/runtime dependency.
- Non-goals: Chua tich hop vao router/service runtime, chua evaluate Recall@5 golden set, chua approve fixture K1, chua vector/BM25 dependency.

## Scope da claim

- Files/areas: Context Pack nay; `backend/app/rag/retrieval.py`; `backend/app/rag/__init__.py`; `scripts/data/evaluate_keyword_retrieval.py`; RAG tests; fixture README.
- API/schema/contracts: Hien thuc noi bo retrieval contract theo D-009; khong phai public REST schema.
- Runtime/data/resources: CLI co the doc 30 fixture raw allowlist de tao diagnostic chunks; khong ghi/sua raw files.
- Risk: `shared`
- Decision Log: D-009 Accepted; khong mo runtime schema/dependency.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Chunking contract | `docs/ai/CHUNKING_CONTRACT.md` | Retrieval boundary: structured filter + keyword tren approved chunks, fail-closed. |
| Phase 3 handoff | `.agents/context-packs/local-20260718-chunking-phase-3.md` | EvidenceChunk builder va review status hien tai. |
| Backend procedure service | `backend/app/services/procedure_service.py` | Ba procedure runtime hien co, chua doi public API. |

## Kiem chung va handoff

- Checks: 18 RAG unit tests pass; strict fixture validator pass 30/30 raw fixtures; Phase 3 chunk build pass 30 docs / 649 chunks / p95 447 / max 450 heuristic tokens; Phase 4 retrieval smoke pass with selected=649, approved=0, quarantined=649, blocked `official_review_required`; default repository guard pass. Plain `git diff --check` currently reports a pre-existing/out-of-scope EOF issue in `docs/DESIGN.md`.
- Rollback/fallback: Bo retrieval module/CLI/tests; Phase 2/3 parser/chunker va raw corpus khong bi thay doi.
- Evidence: `py -3 -m unittest discover -s tests\rag -p test_*.py`; `py -3 scripts\data\validate_chunking_fixtures.py --verify-raw`; `py -3 scripts\data\build_chunking_fixtures.py`; `py -3 scripts\data\evaluate_keyword_retrieval.py`; `py -3 scripts\ci\validate_repo.py`.
- Residual risk: Chua co approved K1 corpus, nen CLI fixture mac dinh chi xac nhan fail-closed; Recall@5 phai lam sau khi co approved source/golden query.
- Files/resources da cham: Context Pack nay; `backend/app/rag/retrieval.py`; `backend/app/rag/__init__.py`; `scripts/data/evaluate_keyword_retrieval.py`; `tests/rag/test_keyword_retrieval.py`; `tests/rag/fixtures/README.md`.
- Claim release: Release khi record chuyen `handoff`.
- Viec tiep theo: K1 approve source/provenance toi thieu cho 3 MVP procedures, sau do tao golden query set va gate Recall@5.
