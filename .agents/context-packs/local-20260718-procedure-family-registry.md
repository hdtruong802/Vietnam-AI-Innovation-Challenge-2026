# Context Pack - local-20260718-procedure-family-registry

## Identity

- Task ID: `local-20260718-procedure-family-registry` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `chore/local-20260718-k1-review-package` / `c9bf0a4`
- Branch / worktree: `feature/local-20260718-procedure-family-registry` / `C:/tmp/vaic-procedure-family-registry`
- AI Log: `chua bat`

## Muc tieu va ranh gioi

- Goal: Trien khai procedure-family registry versioned cho khai sinh, thuong tru, ho kinh doanh; discovery doc dong thoi `data/Data_DVC` va external ignored `dataset_raw`; tao family K1 candidate package cho toan bo ma da thong nhat.
- Success criteria:
  - Registry tracked co dung ten/ma, family, relation type, release tier va source collection; `2.000986` co quan he voi ca khai sinh va thuong tru ma khong nhan doi source.
  - Anchor hien tai van la `1.001193`, `1.004222`, `1.001612`; variant/bundled/supporting/post-registration khong bi tron thanh anchor.
  - Discovery doc strict UTF-8, exact code/name va checksum; doc `2.*` tu `dataset_raw` bang path cau hinh, khong copy vao worktree/Git.
  - Family candidate manifest co mot row moi source, family/relation metadata versioned, tat ca `needs_review`, review fields trong; thieu/trung/mismatch thi fail closed.
  - Report khong chua raw text; output chi duoi ignored `artifacts/`; unit tests synthetic va dry-run tren corpus local pass.
- Constraints: Chi Option 1. Khong intent router/runtime retrieval, khong CI/CD/cloud/frontend, khong sua raw data, khong tu K1/approved, khong copy ignored data sang worktree.
- Stopping conditions: Dung neu can auto-approve, sua/copy raw corpus, thay public API/runtime, tiep tuc router khi chua co task rieng, hoac gap ma/title khong khop registry can user/domain review.

## Scope da claim

- Files/areas: registry metadata tracked, family review helper/CLI trong `scripts/data/`, tests `tests/rag/`, K1/data docs, Context Pack.
- API/schema/contracts: Khong doi REST/runtime. Them `vaic-procedure-family-registry-v1` va `vaic-family-k1-review-v1` cho metadata local.
- Khong cham: `frontend/**`, `backend/app` runtime, `data/Data_DVC/*.txt`, `dataset_raw/**`, `.env`, `.github/**`, cloud/deploy.
- Risk: `shared` - them data registry/review process; D-013 va user Option 1 xac nhan fail-closed.
- Decision Log: D-013; khong can Decision moi vi khong doi runtime/shared API/dependency.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| P0/K1 base | D-013, `scripts/data/k1_review_package.py` | Reuse path/checksum/review gate; anchors van fail closed. |
| User-reviewed code list | Current task prompt + local titles | Registry scope va relation classification. |
| Raw locations | `data/Data_DVC`, external local `dataset_raw` | `1.*` tracked va `2.*` ignored; chi doc. |
| Governance | `docs/ai/SECRETS_AND_DATA.md`, `docs/data/K1_REVIEW_RUNBOOK.md` | Khong raw Git, human K1 bat buoc. |

## Dependencies va resource claim

- Depends on: commits `49dbd7f`, `c9bf0a4`; original workspace local `dataset_raw` chi doc cho dry-run.
- Shared resource: none; generated outputs ignored trong worktree task.
- Claim owner + thoi han: Codex trong task; release khi handoff/done.

## Kiem chung va handoff

- Commands: registry validation; synthetic dual-source tests; family prepare dry-run voi external `dataset_raw`; full RAG tests; formatting/lint/guard; diff review.
- Rollback: revert registry/tooling/docs commit; P0 anchors va runtime khong doi.
- Evidence / ket qua: registry exact 25 source/26 relationship; 7 family unit tests pass; full RAG 56 tests pass; Black va flake8 changed scope pass (`E501,E402,W503` excluded theo baseline); repository guard pass; `git diff --check` pass. Dry-run that doc 16 `Data_DVC` + 9 external `dataset_raw`, tat ca 25 `needs_review`, snapshot `fa5bd8f1a4f740216ce0ea9e332e011e57bf1ca0281862a3fb4f7c64010e2792`. Khong network/provider call.
- Runtime artifact local: `artifacts/family-k1-review/{candidate-family-sources.csv,family-provenance-report.json,family-review-checklist.md}` trong worktree task, deu ignored. Report/manifests chi logical path, khong absolute external path/raw text.
- Risk / chua kiem chung: relation classification la technical candidate, chua human K1/domain approval; chua co family reviewed-manifest validator/release; chua noi intent router/retrieval/runtime.
- Claims da release: tat ca claim release khi commit/handoff.
- Viec tiep theo: task rieng cho intent router + exact-code retrieval sau khi family package review-ready; variant chua K1 van fail closed.
