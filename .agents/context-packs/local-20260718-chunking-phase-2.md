# Context Pack - local-20260718-chunking-phase-2

## Identity

- Task ID: `local-20260718-chunking-phase-2` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `review`
- Status: `handoff`
- Base ref / commit: `cao` / `8c25224`
- Branch / worktree: `cao` / repository hien tai theo yeu cau truc tiep cua user

## Muc tieu va ranh gioi

- Goal: Trien khai normalizer va parser deterministic cho 30 fixture Phase 1, co provenance line/character offsets va cong cu do section-boundary F1.
- Success Criteria: Normalization idempotent; parser output lien tuc va phu toan bo van ban; ID/output deterministic; CLI xac minh raw va bao metric; unit tests, strict fixture evaluation va repository guard pass.
- Constraints: Chi standard library; `dataset_raw/` read-only va khong commit raw text; khong doi public API, dependency, database/index hay frontend; annotation van `needs_review` cho den K1 review.
- Stopping Conditions: Dung neu can doi shared runtime schema/dependency, raw fixture thieu/sai checksum, phat hien PII/secret, hoac can sua ngoai scope da claim.
- Non-goals: Chua chunk theo token budget, tao embedding, retrieval index, procedure pack database hay xu ly toan corpus.

## Scope da claim

- Files/areas: Context Pack nay; `backend/app/rag/`; `scripts/data/evaluate_chunking_parser.py`; `tests/rag/test_normalization_parser.py`; fixture README.
- API/schema/contracts: Hien thuc noi bo `NormalizedDocument` va `ParsedSection` theo D-009; khong phai public REST schema.
- Runtime/data/resources: Doc 30 file allowlist trong `dataset_raw/`; khong ghi/sua raw files.
- Khong duoc cham: Cac thay doi chua commit trong `frontend/`; requirements/package files; database/deploy; backend routers/public models.
- Risk: `shared`
- Decision Log: D-009 Accepted; yeu cau Phase 2 hien tai la peer confirmation cho implementation noi bo nay.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Chunking contract | `docs/ai/CHUNKING_CONTRACT.md` | Taxonomy, ParsedSection invariants va quality gates. |
| Phase 1 handoff | `.agents/context-packs/local-20260718-chunking-phase-1.md` | Fixture scope, strict checks va handoff sang normalizer/parser. |
| Fixture metadata | `tests/rag/fixtures/` | Expected boundaries, checksums va edge cases; khong chua raw text. |
| Data policy | `docs/ai/SECRETS_AND_DATA.md` | Raw corpus chi duoc doc local, khong commit/log content. |

## Kiem chung va handoff

- Checks: unit tests RAG; strict fixture validator; parser evaluation; repository guard; `git diff --check`.
- Rollback/fallback: Bo module/parser CLI/tests; raw corpus khong bi thay doi; retrieval tiep tuc fallback structured lookup theo D-009.
- Evidence: 10 unit tests pass; 30/30 raw fixtures pass checksum/structure; repository guard va `git diff --check` pass. Parser evaluation tren 2,924 lines: boundary precision 0.5150, recall 0.7553, F1 0.6124, line-type accuracy 0.3793.
- Residual risk: Gate F1 0.95 chua dat. Phase 1 labels dang `needs_review`, co adjacent boundaries cung nhan va mot so nhan khong khop ten field; can K1 review truoc khi dung metric lam release gate. Parser khong doc expected labels khi inference.
- Files/resources da cham: Context Pack; `backend/app/rag/`; evaluator CLI; parser tests; fixture README. `dataset_raw/` chi doc; khong cham frontend/public API/dependency/database.
- Claim release: Da release khi record chuyen `handoff`.
- Viec tiep theo: K1 duyet/correct section labels; chay lai evaluator voi `--minimum-boundary-f1 0.95`; chi sau do moi sang Phase 3 chunk builder/token budget.
