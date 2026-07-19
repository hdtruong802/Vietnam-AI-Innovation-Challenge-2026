# Context Pack — local-20260719-light-only-theme

## Identity

- Task ID: `local-20260719-light-only-theme`
- Owner tạm thời: Codex / user-requested
- Mode hiện tại: `verify-demo`
- Base ref / commit: `origin/main` / `3eca590`
- Branch / worktree: `fix/local-20260719-light-only-theme` / `.worktrees/light-only-theme`
- AI Log: chưa bật trong worktree; không commit trong task này nếu chưa onboard.

## Mục tiêu và ranh giới

- Mục tiêu: giao diện demo Portal và Copilot luôn dùng palette light khi máy người dùng đặt system dark.
- Non-goals: dark mode, theme switch, API/backend/deploy flow; không thêm auth thật.
- Acceptance criteria: không còn override `prefers-color-scheme: dark`; native controls dùng light scheme; text/card/placeholder ở Portal có màu đọc được; lint, typecheck, test và build pass.
- Constraints: chỉ sửa frontend theme/demo navigation và `docs/DESIGN.md`/Decision Log; giữ token Portal/Copilot scoped, không thêm dependency.
- Stop condition: dừng và hỏi peer nếu cần đổi public API, auth, runtime/deploy hoặc nếu cần một thiết kế dark mode mới.

## Scope đã claim

- Files/areas: `frontend/src/app/globals.css`, landing components dùng text semantic, `frontend/src/app/page.tsx`, `docs/DESIGN.md`, `docs/ai/DECISIONS.md`.
- API/schema/contracts: không có.
- Risk: `shared`.
- Decision Log: D-020, D-022.

## Context được chọn lọc

| Nguồn | File / ref | Lý do cần đọc |
| --- | --- | --- |
| Design source | `docs/DESIGN.md` | Token Portal/Copilot và yêu cầu accessibility. |
| Global CSS | `frontend/src/app/globals.css` | Nguồn dark-token override và token scope. |
| Landing UI | `frontend/src/app/components/landing/*` | Text/placeholder trên surface sáng. |
| Decision | D-015, D-020, D-022 | Tách palette Portal, demo one-click và quyết định light-only. |

## Dependencies, kiểm chứng và handoff

- Peer confirmation: user đã chọn light-only trong phiên 2026-07-19.
- Shared resource: frontend global theme; release sau khi checks pass.
- Commands: `npm run test`, `npm run lint`, `npm run typecheck`, `npm run build`; kiểm tra browser với system light và dark.
- Rollback: revert D-022/theme patch để quay lại behavior system-driven; không có state runtime/cloud.
- Evidence / handoff:
  - `npm run test`: 4 files, 88 tests passed.
  - `npm run lint`, `npm run typecheck`, `npm run build`: passed.
  - `python scripts/ci/validate_repo.py` và `git diff --check`: passed.
  - Browser local với `prefers-color-scheme: dark`: `color-scheme=light`, body `rgb(248, 250, 252)`, Portal text `rgb(41, 35, 30)`, heading `rgb(13, 27, 61)`; desktop và 390px không có horizontal overflow. Login dialog và Copilot workspace giữ surface/text light.
  - “Vào demo ngay” nay luôn tạo demo session, đóng dialog và gọi `openCopilot()`; state điều hướng có điều kiện đã được bỏ theo D-020.
- Claims đã release: frontend global theme sau khi peer review/merge.
