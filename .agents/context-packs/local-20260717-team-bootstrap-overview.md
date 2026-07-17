# Context Pack — local-20260717-team-bootstrap-overview

> Task Record local cho tài liệu giới thiệu bootstrap nội bộ. Không ghi secret, dữ liệu nhạy cảm hoặc trạng thái GitHub chưa được xác minh.

## Identity

- Task ID: `local-20260717-team-bootstrap-overview` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex (theo yêu cầu hiện tại của team)
- Mode hiện tại: `handoff`
- Base ref / commit: `b3aac84`
- Branch / worktree: `truong` / workspace local hiện tại

## Mục tiêu và ranh giới

- Mục tiêu: tạo một overview tiếng Việt, ngắn gọn cho thành viên mới về bootstrap hiện có, vấn đề được giải quyết và cách dùng; đặt trong `.temp_docs/` không được commit.
- Non-goals: thay đổi README/protocol, tạo policy mới, mô tả application/stack chưa tồn tại, khẳng định GitHub remote/CI/CD đã được bật hoặc thực hiện remote mutation.
- Acceptance criteria:
  - [x] Có `.temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md` với bảng “Đã có / Giải quyết vấn đề / Cách dùng” và quick start năm bước.
  - [x] Tài liệu nêu rõ phần `TBD` và chỉ mô tả facts có bằng chứng trong repo.
  - [x] `.temp_docs/` bị Git ignore; README không thay đổi.
  - [x] Guard, ignore check và `git diff --check` pass.
- Constraints: tài liệu local-only, bằng tiếng Việt, dùng link tương đối; không commit, push, cài công cụ hoặc đổi remote.
- Stop condition / blocker cần hỏi peer: không có thêm; điền `TBD` nếu một thông tin không được xác nhận trong repo.

## Scope đã claim

- Files/areas được phép chạm: `.temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, `.gitignore`, Context Pack này.
- API, schema hoặc contract liên quan: không có.
- Không được chạm: README, application code, protocol, remote/GitHub settings, secrets/data.
- Risk: `isolated`
- Decision Log liên quan: `Không có`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Bootstrap chung | `README.md`, `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Mô tả protocol peer-equal, intake gate, Task Record và flow local-first. |
| Context vận hành | `docs/ai/{PROJECT_CONTEXT,ARCHITECTURE,DECISIONS,TEAM,DEMO,SECRETS_AND_DATA,DEPLOYMENT}.md` | Phân biệt artifact đã có với product/stack/deploy vẫn `TBD`. |
| Quality/GitHub | `scripts/ci/validate_repo.py`, `.github/{BRANCH_RULES,LABELS,repository-settings}.json`, `scripts/github/sync-repo-settings.ps1` | Mô tả guard và cấu hình sẵn sàng publish, không khẳng định remote đã áp dụng. |
| Design audit | `docs/design/README.md`, `scripts/design/impeccable-audit.mjs` | Mô tả Impeccable là CLI advisory portable. |

## Dependencies và resource claim

- Depends on / blocked by: không có.
- Shared resource: `none`.
- Claim owner + thời hạn: Codex trong turn hiện tại; release khi handoff.
- Cách thông báo peer và điều kiện release: file nằm trong folder ignore, dùng để trình bày nội bộ; handoff ghi rõ không publish.

## Kiểm chứng và handoff

- Commands / manual checks: `git check-ignore .temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, `python scripts/ci/validate_repo.py`, `git diff --check`.
- Demo impact và rollback: không ảnh hưởng runtime/demo; rollback là xóa tài liệu local và dòng ignore nếu team không còn cần.
- Evidence / kết quả: `git check-ignore --verbose .temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md` xác nhận `.gitignore:65:.temp_docs/`; `python scripts/ci/validate_repo.py` pass; `git diff --check` pass. Không gọi network, `gh`, remote hoặc cài công cụ.
- Files, API và resources đã chạm: `.temp_docs/TEAM_BOOTSTRAP_OVERVIEW.md`, `.gitignore`, Context Pack này.
- Claims đã release: `released` — không có port, DB, model hoặc demo resource chung được giữ.
- Việc tiếp theo hoặc peer có thể tiếp nhận: chia sẻ file nội bộ trong buổi onboarding; cập nhật lại khi stack/MVP/GitHub workflow được chốt.
