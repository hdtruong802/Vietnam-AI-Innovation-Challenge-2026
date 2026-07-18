# Context Pack — local-20260717-repo-readiness

## Identity

- Task ID: `local-20260717-repo-readiness` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex trong phiên hiện tại
- Mode hiện tại: `review`
- Status: `blocked` — remote `main`/`dev` thay đổi sau fetch cuối và chạm shared docs cùng scope.
- Base ref / commit: `truong` / `75b815531a9a9fab2f71ec9339b9b25bc8bc513a`
- Branch / worktree: `truong` / working tree hiện tại
- AI Log member / tool binding: `chưa bật cho clone hiện tại`

## Mục tiêu và ranh giới

- Mục tiêu: hoàn thiện AI Log pull-ready, đồng bộ tài liệu và kiểm chứng repo để sẵn sàng review trước khi publish nhánh `truong`.
- Non-goals: không stage, commit, push, merge, rebase, đổi HEAD, đăng nhập lại GitHub hoặc thay đổi remote settings.
- Acceptance criteria: onboarding một lệnh và `doctor --strict` hoạt động; guard áp dụng theo policy có mặt trong từng commit; tài liệu hiện hành đồng bộ; `team_docs/phancong.md` được khôi phục; chỉ cache Python ignored bị xóa; toàn bộ check local pass; remote và conflict được rà lại read-only.
- Constraints: giữ mọi Context Pack làm historical record; không lưu session đầy đủ, phản hồi agent, path tuyệt đối, screenshot, secret hoặc PII; bảo toàn thay đổi local hiện có của người dùng.
- Stop condition / blocker cần hỏi peer: dừng nếu remote mới tạo conflict, test/guard không thể khắc phục trong scope, phát hiện secret/PII, hoặc cần xóa file ngoài `__pycache__`/`*.pyc` ignored.

## Scope đã claim

- Files/areas được phép chạm: `scripts/ai_log/`, `tests/ai_log/`, `evidence/ai-log/`, `.githooks/`, repository guard/tests/workflow, tài liệu protocol/context hiện hành, `team_docs/`, Context Pack README và pack của task này.
- API, schema hoặc contract liên quan: `PromptEvent`, `CommitEvidence`, AI Log CLI, local Git hook contract và history-validation policy.
- Không được chạm: lịch sử Git, nội dung các Context Pack hoàn tất khác, application code chưa scaffold, remote GitHub state và raw agent sessions.
- Risk: `shared`
- Decision Log liên quan: D-009; D-006, D-007 và D-008 chỉ được rà tính nhất quán.

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Project context | `docs/ai/PROJECT_CONTEXT.md` | Xác nhận team sáu người, ba MVP và trạng thái kiến trúc. |
| Architecture / decision | `docs/ai/ARCHITECTURE.md`, `docs/ai/DECISIONS.md` | Giữ D-006 Proposed và cập nhật đúng D-009. |
| Protocol | `AGENTS.md`, `docs/ai/TEAM_PROTOCOL.md` | Đồng bộ onboarding, evidence và handoff ngang hàng. |
| Source / tests | `scripts/ai_log/`, `scripts/ci/validate_repo.py`, `tests/` | Implement và kiểm chứng CLI/hook/guard. |

## Dependencies và resource claim

- Depends on / blocked by: định dạng source local phải là JSON/JSONL có metadata workspace đọc được, hoặc dùng manual mode.
- Shared resource: local Git config `core.hooksPath` chỉ được thay trong temporary test repositories; clone hiện tại giữ nguyên ở trạng thái review-only.
- Claim owner + thời hạn: Codex, chỉ trong lượt task này.
- Cách thông báo peer và điều kiện release: handoff nêu rõ diff/check/remote; release sau khi verify hoàn tất.

## Kiểm chứng và handoff

- Commands / manual checks: AI Log tests, repository-guard tests, Impeccable tests, default/range guard, `git diff --check`, Markdown/UTF-8/stale-term audit, cache cleanup và remote/conflict read-only checks.
- Demo impact và rollback: không ảnh hưởng demo application; rollback bằng cách bỏ các thay đổi chưa commit thuộc pack này.
- Evidence / kết quả: AI Log tests 11/11 pass; repository-guard tests 11/11 pass; Impeccable tests 6/6 pass; default guard và `git diff --check` pass. Fetch cuối: `origin/main=731076d`, `origin/dev=c1034ff`, `origin/truong=75b8155`. Remote có 5.704 path thay đổi so với local HEAD và overlap `.gitignore`, `docs/ai/ARCHITECTURE.md`, `docs/ai/DECISIONS.md`, `docs/ai/PROJECT_CONTEXT.md`; D-005/architecture/application status có semantic conflict nên chưa sẵn sàng commit/push.
- AI-Log ID + capture status: `chưa có`
- Files, API và resources đã chạm: AI Log CLI/hooks/policy/tests/guard; protocol/context/docs hiện hành; `team_docs/phancong.md`; ba link `diagram_v3.mmd`; Context Pack README.
- Claims đã release: source scope đã release; remote integration chưa claim.
- Việc tiếp theo hoặc peer có thể tiếp nhận: thống nhất D-005/D-006 và application status với thay đổi mới trên `origin/main`, resolve bốn path overlap trên branch/worktree tích hợp, rồi chạy lại full checks trước commit/push.
