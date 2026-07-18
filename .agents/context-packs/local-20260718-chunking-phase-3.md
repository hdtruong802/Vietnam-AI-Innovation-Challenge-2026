# Context Pack - local-20260718-chunking-phase-3

## Identity

- Task ID: `local-20260718-chunking-phase-3` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `cao` / `270eb8b`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai EvidenceChunk builder deterministic tu output Phase 2, co token budget, provenance va CLI diagnostic tren 30 fixtures.
- Success Criteria: Chunk build deterministic/idempotent; 100% chunk khong vuot hard maximum 450 heuristic tokens; moi chunk co source/section/procedure provenance; CLI khong ghi raw text ngoai `artifacts/`; unit tests va repo guard pass.
- Constraints: Chi standard library; raw corpus read-only va khong commit raw text; khong them dependency/tokenizer runtime, database/index, public API, embedding hay frontend; fixture output giu `review_status=needs_review`.
- Stopping Conditions: Dung neu can thay shared runtime schema/dependency, raw fixture thieu/sai checksum, chunk builder can index approved runtime, phat hien PII/secret, hoac can sua ngoai scope da claim.
- Non-goals: Chua tao embedding/vector store, retrieval ranking, approved source registry, public API response schema, hay xu ly toan corpus.

## Scope da claim

- Files/areas: Context Pack nay; `backend/app/rag/chunking.py`; `scripts/data/build_chunking_fixtures.py`; RAG tests; fixture README.
- API/schema/contracts: Hien thuc noi bo `EvidenceChunk` va `ChunkBuildReport` theo D-009; khong phai public REST schema.
- Runtime/data/resources: Doc 30 file allowlist trong `dataset_raw/`; khong ghi/sua raw files.
- Risk: `shared`
- Decision Log: D-009 Accepted; Phase 3 nam trong data/RAG logical contract, khong mo runtime dependency.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Chunking contract | `docs/ai/CHUNKING_CONTRACT.md` | EvidenceChunk fields, token budget va release gates. |
| Phase 2 handoff | `.agents/context-packs/local-20260718-chunking-phase-2.md` | Parser limitations, fixture status va next-step guidance. |
| Fixture metadata | `tests/rag/fixtures/` | Procedure IDs, checksums va review status without raw content. |

## Kiem chung va handoff

- Checks: 14 RAG unit tests pass; strict fixture validator pass 30/30 raw fixtures; Phase 3 chunk build pass 30 docs / 649 chunks / p95 447 / max 450 heuristic tokens; `git diff --check` pass. Default repo guard currently fails on pre-existing trailing whitespace in `frontend/src/app/page.tsx:623` and `frontend/src/app/page.tsx:651`, outside this task scope.
- Rollback/fallback: Bo module chunker/CLI/tests; parser/normalizer va raw corpus khong bi thay doi.
- Evidence: `py -3 -m unittest discover -s tests\rag -p test_*.py`; `py -3 scripts\data\validate_chunking_fixtures.py --verify-raw`; `py -3 scripts\data\build_chunking_fixtures.py`; `git diff --check`.
- Residual risk: Phase 1 labels van `needs_review`; chunk builder chi tao diagnostic chunks, chua approved retrieval index.
- Files/resources da cham: Context Pack nay; `backend/app/rag/chunking.py`; `backend/app/rag/__init__.py`; `scripts/data/build_chunking_fixtures.py`; `tests/rag/test_chunking_builder.py`; `tests/rag/fixtures/README.md`.
- Claim release: Release khi record chuyen `handoff`.
- Viec tiep theo: Sau Phase 3, can K1 review labels/provenance, sau do Phase 4 co the lam approved source registry + keyword retrieval baseline.
