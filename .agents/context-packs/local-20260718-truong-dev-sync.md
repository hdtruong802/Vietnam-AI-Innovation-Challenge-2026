# Context Pack — local-20260718-truong-dev-sync

## Identity

- Task ID: `local-20260718-truong-dev-sync`
- Owner tạm thời: hdtruong802 / Codex
- Mode hiện tại: `implement`
- Base ref / commit: `origin/truong` / `abb9392`
- Branch / worktree: `truong` / `.worktrees/truong-dev-sync`
- AI Log: `hdtruong802 / codex manual / doctor pass`

## Mục tiêu và ranh giới

- Goal: Đồng bộ `origin/dev` vào `truong` để PR #19 không conflict, giữ API prototype và runtime RAG/LLM từ `dev`.
- Non-goals: Không sửa frontend, data thô, provider credential, dependency, hoặc thêm feature ngoài phần conflict backend.
- Acceptance criteria: Merge sạch; backend import/config không còn marker conflict; API prototype và RAG routes cùng tồn tại; backend lint/test và repository guard pass; push `truong` cập nhật PR #19.
- Constraints: Chỉ resolve backend/shared docs/evidence do merge yêu cầu; không bỏ fail-closed, request/error/trust safeguards.
- Stop condition: Dừng và báo nếu cần thay public API ngoài phần cộng gộp hiện hữu, cần secret/provider thật, hoặc conflict chạm frontend cần sửa thủ công.

## Scope đã claim

- Files/areas: Backend conflict files do merge, `.env.example`, API/decision docs chỉ khi Git yêu cầu merge resolution, Context Pack này và AI Log evidence.
- API/schema/contracts: additive prototype read models và existing RAG/LLM routes.
- Không được chạm: `frontend/**`, raw data/artifacts, secrets.
- Risk: `shared`
- Decision Log: D-006, D-009, D-013.

## Kiểm chứng và handoff

- Commands: `black --check .`, `flake8 .`, `pytest -q` from `backend/`; `validate_repo.py --range origin/dev...HEAD`; `git diff --check`; PR #19 state.
- Evidence: Backend CI-equivalent check passed: Black and Flake8 pass; 39 tests passed (one upstream TestClient deprecation warning). Full root RAG data tests still require ignored `dataset_raw/` owned by the data lane.
- Rollback: Revert merge commit hoặc reset local merge trước khi push; `origin/truong` không đổi cho tới push.
