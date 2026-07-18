# Context Pack - local-20260718-chunking-phase-7

## Identity

- Task ID: `local-20260718-chunking-phase-7` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `56d9a10`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai approved-pack build flow sau K1 review: chap nhan fixture rows da `approved`, tao approved source manifest template, validate provenance bang SourceDocument gate, build approved chunks vao ignored `artifacts/`, va chay Recall@K tren golden queries.
- Success Criteria: Validator/test khong khoa cung `needs_review`; approved source manifest schema bat buoc provenance/review/effective metadata; builder dung boundaries K1-reviewed thay vi parser heuristic; output chi duoc ghi duoi `artifacts/`; unit tests, strict fixture validator, sample approved-pack build, Recall@K smoke va staged guard pass.
- Constraints: Chi standard library; khong them dependency, database/index, embedding, public REST API hay frontend; khong commit raw text/artifacts; khong tu invent official provenance cho production pack.
- Stopping Conditions: Dung neu can sua frontend/image changes cua user, can public API/runtime dependency, raw checksum sai, hoac approved source thieu provenance nhung user yeu cau publish nhu approved.
- Non-goals: Chua tich hop runtime API, chua push, chua tao vector index, chua publish artifacts.

## Scope da claim

- Files/areas: Context Pack nay; RAG approved builder module; data scripts; RAG tests; fixture README; fixture validator/test lifecycle handling.
- API/schema/contracts: Noi bo `ApprovedSourceManifest`/approved chunk build flow theo D-009; khong phai public REST schema.
- Runtime/data/resources: Doc raw allowlist local khi build/check; chi ghi local artifacts duoi ignored `artifacts/`.
- Risk: `shared`
- Decision Log: D-009 Accepted; khong mo runtime schema/dependency.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Chunking contract | `docs/ai/CHUNKING_CONTRACT.md` | Approved-only lifecycle, source provenance, chunk/retrieval gates. |
| Phase 5/6 handoff | `.agents/context-packs/local-20260718-chunking-phase-5-6.md` | Source gate va Recall@K evaluator da co. |
| User K1 changes | `tests/rag/fixtures/chunking_phase1_manifest.csv` working tree | Rows da duoc user chuyen sang `approved`. |

## Kiem chung va handoff

- Checks: 29 RAG unit tests pass; strict fixture validator pass 30/30 raw fixtures after K1 lifecycle update; diagnostic chunk build pass 30 docs / 649 chunks / p95 447 / max 450; keyword retrieval smoke pass fail-closed because diagnostic chunks still lack `source_refs`; synthetic Recall@5 smoke pass 3/3 with recall 1.0000; approved source template CLI writes 30 rows under ignored `artifacts/`; demo clean chatbot pack build pass with 30 sources / 632 approved chunks / max 450; default repository guard and `git diff --check` pass.
- Rollback/fallback: Bo approved builder/template scripts/tests; raw corpus va frontend user changes khong bi cham.
- Evidence: `py -3 -m unittest discover -s tests\rag -p test_*.py`; `py -3 scripts\data\validate_chunking_fixtures.py --verify-raw`; `py -3 scripts\data\build_chunking_fixtures.py`; `py -3 scripts\data\evaluate_keyword_retrieval.py`; `py -3 scripts\data\evaluate_retrieval_golden.py --sample`; `py -3 scripts\data\prepare_approved_source_manifest.py --output artifacts\chunking\approved-sources-template.csv`; `py -3 scripts\data\build_demo_clean_rag_pack.py`; `py -3 scripts\ci\validate_repo.py`; `git diff --check`.
- Residual risk: Production approved pack van can source_ref/authority/jurisdiction that do reviewer dien; demo clean pack dung `local-k1-fixture://...` de chatbot local co data ngay nhung khong phai official legal citation.
- Files/resources da cham: Context Pack nay; `backend/app/rag/approved.py`; `backend/app/rag/retrieval.py`; `backend/app/rag/__init__.py`; `scripts/data/prepare_approved_source_manifest.py`; `scripts/data/build_approved_rag_pack.py`; `scripts/data/build_demo_clean_rag_pack.py`; `scripts/data/validate_chunking_fixtures.py`; `scripts/data/build_chunking_fixtures.py`; `scripts/data/evaluate_keyword_retrieval.py`; RAG tests; fixture README; `tests/rag/fixtures/chunking_phase1_manifest.csv` K1 status changes cua user. Local artifacts da tao: `artifacts/chatbot/clean-approved-sources.csv`, `artifacts/chatbot/clean-rag-pack.jsonl`, `artifacts/chatbot/clean-rag-chunks.jsonl`, `artifacts/chatbot/clean-rag-report.json`.
- Claim release: Release khi record chuyen `handoff`.
- Viec tiep theo: Dien approved source manifest thuc te, build chunks approved vao `artifacts/`, chay golden Recall@5 >= 0.95, roi moi tich hop backend runtime.
