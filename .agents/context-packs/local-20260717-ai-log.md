# Context Pack — local-20260717-ai-log

## Identity

- Task ID: `local-20260717-ai-log` | GitHub Issue: `chưa publish`
- Owner tạm thời: Codex (implementer hiện tại; không có quyền cao hơn peer)
- Mode hiện tại: `verify-demo`
- Base ref / commit: `truong` / `75b815531a9a9fab2f71ec9339b9b25bc8bc513a`
- Branch / worktree: `truong` / working tree hiện tại theo yêu cầu người dùng

## Mục tiêu và ranh giới

- Mục tiêu: thêm AI Log đa-agent chỉ lưu prompt người dùng gắn với repo và ánh xạ chúng vào commit.
- Non-goals: không lưu transcript/session đầy đủ, phản hồi agent, tool output, chain-of-thought, screenshot; không tạo dashboard, MCP, daemon, remote setting hoặc push.
- Acceptance criteria: CLI/hook portable cho Codex, Claude, Cursor và Antigravity; record/schema/guard/tests hoạt động local; commit lỗi capture chỉ cảnh báo và không làm lộ secret/PII.
- Constraints: policy repo là baseline; Python standard library; state/source path chỉ ở `.ai-log/` ignored; không tự quét home; giữ nguyên thay đổi local hiện có.
- Stop condition / blocker cần hỏi peer: dừng nếu cần commit raw session/PII, thêm vendor-native hook, thay remote enforcement hoặc đọc source chưa được `bind` rõ ràng.

## Scope đã claim

- Files/areas được phép chạm: `evidence/ai-log/`, `scripts/ai_log/`, `.githooks/`, tests AI Log/guard, `.gitignore`, protocol/context template, repository guard workflow/script, README và Decision Log.
- API, schema hoặc contract liên quan: `PromptEvent`, `CommitEvidence`, Git commit trailers và CLI AI Log; không đổi product public API.
- Không được chạm: application architecture/public endpoints, `team_docs/`, remote GitHub state, raw agent session hoặc cấu hình native của vendor.
- Risk: `shared`
- Decision Log liên quan: `D-009`

## Context được chọn lọc

| Nguồn | File / line / ref | Lý do cần đọc |
| --- | --- | --- |
| Team protocol | `docs/ai/TEAM_PROTOCOL.md` | Git, handoff, peer-equal và shared workflow |
| Data policy | `docs/ai/SECRETS_AND_DATA.md` | Secret/PII và evidence được phép lưu |
| Repository guard | `scripts/ci/validate_repo.py` | Mở rộng validation và history gate |
| Context template/playbooks | `.agents/context-packs/TEMPLATE.md`, `.agents/playbooks/implement-handoff.md` | Đồng bộ Task Record/handoff |
| Phoenix reference | `https://phoenix.note.transformerlabs.ai` và ảnh người dùng cung cấp | Chỉ tham khảo cách trình bày bảng log |

## Dependencies và resource claim

- Depends on / blocked by: không có dependency runtime mới; Git và Python hiện có.
- Shared resource: Git hook contract và evidence schema.
- Claim owner + thời hạn: Codex, trong task hiện tại; release sau handoff.
- Cách thông báo peer và điều kiện release: D-009 + tài liệu sử dụng; release khi tests/guard/diff check pass.

## Kiểm chứng và handoff

- Commands / manual checks: AI Log tests `6/6` pass; repository-guard tests `10/10` pass; Impeccable wrapper tests `6/6` pass; hook/commit/index smoke chạy trong temporary Git repo; `git diff --check` pass. Default repository guard chỉ còn fail do `diagram_v3.mmd` đang thiếu ngoài scope task.
- Demo impact và rollback: không ảnh hưởng product demo; rollback bằng bỏ `core.hooksPath` local và revert artifact AI Log.
- Evidence / kết quả: CLI prompt-only, bốn adapter, schemas/policy, common Git hooks, dashboard index, D-009, guard/history gate và tests đã hoàn tất local. Working tree hiện tại chưa bật `core.hooksPath` và chưa có remote mutation.
- Files, API và resources đã chạm: `evidence/ai-log/`, `scripts/ai_log/`, `.githooks/`, tests/guard/workflow, `.gitignore`, AGENTS/protocol/template/handoff, README, Decision và data policy.
- Claims đã release: AI Log schema/hook/guard contract đã release cho peer review; không giữ runtime/port/account claim.
- Việc tiếp theo hoặc peer có thể tiếp nhận: peer review D-009; sau adoption, từng member chạy setup/bind với source local của chính mình và team đặt marker CI khi quyết định publish.
