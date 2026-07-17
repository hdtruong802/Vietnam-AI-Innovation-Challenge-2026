# Context Pack — local-20260717-expand-team-overview

> Task Record local để mở rộng cẩm nang bootstrap nội bộ. Không ghi secret, trạng thái GitHub chưa xác nhận hoặc khả năng ứng dụng chưa tồn tại.

## Identity

- Task ID: `local-20260717-expand-team-overview` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex (theo yêu cầu hiện tại của team)
- Mode hiện tại: `handoff`
- Base ref / commit: `b3aac84`
- Branch / worktree: `truong` / workspace local hiện tại

## Mục tiêu và ranh giới

- Mục tiêu: viết lại overview local thành cẩm nang vận hành tiếng Việt, giải thích cụ thể capability đã tích hợp, vấn đề, thời điểm/cách dùng và giới hạn.
- Non-goals: sửa README/protocol/source-of-truth, tạo capability mới, chạy detector, thay đổi GitHub remote/CI/CD, hoặc suy diễn stack/product state.
- Acceptance criteria:
  - [x] Overview có sections cụ thể cho Impeccable, context, protocol, quality/security, GitHub-ready và deployment.
  - [x] Mọi command/interface trong overview khớp artifact hiện có; remote state và các phần `TBD` được ghi rõ.
  - [x] Quick start, flow text, links nội bộ, Git ignore, guard và diff check đều hợp lệ.
- Constraints: cẩm nang local-only, 2–3 trang Markdown, tiếng Việt, chỉ dùng facts hiện có; không commit/push hoặc cài tool.
- Stop condition / blocker cần hỏi peer: không có thêm; dùng `TBD` cho fact chưa được xác nhận.

## Scope đã claim

- Files/areas được phép chạm: `.temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, Context Pack này.
- API, schema hoặc contract liên quan: command contract hiện có của repository guard và Impeccable wrapper, chỉ mô tả lại.
- Không được chạm: README, `AGENTS.md`, team protocol, scripts, `.github/`, `.impeccable/`, remote settings, secrets/data.
- Risk: `isolated`
- Decision Log liên quan: `Không có`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Intake và protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md`, `.agents/playbooks/` | Mô tả prompt gate, Task Record, mode, claims, worktree và handoff. |
| Context vận hành | `docs/ai/{PROJECT_CONTEXT,ARCHITECTURE,TEAM,DEMO,SECRETS_AND_DATA,DEPLOYMENT,DECISIONS}.md` | Phân biệt capability bootstrap với product/stack/deploy vẫn `TBD`. |
| Quality / GitHub | `scripts/ci/validate_repo.py`, `.github/repository-settings.json`, `.github/BRANCH_RULES.md`, `scripts/github/sync-repo-settings.ps1` | Diễn giải guard và artifact prepared-only chính xác. |
| Impeccable | `docs/design/README.md`, `.agents/playbooks/impeccable-audit.md`, `scripts/design/impeccable-audit.mjs`, `.impeccable/config.json` | Diễn giải CLI, reports, exit, waiver và giới hạn. |

## Dependencies và resource claim

- Depends on / blocked by: không có.
- Shared resource: `none`.
- Claim owner + thời hạn: Codex trong turn hiện tại; release khi handoff.
- Cách thông báo peer và điều kiện release: cẩm nang nằm trong folder ignored dùng cho onboarding local; handoff ghi rõ không publish.

## Kiểm chứng và handoff

- Commands / manual checks: link check overview, `git check-ignore .temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, `python scripts/ci/validate_repo.py`, `git diff --check`.
- Demo impact và rollback: không ảnh hưởng runtime/demo; rollback là phục hồi overview cũ hoặc xóa local doc.
- Evidence / kết quả: local Markdown link check pass; `git check-ignore --verbose .temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md` xác nhận `.gitignore:65:.temp_docs/`; `python scripts/ci/validate_repo.py` pass; `git diff --check` pass. Không gọi detector, network, `gh` hay remote.
- Files, API và resources đã chạm: `.temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, Context Pack này.
- Claims đã release: `released` — không có port, DB, model hoặc demo resource chung được giữ.
- Việc tiếp theo hoặc peer có thể tiếp nhận: dùng cẩm nang cho onboarding, cập nhật khi product/stack/remote workflow được chốt.
