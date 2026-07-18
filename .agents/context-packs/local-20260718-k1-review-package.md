# Context Pack - local-20260718-k1-review-package

## Identity

- Task ID: `local-20260718-k1-review-package` | GitHub Issue: `chua publish`
- Owner tam thoi: Codex
- Mode hien tai: `verify-demo`
- Status: `handoff`
- Base ref / commit: `fix/local-20260718-production-hardening-p0` / `49dbd7f`
- Branch / worktree: `chore/local-20260718-k1-review-package` / `C:/tmp/vaic-k1-review-package`
- AI Log: `chua bat`

## Muc tieu va ranh gioi

- Goal: Tao goi K1 review-ready local cho dung ba source canonical, gom candidate manifest, provenance/checksum report, checklist review va validator fail-closed cho manifest da duoc reviewer dien.
- Success criteria:
  - Prepare CLI chi chon dung `1.001193`, `1.004222`, `1.001612`, moi procedure dung mot source; thieu/trung/lac pham vi thi fail.
  - Candidate manifest luon la `needs_review`; cac truong approval/reviewer/effective/permission de trong va khong co code tu dong nang thanh `approved`.
  - Report chi chua metadata/provenance/checksum/issue, khong nhung raw noi dung hoac PII.
  - Checklist neu ro nhung truong reviewer phai xac minh va cach validate sau review.
  - Validate CLI kiem exact schema/set, path containment, UTF-8, raw + normalized checksum, source code/name, URL, permission, effective dates, reviewer va review status; issue nao cung tra exit khac 0 va khong tao release-ready report.
  - Unit tests dung fixture synthetic; dry-run prepare tren corpus local pass; repository guard pass; khong network/provider call.
- Constraints: Bo qua CI/CD, cloud va deploy. Khong sua/copy raw data, `.env`, artifacts cua peer hoac secret. Output runtime chi duoc ghi duoi ignored `artifacts/`.
- Stopping conditions: Dung truoc khi gan `approved` cho source that, tuyen bo K1/legal approval, sua raw corpus, goi web/provider, hoac thay public API/runtime contract.

## Scope da claim

- Files/areas: K1 review helper/CLI moi trong `scripts/data/`, tests trong `tests/rag/`, `docs/data/K1_REVIEW_RUNBOOK.md`, data governance/Project Context va Context Pack nay.
- API/schema/contracts: Khong doi public REST/runtime schema. Manifest K1 la local artifact contract moi va versioned.
- Khong cham: `frontend/**`, `backend/app` runtime, `data/**`, `dataset_raw/**`, `.env`, `artifacts/**` tracked, `.github/**`, cloud/deploy.
- Risk: `shared` - bo sung data review process; khong doi runtime. D-013 da chap nhan fail-closed va yeu cau explicit K1.
- Decision Log: D-013.

## Context duoc chon loc

| Nguon | Ref | Ly do |
| --- | --- | --- |
| Trust/data policy | `docs/ai/SECRETS_AND_DATA.md`, D-006, D-007, D-013 | Human review, provenance, permission, checksum va fail-closed. |
| Canonical source gate | `backend/app/services/rag/source_store.py` | Exact code/name cho ba procedure candidate. |
| Existing approved gate | `backend/app/rag/{sources,approved}.py` | Mau validation/release lifecycle, khong tai su dung auto-approval. |
| Existing tools/tests | `scripts/data/prepare_approved_source_manifest.py`, `tests/rag/test_approved_pack.py` | Bao toan compatibility va bo sung pipeline portable. |

## Dependencies va resource claim

- Depends on: P0 commit `49dbd7f`; corpus tracked `data/Data_DVC` chi doc.
- Shared resource: none; outputs test vao temp, dry-run vao ignored `artifacts/` neu can.
- Claim owner + thoi han: Codex trong task hien tai; release khi handoff/done.

## Kiem chung va handoff

- Commands: unit tests moi; full RAG tests; prepare dry-run tren corpus; validate negative/positive synthetic; repository guard; diff review.
- Rollback: revert tooling/docs commit; runtime P0 khong bi anh huong.
- Evidence / ket qua: 8 K1 unit tests pass; full RAG 49 tests pass; Black check pass; flake8 changed scope pass voi cac rule format legacy duoc loai (`E501,E402,W503`); repository guard pass; `git diff --check` pass. Dry-run corpus that tao dung 3 candidate, snapshot `9d77d7c81a2679ee9f70be595ce1472d9496476471398d8ea970a6e27c7cbf45`; candidate validate exit 1 va khong tao release report. Khong network/provider call.
- Runtime artifact local: `artifacts/k1-review/{candidate-sources.csv,provenance-report.json,review-checklist.md}` trong worktree task, deu ignored; khong commit raw/artifact.
- Risk / chua kiem chung: Chua co human K1/legal approval, official URL/effective-date/permission verification hoac runtime approved release. Tooling chi chung minh integrity/completeness.
- Claims da release: tat ca claim release khi commit/handoff.
- Viec tiep theo: Human reviewer dien `reviewed-sources.csv`; task sau moi validate release-ready report va noi approved pack vao runtime.
