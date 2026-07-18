# Context Pack - local-20260718-chunking-phase-5-6

## Identity

- Task ID: `local-20260718-chunking-phase-5-6` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `f7d6553`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai Phase 5 source approval gate va Phase 6 Recall@K evaluator cho retrieval noi bo.
- Success Criteria: SourceDocument approved phai co provenance/review/effective metadata; metadata chunk build tu approved source khong cho stale/future/unreviewed source lot vao retrieval; Recall@K evaluator deterministic va co synthetic smoke CLI; unit tests va staged guard pass.
- Constraints: Chi standard library; khong them dependency, database/index, embedding, public REST API, frontend hay raw corpus artifact; khong approve Phase 1 fixtures thay K1.
- Stopping Conditions: Dung neu can doi public API/schema, can approved legal provenance that, can sua frontend/docs ngoai scope, hoac can runtime dependency/index.
- Non-goals: Chua tich hop vao router/service runtime, chua tao approved corpus that, chua vector/BM25, chua Recall@5 tren golden legal set that.

## Scope da claim

- Files/areas: Context Pack nay; `backend/app/rag/sources.py`; `backend/app/rag/evaluation.py`; `backend/app/rag/__init__.py`; `scripts/data/evaluate_retrieval_golden.py`; RAG tests; fixture README.
- API/schema/contracts: Hien thuc noi bo `SourceDocument` va retrieval evaluation theo D-009; khong phai public REST schema.
- Runtime/data/resources: Synthetic smoke khong doc raw; optional CLI chi doc chunk JSONL trong ignored `artifacts/`.
- Risk: `shared`
- Decision Log: D-009 Accepted; khong mo runtime schema/dependency.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Chunking contract | `docs/ai/CHUNKING_CONTRACT.md` | SourceDocument fields, approved-only lifecycle, Recall@5 gate. |
| Phase 4 handoff | `.agents/context-packs/local-20260718-chunking-phase-4.md` | Approved-only retrieval baseline va fail-closed behavior. |
| RAG modules | `backend/app/rag/` | Chunk/retrieval interfaces da co. |

## Kiem chung va handoff

- Checks: 24 RAG unit tests pass; strict fixture validator pass 30/30 raw fixtures; chunk build pass 30 docs / 649 chunks / p95 447 / max 450 heuristic tokens; keyword retrieval fixture smoke pass fail-closed with 0 approved chunks; synthetic Recall@5 smoke pass with 3/3 matched, recall 1.0000; default repository guard and `git diff --check` pass.
- Rollback/fallback: Bo source/evaluation modules/CLI/tests; parser/chunker/retriever va raw corpus khong bi thay doi.
- Evidence: `py -3 -m unittest discover -s tests\rag -p test_*.py`; `py -3 scripts\data\validate_chunking_fixtures.py --verify-raw`; `py -3 scripts\data\build_chunking_fixtures.py`; `py -3 scripts\data\evaluate_keyword_retrieval.py`; `py -3 scripts\data\evaluate_retrieval_golden.py --sample`; `py -3 scripts\ci\validate_repo.py`; `git diff --check`.
- Residual risk: Synthetic smoke khong thay K1-approved corpus/golden legal queries; release Recall@5 that van can approved source pack.
- Files/resources da cham: Context Pack nay; `backend/app/rag/sources.py`; `backend/app/rag/evaluation.py`; `backend/app/rag/__init__.py`; `scripts/data/evaluate_retrieval_golden.py`; `tests/rag/test_source_gate.py`; `tests/rag/test_retrieval_evaluation.py`; `tests/rag/fixtures/retrieval_golden_queries.csv`; `tests/rag/fixtures/README.md`.
- Claim release: Release khi record chuyen `handoff`.
- Viec tiep theo: K1 approve source pack toi thieu, xuat chunks approved vao `artifacts/`, roi chay evaluator voi golden queries that va threshold 0.95.
