# Context Pack — local-20260717-team-docs

## Identity

- Task ID: `local-20260717-team-docs` | GitHub Issue: chưa publish
- Owner tạm thời: Codex
- Mode hiện tại: `verify-demo`
- Base ref / commit: `truong` / `75b8155`
- Branch / worktree: `truong` / working tree hiện tại theo yêu cầu

## Mục tiêu và ranh giới

- Mục tiêu: đổi tên `.temp_docs/` thành `team_docs/` và bỏ thư mục tài liệu team khỏi Git ignore.
- Non-goals: không sửa nội dung tài liệu, không commit/push, không thay source-of-truth hoặc remote state.
- Acceptance criteria: bốn file được chuyển nguyên vẹn; `.temp_docs/` không còn; `team_docs/` tồn tại và không bị ignore; repository guard và whitespace checks pass.
- Constraints: policy repo là baseline; giữ nguyên thay đổi đang tồn tại của người dùng; không ghi đè destination/file trùng tên.
- Stop condition / blocker cần hỏi peer: `team_docs/` đã tồn tại, có file trùng tên, move ra ngoài workspace hoặc cần sửa nội dung tài liệu.

## Scope đã claim

- Files/areas được phép chạm: `.gitignore`, `.temp_docs/`, `team_docs/` và Context Pack này.
- API, schema hoặc contract liên quan: không có.
- Không được chạm: nội dung Markdown trong thư mục tài liệu, application source, remote GitHub và các thay đổi dirty khác.
- Risk: `isolated`
- Decision Log liên quan: không có.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Quy tắc chung | `AGENTS.md` | Quy định Task Record, local-only và handoff. |
| Protocol | `docs/ai/TEAM_PROTOCOL.md` | Quy tắc resource claim và tránh conflict. |
| Ignore policy | `.gitignore` dòng 64–65 | Rule local-only cần được gỡ. |

## Dependencies và resource claim

- Depends on / blocked by: destination `team_docs/` phải chưa tồn tại; đã xác nhận trước khi implement.
- Shared resource: `none`
- Claim owner + thời hạn: Codex giữ claim đường dẫn tài liệu và `.gitignore` đến hết turn này.
- Cách thông báo peer và điều kiện release: release sau khi kiểm tra file count/hash, ignore state và guard.

## Kiểm chứng và handoff

- Commands / manual checks: `git check-ignore`, so sánh hash/count trước-sau, `python scripts/ci/validate_repo.py`, unit tests repository guard và `git diff --check`.
- Demo impact và rollback: không ảnh hưởng runtime; rollback bằng cách đổi tên lại và khôi phục ignore rule.
- Evidence / kết quả: destination không tồn tại trước move; bốn file được chuyển và giữ nguyên hash tại thời điểm move; `.temp_docs/` không còn; `team_docs/` không bị ignore; local links pass; repository guard pass; 8 unit tests pass; `git diff --check` pass. Bốn single trailing spaces có sẵn trong `proposal.md` được giữ nguyên vì task không cho phép sửa nội dung.
- Files, API và resources đã chạm: `.gitignore`, đường dẫn `.temp_docs/` -> `team_docs/`, ba tham chiếu trạng thái/đường dẫn hiện hành trong `team_docs/phancong.md`, và Context Pack này. Không thay API/schema.
- Claims đã release: claim `.gitignore` và đường dẫn tài liệu đã release.
- Việc tiếp theo hoặc peer có thể tiếp nhận: review bốn tài liệu đang xuất hiện trong Git status, xử lý whitespace cũ bằng Task Record riêng nếu cần, rồi quyết định commit/publish.
